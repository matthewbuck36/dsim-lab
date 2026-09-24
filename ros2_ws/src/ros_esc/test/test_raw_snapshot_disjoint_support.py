"""Original bracketing support for selected, nonadjacent raw cycles."""
from copy import deepcopy
from types import SimpleNamespace
import math

import pytest
from ros_esc_interfaces.msg import DetectorConfirmation
from ros_esc.supervisor_node.moving_evidence import MovingRawEvidence, snapshot_raw_evidence
from ros_esc.supervisor_node.v2_supervisor import MovingSupervisor, stamp
from ros_esc.v2_stream import time_to_ns
from test_v2_moving_evidence import feed, ready


def snapshot_case(*, direction=1, policy='recurrent_trapping_v1', disjoint=True):
    core = MovingRawEvidence(min_sector_samples=1 if policy == 'recurrent_trapping_v1' else 2)
    core.start_epoch(1, 0)
    feed(core, duration=12 if disjoint else 9,
         dt=.2 if policy == 'recurrent_trapping_v1' else .025,
         phase=lambda t: direction * math.tau * t / 3 + .137,
         position=lambda t: (1. if disjoint and 3 < t < 6 else 0., 0.))
    evidence = ready(core, evidence_policy=policy)
    assert evidence.ready
    if disjoint:
        assert evidence.cycles[0].end_ns < evidence.cycles[1].start_ns
    confirmation = DetectorConfirmation(schema_version=1, run_id='synthetic',
        stream_contract_id='a'*64, frame_id='odom', search_epoch=1,
        confirmation_sequence=1, metric_mode='recurrent_geometry_v3')
    confirmation.source_stamp = stamp(6_000_000_000)
    candidate = SimpleNamespace(confirmation=confirmation, candidate_id=1, accepted_ns=6_010_000_000)
    owner = SimpleNamespace(now=lambda:12_010_000_000, center=lambda c:(0., 0.),
        radius=.5, epsilon=.1, published_snapshots={},
        snapshot_publisher=SimpleNamespace(publish=lambda value:None))
    return MovingSupervisor.snapshot(owner, candidate, evidence), evidence


@pytest.mark.parametrize('direction', [1, -1])
@pytest.mark.parametrize('policy', ['recurrent_trapping_v1', 'angular_profiles_v1'])
@pytest.mark.parametrize('disjoint', [True, False])
def test_original_selected_cycles_roundtrip(direction, policy, disjoint):
    snapshot, evidence = snapshot_case(direction=direction, policy=policy, disjoint=disjoint)
    result = snapshot_raw_evidence(snapshot, evidence_policy=policy)
    assert result.ready and result.sample_ranges == evidence.sample_ranges
    assert result.summary == evidence.summary
    assert [(c.start_ns,c.end_ns,c.sample_stamps,c.sector_counts) for c in result.cycles] == [
        (c.start_ns,c.end_ns,c.sample_stamps,c.sector_counts) for c in evidence.cycles]
    assert result.amplitude == pytest.approx(evidence.amplitude, abs=1e-12)
    assert result.disagreement == pytest.approx(evidence.disagreement, abs=1e-12)
    assert len(result.records) == len(evidence.records)


@pytest.mark.parametrize('tamper', ['gap_inside_cycle', 'duplicate_id_between_groups',
    'duplicate_sequence_between_groups', 'timestamp_order', 'phase_reversal_between_groups',
    'ambiguous_step', 'no_boundary_bracket', 'partial_cycle', 'statistics', 'assignment', 'nonfinite'])
def test_disjoint_support_preserves_original_rejections(tamper):
    original, _ = snapshot_case()
    s = deepcopy(original)
    second = next(i for i,o in enumerate(s.observations) if time_to_ns(o.source_stamp) >= 6_000_000_000)
    if tamper == 'gap_inside_cycle':
        # Leave declared boundaries unchanged: this is a real missing interval
        # within their support, not an omitted unselected revolution.
        for field in ('observations','observation_filter_state','observation_filter_stamp'):
            values = list(getattr(s,field)); del values[4:7]; setattr(s,field,values)
    elif tamper == 'duplicate_id_between_groups':
        s.observations[second].observation_id = s.observations[0].observation_id
    elif tamper == 'duplicate_sequence_between_groups':
        s.observations[second].source_sequence = s.observations[0].source_sequence
    elif tamper == 'timestamp_order':
        s.observations[second].source_stamp = deepcopy(s.observations[0].source_stamp)
    elif tamper == 'phase_reversal_between_groups':
        for obs in s.observations[second:]: obs.sensor_world_phase_rad *= -1
    elif tamper == 'ambiguous_step':
        s.observations[3].sensor_world_phase_rad = s.observations[2].sensor_world_phase_rad + math.pi
    elif tamper == 'no_boundary_bracket':
        for field in ('observations','observation_filter_state','observation_filter_stamp'):
            setattr(s,field,list(getattr(s,field))[1:])
    elif tamper == 'partial_cycle':
        s.revolution_end[0] = stamp(time_to_ns(s.revolution_end[0])-100_000_000)
    elif tamper == 'statistics': s.candidate_cost_lower -= .01
    elif tamper == 'assignment': s.revolution_sample_end[0] -= 1
    else: s.observations[second].raw_cost = math.nan
    assert not snapshot_raw_evidence(s,evidence_policy='recurrent_trapping_v1').ready
