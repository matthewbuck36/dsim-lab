# R20 execution preparation appendix

Frozen before synthetic generation or numerical fits. The exact generator law,
coefficient scales, cohort populations, seed equations and RNG draw order are
in `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r20_local_attraction_v1/controls_config.json`, SHA256 `3336a05a9931befe624815f004743665cceb09c0944abf16428514329f87e195`.
The generator implements the adopted plan without post-result threshold tuning.
Each 840-row episode uses independent orientation and rotor phase. Calibration
is saved after 2,388 fits and before evaluation inputs are generated. All 1,660
inputs and 4,980 fits are retained, including unavailable cases.

Tracking integration is frozen in the same external root's
`tracking_integration_plan.json`: midpoint at 5 ms, three 28-second cases,
30 Hz descriptive samples, and final state at 28 seconds. These are mathematical
unicycle component measurements; entry, ROS transport and Gazebo remain untested.

The attraction decision uses the full covariance and rejects nonzero error in
numerical covariance null directions (relative eigenvalue tolerance 1e-10;
null error roundoff tolerance 1e-12 times max(1,error norm)). It never floors
curvature or supplies uncertainty in unsupported directions. The empirical
multiplier excludes harmonic/spatial model bias. Source and execution pins are
saved before each finite job. Full/half fits share the anchor and map, adjacent
time intervals and additive row count; source/epoch authority remains outside
this pure component.

Selected-field preparation follows separately before any model call.
