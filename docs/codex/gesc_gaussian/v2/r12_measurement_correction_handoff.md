# R12 measurement correction: complete

Completed 2026-09-11 UTC under the [prospective plan](r12_measurement_correction_plan.md).
Two existing owners changed; no detector, controller, verification policy,
scientific threshold or simulation was changed or run.

- `run_scenario._repository_root()` now resolves a normal current checkout
  through its nearest filesystem Git marker without spawning a subprocess.
  Explicit Git repository/discovery/configuration overrides and the existing
  fallbacks retain Git authority. GIT_PAGER does not trigger that fallback.
- `evaluate_m4._arrival_metrics(..., binding_method='recorded_pose_arrival_v1')`
  binds time to the unique valid readiness-scoped recorded /odom pose at the
  exact evaluator bag timestamp. It checks the recorded position, goal/radius,
  distance, frame, source time and recovery evidence. The separately valid live
  arrival may be a different sample. Historical defaults remain unchanged;
  no old or new experiment automatically selects this private opt-in method.
  A later prospective experiment must explicitly select it.

The one focused bundle passed 129/129 checks in 6.896822 seconds outer
(4.58 seconds pytest), with 859 stable source/helper pins and 21 stable selected
entry points. The import component then completed in 1.384024 seconds with
zero subprocess events. The science single-process gate remains unchanged.

One filtered B/noise read completed the separate arrival reassessment in
3.003445 seconds total (1.256668 seconds reading). The exact recorded arrival
was **283.167 seconds**, at 0.498218441926 m from the global source. The live
monitor's different pose appears in the same bag 34 ms later, at 283.201 seconds.
The original unavailable time is retained, and the historical default exactly
reproduced it. The recorded source time was not replaced by live time.

All 870 prepared source/small-input hashes remained stable for that probe.
Raw hashes were inherited from acquisition receipts; raw stat stability was
newly checked. This does not claim a fresh raw-hash verification. Independent
cached review passed 25 checks with 22 stable selected references.

Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r12_measurement_correction_v1/`.

- `focused_v1/source_validation.json`: source session 9350, terminal/reaped 0.
- `import_result.json`: session 36390, terminal/reaped 0.
- `arrival_result.json`: session 36491, terminal/reaped 0.
- `component_review.json`: independent review, SHA256
  `fbe6e190ca0564d38bf0d41cfaf1006be7ccd4cf2c7d81a211af255211b18811`.
- Before copies, exact patches, held owner receipts and preparation are in the
  same directory; [validation](validation/r12_measurement_correction.md) retains
  commands, limits, hashes and the material checkpoint.

V12 remains CLOSED_INCOMPLETE: twelve complete acquisitions, four unstarted
delay cases, two completed scientific blocks. Its results were not rewritten.
The noisy moving verification and direction failures remain unresolved.

Next work is a prospectively bounded retained-data profile/direction study,
including a fresh qualified D/noise reference product through the existing
numerical owner. A successful arrival-time correction does not qualify the
whole noisy block or release a matrix. Retain all scheduled/eligible/failure
denominators and treat every reused V12 input as exposed development evidence.

No runtime is active. Branch remains `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes are uncommitted.
No physical/Pi/snapshot/V1, commit or push action occurred. The full research
goal remains incomplete.
