"""Availability and research-boundary contracts for the one-owner V3 core.

Synthetic inputs and an inert worker isolate control policy. These are not
Gazebo or physical qualification, and no test starts ROS or a device.
"""
from collections import deque
from dataclasses import replace
import math
from types import SimpleNamespace

import numpy as np
import pytest

from ros_esc.gesc_v3.core import V3Core
from ros_esc.gesc_v3.records import Command, CoreConfig, Observation, Pose
from ros_esc.gesc_v3.worker import JobResult
from ros_esc.gesc_v3.numerics.objective import AffineTerm
from ros_esc.gesc_v3.numerics.rolling import compute_coherence


class Controller:
    """The original public numerical interface, with transparent finite math."""
    k_vx=.5
    k_wz=5.
    max_vx=.05
    max_wz=.3

    def controller_output(self, time, state, input_values):
        return np.array([self.k_vx*input_values[0],0.,0.,0.,0.,self.k_wz*input_values[1]])


class Worker:
    def __init__(self):
        self.ready=False
        self.permit=False
        self.results=deque()
        self.submissions=[]
        self.poll_count=0

    def poll(self):
        self.poll_count+=1
        return self.results.popleft() if self.results else None

    def submit(self, key, function, args, timeout):
        if not self.permit:
            return False
        self.submissions.append((key,function,args,timeout))
        self.permit=False
        return True


def make_core(config=None):
    return V3Core(Controller(),Worker(),config or CoreConfig())


def observation(t=10., sequence=1, *, x=0., y=0., yaw=0., phase=0.,
                raw=-2., source='sensor-A', frame='odom', receipt=None):
    pose=Pose(t,x,y,yaw,frame)
    world=yaw+phase
    return Observation(source,sequence,t,t if receipt is None else receipt,pose,
        phase,raw,x+.18*math.cos(world),y+.18*math.sin(world))


def feed(core,t=10.,sequence=1,*,steady=None,**kwargs):
    obs=observation(t,sequence,**kwargs)
    steady=t if steady is None else steady
    assert core.update_pose(obs.pose,t,steady)
    assert core.ingest_observation(obs,t,steady)
    return obs


def drive(core,t=10.,sequence=1,**kwargs):
    obs=feed(core,t,sequence,**kwargs)
    command=core.tick(t,t)
    assert core.availability=='ACTIVE' and command.vx>0
    return obs,command


def event_reasons(core):
    return [event.reason for event in core.drain_events()]


def test_first_usable_direction_drives_without_worker_recording_or_cycles():
    core=make_core()
    _,command=drive(core)
    assert command==Command(.05,0.)
    assert not core.worker.ready and not core.worker.submissions
    assert core.last_direction.completed_cycle_count==0
    assert core.last_direction.fallback_used
    assert core.gesc.previous_source_ns==10_000_000_000
    assert core.gesc.state==0.  # first source is dt=0, not wall-clock catch-up


def test_first_zero_direction_waits_then_recovers_on_real_sample():
    core=make_core();feed(core,raw=0.)
    assert core.tick(10.,10.)==Command()
    assert core.availability=='WAITING_INPUT'
    feed(core,10.2,2,raw=-2.)
    assert core.tick(10.2,10.2).vx>0 and core.availability=='ACTIVE'


def test_expired_inputs_zero_and_fresh_source_automatically_resumes():
    core=make_core();drive(core)
    assert core.tick(10.500001,10.500001)==Command()
    assert core.availability=='WAITING_INPUT' and not core.terminal
    feed(core,10.8,2,x=.01)
    assert core.tick(10.8,10.8).vx>0
    assert core.availability=='ACTIVE'


def test_paused_source_clock_still_expires_on_monotonic_receipt_age():
    core=make_core();drive(core)
    assert core.tick(10.,10.500001)==Command()
    assert core.availability=='WAITING_INPUT'


def test_duplicate_does_not_renew_original_input_age():
    core=make_core();obs,_=drive(core)
    assert not core.ingest_observation(replace(obs,receipt_stamp=10.4),10.4,10.4)
    assert core.observation_received==10.
    assert core.observation.receipt_stamp==10.
    assert core.update_pose(Pose(10.4,.01,0.,0.),10.4,10.4)
    assert core.tick(10.51,10.51)==Command()
    assert core.availability=='WAITING_INPUT'


def test_invalid_sample_is_rejected_without_destroying_fresh_control():
    core=make_core();drive(core)
    assert not core.ingest_observation(observation(10.1,2,raw=math.nan),10.1,10.1)
    assert core.tick(10.1,10.1).vx>0
    assert core.observation_received==10.
    assert core.tick(10.51,10.51)==Command()


@pytest.mark.parametrize('updates',[
    {'receipt':10.7},
    {'raw':math.inf},
])
def test_future_or_nonfinite_sample_never_admits(updates):
    core=make_core();drive(core)
    candidate=observation(10.1,2,**updates)
    assert not core.ingest_observation(candidate,10.1,10.1)
    assert core.observation.sequence==1


def test_pose_frame_change_is_terminal_and_cannot_auto_resume():
    core=make_core();drive(core)
    assert not core.update_pose(Pose(10.1,0.,0.,0.,'map'),10.1,10.1)
    assert core.availability=='FAULTED' and core.command==Command()
    assert not core.ingest_observation(observation(10.2,2),10.2,10.2)
    assert core.tick(10.2,10.2)==Command()


def test_observation_frame_conflict_is_terminal():
    core=make_core();drive(core)
    assert not core.ingest_observation(observation(10.1,2,frame='map'),10.1,10.1)
    assert core.availability=='FAULTED' and core.command==Command()


def test_clock_rollback_is_terminal():
    core=make_core();drive(core)
    assert core.tick(9.99,10.1)==Command()
    assert core.availability=='FAULTED'


def test_operator_stop_is_terminal_and_does_not_poll_or_resume():
    core=make_core();drive(core)
    polls=core.worker.poll_count
    assert core.stop(10.1)==Command()
    assert not core.ingest_observation(observation(10.2,2),10.2,10.2)
    assert core.tick(10.2,10.2)==Command()
    assert core.availability=='STOPPED' and core.worker.poll_count==polls


def test_candidate_neighborhood_failure_keeps_fresh_search_motion():
    core=make_core();drive(core)
    core.begin_candidate((2.,0.),10.,10.)
    assert core.activity=='VERIFY'
    assert core.tick(10.05,10.05).vx>0
    assert core.activity=='SEARCH' and core.availability=='ACTIVE'
    assert 'candidate_neighborhood_left' in event_reasons(core)


def test_stationary_verification_cancels_research_without_terminal_stop():
    core=make_core();drive(core)
    core.begin_candidate((.02,0.),10.,10.)
    feed(core,10.3,2)
    core.tick(10.3,10.3)
    feed(core,10.6,3)
    assert core.tick(10.6,10.6).vx>0
    assert core.activity=='SEARCH' and core.availability=='ACTIVE'
    assert 'verification_translation_interrupted' in event_reasons(core)


def test_fresh_moving_approach_continues_beyond_old_approach_and_total_deadlines():
    core=make_core();drive(core)
    core.begin_candidate((.2,0.),10.,10.)
    candidate=core.candidate
    # A moving trajectory stays in the neighborhood but outside the admission
    # radius for45s. This is a policy fixture, not a Gazebo trajectory claim.
    for index in range(1,226):
        elapsed=index*.2
        angle=.2*elapsed
        phase=2*math.pi*elapsed/3
        feed(core,10.+elapsed,index+1,x=.2-.2*math.cos(angle),
             y=.2*math.sin(angle),phase=phase,raw=-2.+.3*math.cos(phase))
        command=core.tick(10.+elapsed,10.+elapsed)
        assert core.availability=='ACTIVE' and command.valid()
        assert core.activity=='VERIFY' and core.candidate.identity==candidate.identity
        assert core.candidate.collection_started is None
    assert core.candidate.started==10.
    assert not any('timeout' in reason for reason in event_reasons(core))
    # Unlimited approach time does not make an old measurement usable.
    assert core.tick(55.500001,55.500001)==Command()
    assert core.availability=='WAITING_INPUT' and core.candidate is None


def test_moving_collection_waits_for_late_evidence_without_coverage_deadline(monkeypatch):
    core=make_core();drive(core,x=.05)
    core.begin_candidate((.03,0.),10.,10.)
    evaluate=core.evidence.evaluate
    pending=[True]
    def delayed_evidence(*args,**kwargs):
        result=evaluate(*args,**kwargs)
        return replace(result,ready=False,reason='synthetic_pending_coverage') if pending[0] else result
    monkeypatch.setattr(core.evidence,'evaluate',delayed_evidence)
    for index in range(1,226):
        elapsed=index*.2
        angle=.4*elapsed
        phase=2*math.pi*elapsed/3
        feed(core,10.+elapsed,index+1,x=.03+.02*math.cos(angle),
             y=.02*math.sin(angle),phase=phase,raw=-2.+.3*math.cos(phase))
        core.tick(10.+elapsed,10.+elapsed)
        assert core.availability=='ACTIVE' and core.activity=='VERIFY'
    assert core.candidate.started==10.
    assert core.candidate.collection_started==pytest.approx(10.2)
    # Release actual qualified evidence after45s; the same candidate proceeds
    # to bounded numerical design, with its original tracking phase intact.
    pending[0]=False
    elapsed=45.2;angle=.4*elapsed;phase=2*math.pi*elapsed/3
    feed(core,10.+elapsed,227,x=.03+.02*math.cos(angle),
         y=.02*math.sin(angle),phase=phase,raw=-2.+.3*math.cos(phase))
    core.tick(10.+elapsed,10.+elapsed)
    assert core.activity=='DESIGN' and core.pending_fill is not None
    assert core.design_started==pytest.approx(55.2)
    assert core.candidate.started==10.


def test_fill_worker_rejection_cancels_candidate_but_driving_continues():
    core=make_core();drive(core)
    core.begin_candidate((0.,0.),10.,10.)
    core.activity='DESIGN'
    core.pending_key=('fill',core.epoch,core.objective_revision,core.candidate.identity,0)
    core.worker.results.append(JobResult(core.pending_key,error='poor_support'))
    assert core.tick(10.1,10.1).vx>0
    assert core.activity=='SEARCH' and not core.terminal and core.registry.active_count==0
    assert any('poor_support' in r for r in event_reasons(core))


def test_canceled_candidate_worker_result_cannot_commit_or_renew_input():
    core=make_core();drive(core)
    core.begin_candidate((0.,0.),10.,10.)
    key=('fill',core.epoch,core.objective_revision,core.candidate.identity,0)
    core.pending_key=key
    core.cancel_candidate(10.1,'test_cancel')
    # This deliberately invalid payload must remain completely unexamined.
    core.worker.results.append(JobResult(key,value=object()))
    assert core.tick(10.2,10.2).vx>0
    assert core.registry.generation==0 and core.observation_received==10.
    assert core.tick(10.51,10.51)==Command()


def test_source_restart_does_not_allow_old_source_to_resume():
    core=make_core();drive(core)
    feed(core,10.2,1,source='sensor-B')
    assert core.tick(10.2,10.2).vx>0
    assert not core.ingest_observation(observation(10.3,2,source='sensor-A'),10.3,10.3)
    assert core.source_instance=='sensor-B' and core.observation_received==10.2


def coherent_core():
    core=make_core()
    for i in range(47):
        t=10.+i*.2
        phase=2*math.pi*i/15
        feed(core,t,i+1,x=.002*i,phase=phase,raw=-2+.3*math.cos(phase))
        core.tick(t,t)
    return core,t


def test_worker_coherence_result_does_not_renew_sample_age():
    core,t=coherent_core()
    job=core.rolling.coherence_job()
    assert job is not None
    key=('coherence',core.epoch,core.objective_revision,job.source_stamp_ns)
    core.worker.results.append(JobResult(key,value=compute_coherence(job)))
    core.tick(t+.1,t+.1)
    assert core.observation_received==t
    assert core.last_direction.observation.source_stamp_ns==round(t*1e9)
    assert core.tick(t+.500001,t+.500001)==Command()
    assert core.availability=='WAITING_INPUT'


def test_old_coherence_context_never_changes_new_objective():
    core,t=coherent_core()
    job=core.rolling.coherence_job();assert job is not None
    response=compute_coherence(job)
    old_epoch=core.epoch
    core._search_epoch(t,'replacement')
    core.worker.results.append(JobResult(('coherence',old_epoch,core.objective_revision,
                                         job.source_stamp_ns),value=response))
    core.tick(t+.1,t+.1)
    assert not core.last_direction.coherence_available
    assert core.observation_received==t


def test_numerical_jobs_use_finite_coherence_and_fill_deadlines():
    core,t=coherent_core();core.worker.permit=True
    core.tick(t+.01,t+.01)
    key,function,args,timeout=core.worker.submissions[-1]
    assert key[0]=='coherence' and timeout==.5 and len(args)==1
    core.begin_candidate((core.pose.x,0.),t,t)
    core.activity='DESIGN';core.pending_fill=object();core.worker.permit=True
    core._submit_work(t)
    key,function,args,timeout=core.worker.submissions[-1]
    assert key[0]=='fill' and timeout==5. and len(args)==1


def test_raw_evidence_preserves_actual_yaw_and_original_stamp():
    core=make_core();obs=feed(core,yaw=.4)
    record=core.evidence.records[-1]
    assert record.observation.base_yaw_rad==obs.pose.yaw
    assert record.stamp_ns==round(obs.stamp*1e9)
    assert core.samples[record.stamp_ns].yaw==obs.pose.yaw


def test_search_and_verification_do_not_apply_escape_affine_term():
    core=make_core();drive(core)
    core.affine_terms=(AffineTerm((0.,0.),(.5,0.),10.,maximum_age_sec=35.),)
    feed(core,10.2,2,x=.01)
    assert core.last_objective.augmented==pytest.approx(-2.)
    core.begin_candidate((.01,0.),10.2,10.2)
    feed(core,10.4,3,x=.02)
    assert core.last_objective.augmented==pytest.approx(-2.)


def test_escape_cancellation_clears_affine_authority():
    core=make_core();drive(core)
    core.activity='ESCAPE'
    core.affine_terms=(AffineTerm((0.,0.),(.5,0.),10.,maximum_age_sec=35.),)
    core.cancel_candidate(10.1,'escape_complete')
    assert core.activity=='SEARCH' and not core.affine_terms


def prepared_proposal(t=10.,generation=0):
    from ros_esc.gesc_v3.numerics.basin import BasinSample
    from ros_esc.gesc_v3.numerics.fill import PreparedProposal
    samples=tuple(BasinSample(t-4.+i*.2,.001*i,0.,.4,math.nan,False,
                             -2.,math.nan,False,1) for i in range(20))
    values=dict(source_timestamp=t-.2,center=(.5,0.),amplitude=1.,
        covariance=((.25,0.),(0.,.25)),sigma_major=.5,sigma_minor=.5,
        orientation=0.,support_radius=1.5,exit_radius=.4,confidence=.8,
        sample_count=20,fit_residual=.001,fit_condition_number=100.,
        fit_condition_number_valid=True,design_escalations=0)
    return PreparedProposal(tuple(values.items()),samples,None,None,generation,20,())


def arm_design(core,t=10.):
    core.begin_candidate((core.pose.x,core.pose.y),t,t)
    core.candidate=replace(core.candidate,collection_started=t)
    core.activity='DESIGN';core.design_started=t
    core.pending_fill=SimpleNamespace(candidate_lower=-2.1)
    core.pending_key=('fill',core.epoch,core.objective_revision,
                      core.candidate.identity,core.registry.generation)
    return core.pending_key


def test_fill_result_waits_for_new_sample_then_commits_without_planned_zero():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    command=core.tick(10.05,10.05)
    assert command.vx>0 and core.availability=='ACTIVE'
    assert core.registry.generation==0 and core.ready_proposal is not None
    assert core.observation.stamp==10. and core.objective_revision==0
    feed(core,10.2,2,x=.002)
    assert core.registry.generation==1 and core.registry.active_count==1
    assert core.objective_revision==1 and core.observation.stamp==10.2
    assert core.gesc.previous_source_ns==10_200_000_000
    assert core.rolling._result.observation.objective_revision==1
    assert core.rolling._result.observation.source_stamp_ns==10_200_000_000
    assert core.gesc.state==0.  # no integration across changed objective
    assert abs(core.tick(10.2,10.2).vx)>0
    assert len(core.drain_fills())==1


def test_stale_registry_generation_consumes_no_identity_or_objective():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal(generation=1)))
    core.tick(10.05,10.05)
    feed(core,10.2,2,x=.002)
    assert core.registry.generation==0 and core.registry.snapshot().next_id==1
    assert core.objective_revision==0 and not core.drain_fills()
    assert core.activity=='SEARCH' and core.tick(10.2,10.2).vx>0
    assert any('registry_generation_changed' in r for r in event_reasons(core))


def test_invalid_prepared_geometry_does_not_partially_commit():
    core=make_core();drive(core)
    key=arm_design(core)
    proposal=prepared_proposal();values=dict(proposal.version_values)
    values['amplitude']=-1.
    proposal=replace(proposal,version_values=tuple(values.items()))
    core.worker.results.append(JobResult(key,value=proposal))
    core.tick(10.05,10.05)
    feed(core,10.2,2,x=.002)
    assert core.registry.generation==0 and core.registry.active_count==0
    assert core.registry.snapshot().next_id==1 and core.objective_revision==0
    assert core.activity=='SEARCH' and core.tick(10.2,10.2).vx>0


def test_fill_completed_after_input_expiry_is_discarded_before_commit():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    assert core.tick(10.51,10.51)==Command()
    assert core.ready_proposal is None and core.pending_key is None
    feed(core,10.6,2,x=.002)
    assert core.tick(10.6,10.6).vx>0
    assert core.registry.active_count==0 and core.registry.generation==0


def test_duplicate_after_preparation_cannot_trigger_fill_commit():
    core=make_core();obs,_=drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,10.05)
    assert not core.ingest_observation(replace(obs,receipt_stamp=10.1),10.1,10.1)
    assert core.registry.generation==0 and core.observation_received==10.
    assert core.tick(10.1,10.1).vx>0


def test_design_budget_starts_when_design_started_not_candidate_start():
    core=make_core();drive(core)
    key=arm_design(core)
    # Candidate began long ago; only elapsed design computation counts here.
    core.candidate=replace(core.candidate,started=-5.)
    core.design_started=10.
    assert core.tick(10.1,10.1).vx>0 and core.activity=='DESIGN'
    # Fresh continuing translation while the optional worker remains unavailable.
    for i in range(1,27):
        t=10.+i*.2
        feed(core,t,i+1,x=.003*i)
        command=core.tick(t,t)
    assert core.activity=='SEARCH' and command.vx>0 and core.availability=='ACTIVE'
    assert 'design_timeout' in event_reasons(core)


def test_escape_uses_selected_raw_off_affine_on_weights():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,10.05);feed(core,10.2,2,x=.002)
    assert core.activity=='ESCAPE'
    value=core.last_objective
    assert value.raw==-2.
    assert value.affine!=0.
    assert value.augmented==pytest.approx(value.gaussian+value.affine)


def escaping_core(*, exit_radius=None, config=None):
    core=make_core(config);drive(core)
    key=arm_design(core)
    proposal=prepared_proposal()
    if exit_radius is not None:
        values=dict(proposal.version_values)
        values['exit_radius']=exit_radius
        proposal=replace(proposal,version_values=tuple(values.items()))
    core.worker.results.append(JobResult(key,value=proposal))
    core.tick(10.05,10.05);feed(core,10.2,2,x=.002)
    assert core.activity=='ESCAPE'
    return core


def slow_escape_beyond_former_deadline(*, direct_assistance=True):
    core=escaping_core(exit_radius=.8,
        config=CoreConfig(direct_escape_assistance_enabled=direct_assistance))
    for index in range(1,226):
        elapsed=index*.2
        stamp=10.2+elapsed
        phase=2*math.pi*elapsed/3
        feed(core,stamp,index+2,x=.002+.005*elapsed,
             phase=phase,raw=-2.+.3*math.cos(phase))
        command=core.tick(stamp,stamp)
        assert core.availability=='ACTIVE' and command.valid()
        assert core.activity=='ESCAPE' and core.pending_search is None
        if not direct_assistance:
            # Use the actual measured-cost GESC direction and the transparent
            # fixture controller; a direct heading command cannot substitute.
            direction=core.last_direction.final_body
            assert command==Command(
                float(np.clip(.5*direction[0],-.05,.05)),
                float(np.clip(5.*direction[1],-.3,.3)))
    assert core.escape_tracker.latest.stalled
    assert core.escape_assisted is direct_assistance
    assert core.last_objective.affine!=0.
    assert core.last_objective.augmented==pytest.approx(
        core.last_objective.gaussian+core.last_objective.affine)
    assert sum(event.kind=='escape_assist' for event in core.drain_events())==int(direct_assistance)
    return core,stamp,index+2


@pytest.mark.parametrize('direct_assistance',[True,False])
def test_escape_and_affine_guidance_continue_until_late_measured_spatial_exit(direct_assistance):
    core,stamp,sequence=slow_escape_beyond_former_deadline(direct_assistance=direct_assistance)
    revision=core.objective_revision
    start=stamp
    # Continue the same fresh trajectory until it crosses the frozen exit
    # radius and satisfies the actual progress / stable-exit hold criteria.
    for step in range(1,151):
        stamp=start+step*.2
        x=.227+.05*step*.2
        sequence+=1
        feed(core,stamp,sequence,x=x,phase=2*math.pi*(stamp-10.2)/3)
        core.tick(stamp,stamp)
        if core.pending_search is not None:
            break
    assert core.pending_search=='escape_complete'
    assert core.escape_tracker.latest.stable_exit
    assert core.activity=='ESCAPE' and core.objective_revision==revision
    assert core.affine_terms
    feed(core,stamp+.2,sequence+1,x=x+.01,phase=2*math.pi*(stamp+.2-10.2)/3)
    assert core.activity=='SEARCH' and not core.affine_terms
    assert core.objective_revision==revision+1
    assert core.last_objective.affine==0.
    assert not any(reason=='escape_timeout' for reason in event_reasons(core))


@pytest.mark.parametrize('direct_assistance',[True,False])
@pytest.mark.parametrize('ending',['input_expiry','operator_stop','frame_fault'])
def test_unlimited_escape_duration_preserves_actual_stop_conditions(ending,direct_assistance):
    core,stamp,_=slow_escape_beyond_former_deadline(direct_assistance=direct_assistance)
    if ending=='input_expiry':
        command=core.tick(stamp+.500001,stamp+.500001)
        assert core.availability=='WAITING_INPUT'
    elif ending=='operator_stop':
        command=core.stop(stamp+.1)
        assert core.availability=='STOPPED'
    else:
        assert not core.update_pose(Pose(stamp+.1,.227,0.,0.,'map'),stamp+.1,stamp+.1)
        command=core.tick(stamp+.1,stamp+.1)
        assert core.availability=='FAULTED'
    assert command==Command()
    assert not core.affine_terms and core.escape_tracker is None


def report_stable_exit(core):
    core.escape_tracker=SimpleNamespace(
        geometry=SimpleNamespace(started_sec=10.2,exit_radius=.4),
        update=lambda pose:SimpleNamespace(stable_exit=True,stalled=False,radial_distance=.6))


def test_escape_exit_defers_objective_change_until_new_sample_without_planned_zero():
    core=escaping_core();revision=core.objective_revision
    report_stable_exit(core)
    assert abs(core.tick(10.25,10.25).vx)>0
    assert core.availability=='ACTIVE' and core.activity=='ESCAPE'
    assert core.pending_search=='escape_complete'
    assert core.objective_revision==revision and core.affine_terms
    assert core.rolling._result.observation.source_stamp_ns==10_200_000_000
    feed(core,10.4,3,x=.004)
    assert core.objective_revision==revision+1
    assert core.activity=='SEARCH' and not core.affine_terms
    assert abs(core.tick(10.4,10.4).vx)>0 and core.availability=='ACTIVE'
    assert core.rolling._result.observation.source_stamp_ns==10_400_000_000
    assert core.gesc.state==0. and core.last_objective.affine==0.


def test_deferred_escape_transition_cannot_continue_past_input_expiry():
    core=escaping_core();report_stable_exit(core)
    assert abs(core.tick(10.25,10.25).vx)>0
    assert core.tick(10.700001,10.700001)==Command()
    assert core.availability=='WAITING_INPUT' and not core.terminal
    assert core.pending_search is None and not core.affine_terms
    feed(core,10.8,3,x=.004)
    assert abs(core.tick(10.8,10.8).vx)>0 and core.availability=='ACTIVE'


def install_known_fill(core):
    proposal=prepared_proposal()
    staged=core.registry.stage_commit(dict(proposal.version_values),proposal.samples,
        expected_generation=0,strict=True)
    _,active=core.registry.commit_staged(staged)
    core.filled_costs.append(-2.1)
    return active


def test_candidate_inside_known_fill_is_not_ranked_as_another_source(monkeypatch):
    core=make_core();drive(core,x=.5)
    install_known_fill(core)
    core.begin_candidate((.5,0.),10.,10.)
    def forbidden(*args,**kwargs):
        raise AssertionError('known-filled candidate must be suppressed before cost ranking')
    monkeypatch.setattr(core.evidence,'evaluate',forbidden)
    assert core.tick(10.05,10.05).vx>0
    assert core.activity=='SEARCH' and core.availability=='ACTIVE'
    assert not any(event.kind=='best_source' for event in core.drain_events())
    assert core.registry.generation==1 and core.registry.active_count==1


@pytest.mark.parametrize('upper,expected_best',[(-3.,True),(-2.,False)])
def test_distinct_candidate_rank_is_event_only_and_keeps_driving(monkeypatch,upper,expected_best):
    core=make_core();drive(core,x=3.)
    install_known_fill(core)
    core.begin_candidate((3.,0.),10.,10.)
    summary=SimpleNamespace(upper=upper,lower=upper)
    monkeypatch.setattr(core.evidence,'evaluate',lambda *a,**k:
        SimpleNamespace(ready=True,summary=summary))
    assert core.tick(10.05,10.05).vx>0
    assert core.activity=='SEARCH' and core.availability=='ACTIVE'
    assert any(event.kind=='best_source' for event in core.drain_events()) is expected_best
    assert core.registry.active_count==1


def test_leaving_candidate_during_design_cancels_prepared_fill_before_commit():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,10.05)
    feed(core,10.2,2,x=2.)
    assert core.registry.active_count==0 and core.registry.generation==0
    assert core.activity=='SEARCH' and core.tick(10.2,10.2).vx>0


def test_selected_escape_repulse_switches_once_to_assist_and_stall_does_not_abort():
    core=escaping_core();revision=core.objective_revision
    command=core.tick(10.21,10.21)
    assert not core.escape_assisted and command.vx<0  # selected GESC repulsion
    core.escape_tracker=SimpleNamespace(
        geometry=SimpleNamespace(started_sec=10.2,exit_radius=.4),
        update=lambda pose:SimpleNamespace(stable_exit=False,stalled=True,radial_distance=.2))
    assert core.tick(10.25,10.25).vx>0
    assert core.escape_assisted and core.pending_search is None
    assert core.activity=='ESCAPE' and core.objective_revision==revision
    assert core.tick(10.3,10.3).vx>0
    assert core.activity=='ESCAPE' and core.pending_search is None
    events=core.drain_events()
    assert sum(event.kind=='escape_assist' for event in events)==1


@pytest.mark.parametrize('value',['false',0,None])
def test_direct_escape_assistance_requires_an_actual_boolean(value):
    with pytest.raises(ValueError,match='direct_escape_assistance_enabled must be boolean'):
        CoreConfig(direct_escape_assistance_enabled=value)


def test_fresh_authoritative_observation_outside_design_radius_cannot_commit():
    core=make_core();drive(core)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,10.05)
    # The authoritative source observation can arrive before the controller's
    # independent latest-pose subscription. Both remain fresh; source geometry
    # itself already proves departure from the frozen candidate neighborhood.
    assert core.ingest_observation(observation(10.2,2,x=2.),10.2,10.2)
    assert core.registry.generation==0 and core.registry.active_count==0
    assert core.activity=='SEARCH' and core.tick(10.2,10.2).vx>0


def test_collection_admission_does_not_restart_centered_reference_phase(monkeypatch):
    import ros_esc.gesc_v3.core as core_module
    core=make_core();drive(core)
    core.begin_candidate((.05,0.),10.,10.)
    for i in range(1,11):
        feed(core,10.+i*.2,i+1,x=.004*i)
    core.candidate=replace(core.candidate,collection_started=12.)
    observed=[]
    original=core_module.tracking_command
    def capture(*args,**kwargs):
        observed.append(args[4])
        return original(*args,**kwargs)
    monkeypatch.setattr(core_module,'tracking_command',capture)
    core.tick(12.05,12.05)
    assert observed==pytest.approx([2.05])
    assert core.activity=='VERIFY'


def test_recurrent_geometry_keeps_pose_observations_between_cost_samples():
    core=make_core();drive(core)
    count=core.detector.retained_point_count
    assert core.update_pose(Pose(10.05,.001,0.,0.),10.05,10.05)
    assert core.update_pose(Pose(10.1,.002,0.,0.),10.1,10.1)
    assert core.detector.retained_point_count==count+2
    assert core.observation.stamp==10.  # no fabricated source-cost observation


def test_queued_pose_checks_detector_freshness_at_current_time_not_old_receipt():
    core=make_core()
    feed(core,10.,steady=200.05)
    count=core.detector.retained_point_count
    assert core.update_pose(Pose(10.03,.001,0.,0.),10.1,200.1,receipt_steady=200.03)
    assert core.detector.retained_point_count==count+1
    assert core.pose_received==200.03
    assert core.observation_received==200.05
    assert core._fresh(10.1,200.1) is None
    assert core._fresh(10.1,200.03)=='direction_expired'  # Previous counterexample.


def test_queued_observation_commits_ready_fill_using_current_pose_freshness():
    core=make_core()
    feed(core,10.,steady=200.)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,200.05)
    assert core.ready_proposal is not None
    assert core.update_pose(Pose(10.09,.002,0.,0.),10.1,200.1,receipt_steady=200.09)
    assert not core._fresh_pose(10.1,200.08)  # Old receipt is earlier than this pose.
    assert core.ingest_observation(observation(10.08,2,x=.001),10.1,200.1,
                                   receipt_steady=200.08)
    assert core.registry.generation==1 and core.registry.active_count==1
    assert core.observation_received==200.08 and core.pose_received==200.09
    assert core.objective_revision==1


@pytest.mark.parametrize('receipt',[199.5,200.2,math.nan])
def test_queued_receipt_age_rejection_cannot_renew_input_or_commit(receipt):
    core=make_core()
    feed(core,10.,steady=200.)
    key=arm_design(core)
    core.worker.results.append(JobResult(key,value=prepared_proposal()))
    core.tick(10.05,200.05)
    assert not core.update_pose(Pose(10.08,.002,0.,0.),10.1,200.1,receipt_steady=receipt)
    assert not core.ingest_observation(observation(10.08,2),10.1,200.1,
                                       receipt_steady=receipt)
    assert core.pose_received==core.observation_received==200.
    assert core.pose.stamp==core.observation.stamp==10.
    assert core.registry.generation==0 and core.ready_proposal is not None
    assert core.tick(10.1,200.6)==Command()
    assert core.availability=='WAITING_INPUT' and core.registry.generation==0


def test_nomination_keeps_detector_evaluation_source_time(monkeypatch):
    core=make_core();drive(core)
    result=SimpleNamespace(confirmed_event=True,mean_xy=(.001,0.),
                           stamp_ns=10_000_000_000,end_ns=10_000_000_000)
    monkeypatch.setattr(core.detector,'update',lambda *args:(result,))
    assert core.update_pose(Pose(10.1,.001,0.,0.),10.1,10.1)
    assert core.candidate is not None
    assert core.candidate.confirmed==10.
    assert core.candidate.started==10.1


@pytest.mark.parametrize('yaw,tracking_sign',[(0.,-1.),(math.pi,1.)])
def test_centered_fill_sweep_cancels_forward_or_reverse_guidance_without_stop(
        monkeypatch,yaw,tracking_sign):
    import ros_esc.gesc_v3.core as core_module
    core=make_core();install_known_fill(core)
    _,search_command=drive(core,x=2.11,yaw=yaw)
    # Candidate center is outside the existing support radius (not a reused
    # fill), but this approach would enter support_radius+.1 within .5 sec.
    core.begin_candidate((2.01,0.),10.,10.)
    proposed=[]
    original=core_module.tracking_command
    def capture(*args,**kwargs):
        values=original(*args,**kwargs)
        proposed.append(float(values[0]))
        return values
    monkeypatch.setattr(core_module,'tracking_command',capture)
    command=core.tick(10.05,10.05)
    assert len(proposed)==1 and math.copysign(1.,proposed[0])==tracking_sign
    assert core.activity=='SEARCH' and core.availability=='ACTIVE'
    assert command==search_command and abs(command.vx)>0
    assert core.registry.active_count==1 and core.registry.generation==1
    assert any(e.kind=='candidate_cancelled'
               and e.reason=='verification_fill_corridor_unavailable'
               for e in core.drain_events())


def test_centered_fill_sweep_allows_outward_translation():
    core=make_core();install_known_fill(core)
    drive(core,x=2.11)
    core.begin_candidate((2.2,0.),10.,10.)
    command=core.tick(10.05,10.05)
    assert core.activity=='VERIFY' and core.availability=='ACTIVE'
    assert command.vx>0
