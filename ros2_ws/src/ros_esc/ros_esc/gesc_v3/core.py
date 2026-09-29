"""One control owner, with local research state and optional numerical work.

Availability is independent from candidate qualification. Losing a fit never
revokes a fresh direction; losing essential input produces a recoverable zero.
This module knows no ROS graph, recorder, simulator field or device driver.
"""

from collections import deque
from dataclasses import dataclass
import math

import numpy as np

from .records import Command, CoreConfig, Event
from .numerics.basin import BasinSample, EstimatorConfig
from .numerics.evidence import MovingRawEvidence, RawObservation
from .numerics.escape import (
    EscapeGeometry, EscapeProgressTracker, FillAvoidance, Pose2D, RecenterControlConfig,
    approach_continuity_evidence, latch_direct_escape_direction,
    recent_approach, recenter_command, command_sweep_is_safe,
)
from .numerics.fill import PreparationInput, compute_fill_proposal
from .numerics.fill_design import FillDesignConfig
from .numerics.gesc import InstantaneousGesc
from .numerics.objective import AffineTerm, compose_cost
from .numerics.recurrent import RecurrentGeometryDetector
from .numerics.registry import FillRegistry, RegistryConfig
from .numerics.rolling import (
    DemodulatedSample, DirectionObservation, RollingGesc, compute_coherence,
)
from .numerics.verification import tracking_command


def ns(seconds):
    return round(seconds * 1_000_000_000)


@dataclass(frozen=True)
class Candidate:
    identity: int
    center: tuple
    confirmed: float
    started: float
    collection_started: float | None = None


class V3Core:
    """Call from a single executor thread; worker results are immutable data."""

    def __init__(self, controller, worker, config=CoreConfig()):
        self.config, self.controller, self.worker = config, controller, worker
        self.availability, self.activity = 'WAITING_INPUT', 'SEARCH'
        self.reason = 'initial_inputs'
        self.events, self.fill_events = deque(maxlen=1024), deque(maxlen=64)
        self.pose = self.observation = None
        self.pose_received = self.observation_received = -math.inf
        self.last_tick = None
        self.source_instance = None
        self.retired_sources = deque(maxlen=16)
        self.epoch = self.candidate_sequence = self.objective_revision = 0
        self.candidate = self.pending_fill = None
        self.ready_proposal = self.design_started = None
        self.pending_key = self.last_coherence_key = None
        self.registry = FillRegistry(RegistryConfig(
            maximum_cluster_samples=config.maximum_snapshot))
        self.gesc = InstantaneousGesc(omega=config.washout_omega,
                                     arm_length_m=config.sensor_radius)
        self.rolling = RollingGesc()
        self.detector = RecurrentGeometryDetector()
        self.evidence = MovingRawEvidence(max_observations=config.maximum_history,
                                          max_snapshot=config.maximum_snapshot)
        self.samples = {}
        self.pose_history = deque(maxlen=config.maximum_history)
        self.filled_costs, self.affine_terms = [], ()
        self.escape_tracker = self.escape_direction = None
        self.pending_search = None
        self.escape_assisted = False
        self.motion_anchor = None
        self.last_objective = self.last_direction = None
        self.command = Command()

    @property
    def terminal(self):
        return self.availability in ('STOPPED', 'FAULTED')

    def emit(self, now, kind, reason):
        self.events.append(Event(now, kind, self.activity, str(reason)))

    def _availability(self, now, state, reason):
        if (state, reason) != (self.availability, self.reason):
            self.availability, self.reason = state, reason
            self.emit(now, 'availability', f'{state}: {reason}')

    def fault(self, now, reason):
        if not self.terminal:
            self.cancel_candidate(now, reason)
            self._availability(now, 'FAULTED', reason)
        self.command = Command()
        return self.command

    def stop(self, now):
        self.cancel_candidate(now, 'operator_stop')
        self._availability(now, 'STOPPED', 'operator_stop')
        self.command = Command()
        return self.command

    def _search_epoch(self, now, reason):
        self.epoch += 1
        self.detector.start_epoch(str(self.epoch), ns(max(0., now)))
        self.evidence.start_epoch(str(self.epoch), ns(max(0., now)))
        self.samples.clear()
        self.emit(now, 'search_epoch', reason)

    def update_pose(self, pose, now, steady, *, receipt_steady=None):
        """Evaluate freshness now while retaining the original callback receipt."""
        receipt = steady if receipt_steady is None else receipt_steady
        if self.terminal or not pose.valid():
            return False
        if self.pose is not None and pose.frame != self.pose.frame:
            self.fault(now, 'pose_frame_changed')
            return False
        if (not 0 <= now-pose.stamp <= self.config.input_expiry
                or not 0 <= steady-receipt <= self.config.input_expiry):
            return False
        if self.pose is not None and pose.stamp <= self.pose.stamp:
            return False
        self.pose, self.pose_received = pose, receipt
        self.pose_history.append(Pose2D(pose.stamp, pose.x, pose.y, pose.yaw))
        if self.activity == 'SEARCH' and self.source_instance is not None and self._fresh(now, steady) is None:
            try:
                for result in self.detector.update(ns(pose.stamp), (pose.x, pose.y), pose.frame):
                    if result.confirmed_event:
                        boundary = result.end_ns if result.end_ns is not None else result.stamp_ns
                        self.begin_candidate(tuple(result.mean_xy), boundary*1e-9, now)
                        break
            except (ValueError, ArithmeticError, np.linalg.LinAlgError):
                self._search_epoch(pose.stamp, 'detector_data_rejected')
        return True

    def ingest_observation(self, observation, now, steady, *, receipt_steady=None):
        """Use current evaluation time, without renewing a queued sample's age."""
        receipt = steady if receipt_steady is None else receipt_steady
        if self.terminal or not observation.valid():
            return False
        expiry = self.config.input_expiry
        if (not 0 <= now-observation.stamp <= expiry
                or not 0 <= now-observation.receipt_stamp <= expiry
                or not 0 <= steady-receipt <= expiry
                or observation.pose_support_age > .05
                or observation.phase_support_age > .05):
            return False
        if self.pose is not None and observation.pose.frame != self.pose.frame:
            self.fault(now, 'observation_frame_conflict')
            return False
        if observation.source_instance in self.retired_sources:
            return False
        if observation.source_instance != self.source_instance:
            if self.observation is not None and observation.stamp <= self.observation.stamp:
                return False
            if self.source_instance is not None:
                self.retired_sources.append(self.source_instance)
            self.source_instance = observation.source_instance
            self.observation = None
            self.gesc.reset()
            self.rolling.invalidate('source_restart')
            self.cancel_candidate(now, 'source_restart')
            self._search_epoch(observation.stamp, 'source_restart')
        old = self.observation
        if old is not None and (observation.stamp <= old.stamp
                                or observation.sequence <= old.sequence):
            return False  # receipt of a duplicate never refreshes control
        if old is not None and observation.stamp-old.stamp > expiry:
            self.cancel_candidate(now, 'observation_gap')
            self._search_epoch(observation.stamp, 'observation_gap')
        if self.pending_search is not None:
            self.cancel_candidate(now, self.pending_search)
        # Apply prepared objective changes at a new real sample, never by
        # replaying an old direction or pausing for a worker acknowledgment.
        if self.ready_proposal is not None and self._fresh_pose(now, steady):
            self._check_design_motion(now)
            if (self.candidate is not None
                    and math.dist((observation.pose.x, observation.pose.y), self.candidate.center)
                    > self.config.candidate_radius):
                self.cancel_candidate(now, 'design_observation_neighborhood_left')
            if self.ready_proposal is not None:
                self._commit_proposal(self.ready_proposal, now)
        try:
            objective = compose_cost(observation.raw_cost,
                (observation.sensor_x, observation.sensor_y), observation.stamp,
                fills=tuple(c.active_fill for c in self.registry.active_clusters),
                affine_terms=self.affine_terms,
                sensor_weight=0. if self.activity == 'ESCAPE' else 1.,
                affine_weight=1. if self.activity == 'ESCAPE' else 0.)
            demod = self.gesc.update(ns(observation.stamp), objective.augmented,
                                     observation.phase)
            world_phase = observation.pose.yaw + observation.phase
            direction_observation = DirectionObservation(
                observation.sequence, ns(observation.stamp), ns(observation.receipt_stamp),
                observation.pose.yaw, world_phase, self.objective_revision,
                observation.pose.frame)
            self.rolling.update(DemodulatedSample(direction_observation,
                                                  demod.direction_body))
        except (ValueError, ArithmeticError):
            self.emit(now, 'sample_rejected', 'invalid_objective_or_demodulation')
            return False
        self.observation, self.observation_received = observation, receipt
        self.last_objective = objective
        stamp = ns(observation.stamp)
        # Raw evidence is never replaced by augmented objective values.
        record = RawObservation(observation.sequence+1, observation.sequence+1,
            stamp, observation.pose.x, observation.pose.y, observation.raw_cost,
            world_phase, base_yaw_rad=observation.pose.yaw)
        state = 2 if self.activity == 'SEARCH' else 3
        self.evidence.add(record, state, stamp)
        self.samples[stamp] = BasinSample(observation.stamp, observation.pose.x,
            observation.pose.y, observation.pose.yaw, math.nan, False,
            observation.raw_cost, math.nan, False, state)
        while len(self.samples) > self.config.maximum_history:
            self.samples.pop(next(iter(self.samples)))
        return True

    def begin_candidate(self, center, confirmed, now):
        """Internal detector transition; no extra owner or acknowledgment."""
        if self.terminal or self.candidate is not None:
            return
        if len(center) != 2 or not all(math.isfinite(v) for v in center):
            return
        self.candidate_sequence += 1
        self.candidate = Candidate(self.candidate_sequence, center, confirmed, now)
        self.activity = 'VERIFY'
        self.motion_anchor = self.pose
        self.emit(now, 'candidate', 'recurrent_geometry_confirmed')

    def cancel_candidate(self, now, reason):
        active = self.candidate is not None or self.activity != 'SEARCH'
        self.candidate = self.pending_fill = self.pending_key = None
        self.ready_proposal = self.design_started = None
        self.escape_tracker = self.escape_direction = None
        self.pending_search = None
        self.escape_assisted = False
        if self.activity == 'ESCAPE':
            self._reset_objective('escape_finished')
        self.affine_terms = ()
        self.activity, self.motion_anchor = 'SEARCH', None
        if active:
            self.emit(now, 'candidate_cancelled', reason)
            self._search_epoch(now, reason)

    def _reset_objective(self, reason):
        self.objective_revision += 1
        self.gesc.reset()
        self.rolling.invalidate(reason)
        self.last_direction = None

    def _fresh_pose(self, now, steady):
        return (self.pose is not None
                and 0 <= now-self.pose.stamp <= self.config.input_expiry
                and 0 <= steady-self.pose_received <= self.config.input_expiry)

    def _fresh(self, now, steady):
        if self.pose is None or self.observation is None:
            return 'missing_pose_or_direction'
        e = self.config.input_expiry
        for label, source, received in (
                ('pose', self.pose.stamp, self.pose_received),
                ('direction', self.observation.stamp, self.observation_received),
                ('observation_receipt', self.observation.receipt_stamp, self.observation_received)):
            if not 0 <= now-source <= e or not 0 <= steady-received <= e:
                return f'{label}_expired'
        return None

    def _poll_worker(self, now):
        result = self.worker.poll()
        if result is None:
            return
        if not result.key:
            self.emit(now, 'numerical_unavailable', result.error)
            return
        if result.key[0] == 'coherence':
            if result.error is None and result.key[1:3] == (self.epoch, self.objective_revision):
                self.rolling.apply_coherence(result.value)
            return
        if result.key != self.pending_key or self.candidate is None:
            return  # canceled/replaced work cannot mutate a registry
        if result.error is not None:
            self.cancel_candidate(now, f'fill_rejected: {result.error}')
            return
        self.ready_proposal = result.value

    def _commit_proposal(self, proposal, now):
        try:
            if proposal.registry_generation != self.registry.generation:
                raise ValueError('registry_generation_changed')
            staged = self.registry.stage_commit(dict(proposal.version_values),
                proposal.samples, cluster_id=proposal.cluster_id,
                expected_generation=proposal.registry_generation,
                exact_target=proposal.exact_target, strict=True)
            superseded, active = self.registry.commit_staged(staged)
        except (ValueError, ArithmeticError, TypeError) as exc:
            self.cancel_candidate(now, f'fill_rejected: {exc}')
            return
        self.filled_costs.append(self.pending_fill.candidate_lower)
        if superseded is not None:
            self.fill_events.append(superseded)
        self.fill_events.append(active)
        self.pending_key, self.pending_fill, self.ready_proposal = None, None, None
        self._reset_objective('fill_committed')
        self.emit(now, 'fill_created', f'fill={active.fill_id} revision={active.revision}')
        self._begin_escape(active, now)

    def _begin_escape(self, fill, now):
        history = tuple(self.pose_history)
        approach = recent_approach(history, .5)
        geometry = EscapeGeometry(fill.fill_id, *fill.center, fill.exit_radius,
                                  now, *approach)
        continuity = approach_continuity_evidence(history, fill.center, fill.exit_radius,
            interior_anchor_fallback_enabled=True, interior_anchor_min_displacement_m=.5)
        if continuity is None:
            self.cancel_candidate(now, 'escape_missing_approach_history')
            return
        selected = latch_direct_escape_direction((self.pose.x, self.pose.y),
                                                  continuity.direction, ())
        if selected is None:
            self.cancel_candidate(now, 'escape_direction_unavailable')
            return
        # This term belongs to the active escape and is removed on measured
        # completion or cancellation; elapsed time alone does not revoke it.
        self.affine_terms = (AffineTerm(tuple(fill.center),
            tuple(self.config.escape_affine_magnitude*v for v in selected.direction),
            now, maximum_age_sec=0.),)
        self.escape_direction = selected.direction
        self.escape_tracker = EscapeProgressTracker(geometry)
        self.escape_tracker.update(self.pose_history[-1])
        self.activity = 'ESCAPE'
        self.escape_assisted = False
        self.emit(now, 'escape_started', f'fill={fill.fill_id}')

    def _verify(self, now):
        candidate = self.candidate
        # Valid moving approach / coverage has no elapsed-time deadline. Fresh
        # input, neighborhood, translation and evidence validity still govern it.
        position = (self.pose.x, self.pose.y)
        if math.dist(position, candidate.center) > self.config.candidate_radius:
            self.cancel_candidate(now, 'candidate_neighborhood_left')
            return
        if any(math.dist(candidate.center, cluster.active_fill.center)
               <= max(cluster.active_fill.support_radius, cluster.active_fill.exit_radius)
               for cluster in self.registry.active_clusters):
            self.cancel_candidate(now, 'candidate_already_filled')
            return
        if self.motion_anchor is not None and self.pose.stamp-self.motion_anchor.stamp >= .5:
            if math.dist(position, (self.motion_anchor.x, self.motion_anchor.y)) < .001:
                self.cancel_candidate(now, 'verification_translation_interrupted')
                return
            self.motion_anchor = self.pose
        if candidate.collection_started is None and math.dist(position, candidate.center) <= .08:
            self.candidate = candidate = Candidate(candidate.identity, candidate.center,
                candidate.confirmed, candidate.started, now)
        if candidate.collection_started is None:
            return
        evidence = self.evidence.evaluate(candidate.center, self.config.candidate_radius,
                                           .15, ns(candidate.confirmed))
        if not evidence.ready:
            return
        if self.registry.active_count >= 1:
            if all(evidence.summary.upper < lower for lower in self.filled_costs):
                self.emit(now, 'best_source', 'raw_interval_strictly_lower_than_filled_candidates')
            self.cancel_candidate(now, 'candidate_ranked_continue_search')
            return
        try:
            support = tuple(self.samples[r.stamp_ns] for r in evidence.records)
            self.pending_fill = PreparationInput(support, self.registry.snapshot(),
                EstimatorConfig(minimum_valid_samples=20),
                FillDesignConfig(sigma_floor_m=.5, amplitude_max=6.25, exit_sigma=2.7),
                self.registry.config, self.observation.stamp,
                evidence.summary.lower, 1.25, True, 1)
        except (KeyError, ValueError):
            self.cancel_candidate(now, 'verification_support_unavailable')
            return
        self.activity = 'DESIGN'
        self.design_started = now
        self.emit(now, 'design_started', f'samples={len(support)}')

    def _submit_work(self, now):
        if self.activity == 'DESIGN' and self.pending_key is None:
            key = ('fill', self.epoch, self.objective_revision,
                   self.candidate.identity, self.registry.generation)
            if self.worker.submit(key, compute_fill_proposal, (self.pending_fill,),
                                  timeout=self.config.preparation_timeout):
                self.pending_key = key
            return
        if self.activity != 'DESIGN':
            job = self.rolling.coherence_job()
            if job is not None:
                key = ('coherence', self.epoch, self.objective_revision, job.source_stamp_ns)
                if key != self.last_coherence_key and self.worker.submit(
                        key, compute_coherence, (job,), timeout=.5):
                    self.last_coherence_key = key

    def tick(self, now, steady):
        if self.terminal:
            return Command()
        if not all(math.isfinite(v) for v in (now, steady)) or now < 0:
            return self.fault(max(now, 0.) if math.isfinite(now) else 0., 'invalid_clock')
        if self.last_tick is not None and now < self.last_tick:
            return self.fault(now, 'clock_discontinuity')
        self.last_tick = now
        reason = self._fresh(now, steady)
        if reason is not None:
            self.cancel_candidate(now, reason)
            self._availability(now, 'WAITING_INPUT', reason)
            self.command = Command()
            # Reap optional work, but never commit a fill while input is absent.
            self._poll_worker(now)
            return self.command
        self._poll_worker(now)
        self.last_direction = self.rolling.evaluate(ns(now), self.pose.yaw, ns(self.pose.stamp))
        # The new objective resets direction history. Wait for one actual sample.
        if not self.last_direction.output_valid:
            self._availability(now, 'WAITING_INPUT', 'direction_unavailable')
            self.command = Command()
            return self.command
        self._availability(now, 'ACTIVE', 'fresh_inputs')
        if self.activity in ('VERIFY', 'DESIGN'):
            self._verify(now) if self.activity == 'VERIFY' else self._check_design_motion(now)
        self._submit_work(now)
        pose = self.pose
        try:
            if self.activity in ('VERIFY', 'DESIGN'):
                candidate = self.candidate
                elapsed = now-candidate.started
                values = tracking_command(self.controller, candidate.center,
                    (pose.x, pose.y), pose.yaw, elapsed,
                    approach=candidate.collection_started is None)
                command = Command(float(values[0]), float(values[5]))
                avoidances = tuple(FillAvoidance(fill.fill_id, fill.cluster_id,
                    *fill.center, fill.support_radius+.1)
                    for fill in (c.active_fill for c in self.registry.active_clusters))
                sweep_yaw = pose.yaw + (math.pi if command.vx < 0 else 0.)
                if not command_sweep_is_safe((pose.x, pose.y), sweep_yaw, abs(command.vx),
                                              self.config.input_expiry, avoidances):
                    self.cancel_candidate(now, 'verification_fill_corridor_unavailable')
                    command = self._search_command(now)
            elif self.activity == 'ESCAPE':
                tracker = self.escape_tracker
                progress = tracker.update(Pose2D(pose.stamp, pose.x, pose.y, pose.yaw))
                transition = None
                if progress.stable_exit:
                    transition = 'escape_complete'
                elif (progress.stalled and not self.escape_assisted
                      and self.config.direct_escape_assistance_enabled):
                    self.escape_assisted = True
                    self.emit(now, 'escape_assist', 'radial_progress_stalled')
                if transition is not None and self.pending_search is None:
                    self.pending_search = transition
                    self.emit(now, 'escape_finished', transition)
                # Change the objective on the next actual source sample. This
                # short bounded continuation avoids a synthetic transition stop.
                if self.escape_assisted:
                    distance = max(0., tracker.geometry.exit_radius-progress.radial_distance)+.5
                    linear, angular = recenter_command(self.escape_direction, pose.yaw, distance,
                        RecenterControlConfig(max_linear_velocity_mps=self.config.max_vx,
                                               max_angular_velocity_rps=self.config.max_wz))
                    command = Command(linear, angular)
                else:
                    command = self._search_command(now)
            else:
                command = self._search_command(now)
            if not command.valid():
                raise ValueError('nonfinite command')
        except (ValueError, ArithmeticError, TypeError, IndexError) as exc:
            return self.fault(now, f'invalid_controller_output: {exc}')
        self.command = Command(float(np.clip(command.vx, -self.config.max_vx, self.config.max_vx)),
                               float(np.clip(command.wz, -self.config.max_wz, self.config.max_wz)))
        return self.command

    def _check_design_motion(self, now):
        candidate = self.candidate
        # Queue contention does not extend the original finite research budget.
        if now-self.design_started > self.config.preparation_timeout:
            self.cancel_candidate(now, 'design_timeout')
        elif math.dist((self.pose.x, self.pose.y), candidate.center) > self.config.candidate_radius:
            self.cancel_candidate(now, 'design_neighborhood_left')
        elif self.motion_anchor is not None and self.pose.stamp-self.motion_anchor.stamp >= .5:
            if math.dist((self.pose.x, self.pose.y),
                         (self.motion_anchor.x, self.motion_anchor.y)) < .001:
                self.cancel_candidate(now, 'design_translation_interrupted')
            else:
                self.motion_anchor = self.pose

    def _search_command(self, now):
        pose = self.pose
        values = self.controller.controller_output(now,
            np.array([pose.x, pose.y, 0., 0., 0., pose.yaw]),
            np.asarray(self.last_direction.final_body))
        return Command(float(values[0]), float(values[5]))

    def drain_events(self):
        result = tuple(self.events)
        self.events.clear()
        return result

    def drain_fills(self):
        result = tuple(self.fill_events)
        self.fill_events.clear()
        return result
