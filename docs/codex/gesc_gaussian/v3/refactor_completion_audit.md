# ESC/V3 refactor requirement audit — 2026-09-28

Scope: the [accepted implementation plan](refactor_plan.md), including preserved
Gazebo live plots and external physical adapters. This audit closes the
software refactor only. New Gazebo research and physical qualification are
subsequent work, not implicitly passed by unit tests.

All receipts below are under
[`refactor_20260928T195707Z`](/home/mattb/Experiments/GESC-Gaussian/v3/refactor_20260928T195707Z).
Final receipt: `final_installed_entrypoint_tests.log`; bags and renders are in
`final_installed_entrypoint_artifacts/`. The final installed suite passed **196 tests**, no skips, in 9.04 s. Three
packages built successfully. NumPy emitted existing matrix-deprecation warnings
in the original-profile comparisons; they are not hidden test failures.

| Accepted requirement | Current authoritative evidence | Result |
| --- | --- | --- |
| 1. Preserve tree/refs/installations; remove generated tracking; fresh symlink build | `receipt.json`, `hygiene.json`, `additional_generated_hygiene.json`, `final_structure_receipt.json`; archive digest checked; original refs unchanged; no generated files tracked; `workspace_build.log` and `final_build_and_tests.log` | PASS |
| 2. Single profile/environment resolution, short original aliases, no runtime build or JSON rewrite, installed/custom configuration | `ros_esc/profiles.py`, installed `config/profiles`; 19 aliases and six launch arguments; `test_v3_profiles.py`; `installed_interfaces_profile.txt` | PASS |
| 3. One V3 owner through controller entrypoint; local selected numerical helpers; retire distributed ROS choreography | `controller_node_script.main --v3`, `gesc_v3/{node,core}.py`, pure `numerics`; original-source golden fixture; `test_v3_numerics.py`, `test_v3_core.py`, actual installed `controller_node --v3` subprocess; retired modules absent from installed import graph | PASS |
| 4. One private bounded worker; no FIFO; expiry/stale rejection; sole commit owner; 4000-sample cap | `gesc_v3/worker.py`, `core.py`, `numerics/fill.py`; worker/core/ROS tests, including 2 s worker load, allocation failure and delayed proposals; no worker ROS initialization or registry authority | PASS |
| 5. Exactly eight interfaces; honest observed timing/provenance; telemetry-only events/fills | Interface source/CMake/install inventory; `SensorObservation.msg`, adapter/conversion tests, no invented ADC time/device sequence; `test_v3_observation*.py`, ordinary V3 bag decode tests | PASS |
| 6. ACTIVE/WAITING_INPUT recovery; terminal STOPPED/FAULTED; no full-cycle/recorder startup qualification; candidate failure nonfatal | Core and legacy controller tests; isolated real ROS graph expiry/recovery and subprocess SIGINT final-zero test; node-fault tests cover optional publisher failures, competing owner and integrity failures | PASS |
| 7. Original numerical API, signs/units/methods; first physical-target V3 configuration | Original 17 wrapper/config comparisons, 19 profile/module API checks, cost-model golden tests; selected 5 Hz, nominal20RPM, 54-degree acquisition metadata, gain0.5 and caps0.05/0.30 resolved from current profile/controller JSON | PASS |
| 8. Optional default standard bag; ordinary-path analysis; no live CSV/report/recorder gating | `run_tools`, launch actions, live plot implementation; real standard SQLite/V3 bags, offline CLI/plots and recorder subprocess shutdown tests; compact topic list | PASS |
| 9. Retire obsolete active code/tests/workflows; concise usage/architecture/environment/tests/history | `retirement_manifest.json`: 523 moved files verified; 1437 generated tracked entries removed; current root/package READMEs and `docs/esc_*.md`; old source and nested obsolete READMEs preserved externally and on frozen refs | PASS |

## Explicit corrections and boundaries

- Interactive Gazebo retains automatic original Matplotlib plotting. Physical
  and headless modes disable it. Plot failures do not control motion.
- No `turtlebot3_vehicle_nodes` was added to this repository. No Pi transfer,
  build, firmware, deployment, ROS/device launch or physical action occurred
  during this implementation. Restored physical V1 is preserved.
- Continuous translation remains required during verification/design. There is
  no stationary collection fallback. Tests establish policy and command
  behavior; actual trajectory continuity remains a Gazebo/physical question.
- Normal runs continue until Ctrl+C. Stronger-source detection is an event.
- The first V3 profile remains a selected two-source, one-fill configuration.
  It is not broadly qualified or a general unknown-source-count solution.
- Historical 354-degree/optional10/15Hz instructions remain superseded for the
  restored Pi. Current V3 metadata does not apply calibration a second time.
- Active simulation source contains no `phase09` references. Historical phase
  documentation/reports and archived source retain their original identifiers.

## Findings resolved during completion review

The audit found and corrected additional generated files under
`extremum-seeking`, optional-worker queue allocation escaping error handling,
missing current test documentation and stale nested runtime READMEs. Core
review also corrected the selected gain, repulse-to-assist transition, known-fill
suppression, both pose checks before a fill commit, centered reference phase,
full-rate odometry detector input and source-boundary timestamps. Final tests
were rerun after these changes; intermediate failures remain in the receipts.

Explicit compatibility repairs: Lie-bracket consumes its intended scalar cost
component; invalid legacy filter integration is finite and recoverable; the
rotation direction initializer no longer overwrites its documented unknown
state with uninitialized memory. Ordinary valid numerical traces and selected
V2 math retain comparison evidence. No general trajectory equivalence claim is
made.

The inherited optional ADC matcher remains unvalidated and is disabled in V3.
The host scheduling check is not Pi CPU qualification. No new Gazebo or physical
run was executed. Changes are committed on `refactor/esc-v3`; generated-file
cleanup is recorded separately in `24d4a29`. Frozen V1/V2 references are
unchanged. The external `git_cleanup_receipt.json` records both checkpoint
commits and the final Git status. Large evidence and generated build trees
are outside Git. Read the [usage guide](../../../esc_usage.md) before subsequent
tests.
