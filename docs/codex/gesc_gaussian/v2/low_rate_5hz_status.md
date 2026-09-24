# V2 5 Hz feasibility status

CLOSED — SELECTED-CASE BEHAVIORAL SUCCESS. Run_05 completed fill, assisted escape, resumed SEARCH and global proximity at actual 5 Hz/20 RPM. All ten behavior/cleanup predicates passed; the original recording-completeness predicate remains FAIL under strict coverage rules. See [final handoff](low_rate_5hz_handoff.md). Physical commissioning remains paused. Branch `experiment/gesc-gaussian-v2-5hz-20260924` preserves accepted Test D at d1779b6. Earlier entries below are chronological evidence, not current dispatch instructions.

Source preparation is complete: 197 focused/relevant tests pass; xacro default30Hz and selected5Hz expansions pass, with differential-drive odometry still30Hz. The selected rolling launch excludes the other joint-state broadcaster, so the selected plugin is the source cadence owner. No rebuild required: existing accepted Q5 overlay resolves the live source/launch files.

Experimental MOVING policy disables rolling sector population density; policy descriptor names the experiment and hashes it distinctly. Complete rotations, original source gaps/freshness and numerical coherence remain. Recurrent raw verification/snapshot reconstruction uses one actual sample per sector; other paths retain two. Gaussian fitting retains its40-valid-sample requirement. Original post-run validators retain two per sector, so report their density failures separately from simulated behavior.

Evidence root: `/home/mattb/Experiments/GESC-Gaussian/v2/low_rate_20260924`. See source_tests_01/receipt_01.json and cadence_configuration_check.json. Initial stale generated-interface test import, unknown scenario rate override and topology source-binding mismatch are preserved; no simulation has launched. The scenario allowlist correction is implemented. Fresh scenario geometry source-binding refresh is pending, then run_01 preparation and one bounded visible mobile simulation.

Baseline scenario: seed26091152, same world/start/controller,20RPM,5Hz; baseline nominal30Hz D arrival158.053simsec. No physical/Pi changes, mobile trial or completion claim.

## Actual dispatch

Run_01 is consumed and CLOSED_INFRASTRUCTURE_FAILURE before Gazebo: child runner selected Q5's older generated interfaces, missing RecurrentConvergenceDiagnostics. Source stable and strict outer cleanup PASS, session26111 terminal. Topology binding refresh changed only URDF hash and result hash; numerical geometry identical.

Run_02 freshly prepared with Q5 simulation source/launch overlay plus the existing R21 generated interfaces sourced afterward. Explicit interface imports now pass. Fresh receipt696source pins/8source changes; no rebuild. Session45415 dispatched under1125s external/1120s owner bounds. Read its eventual attempt_result.json and scenario_summary.yaml; do not rerun either helper. No physical robot action.

## First exposure closed; focused follow-up running

Run_02 session45415terminal0,421.447s wall; source stable, strict outer/native cleanup and final commandszero/readinessfalse PASS. BehavioralFAIL: nofill/escape/globalarrival before360s recoverytimeout. Actual5Hz unique source stream,1793readiness observations,0gaps>0.5s,0rolling resets. Rolling direction8724/8961qualified diagnostic outputs(97.355%). Detection114.1simsec. Original strict coverage/lifecycle validator failures retained.

Exact first fillresult129.0s REJECTED insufficientvalidimmutablesupport.40assignedrawsamples in14/13/13world-phase cycles;34valid after6cost_MADrejections, belowminimum40. Existing compute_fill_proposal offline withminimum30accepts34, residual9.22947e-5, condition1.968671e6valid, confidence0.687547,0escalations. Evidence run_02/fill_diagnosis_01/min30_proposal.json; originalfailureremains.

Run_03 changes only selected gaussian_fill_minimum_valid_samples40→30. Same5Hz/20RPM/seed/field/start/controller, same frozen8source changes, no build or repeatregressions. Fresh696sourcepins; session13144 launched under1125s externalbound. No physicalaction. Do not rerun consumedhelpers.

## Run_03 closed and diagnosed

Session 13144 terminated (wrapper exit 0), 258.292 seconds wall. The original recorder was interrupted after the first terminal fill rejection; exact PID/start-time/signal evidence is in `run_03/early_stop_receipt.json`. Bag finalized, final zero/readiness false and strict native/outer process cleanup passed. Metadata `target_clean_shutdown=false` and its original completeness failure are retained.

Actual unique source cadence was 5 Hz, with 1,031 readiness-interval source samples, no gaps above 0.5 seconds, no rolling resets and 4,760/5,154 qualified direction diagnostic publications (92.355%; these publications are not unique samples). Trap detection occurred at 120.1 simulated seconds. Fill was rejected at 125.7 seconds with `invalid recurrent raw snapshot: invalid_raw_snapshot`; no fill, escape or arrival occurred. Original strict density/lifecycle failures remain recorded.

Tracing the existing snapshot owner exposed `raw support was interrupted` from `source_gap`. Selected cycles were 62.151–65.085, 68.043–71.012 and 71.012–73.986 simulated seconds. Each has 15 actual samples and no internal gap above 0.2 seconds. Serializing only selected support omits an intervening cycle and introduces a 2.6-second jump. This is a producer/reconstruction mismatch, not a demonstrated source dropout. The selected minimum 30 was confirmed but never reached. See `run_03/snapshot_diagnosis_01/{diagnosis.json,finding.md,receipt.json}`.

Next: focused raw-owner correction and tests, offline replay, then fresh run_04 only if those pass. No Pi change or physical motion; old physical commissioning goal remains paused, 0/3 qualified acquisitions.

## Run_04 preparation

The snapshot correction is complete in the existing raw owner: replay overlapping selected support together and disjoint support groups separately. Global source order, unique observation/source identities and common rotation direction are checked; each group uses unchanged admission/gap/reversal checks. Original cycle geometry, assignments and statistics are then recomputed and compared.

79 focused tests pass (19 new disjoint-support cases). The exact failed run_03 snapshot reconstructs successfully without changing its samples or declared statistics. Its original minimum-30 proposal succeeds with 45 assigned and 37 retained samples; six cost-MAD and two position-increment outliers remain excluded. Receipt: `run_03/snapshot_correction_01/receipt.json`, SHA-256 `7a65a2bee72e97e965bec4fefd7102f52a06c59242525ab1964cdbee01eff522`. Source SHA-256 `d761dc79d6d1b6eed8e5f2bc1683cf5202a6e8ca0fe22b770ddcc1e632272386`.

Fresh run_04 preparation passed with 696 source pins and eight production changes from the accepted baseline; prepared receipt SHA-256 `fab782ec4beac94cdc4f492226b744b8c18fb9f86d47a441669a4edd173cbbf6`. Same 5 Hz, 20 RPM, minimum 30, seed and scenario as run_03. The only new production delta is snapshot reconstruction. No build was needed. Independent review precedes dispatch; preserve source pins throughout the bounded run.

Independent review passed with all 12 receipt pins verified: `run_03/snapshot_correction_01/independent_review_01.json`, SHA-256 `a942fdceaf55d3cfd853a4ad7f918b0a9ac1268043b9ca43ba35d3173b0ab744`. Run_04 launched under the original 1,125-second external bound in session 56535. Read finalized receipts before bag analysis; do not rerun its consumed helper.

## Run_04 closed; remaining count threshold

Run_04 reached the original fitting stage and rejected at 126.8 simulated seconds: `insufficient valid immutable support`. The corrected snapshot was usable. Its three revolutions held 13/13/13 actual samples (39 total); the original outlier filters retained 22 after excluding 11 cost-MAD and six position-increment-MAD samples. Original minimum 30 reproduced the failure offline. Minimum 20 produced a proposal with those same 22 retained samples and zero design escalations; no outlier or fit rule changed.

The quadratic condition number was approximately 1.675465e8, above the configured 1e8 limit. This is an invalid quadratic fit, not a passing numerical fit. The existing designer nevertheless allows a proposal using its established handling for an invalid quadratic (zero curvature contribution and zero fit-condition confidence component, with remaining finite/grid checks). Proposal confidence was 0.660053. This only supports trying the downstream behavior; it is not a reliability claim.

Run_04 was stopped through its exact existing recorder with SIGINT at 19:19:14 UTC. Session 56535 is terminal, 262.238 seconds wall; source pins remained stable. Bag writer and owned process/kernel cleanup completed. Original strict outer cleanup is FAIL because external observer node `/_ros2cli_15614` remained visible (no owned/session survivors); the long-lived topic monitor has since been stopped. A fresh existing-owner inspection, `run_04/post_observer_cleanup_01.json`, proves no new graph nodes or owned/session processes remain. The original failure is unchanged. The general cadence analyzer refused the original failed-cleanup receipt before opening the bag (`run_04/analysis.log`); focused diagnosis used explicit closed-writer proof and preserves the graph failure.

Run_05 will change only selected minimum valid samples from 30 to 20. No source change, rebuild or regression repeat; same 5 Hz/20 RPM/scenario. No persistent observer during final cleanup. This is the last exposure for the current experiment, regardless of outcome.

Run_05 preparation passed: 696 pins/eight production changes, SHA-256 `3f1825921c0da00cd7ee3313eddb6958b9a4fd1c67803418dcc575c0fe7190ab`. Root independently verified scenario differences are only minimum 30 to 20 and the output root. Session 9532 uses the existing 1,125-second external bound and normal arrival/stage-timeout stop. Do not rerun its consumed helper. Run_04 diagnosis is sealed at `run_04/fill_diagnosis_01/receipt.json`, SHA-256 `dac099206629894bfb3d45b5961394ab095e678eaf6f9ca8e854e3755d53a41d`.

## Run_05 behavioral result

Session 9532 is terminal, wrapper exit 0, 228.931 seconds wall. Original arrival-triggered stopping completed without manual interruption. Attempt status `ATTEMPT_RETAINED`, source pins stable, native and outer strict cleanup PASS, no remaining graph nodes or owned/session processes. Bag and target shutdown metadata, final velocity/arm command zeros and readiness handback passed.

The original evaluator observed exactly one fill and the full path SEARCH → VERIFY_EXTREMUM → DESIGN_OR_MERGE_FILL → ESCAPE_REPULSE → ESCAPE_ASSIST → SEARCH. Local recovery, command ownership and post-recovery global proximity passed. The first qualifying global sample was 0.498395 m from the declared global source, without interpolation; final distance was 0.494997 m. GOAL_HOLD/ranked autonomous goal confirmation was not demonstrated or required by this selected arrival experiment.

Closed cadence analysis (`run_05/analysis_01/analysis.json`, 2.434 seconds) measured exactly 5 Hz for 912 unique source observations in the readiness interval. There were no duplicate keys, regressions or gaps above 0.5 seconds; intervals were 0.2 seconds. All 4,563 direction diagnostic publications were output-valid, 3,948 (86.522%) qualified. Three rolling resets were explicitly `objective_changed` during fill/state transitions; none was a source-gap reset. Diagnostic publications are not independent acquired samples.

Original completeness remains FAIL for `v2_synchronized_stream_contract`, `v2_lifecycle_contract`, and the consequent `algorithm_event_source_causality` chain. The unchanged validators demand two observations per sector and at least 24 per snapshot cycle. The overall original classification remains `recording_evidence_invalid`; do not call this an original-contract acceptance pass. It is one clean selected-case demonstration of reduced-density V2 behavior, without noise/delay qualification or physical readiness.

Independent closed review (`run_05/outcome_review_01/review_02.json`, SHA-256 `7c884e2c88329300599ae7347dd6f4000dc096a029092d32cb2e0d5ef65eac02`) confirms detection publication at 84.1 s, prepared/activated fill at 99.9 s, ESCAPE_REPULSE at 100.3 s, ESCAPE_ASSIST at 104.3 s, recovered SEARCH at 122.7 s and evaluator arrival at 185.327 s. The original estimator retained 28 of 43 assigned samples, excluding 12 cost-MAD and three position-increment-MAD outliers. This run's quadratic fit also exceeded its condition limit (155,958,870.759 versus 100,000,000); the valid predictor and original designer fallback permitted the fill. Residual was 9.48538e-5. Neither the successful behavior nor the finite published condition flag makes that quadratic fit valid. Initial review serialization failed on legal NaN telemetry; the partial report and fresh normalized report are both retained.

No further run is planned. Context validation, whitespace/diff review, final process inventory and the standard V2 checkpoint complete the bounded milestone; exact closeout receipts are in `closeout_01/`. Source changes remain uncommitted. Physical goal remains paused and unqualified (0/3), with no Pi or base-motion action.
