"""Selected 5 Hz/20 RPM density experiment; no ROS graph or recorded inputs."""

import math
from types import SimpleNamespace

import pytest
from ros_esc_interfaces.msg import DetectorConfirmation
from ros_esc.filter_node.rolling_gesc import RollingGesc, RollingGescConfig
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence, snapshot_raw_evidence
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor, stamp
from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY, policy_descriptor, policy_config_sha256,
)
from test_rolling_gesc import feed, ns, times
from test_v2_moving_evidence import feed as feed_raw, ready


@pytest.mark.parametrize('direction', [1, -1])
def test_five_hz_twenty_rpm_mean_qualifies_without_twenty_four_samples(direction):
    moving = RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    strict = RollingGesc()
    phase = lambda t: direction * math.tau * t / 3 + .137
    for core in (moving, strict):
        feed(core, times(9.2, rate=5), phase=phase)
    result = moving.evaluate(ns(9.2), 0., ns(9.2))
    assert result.qualified and result.output_valid and result.actual_blend_weight == .75
    assert all(c.sample_count == 15 and min(c.sector_counts) == 1 for c in result.cycles)
    assert result.max_gap_ns == 200_000_000
    assert not strict.evaluate(ns(9.2), 0., ns(9.2)).qualified


def test_sparse_moving_still_requires_full_revolutions_freshness_and_finite_direction():
    core = RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    feed(core, times(2.8, rate=5))
    assert not core._result.mean_full and not core._result.qualified
    feed(core, times(9.2, rate=5)[15:])
    assert core.evaluate(ns(9.2), 0., ns(9.2)).qualified
    assert not core.evaluate(ns(9.8), 0., ns(9.8)).output_valid
    result = feed(core, [10.], vector=lambda t: (2., 0.))[-1]
    assert not result.qualified and result.reset_reason == 'source_gap'
    weak = RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    feed(weak, times(9.2, rate=5), vector=lambda t: (0., 0.))
    assert not weak.evaluate(ns(9.2), 0., ns(9.2)).output_valid


def test_five_hz_recurrent_snapshot_reconstruction_keeps_one_real_sample_per_sector():
    sparse = MovingRawEvidence(min_sector_samples=1)
    strict = MovingRawEvidence()
    for core in (sparse, strict):
        core.start_epoch(1, 0)
        feed_raw(core, dt=.2)
    evidence = ready(sparse, evidence_policy='recurrent_trapping_v1')
    assert evidence.ready and len(evidence.records) == 46
    assert not ready(strict, evidence_policy='recurrent_trapping_v1').ready
    assert all(sum(c.sector_counts) == 15 and min(c.sector_counts) == 1 for c in evidence.cycles)
    confirmation = DetectorConfirmation(schema_version=1, run_id='synthetic',
        stream_contract_id='a'*64, frame_id='odom', search_epoch=1,
        confirmation_sequence=1, metric_mode='recurrent_geometry_v3')
    confirmation.source_stamp = stamp(6_000_000_000)
    candidate = SimpleNamespace(confirmation=confirmation, candidate_id=1,
                                accepted_ns=6_010_000_000)
    owner = SimpleNamespace(now=lambda:9_010_000_000, center=lambda c:(0., 0.),
        radius=.5, epsilon=.1, published_snapshots={},
        snapshot_publisher=SimpleNamespace(publish=lambda value:None))
    snapshot = MovingSupervisor.snapshot(owner, candidate, evidence)
    reconstructed = snapshot_raw_evidence(snapshot, evidence_policy='recurrent_trapping_v1')
    assert reconstructed.ready and reconstructed.sample_ranges == evidence.sample_ranges
    assert reconstructed.summary == evidence.summary
    assert not snapshot_raw_evidence(snapshot).ready  # Legacy reconstruction stays strict.


def test_nonempty_sector_medians_are_still_required():
    core = MovingRawEvidence(min_sector_samples=1)
    core.start_epoch(1, 0)
    feed_raw(core, dt=.3)  # Ten actual samples cannot populate twelve sectors.
    assert len(core.cycles) == 3
    assert not ready(core, evidence_policy='recurrent_trapping_v1').ready
    assert any(0 in cycle.sector_counts for cycle in core.cycles)


@pytest.mark.parametrize('minimum', [0, -1, 3, True, 1., None])
def test_raw_population_override_is_bounded_and_strictly_typed(minimum):
    with pytest.raises(ValueError):
        MovingRawEvidence(min_sector_samples=minimum)


def test_policy_metadata_names_the_experiment_without_relabeling_legacy():
    descriptor = policy_descriptor(MOVING_CYCLE_POLICY)
    assert descriptor['experiment'] == 'nominal_5hz_density_relaxation_20260924'
    assert descriptor['experimental_sector_density_gate'] == 'disabled'
    assert descriptor['minimum_samples_per_sector'] == 0
    assert descriptor['experimental_recurrent_raw_minimum_samples_per_sector'] == 1
    legacy = policy_descriptor(THREE_CYCLE_POLICY)
    assert legacy['minimum_samples_per_sector'] == 2 and 'experiment' not in legacy
    assert policy_config_sha256(THREE_CYCLE_POLICY) == (
        'cc1443775f70b725a4ddf4929c7fb8302ae9c7f891165f3c71440da85914ed98')
    assert policy_config_sha256(MOVING_CYCLE_POLICY) != (
        '30ed4c7b7ebfa3c643b58928b13280644cd89dc39024e3e1a0d3e52d763b75ff')
