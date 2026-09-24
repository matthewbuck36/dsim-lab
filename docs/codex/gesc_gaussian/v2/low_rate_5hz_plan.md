# V2 5 Hz Gazebo feasibility experiment

User requested on 2026-09-24: prioritize progress toward physical mobile tests by testing V2 at 5 Hz in Gazebo and ignoring the prior sampling-density coverage requirement. This is a new simulation experiment; physical commissioning stays paused.

Work on branch `experiment/gesc-gaussian-v2-5hz-20260924`, preserving accepted Test D at `d1779b6` and all historical evidence. No Pi edits, firmware changes or physical motion. Reuse existing launch, algorithm, recorder, scenario runner, validation and cleanup owners.

## Single current milestone

Run one fresh visible nominal Test D mobile simulation with seed 26091152 and its established world/start/controller, 20 RPM arm, nominal 5 Hz source stream. Existing normal-speed 30 Hz D reference arrived at 158.053 simulated seconds. The comparison is a selected-case feasibility check, not a robustness claim.

Expose source cadence through the existing Gazebo joint-state publisher with a 30 Hz default and a 5 Hz scenario override. Modify only the necessary V2 sample-density checks on the experimental branch and record the exact changed policy descriptor/hash; retain finite data, fresh timestamps, synchronization, complete-revolution integration, geometry, command ownership, final zero and bounded cleanup. Report any further blockers rather than silently changing them. Default legacy methods remain unaffected.

Use focused synthetic low-rate/legacy regressions, existing native parameter/metadata validation, and one bounded visible run. Keep original completeness and behavioral results separate from the fact that sampling density has been relaxed. Measure actual source cadence and useful rolling direction; report convergence, fill, escape, arrival, fail reasons and shutdown. Do not rerun the historical matrix. A follow-up run is justified only by an actionable failure or correction.

Artifacts: `/home/mattb/Experiments/GESC-Gaussian/v2/low_rate_20260924`. Fresh attempt directories/IDs, never consumed helpers. Update this experiment status/handoff and the V2 live pointers, run the existing checkpoint owner at the material result boundary. No commit or push requested.

## Evidence-backed second exposure
Run_02 actual5Hz,0>0.5s gaps, qualified direction97.36%, trapconfirmed114.1simsec. Fill rejected129s because40assigned samples became34valid after6cost-MAD rejections, belowminimum40. Run_03 changes only the selected fillminimum40→30; preserveoutlierrejection/fitqualitychecks. Require offline original-proposal replay first; no repeatedsoftwarebuildorregressionofunchangedcode. This follow-up tests the requested density relaxation consistently through the fill input stage.

## Snapshot contract correction and final bounded exposure

Run_03 rejected before fitting because the producer selected three nonadjacent eligible revolutions and serialized their support union, while the consumer assumed a continuous stream. Each selected revolution has 15 actual samples and maximum 0.2-second internal gaps; the omitted intervening revolution creates a 2.6-second jump only in the serialized union. Evidence: `run_03/snapshot_diagnosis_01/finding.md` under the artifact root.

Correct this bounded producer/consumer mismatch using the existing raw-evidence owner. Preserve the 0.5-second within-support gap limit, original admission/identity/order checks, full rotations, assignments, geometry and exact statistics. Require focused regression tests and offline replay of the failed snapshot through the corrected owner and original fill proposal. Run_04 then changes only this correction relative to run_03; retain 5 Hz, 20 RPM, minimum 30 and the same seed/world/controller. Stop after this exposure and report the actual feasibility boundary; no automatic matrix or physical deployment.

## Final sample-count-only amendment

Run_04 passed the corrected snapshot stage, but its 39 assigned samples became 22 after the unchanged outlier filters (11 cost MAD, six position-increment MAD), below minimum 30. This still prevented the requested reduced-density experiment from exercising a fill. Captured-configuration offline replay at minimum 20 produces a proposal through the existing estimator/design path, without relaxing outlier or numerical rules. Report any estimator fallback honestly; a computed proposal does not establish a successful quadratic fit.

One final fresh run_05 changes only selected minimum valid samples 30 to 20. Retain all source, cadence, arm speed and scenario settings. No rebuild or unchanged regression repeats. Do not lower the count again or begin a matrix after this run; close with the observed feasibility boundary. Any live topic inspection must terminate before cleanup; preserve run_04's original external-observer graph-cleanup failure and separate subsequent clean-state evidence.

## Closed outcome

Run_05 demonstrated the requested selected-case feasibility: actual 5 Hz, 20 RPM, one fill, assisted escape, resumed SEARCH and arrival within 0.5 m of the global source at 185.327 simulation seconds. The original strict coverage/completeness result stays FAIL. The valid predictor/existing designer fallback was used despite an invalid quadratic condition number. See the [handoff](low_rate_5hz_handoff.md) for exact evidence and limits. This milestone is closed; no automatic additional run or physical deployment is planned.
