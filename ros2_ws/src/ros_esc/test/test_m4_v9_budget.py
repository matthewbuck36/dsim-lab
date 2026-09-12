"""Prospective dispatcher budget regressions; no ROS/model/acquisition jobs.

Reuse the retained frozen_dispatch fixture and actual dispatcher. Only its fake
monotonic clock and injected science callback advance; the existing synthetic
recording, ownership, binding, cleanup and receipt checks remain active.

V7/V8 below identify retained monotonic origins, not experiment selection: the
shared budget owner is exercised with the original fixture's valid V1 contract.
The first case is already reserved from suite start, so its elapsed admission
allowance is zero. A large monotonic origin must not consume any of that budget.
"""

import json
import math
from pathlib import Path

import pytest

# Import/re-export the existing fixture; do not clone its fake recorder or gates.
from test_m4_dispatch import dispatch, frozen_dispatch


@pytest.mark.parametrize('origin', [100., 56063.905715417, 60906.478755597],
                         ids=['original_fixture_origin', 'retained_v7_origin', 'retained_v8_origin'])
def test_exact_fit_all_sixteen_is_independent_of_retained_monotonic_origin(
        frozen_dispatch, origin):
    fixture = frozen_dispatch
    fixture.clock[0] = origin
    fixture.faults.update(case_elapsed=900., science_elapsed=220., behavior=True)
    result = fixture.run()
    assert result['status'] == 'COMPLETE', result['failure']
    assert fixture.calls == list(range(1, 17))
    assert [row[0] for row in fixture.analyses] == [0, 1, 2, 3]
    assert fixture.releases == [4] and len(fixture.finalized) == 1
    assert len(fixture.finalized[0]) == 16
    assert all(row['status'] == 'COMPLETE' and row['integrity_passed'] is True
               and row['behavior_passed'] is False for row in result['slots'])
    started = json.loads((Path(fixture.contract['root'])/'acquisition/started.json').read_text())
    # Slot 1 starts at the reserved suite origin; it has no elapsed work to reject.
    assert started['started_monotonic'] == result['slots'][0]['started_monotonic'] == origin
    assert result['slots'][0]['case_deadline'] == origin+900.
    assert result['suite_deadline'] == started['suite_deadline'] == origin+15300.
    assert result['elapsed_wall_sec'] < 15300.
    assert result['replacements_dispatched'] is False


def test_original_221_second_science_overrun_still_seals_next_dispatch(frozen_dispatch):
    fixture = frozen_dispatch
    fixture.faults.update(case_elapsed=900., science_elapsed=221.)
    result = fixture.run()
    assert result['status'] == 'INCOMPLETE'
    assert fixture.calls == [1, 2, 3, 4]
    assert [row[0] for row in fixture.analyses] == [0]
    assert all(row['status'] == 'COMPLETE' for row in result['slots'][:4])
    assert all(row['status'] == 'UNSTARTED' for row in result['slots'][4:])
    assert 'envelopes' in result['failure']
    # The existing release hook ran after development analysis; no holdout ran.
    assert fixture.releases == [4] and len(fixture.finalized[0]) == 16
    assert result['replacements_dispatched'] is False


@pytest.mark.parametrize('completed_cases,admission_point',
                         [(4, 3820.), (8, 7640.), (12, 11460.)],
                         ids=['after_development', 'after_nominal_holdout', 'after_noise_holdout'])
@pytest.mark.parametrize('position', ['before', 'at', 'after'])
def test_next_representable_block_admission_boundary_is_strict(
        frozen_dispatch, monkeypatch, completed_cases, admission_point, position):
    fixture = frozen_dispatch
    fixture.clock[0] = 0.
    fixture.faults.update(case_elapsed=900., science_elapsed=220.)
    # Explicit schedule witnesses: 4/8/12 completed 900s cases and 1/2/3
    # completed 220s science blocks. Do not reproduce the admission expression.
    point = (math.nextafter(admission_point, -math.inf) if position == 'before'
             else math.nextafter(admission_point, math.inf) if position == 'after'
             else admission_point)
    actual_dispatch = dispatch.dispatch
    injected = []

    def invoke_with_clock_witness(*args, **kwargs):
        original_analysis = kwargs['analyze_block']

        def analysis(*arguments):
            result = original_analysis(*arguments)
            block = arguments[1]
            if block == completed_cases//4-1:
                assert fixture.calls == list(range(1, completed_cases+1))
                assert fixture.clock[0] == admission_point
                fixture.clock[0] = point
                injected.append(point)
            return result

        kwargs['analyze_block'] = analysis
        return actual_dispatch(*args, **kwargs)

    # Interpose only on the existing injectable science hook; every dispatcher
    # admission/evidence/release/finalization path remains the production owner.
    monkeypatch.setattr(dispatch, 'dispatch', invoke_with_clock_witness)
    result = fixture.run()
    assert injected == [point]
    assert fixture.releases == [4]
    assert len(fixture.finalized) == 1 and len(fixture.finalized[0]) == 16
    if position == 'after':
        assert result['status'] == 'INCOMPLETE'
        assert 'envelopes' in result['failure']
        assert fixture.calls == list(range(1, completed_cases+1))
        assert all(row['status'] == 'COMPLETE' for row in result['slots'][:completed_cases])
        assert all(row['status'] == 'UNSTARTED' for row in result['slots'][completed_cases:])
        assert len(fixture.analyses) == completed_cases//4
    else:
        assert result['status'] == 'COMPLETE', result['failure']
        assert fixture.calls == list(range(1, 17))
        assert [row[0] for row in fixture.analyses] == [0, 1, 2, 3]
        assert all(row['status'] == 'COMPLETE' for row in result['slots'])
    assert result['replacements_dispatched'] is False
