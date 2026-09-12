# Q1 acquisition purpose, identities and safety receipts — 2026-09-09

Status: source and focused validation complete for parent integration. No Gazebo,
hardware, data acquisition, field qualification, commit or push. The Q1 dispatch
freeze, installed bindings and release remain separate parent-owned work.

## Narrow scenario extension

The existing schema/runner now accept `schema_version: 2` with top-level
`purpose: qualification_observation`. Other schema numbers and purpose spellings
are rejected. Suites omitting purpose retain their existing version restrictions,
formal predicates, case keys and staged recovery behavior. The optional simulated
duration key is omitted from legacy normalized execution dictionaries when it was
not supplied; an explicitly supplied zero or positive value remains explicit.

Only this acquisition purpose admits the selected later-version launch controls
without requiring VERIFY or staged recovery. Merged frozen/case controls still
pass `_validate_correction_overrides`; singleton robust rolling validation now
occurs after the frozen merge so a frozen selector cannot bypass it. Acquisition
requires observation-only true, counted mode, explicit positive radius/tolerance,
known count two, integer fill limit one, exactly one positive direct-input local
source and a stronger positive direct-input goal source, both inside validated
bounds. It excludes validation world/contacts. It requires a positive simulated
duration and both stop-on-run-failure and stop-on-cleanup-failure policies.

Acquisition success is exactly `recording_complete`, `cleanup_complete`, and
`no_forbidden_events`. The controller contract must forbid `FAILSAFE` and
`RECENTER_STARTED`; it cannot require a lifecycle or terminal state. These are
acquisition safety outcomes, not detector/Gaussian behavioral success. Existing
schema2 execution uses the ordinary recorder/cleanup path, never the schema>=5
live staged-recovery monitor.

Purpose is preserved in normalized suite, resolved case, deterministic case-key
input, scenario metadata, dry-run summary and each dry-run record. Optional API
`execute_suite(..., run_id=None)` and CLI `--run-id` accept a validated string only
when exactly one run expands after case selection. The exact identity enters
shared V2 launch configuration, metadata and recorder argv. Invalid/cardinality
errors occur before ROS setup. Existing recorder refusal of a pre-existing run
directory remains authoritative; no automatic replacement or new identity is used.

## Actual safety receipt behavior

Tests serialize real `AlgorithmEvent` messages and run the existing deserializer,
`_bag_outcomes`, classification and `execute_suite` dispatch. Enum values are
`EVENT_FAILSAFE=70` and `EVENT_RECENTER_STARTED=50`. The acquisition event window
is first recorded readiness true through first subsequent recorded false,
inclusive. In-window events fail the safety predicate; events before/after that
window do not. Safety failure prevents dispatch of the next fixture case even
when recording and cleanup are complete. Cleanup failure independently stops
dispatch; clean controls execute both fixture cases. Failed fixture artifacts
are retained by the real runner artifact-writing path.

Actual `RecordingCoordinator.request_stop()` publishes readiness false before
stop true. Actual `SupervisorNode` stop/timer callbacks then emit FAILSAFE.
Callback tests collect publication order separately from simulated transport
receipt order. With false received first, normal shutdown is excluded. With its
receipt deliberately delayed until after FAILSAFE, the existing check
conservatively fails. Equal boundary receipts are included and also fail.

This is **not a guarantee of cross-topic DDS/bag ordering**. The new tests use real
node callbacks and message serialization with controlled publisher delivery;
they do not claim a new DDS acquisition test. A delayed readiness-false receipt
can therefore produce a conservative acquisition failure. No fault is silently
excused based on detail text or presumed shutdown intent. Q1 must retain and
diagnose such an outcome rather than automatically rerunning or widening its
accepted interval. The earlier duration-owner tests separately cover existing
ordered final-zero/process cleanup.

## Exact commands and retained outcomes

Commands run from `/home/mattb/dsim-lab`; every pytest invocation used:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=187 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q <selection> > <log> 2>&1
```

All logs below are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Log | Exact selection after `-q` | Outcome |
| --- | --- | --- |
| `q1_acquisition_safety_v1.log` | `ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py` | Exit0,39 passed in2.23s. This precedes the extra strict integer fill-limit check. |
| `q1_acquisition_safety_regressions_v1.log` | `ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py ros2_ws/src/ros_esc/test/test_q1_runner_contract.py ros2_ws/src/ros_esc/test/test_scenario_schema.py ros2_ws/src/ros_esc/test/test_scenario_runner.py` | Exit124 timeout; pytest printed1 failed,446 passed,1 skipped in121.13s. This is not a clean bounded suite pass. Failure was the exact legacy execution dictionary acquiring default `simulation_duration_sec: 0.0`; skip was the explicitly opt-in Gazebo E2E test. |
| `q1_acquisition_safety_v2.log` | `ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py ros2_ws/src/ros_esc/test/test_q1_runner_contract.py ros2_ws/src/ros_esc/test/test_scenario_schema.py::test_m4_2_freezes_progress_guidance_probe_and_two_light_gate` | Exit0,52 passed in2.53s after preserving omitted-key output shape. Covers all new tests and the precise failed legacy assertion. |

Parent requested no repetition of the446 already completed passing assertions
merely to obtain a different timing result. The failed/timed-out attempt remains
unchanged. Both `validate_phase_context.sh v2 implement` with30s timeout and
assigned-source `git diff --check` pass.

## Source and log boundary

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py` | `36db60ae730062162012611d4553f48ea8c95ab5b6b916f6eed20e5dabed6088` |
| `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py` | `45e49cb0dd29ca5f94ca1c7a36e8273fe54b5b7ac0a74b4d07df14e34656416b` |
| `ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py` | `a8428ba396fdfd3fc5073519820c3e8f12bd2f46adcaddd8d363fc41941bb59d` |
| `q1_acquisition_safety_v1.log` | `67c7b84fbda87be3f3aed9c97b0b0e0278eef6b7b837681d227ccbdd739b9f30` |
| `q1_acquisition_safety_regressions_v1.log` | `3b713e061a199030017c8bd00afb74ddc553515314d1ffca69be4aa940102293` |
| `q1_acquisition_safety_v2.log` | `dbbeef852ce9cf71548492f67858b98abe217d9d713d4f0074f465a8f207cf76` |

M3 archive and earlier V1/V2 research evidence were not edited. These changes
establish a reviewable acquisition path; they do not release Q1 Gazebo dispatch.

## Final four-case shadow-event regression

Read-only orchestration review found that the initial Q1 scenario forbade
`CONVERGENCE_CONFIRMED`, although the existing detector intentionally emits that
event in observation mode. Root removed that veto from all four cases; fill,
GOAL and safety vetoes remain. New fixtures load the actual Q1 YAML, serialize
these events through the existing bag parser, and classify all four selected
seeds. A shadow confirmation passes acquisition; FILL_CREATED, GOAL_REACHED,
FAILSAFE and RECENTER_STARTED each fail. No scientific labels are evaluated.

Using the exact sourced overlay/domain187/timeout90s prefix above with selection
`ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py` and redirected output
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_acquisition_safety_v3.log`:
**exit0,45 passed in2.41s**. This is the final focused test boundary.

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/test/test_q1_acquisition_safety.py` | `00478886632914c3443f0a980c998f813fbc4bd6592c83f374d0606f87039a7d` |
| `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/q1_primary_shadow_v1.yaml` | `7c1df007200bdb461c68033440b2b64da12ffb5148a24c0dffe0fc5dd18f8f6a` |
| `q1_acquisition_safety_v3.log` | `f4009caca22b705b36a2c83537e1f8f9f6487a6d7a377e81c901c453d7758c62` |

The review also identified missing enforcement of the contract's ROS domain in
the acquisition wrapper. Root added strict environment equality before output
creation or ROS work. Final read-only inspection found no further material issue
in `freeze_q1_contract.py`, `acquire_q1.py`, or `evaluate_q1.py`: temporary recorder
metadata paths are declared semantic templates, exact launch/resolved cases are
checked afterward, receipt chains are verified between cases, and existing
owners perform execution and numerical analysis. Their hard execution limits
remain the explicitly prescribed external timeout commands; the wrappers were
not executed by this review.
