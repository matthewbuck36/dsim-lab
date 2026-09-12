# R7 paired approach prototype handoff

2026-09-10: finite prototype nomination PASS. Session14834 is terminal/reaped.
All138 trajectories completed;383 source/helper/input pins stayed unchanged.
Final execution summary elapsed45.201062s includes output hashing; the earlier
receipt time is44.980205s. Both are below the90s cap.

| Law | Required starts | Separate hard starts |
| --- | ---: | ---: |
| Existing circular approach |63/63 pass|4/6 pass|
| Fixed-center approach, unchanged circular collection |63/63 pass|6/6 pass|

No pass-to-fail regressions occurred. Readiness became later in28 pairs (maximum
0.6s), earlier in18 and unchanged in21; two previously failed hard cases gained
readiness and have no paired time. This is not a uniform timing improvement.

For the exact C01 anchor, modeled admission improved from5.75s to1.225s while
eligible readiness remained8.0s. D02 admission improved4.85→4.575s, with readiness
13.2→13.3s; D03 admission5.2→4.975s, readiness13.2→13.4s. All keep the original
0.1s initial elapsed offset,0.08m admission and8/12/20s limits. Command ceilings
and continuous commanded-motion criteria passed every nominated case.

The baseline model did **not** reproduce actual C01's approach failure. The
optimistic synthetic signal and ideal unicycle model do not establish its
physical cause, real-field repeatability or direction quality. Actual C01 also
contains92 zero publications among482 VERIFY commands (19.09%); pulse duration,
actuator effects and their contribution to the model difference are not isolated.
The existing native motion metric still measures continuous VERIFY only, with no
DESIGN or escape. No observation is excluded or reclassified.

Exact artifacts and command: [validation](validation/r7_approach_feasibility.md),
external `development/20260910/r7_approach_feasibility_v1/` under the V2 experiment
root. Result SHA256 `9ea9b4e48c7a3f871c85b32e13feda0f612c61158dba990295e2b98a8143fb03`;
receipt SHA256 `1c1e465b30d0829a42ce08b82d4d094f58f01ac6898cabac1a0c24f7988debaa`.
Raw trajectories, reasons, paired times, all failures and late/pre-admission
readiness remain retained. No ROS, Gazebo or field/reference solver ran.

Next: separately adopt and source-validate the bounded phase selection in the
existing tracking/supervisor owners, then save a new visible C trial. Its
hypothesis is improved approach margin, not proven resolution of C01's cause.
R6 zero-only expiry and R5 activated-fill handoff remain preserved. New empirical
arrival, full continuous acquisition, usable analysis and direction evidence are
still required. V11 remains NOT_ADOPTED. Branch V2 at3369cfc, changes uncommitted.
