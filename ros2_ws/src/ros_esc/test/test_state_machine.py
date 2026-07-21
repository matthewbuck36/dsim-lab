"""Focused transition tests for the Phase 02 supervisor."""

import math

import pytest

from ros_esc.supervisor_node.state_machine import (
    STATE_WEIGHTS,
    State,
    StateMachineConfig,
    SupervisorStateMachine,
    TransitionInputs,
)


def config(**overrides):
    values = {
        "convergence_hold_sec": 2.0,
        "goal_score_threshold": 0.95,
        "goal_hold_sec": 3.0,
        "undesired_score_hold_sec": 3.0,
        "verification_max_sec": 10.0,
        "fill_design_timeout_sec": 5.0,
        "escape_max_sec": 20.0,
        "recenter_after_escape": True,
        "recenter_max_sec": 30.0,
    }
    values.update(overrides)
    return StateMachineConfig(**values)


def enter_verify(machine):
    machine.step(0.0, TransitionInputs(convergence=True))
    transition = machine.step(2.0, TransitionInputs(convergence=True))
    assert transition.current == State.VERIFY_EXTREMUM


def enter_design(machine, request_timestamp=11.0):
    enter_verify(machine)
    machine.step(
        2.0,
        TransitionInputs(source_score=0.2, source_score_valid=True),
    )
    transition = machine.step(
        5.0,
        TransitionInputs(source_score=0.2, source_score_valid=True),
    )
    assert transition.current == State.DESIGN_OR_MERGE_FILL
    machine.register_fill_request(request_timestamp)


def enter_repulse(machine):
    enter_design(machine)
    transition = machine.step(
        5.1,
        TransitionInputs(
            fill_result="success",
            fill_source_timestamp=11.0,
            fill_id=4,
        ),
    )
    assert transition.current == State.ESCAPE_REPULSE


def test_initial_state_and_explicit_weights_for_every_state():
    machine = SupervisorStateMachine()
    assert machine.state == State.SEARCH
    assert machine.weights == (1.0, 1.0, 0.0)
    assert set(STATE_WEIGHTS) == set(State)
    assert STATE_WEIGHTS[State.ESCAPE_REPULSE] == (0.0, 1.0, 0.0)
    assert STATE_WEIGHTS[State.ESCAPE_ASSIST] == (0.0, 1.0, 1.0)
    assert STATE_WEIGHTS[State.FAILSAFE] == (0.0, 0.0, 0.0)


def test_convergence_requires_continuous_dwell_and_exact_boundary():
    machine = SupervisorStateMachine()
    machine.step(0.0, TransitionInputs(convergence=True))
    machine.step(1.0, TransitionInputs(convergence=False))
    machine.step(1.5, TransitionInputs(convergence=True))
    assert machine.step(3.49, TransitionInputs(convergence=True)) is None
    transition = machine.step(3.5, TransitionInputs(convergence=True))
    assert transition.current == State.VERIFY_EXTREMUM


def test_high_score_goal_dwell_and_latch():
    machine = SupervisorStateMachine()
    enter_verify(machine)
    machine.step(2.0, TransitionInputs(source_score=0.95, source_score_valid=True))
    transition = machine.step(
        5.0,
        TransitionInputs(source_score=0.95, source_score_valid=True),
    )
    assert transition.current == State.GOAL_HOLD
    assert machine.step(100.0, TransitionInputs()) is None


def test_threshold_alternation_resets_opposite_dwell_then_times_out():
    machine = SupervisorStateMachine(config=config(verification_max_sec=4.0))
    enter_verify(machine)
    machine.step(2.0, TransitionInputs(source_score=0.96, source_score_valid=True))
    machine.step(3.0, TransitionInputs(source_score=0.94, source_score_valid=True))
    machine.step(4.0, TransitionInputs(source_score=0.96, source_score_valid=True))
    transition = machine.step(
        6.0,
        TransitionInputs(source_score=0.94, source_score_valid=True),
    )
    assert transition.current == State.FAILSAFE
    assert transition.reason == "verification timeout"


def test_invalid_score_in_verification_fails_safe():
    machine = SupervisorStateMachine()
    enter_verify(machine)
    transition = machine.step(2.1, TransitionInputs(source_score_valid=False))
    assert transition.current == State.FAILSAFE


def test_low_score_dwell_requests_design_and_late_result_is_ignored():
    machine = SupervisorStateMachine()
    enter_design(machine)
    assert machine.step(
        5.2,
        TransitionInputs(fill_result="success", fill_source_timestamp=10.0),
    ) is None
    assert machine.state == State.DESIGN_OR_MERGE_FILL


def test_matching_fill_success_enters_repulse_and_tracks_fill():
    machine = SupervisorStateMachine()
    enter_repulse(machine)
    assert machine.active_fill_count == 1
    assert machine.active_escape_fill_id == 4


@pytest.mark.parametrize("result", ["rejected", "invalid"])
def test_fill_rejection_or_invalid_result_fails_safe(result):
    machine = SupervisorStateMachine()
    enter_design(machine)
    transition = machine.step(
        5.1,
        TransitionInputs(fill_result=result, fill_source_timestamp=11.0),
    )
    assert transition.current == State.FAILSAFE


def test_fill_design_timeout():
    machine = SupervisorStateMachine()
    enter_design(machine)
    transition = machine.step(10.0, TransitionInputs())
    assert transition.current == State.FAILSAFE


def test_bounded_and_unbounded_stable_exit_paths():
    bounded = SupervisorStateMachine()
    enter_repulse(bounded)
    assert bounded.step(6.0, TransitionInputs(stable_exit=True)).current == State.RECENTER

    unbounded = SupervisorStateMachine(config=config(recenter_after_escape=False))
    enter_repulse(unbounded)
    assert unbounded.step(6.0, TransitionInputs(stable_exit=True)).current == State.SEARCH


def test_single_redesign_enters_assist_and_preserves_escape_deadline():
    machine = SupervisorStateMachine()
    enter_repulse(machine)
    escape_start = machine.escape_started_sec
    transition = machine.step(6.0, TransitionInputs(stalled=True))
    assert transition.current == State.DESIGN_OR_MERGE_FILL
    machine.register_fill_request(12.0)
    transition = machine.step(
        6.2,
        TransitionInputs(
            fill_result="success",
            fill_source_timestamp=12.0,
            fill_id=5,
        ),
    )
    assert transition.current == State.ESCAPE_ASSIST
    assert machine.escape_started_sec == escape_start
    assert machine.active_fill_count == 2


def test_escape_and_assisted_escape_share_total_timeout():
    machine = SupervisorStateMachine(config=config(escape_max_sec=2.0))
    enter_repulse(machine)
    machine.step(6.0, TransitionInputs(stalled=True))
    machine.register_fill_request(12.0)
    machine.step(
        6.5,
        TransitionInputs(fill_result="success", fill_source_timestamp=12.0),
    )
    transition = machine.step(7.1, TransitionInputs())
    assert transition.current == State.FAILSAFE
    assert "escape timeout" in transition.reason


def test_assisted_exit_and_recenter_completion():
    machine = SupervisorStateMachine()
    enter_repulse(machine)
    machine.step(6.0, TransitionInputs(stalled=True))
    machine.register_fill_request(12.0)
    machine.step(
        6.1,
        TransitionInputs(fill_result="success", fill_source_timestamp=12.0),
    )
    assert machine.step(7.0, TransitionInputs(stable_exit=True)).current == State.RECENTER
    assert machine.step(8.0, TransitionInputs(recenter_complete=True)).current == State.SEARCH


def test_recenter_timeout():
    machine = SupervisorStateMachine(config=config(recenter_max_sec=2.0))
    enter_repulse(machine)
    machine.step(6.0, TransitionInputs(stable_exit=True))
    assert machine.step(8.0, TransitionInputs()).current == State.FAILSAFE


@pytest.mark.parametrize(
    "fault_input",
    [
        TransitionInputs(pose_valid=False),
        TransitionInputs(sensor_valid=False),
        TransitionInputs(explicit_stop=True),
        TransitionInputs(controller_fault=True),
    ],
)
def test_global_faults_latch_failsafe(fault_input):
    machine = SupervisorStateMachine()
    transition = machine.step(0.1, fault_input)
    assert transition.current == State.FAILSAFE
    assert machine.step(5.0, TransitionInputs()) is None


def test_backward_clock_and_nonfinite_configuration_fail_safe():
    machine = SupervisorStateMachine(now_sec=5.0)
    transition = machine.step(4.0, TransitionInputs())
    assert transition.current == State.FAILSAFE
    with pytest.raises(ValueError):
        StateMachineConfig(goal_hold_sec=math.nan)
