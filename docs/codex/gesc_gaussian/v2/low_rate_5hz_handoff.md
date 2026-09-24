# V2 5 Hz Gazebo feasibility handoff

Closed feasibility experiment, 2026-09-24: **run_05 demonstrated fill, assisted escape, resumed SEARCH and arrival within 0.5 m of the global source at actual 5 Hz and 20 RPM.** This is one selected nominal case. The original strict coverage/completeness classification remains FAIL. All ten other behavior/cleanup predicates passed, and final commands and process cleanup were verified. No further exposure is scheduled. Physical commissioning remains paused, with **0/3 qualified physical acquisitions**. This experiment made no Pi, firmware or physical-motion changes.

The user requested a quick, useful mobile Gazebo V2 feasibility test at **5 Hz and 20 RPM**, relaxing the previous sampling-density requirement. Work is isolated on `experiment/gesc-gaussian-v2-5hz-20260924`; accepted Test D remains preserved at `d1779b6`. The matched nominal scenario uses seed `26091152`, the established world/start/controller, and visible normal-speed Gazebo. The accepted 30 Hz reference arrived at 158.053 simulated seconds. This experiment is a selected-case feasibility test, not a replacement baseline or robustness qualification.

## Source and validation

Eight production files differ from the accepted baseline. The three rotating-sensor launch/URDF owners and `scenario_runner/scenario_schema.py` expose and allow a selected joint-state source cadence override, retaining the 30 Hz default and 30 Hz differential-drive odometry. The selected rolling graph excludes the other joint-state broadcaster. The remaining owners are `filter_node/rolling_gesc.py`, `v2_direction_policy.py`, `supervisor_node/moving_evidence.py` and `supervisor_node/v2_supervisor.py`.

The experimental moving policy disables rolling sector population density and records the relaxation in its descriptor/hash. Complete revolutions, original 0.5-second source-gap limit, freshness, finite geometry and numerical coherence remain. Recurrent verification and snapshot reconstruction require one actual sample in each sector; other raw modes retain two, and the THREE_CYCLE policy remains unchanged. Strict accepted MOVING behavior is preserved at the baseline commit, rather than as a second selectable runtime mode on this branch.

Initial source validation passed **197 focused/relevant tests**, including 5 Hz/20 RPM synthetic streams, legacy behavior and snapshot reconstruction. The later snapshot correction passed **79 focused tests**, including 19 new cases and an independent review. These are successive validation sets, not a claim of 276 unique tests. The correction changes only reconstruction in the existing raw owner: overlapping support is replayed together, disjoint support groups separately. Global ordering, unique identities, common rotation direction, within-group gaps/reversals, full cycles and exact original statistics remain checked. It does not interpolate omitted history or claim that omitted history was continuous.

Original post-run coverage validators still require two samples per sector. Preserve and report their failures separately from simulated behavior; no validator was weakened to obtain a PASS. Gaussian outlier rejection and numerical rules also remain unchanged. Only the scenario's minimum valid fill-sample count changed between the later attempts.

## Retained attempts

All paths below are under `/home/mattb/Experiments/GESC-Gaussian/v2/low_rate_20260924`.

| Attempt | Selected fill minimum | Closed result / current state |
| --- | ---: | --- |
| run_01 | 40 | Infrastructure failure before Gazebo: Q5's older generated interfaces lacked `RecurrentConvergenceDiagnostics`. Cleanup passed. |
| run_02 | 40 | Actual 5 Hz source, no gaps above 0.5 seconds and no rolling resets; 97.355% of direction diagnostic publications qualified. Detection occurred, but fill rejected: 40 assigned samples, 34 retained after original cost-MAD rejection, below 40. No fill, escape or arrival before recovery timeout. Final zero/readiness false and cleanup passed. Offline minimum-30 replay produced a proposal; original run remains failed. |
| run_03 | 30 | Fill rejected an invalid raw snapshot before fitting. Three individually valid 15-sample cycles were nonadjacent; serializing their support union introduced a 2.6-second omitted section that continuous replay mistook for a source gap. The correction reconstructs the exact retained snapshot with unchanged statistics; its original minimum-30 fitter retained 37 of 45 samples and produced a proposal. The actual run remains failed and early-stopped, with `target_clean_shutdown=false`; writer and process cleanup passed. |
| run_04 | 30 | Corrected snapshot reached fitting, but only 22 of 39 assigned samples survived original outlier checks, below 30. Offline minimum-20 replay produced a proposal with those same 22 samples. Original strict outer cleanup is **FAIL** because an external observer node remained visible; owned processes and bag writer closed. After stopping that observer, a fresh existing-owner inspection proved a clean graph/process state. The supplemental check does not overwrite the original failure. |
| run_05 | 20 | **Selected-case behavioral success.** One fill, assisted escape, resumed SEARCH and post-recovery global proximity. Actual 5 Hz with no source gaps; original arrival-triggered stop, target/bag shutdown and strict cleanup passed. Original completeness remains FAIL under unchanged coverage/lifecycle checks. |

The run_04 minimum-20 replay is **not a passing quadratic fit**: its condition number was approximately `1.675465e8`, above the configured `1e8` limit. The existing designer still permitted a proposal through its established invalid-quadratic handling, with zero curvature contribution and zero fit-condition confidence component. Other finite/grid checks remained. Proposal confidence was 0.660053, with zero design escalations. This supports observing downstream behavior, not a numerical-quality or reliability claim.

Useful evidence:

- `source_tests_01/receipt_01.json` and `cadence_configuration_check.json`: source tests and default/selected cadence checks; initial import/preparation failures are retained.
- `run_02/{attempt_result.json,analysis_01/analysis.json,fill_diagnosis_01/min30_proposal.json}`.
- `run_03/snapshot_diagnosis_01/` and `run_03/snapshot_correction_01/{receipt.json,independent_review_01.json}`: exact failure, correction, 79 tests and offline replay.
- `run_04/{attempt_result.json,post_observer_cleanup_01.json,fill_diagnosis_01/finding.md,fill_diagnosis_01/proposal_comparison.json}`. The general cadence analyzer refused the original failed-cleanup receipt; focused diagnosis used explicit closed-writer proof and retained that limitation.
- `run_05/{PLAN.md,prepared.json,started.json,command.json,dispatch.log}`. Preparation binds 696 source files and the eight changed production files. Prepared SHA-256: `3f1825921c0da00cd7ee3313eddb6958b9a4fd1c67803418dcc575c0fe7190ab`.

## Recovery and commands

Read the current plan/status and actual receipts before acting. Preparation and execution helpers are one-use; **do not rerun run_01 through run_05 helpers**. Do not read an active SQLite bag. No rebuild was needed: the accepted Q5 overlay resolves the reviewed live source/launch files, but the newer R21 generated interface overlay must be sourced afterward:

```bash
cd /home/mattb/dsim-lab
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/install/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/build_interfaces_v1/install/local_setup.bash
export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0
unset RMW_IMPLEMENTATION
```

The exact consumed scenario command is retained in each attempt's `command.json`; preparation and bounded launcher commands are in its `PLAN.md`. Run_05 used the original `run_scenario` / `record_run` owners, strict `subreaper_group_v3` cleanup, a 1,120-second wrapper budget and an external `timeout --signal=INT --kill-after=5s 1125s` bound. Its helper is consumed and terminal. Recover the final receipts and existing analyses; do not restart it.

## Run_05 closed outcome

Session 9532 exited 0 after 228.931 wall seconds. `attempt_result.json` reports `ATTEMPT_RETAINED`, source stability and strict native/outer cleanup PASS. The original scenario stopped on its observed global-arrival condition. Bag and target clean-shutdown metadata and final command zeros passed; no owned/session processes or new graph nodes remained. The overall original scenario classification is still `recording_evidence_invalid`, because completeness is one of its required predicates.

The original evaluator reports SEARCH → VERIFY_EXTREMUM → DESIGN_OR_MERGE_FILL → ESCAPE_REPULSE → ESCAPE_ASSIST → SEARCH, one active fill cluster, correct escape-command ownership and a valid noninterpolated post-recovery global-proximity sample at **185.327 simulation seconds**. That sample is 0.498395 m from the global source; final distance is 0.494997 m. The matched retained 30 Hz reference arrived at 158.053 seconds; this single comparison does not establish a general performance difference. This demonstrates arrival under the established 0.5 m criterion, not autonomous GOAL_HOLD or counted-candidate global confirmation.

`run_05/analysis_01/analysis.json` measured 912 unique observations at 5 Hz during the readiness interval, with 0.2-second source intervals, no duplicates/regressions and no gaps above 0.5 seconds. All 4,563 direction diagnostic publications were output-valid; 3,948 (86.522%) were qualified. Three resets were `objective_changed` during fill/state transitions, not source-gap resets. Diagnostic publications are not independent sensor samples. The read-only analysis finished in 2.434 seconds and verified the original bag files remained unchanged.

The independent closed review, `run_05/outcome_review_01/review_02.json`, confirms detection publication at 84.1 s (84.0 s source history), fill preparation/activation at 99.9 s, ESCAPE_REPULSE at 100.3 s, ESCAPE_ASSIST at 104.3 s and recovered SEARCH at 122.7 s. Exact captured-configuration estimator replay retained 28 of 43 assigned samples, rejecting 12 cost-MAD and three position-increment-MAD outliers. This successful run also used the existing invalid-quadratic handling: condition 155,958,870.759 exceeds the 100,000,000 limit, while the predictor is valid and its 9.48538e-5 residual matches the published fill. The fill/behavior success does not establish a well-conditioned quadratic fit. The original NaN-telemetry JSON serialization failure is retained beside the normalized final review.

The three original failed completeness checks are `v2_synchronized_stream_contract`, `v2_lifecycle_contract` and the consequent `algorithm_event_source_causality` chain. They retain the original two-per-sector and 24-per-revolution requirements. No failed receipt was relabeled. The experimental source changes and minimum 20 enabled one behavioral demonstration; robustness with noise, delay or hardware remains untested.

Changes remain uncommitted on the separate experimental branch. Accepted simulation and V1 commits remain preserved. Final context/diff/process checks and the standard V2 checkpoint are recorded in the artifact root's `closeout_01/`. The next physical work must integrate this experiment with the existing physical owners and physical speed/clock settings; do not deploy the simulation branch wholesale or start base motion from this handoff.

The physical arm-only goal remains paused. Its unchanged completion criterion is three separately recorded, consecutive qualified acquisitions; none are yet qualified. No mobile physical V2 stage is authorized by this simulation result alone, and no base-motion experiment belongs to the paused arm-only goal.
