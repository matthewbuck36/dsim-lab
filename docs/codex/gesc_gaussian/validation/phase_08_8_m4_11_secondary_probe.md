# Phase 08.8 M4.11 fixed v8.10 secondary visible result

Date: 2026-07-31
Committed dispatch boundary: `f3bfb1f`
Scenario: `phase08_v8_10_secondary_visible_probe.yaml`
Case: `v8_10_secondary_probe_r1p5_a67p5_h25_19851`
Seed: `19851`
Profile: `robust_gaussian_v1`

## Disposition

**CLOSED / FIXED FORMAL FAIL / SCIENTIFIC LOCAL-RECOVERY-TO-GLOBAL
BEHAVIOR COMPLETED / DIRECT-REPULSE OWNERSHIP PASS / DECLARED-SOURCE
STAGE-A ASSOCIATION FALSE NEGATIVE / NO RETRY.**

The one authorized v8.10 secondary visible probe executed once with Gazebo
GUI enabled. It completed one detected basin convergence, created exactly
one typed fill, escaped by the accepted direct-repulse branch, resumed
ordinary GESC, confirmed a second candidate, ranked that candidate strictly
lower, emitted `GOAL_REACHED`, entered `GOAL_HOLD`, and finished
`0.105549 m` from the declared global.

It nevertheless failed four formal predicates because the staged evaluator
could not associate the observed first convergence/fill cluster with the
declared local lamp coordinate within its fixed `0.60 m` gate. Stage A
therefore remained formally incomplete until its `360 s` timeout, and the
already-achieved global proximity could not receive Stage B credit.

This fixed result is not retried or relabeled. The five v8.10 secondary
repeats, M6 broader matrix, and any later v8.10 Gazebo execution remain
prohibited.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  f3bfb1fcdd42c58e00581644a36ebe3fbdd2f9f2
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_secondary_visible_probe.yaml
installed scenario SHA-256:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
ROS_DOMAIN_ID:
  227
presentation:
  visible Gazebo GUI
attempts / retries:
  1 / 0
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/
  phase08_v8_10_secondary_visible_probe_summary.yaml
SHA-256:
  6857aaa727b63079aa3910ecbdd110f51ae9dc68f5a9b63295358d7976d1f4e1
```

Exact summary-owned run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/2026-07-31/
  20260731T191433826976Z_simulation_phase08_v8_10_secondary_visible_probe-
  v8_10_secondary_probe_r1p5_a67p5_h25_19851_5cffc8a7
```

```text
started:                       2026-07-31T19:14:32.804136Z
completed:                     2026-07-31T19:21:45.435149Z
runner return code:            1
record process return code:    0
record process timed out:      false
recording complete:            true
authoritative completeness:    PASS
final command zero:            PASS
final readiness false:         PASS
bag sqlite quick_check:        ok
cleanup:                       PASS
remaining new nodes:           none
remaining session processes:   none
formal predicates:             10/14 PASS
```

Recorder metadata proves the runner-CWD correction:

```text
working_directory: /home/mattb/dsim-lab
repository_root:   /home/mattb/dsim-lab
commit:            f3bfb1fcdd42c58e00581644a36ebe3fbdd2f9f2
dirty:             false
untracked_paths:   []
```

Dispatch log:

```text
/tmp/phase08_8_m4_11_v8_10_secondary_visible_dispatch.log
SHA-256:
  75af334fe271276395e1e9879bbb7949d3e1541f66e72e7fe7a9954c0e620f43
```

## Formal failure

The four failed predicates were:

```text
local_recovery_stage:            false
fill_cardinality:                false
post_recovery_global_proximity:  false
ground_truth_goal:               false
```

They are one cascading evaluator failure, not four independent behavioral
failures.

The detector confirmed the first convergence at:

```text
observed convergence center:
  (1.1932522798, 1.8213642373) m
declared local lamp:
  (0.5740251485, 1.3858192988) m
convergence-to-declared-local:
  0.7570611822 m
formal association maximum:
  0.60 m
```

The Gaussian estimator then placed the one fill at:

```text
fill center:
  (1.1854262109, 1.8223420991) m
fill-to-observed-convergence:
  0.0078869239 m
fill-to-declared-local:
  0.7512412491 m
fill-to-global:
  2.8586339145 m
created / typed / active clusters:
  [1] / [1] / [1]
assigned clusters:
  []
unassigned clusters:
  [1]
```

The fill is accurately centered on the detector's observed basin, but that
basin is more than `0.60 m` from the local lamp marker. This layout uses two
overlapping source fields. The retained trajectory and signal evidence are
consistent with the aggregate-cost basin being shifted away from the lamp
coordinate. The evaluator's `local_association_mode=declared_source`
incorrectly assumes that the lamp coordinate and aggregate-field local
extremum remain colocated closely enough for this layout.

Because cluster `1` was unassigned, the live monitor never marked Stage A or
fill cardinality complete. It therefore never opened Stage B, even though
the controller had already reached and ranked the global:

```text
scientific local-recovery exit sim time:
  115.6 s
controller GOAL_REACHED sim time:
  233.2 s
Stage A evaluator timeout sample:
  360.154 s
timeout position:
  (3.5843550796, 3.5634411591) m
distance from global:
  0.1055488518 m
```

The explicit stop at the Stage A timeout moved the post-readiness shutdown
state to `FAILSAFE`. It occurred after readiness became false and is not an
accepted-motion forbidden state or controller failure. No `RECENTER`,
`FAILSAFE`, or `TIMEOUT` occurred inside the formal readiness interval.

## Scientific behavior and schema-v13 direct branch

The accepted direct path occurred:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Schema v13 correctly selected and passed the direct-repulse ownership branch:

```text
branch:
  direct_repulse
evidence mode:
  bounded_direct_repulse_schema_v13
repulse state / control samples:
  438 / 2,833
nonzero GESC control samples:
  2,833
mature radial-progress samples:
  378
minimum mature radial progress:
  0.167010 m
maximum mature radial progress:
  0.221805 m
maximum radial distance:
  1.429333 m
frozen exit radius:
  1.366771 m
fill-to-exit distance:
  1.440018 m
selected/actual alignment:
  0.973428466
returned SEARCH samples:
  2,170
ordinary GESC ownership restored:
  true
supervisor authority cleared:
  true
```

No assist interval was applicable. The legacy
`supervisor_owned_escape_assist` field therefore reports no valid assist
interval, but the gating schema-v13 `escape_command_ownership` predicate
passes the direct branch exactly as designed.

The two raw candidate intervals were:

```text
candidate one:
  estimate  -0.2290496649
  lower     -0.2312067119
  upper     -0.2268926180
candidate two:
  estimate/lower/upper  -3.8372093023
strict separation margin:
  3.6060025904
candidate ordinal / filled count / known source count:
  2 / 1 / 2
decision:
  GOAL_REACHED
```

Thus the controller independently completed the intended counted-source
policy: treat candidate one as unknown, fill and escape it, find candidate
two, and identify candidate two as globally stronger by raw cost.

## One-time offline analysis

The analyzer target was read verbatim from the exact scenario summary after
the failed population closed. The run directory was proven below the fresh
root with a complete bag before the sole invocation.

```text
analyze_run invocations:       exactly 1
return code:                   0
analysis status:               complete
analysis failures:             []
fresh Phase 05 validation:     PASS
critical inputs:               complete
plots:                         9/9
fill count:                    1
escape attempts/successes:     1/1
assisted:                      false
failsafe/timeout in analysis:  false/false
escape time:                   22.046193 s
path length:                   13.368343 m
goal convergence time:         232.764208 s
terminal state:                GOAL_HOLD
```

Analysis log:

```text
/tmp/phase08_8_m4_11_v8_10_secondary_visible_analysis.log
SHA-256:
  1e016f46d4515e229b19a492cf74a8d3b360e3ae458181cddeecf5bd189ffbc2
```

The trajectory plot was visually inspected. It shows convergence and one
fill at the shifted first aggregate-cost basin, direct escape, ordinary
transit, and final capture around the global source.

## Artifact hashes

```text
bag/bag_0.db3:
  de82489ace8f69895e2b67e91d68bd66e49f6b208b561539ae018cf0de20dd08
bag/metadata.yaml:
  c90ee1f71c6cdf03069635e69f28dfb77499fb9d337777d08184925e096fa84b
metadata.yaml:
  fa954686c74860a4c4bd65318ff2ef56df1c36166fa255f4d0d990ae216b37a9
completeness.json:
  63c82f4d71d92636cd346278f15a44078c7c2e764089747fe9b19f7f439336e1
scenario_result.yaml:
  0a1e643ab211835053731e60fd7e0c5b6b9af1a4d35fd1680d1bc363ac8660a7
resolved_scenario.yaml:
  4f6efe28732afc2685d21efe24667ac6595ab6dcf394a769a4d4d9855288ac13
analysis/phase07/analysis_completeness.json:
  2a039fa7952d4a4663f6332087458e0e0e5da7a615e70f6b530348758f0cd679
analysis/phase07/summary_metrics.json:
  872dc121447efbf856e855a95eb66d4ec25429413ea5aaa901477d12012901a1
```

Plot SHA-256 values:

```text
candidate_ranking.png
  24d09e274fdabaffec1a7b295c88a99029f354e41268911865b4339e02e2eb66
command_saturation.png
  8aa65e850fb95408aacd4142109be0681c7321808bb61b3e7f21d5804edca3d7
components.png
  784d3c3030fcdd71eb88d1cd04a272065926d844949d602b040c202fd29ff890
cost.png
  964e239bf8926b1fefad229c6edb71a6dd20f579e1d7478103538f97616f830c
gaussian_history.png
  ea94db82f3bf2c5ce7a0974d3b1250e8e014fa6bb42d7fff5e5070aa16813fd4
radial_escape.png
  0fbce1572e1c8598d3e03137fc9dcf5b47d6ba0ba3049b7ad4d025f0c11ed50f
state_events.png
  df3ace7765ef122cfe64ef898f353259ef264c6ff001e86abcd736fc37956e99
trajectory_sources_fills.png
  ec7810a1c250e4f7b19eeb781f51461edd724620e93670d5cc350a137234bea0
weights.png
  9da478c052dc2c8056a28f25012cda00fe4b94ef2667e19a37b2d12aa4369492
```

## Fixed-version conclusion

The v8.10 secondary-visible gate is formally failed and closed. Seeds
`19861..19865` are not dispatched, and M6 is not authorized. The independently
passing primary visible probe and `10/10` primary population remain valid.

A future version may correct evaluator ground truth by precomputing the
aggregate-field local extremum offline or by associating the one pre-global
basin without assuming it is colocated with a lamp. That evaluator geometry
must remain inaccessible to the controller and must be planned and frozen
before another run. Simply widening `0.60 m` after observing this outcome
would be outcome-based gate weakening and is not permitted.

The fixed result provides strong scientific evidence that the algorithm
escaped a shifted first basin and converged to the stronger second source,
but it is not a formal secondary-layout pass under the declared v8.10
contract.
