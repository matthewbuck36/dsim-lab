# Phase 08.8 M4.9 Fixed V8.8 Primary-Repeat Result

## Disposition

**CLOSED / FIXED POPULATION FAIL AT 5/6 FORMAL PASSES / ALL SIX
DISPATCHED RUNS COMPLETED THE SCIENTIFIC BEHAVIOR / VALID DIRECT-REPULSE
RECOVERY REJECTED BY THE ASSIST-ONLY EVIDENCE TOPOLOGY.**

The sealed v8.8 primary population executed seeds `19611` through `19616`
exactly once and in order. Seeds `19611..19615` passed all fourteen fixed
predicates. Seed `19616` found the local candidate, created exactly one fill,
escaped the filled basin, found and strictly ranked the second candidate, and
converged to within `0.104056 m` of the declared global. It nevertheless
failed the fixed v8.8 result contract because its successful recovery followed
the already-designed direct path

```text
ESCAPE_REPULSE -> SEARCH
```

instead of entering the fallback

```text
ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

The runner stopped after that fixed failure. Seed `19616` was not retried,
and seeds `19617..19620` were not dispatched. The v8.8 secondary visible
probe, secondary repeats, broader matrix, three-light execution, and physical
motion were not authorized.

This report preserves v8.8 as failed. It does not add seed `19616` to the
formal-pass count or weaken any result after dispatch.

## Frozen dispatch

Dispatch HEAD:

```text
5e69f11
phase 08.8: authorize v8.8 primary repeats
```

Installed scenario:

```text
/tmp/phase08_8_v8_8_release_final.L0zEGg/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_8_primary_repeats.yaml
SHA-256:
  003230a00ddc0ab07adad5957012c3c28539119fbbb885a3edcd5f594b4298ca
```

The source scenario had the same SHA-256. The population used isolated
`ROS_DOMAIN_ID=223`, serial headless Gazebo, `stop_on_run_failure=true`,
`stop_on_cleanup_failure=true`, no retry, a `720.0 s` per-run simulation
timeout, a `900.0 s` per-run wall timeout, and an outer `9,600 s` timeout
with bounded interrupt/kill handling. No external ROS or DDS participant
joined the domain during the sealed population.

The runner returned `1` after writing its normal stopped-early summary at the
first formal failure. At closure, no Gazebo, scenario-runner, recorder,
rosbag-recorder, analyzer, or physical process remained.

Console log:

```text
/tmp/phase08_8_m4_9_v8_8_primary_repeats_run.log
SHA-256:
  9a14fceea16bb07b6f543c14714b65d8b0d0745f6b101626722acb8ead9d3b75
```

## Retained population

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_repeats/scenario_summaries/
  20260731T152229585403Z_phase08_v8_8_primary_repeats.yaml
SHA-256:
  088e54b95af59f4941be93b869c033e7e34a9ae9c61d42ca4b93f353c77aa6e9
```

The runner recorded:

```text
started:   2026-07-31T15:22:29.585403Z
completed: 2026-07-31T15:58:10.302333Z
resolved:  10 seeds
executed:   6 seeds
formal:     5 pass / 1 fail
behavior:   6 pass / 0 fail
recording:  6/6 complete
cleanup:    6/6 pass
sqlite:     6/6 read-only quick_check=ok
```

Per-run fixed results:

| Seed | Formal | Stage A sim s | Stage B s | Exit alignment | Ranking margin | Final global distance m |
|---:|:---:|---:|---:|---:|---:|---:|
| 19611 | PASS | 162.606 | 125.018 | 0.992652419 | 1.449977017 | 0.108205 |
| 19612 | PASS | 186.603 | 108.426 | 0.996037173 | 1.238716245 | 0.138014 |
| 19613 | PASS | 191.826 | 103.700 | 0.999973028 | 1.402942078 | 0.139779 |
| 19614 | PASS | 174.712 | 114.002 | 0.999723482 | 0.991743890 | 0.165479 |
| 19615 | PASS | 179.126 | 117.402 | 0.999507870 | 1.118214205 | 0.139126 |
| 19616 | FAIL | contract unavailable | contract unavailable | direct 0.947518 | 0.988865148 | 0.104056 |

Seeds `19611..19615` each followed the assisted path, produced one typed
active fill, proved schema-v12 causal assist entry, proved schema-v11 causal
assist exit, ranked the second raw-cost interval strictly below candidate
one, and produced the first valid noninterpolated post-ranking sample inside
the fixed evaluator-only `0.50 m` radius.

Their schema-v12/schema-v11 handoffs were:

| Seed | Entry handoff ms | Steady owned samples | Exit handoff ms |
|---:|---:|---:|---:|
| 19611 | 5.783 | 2,627 | 7.721 |
| 19612 | 3.320 | 2,018 | 7.721 |
| 19613 | 4.509 | 1,760 | 3.299 |
| 19614 | 9.698 | 2,663 | 10.827 |
| 19615 | 7.655 | 2,664 | 8.557 |

All are below the fixed `150 ms` evaluator-only bound. The global coordinate
was never available to controller motion. Physical stopping remains manually
operator-controlled with `Ctrl+C`.

## Seed 19616 formal failure

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_repeats/2026-07-31/
  20260731T155106376968Z_simulation_phase08_v8_8_primary_repeats-
  v8_8_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_86adf15e
```

Its observed scientific state path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

The fixed scenario instead required:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

and required `ESCAPE_STALLED` plus
`supervisor_owned_escape_assist`. Because the fallback was not needed, all
three were absent.

The resulting formal predicate cascade was:

```text
required_state_path:                 false
required_events:                     false
required_event_sequence:             false
local_recovery_stage:                false
supervisor_owned_escape_assist:      false
controller_goal:                     false
ground_truth_goal:                   false
post_recovery_global_proximity:      false
```

The last four values are not independent navigation failures. Stage A
withheld its completion stamp solely because it accepted only the assisted
path. Candidate ranking and post-recovery proximity are intentionally gated
on that stamp. The live monitor therefore requested an orderly evidence stop
at the `360.0 s` Stage A budget even though `GOAL_REACHED` had already
occurred.

Recording, exact one-fill cardinality, terminal `GOAL_HOLD`, forbidden
state/event absence during the result scope, final readiness false, final
zero commands, sqlite integrity, and cleanup all passed.

### Direct-recovery evidence

The local candidate evidence was:

```text
local convergence point:            (1.222595, 0.970340) m
distance to declared local:          0.185421 m
fill center:                         (1.372740, 1.053878) m
fill-to-convergence distance:        0.171819 m
created / typed / active clusters:   [1] / [1] / [1]
merge or supersession:               none
```

The accepted fill's frozen geometry was:

```text
exit radius:                         1.366771 m
selected revision-one direction:    (0.686844133, 0.726804745)
```

The direct repulse interval lasted `23.328587 s`. The standard analyzer
classified it as a successful, non-assisted, non-stalled, non-timeout,
non-failsafe escape. Read-only alignment against the odometry sample nearest
the recorded stable-exit transition gives:

```text
stable-exit simulation time:         197.5 s
nearest exit position:               (2.610167, 1.711114) m
odometry/transition stamp delta:      1.188186 ms
fill-to-exit distance:                1.401137 m
selected/actual-exit alignment:       0.947517529
```

The retained synchronized evidence contains `3,015` valid
`ESCAPE_REPULSE` control samples. On every one:

```text
maximum |supervisor contribution|:   0.0
maximum |combined - GESC|:            0.0
```

All `2,640` samples with a mature radial-progress window reported progress
between `0.059685 m` and `0.225543 m`, above the fixed `0.05 m` stall
threshold. No sample reported stalled. Requiring this successful trajectory
to enter `ESCAPE_ASSIST` would contradict the controller's fixed rule that
assist is a fallback only after measured stall.

The post-recovery scientific evidence was:

```text
candidate-one retained lower bound: -2.8483441544287578
candidate-two interval:             [-3.8372093023255816,
                                     -3.8372093023255816]
strict separation margin:            0.9888651478968238
candidate ordinal / source count:     2 / 2
GOAL_REACHED simulation time:         314.7 s
final retained position:             (3.535256, 3.597901) m
final global distance:                0.104056 m
```

The trajectory, radial-escape, state/event, and candidate-ranking plots
visually confirm local capture, monotonic direct escape, ordinary
post-recovery transit, strict second-candidate ranking, and final capture
around the declared global.

## Root cause and correction boundary

This is an evaluator-topology integration defect, not a controller, detector,
fill, affine, ranking, or navigation defect.

The Phase 08.8 architecture already states that both of these are valid:

```text
direct:
  ESCAPE_REPULSE -> SEARCH

fallback:
  ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

The implementation instead makes Stage A choose only the assisted recovery
path whenever `open_field_escape_assist_enabled=true`, and the fixed v8.8
scenario independently requires `ESCAPE_ASSIST`, `ESCAPE_STALLED`, and
`supervisor_owned_escape_assist` on every seed. That rejects the exact case
where Gaussian plus affine repulsion succeeds strongly enough that fallback
translation is unnecessary.

A fresh evidence version may:

1. accept either declared recovery topology;
2. require direct-path geometry, radial progress, ordinary GESC ownership,
   zero supervisor contribution, stable exit, and returned-search cleanup
   when assist is not entered;
3. retain the complete schema-v12 supervisor-ownership contract whenever
   assist is entered;
4. make the common event sequence independent of the conditional
   `ESCAPE_STALLED` event;
5. preserve v8.8 and schema versions through v12 exactly; and
6. change no controller, supervisor, detector, fill, modified cost, source,
   world, motion, ranking, timeout, cleanup, or stop behavior.

It must not merely mark a missing assist as passed. The direct branch needs
positive proof that the accepted fill caused a bounded, aligned, stable
escape under ordinary GESC ownership.

## One-time offline analysis

The standard analyzer ran exactly once for each of the six dispatched runs
after the population closed. Every invocation returned zero, reported
`analysis_failures=[]`, passed fresh Phase 05 validation, produced every
expected table, and produced all nine plots. Every analysis status is
`complete`.

```text
seed 19611: complete, 9/9 plots
seed 19612: complete, 9/9 plots
seed 19613: complete, 9/9 plots
seed 19614: complete, 9/9 plots
seed 19615: complete, 9/9 plots
seed 19616: complete, 9/9 plots
```

The common analyzer warnings are only the recorded/default fallback
declarations for channel index, synchronization tolerance, and supervisor
publish rate. No critical input, recording check, plot, or scientific event
is missing.

Analyzer log SHA-256 values:

```text
19611  e0a99df1f6d20feda97d4ad132272eface16fc904e94a9dab9cc22e5505a2af0
19612  1b1d1adfa6fc03fd5299883824f7e9fa2579904afaf400e56ecf1c77e8f73635
19613  2484874f28b605738d849c8a1bb9fd8022c953d7bc04d50724713d71dff4df62
19614  ae2d32c5444e72c04ba90a7a9b4d1df7260d0ae4ad278010340faa269480ec01
19615  835b284124080722796c5f07da387e854e9180393c9ea6d446cb604f2f7dfa32
19616  76eabd0379d56abed7167f919ab78ecf3c190070a65d84c8b3535af3a566c0e1
```

Each plot directory is:

```text
<run>/analysis/plots/
```

## Artifact hashes

```text
seed   raw bag                                                           completeness
19611  b97d39b4c0e58d06d595a2e10febe964737eca3379d56730022a017ef26223cd  4b7e5a6819053836834a732fb0fd89af529d089b3dc3d2d3c3a85392ad4e27c8
19612  8379fdeb70da504b3060648a345d183451b2bf4252252023f080bc839263b724  e12b0c6b983eebeb683e91367bd690b8d19aa81a15ee37272b0daf1fa7e9c39f
19613  e50c475f1455956f4f710ff03630be5448ca14845345a026b37214eea84846e3  89db21daf9970483bcdbf6f3cbc056560e3307db24e401987b32c69a1404cd4b
19614  b790ada7d15de6e551c5e0caf98b7cee69fab5d39917cfd5377c316af3568f3c  786985f2843604cfc4cf36e0324586222906fff745f25597eb48d651eeae5058
19615  5d44504bf5797cd627afcf99660ad79a668d3e24fc72e1f0616bc3ffd82a2f07  b71afecb9fbe0977e270b5834065d7435918b7b7f7554ab4131b23141b771a97
19616  5e610277441d4e2d6994986f141ab75c91516a5d18f84b03bfa4af6b3e8f1a79  42b1582eacde44f2e46a82dbb3dfb22646e44575b4436637d58ef3a450b123c0
```

```text
seed   scenario_result                                                   analysis_completeness
19611  66f214bdec79b167a8894f66f4f08e6e58dcaebff9df322597ecd1bc5b08bab9  cba73dbf06ac9d5f4afaa085aa14cac56f8fa904d6d8e7fcb3c3647835da8cb2
19612  1fcb84f630d9ebefcf5b5037578f53ec6338bc3fe875e31900ee389ca3af7424  246ca4b7a7b89003e865919c448d82447509e35e0d9c6c7d353c2fbc63fdb8a8
19613  f02952f5d8bc7b776adca2d40683f170660caae558bed80cc84431d4e420855c  a3e41961a566a083906bde66859b916d2cda98d1a8f5e325e3fffee8245b54c6
19614  530ae8f9b2393859290e9365fb6d8c9638b3f3410bbdd58d9a19d35c39cc7afa  40c7a2390ef9327c612c2ff44476173e534d106ad4c57d28015069f9cd94d8c4
19615  0d8afa14f18492472a19296d363eb106f9a1fed7d97bc227dc6c9145900427f8  cb9783aaecfadba05d72cf644107886755f7776b016aee3a1984bb95afe1222c
19616  8d54edd621f29a1ee6f493d1a61c4c3398b80b9188d9de7c7961de2d23b5733f  16d494f7c9b521fa8cdd3efdace515c187cf665747e1bd3628778645b0031216
```

## Fixed-version conclusion

The v8.8 primary-repeat gate is formally failed and closed at `5/6` formal
passes with six of ten declared seeds dispatched. The complete intended
scientific behavior occurred in all six runs. The first five required the
supervisor-owned fallback and proved it. The sixth did not stall, completed a
bounded aligned direct repulse, and therefore correctly never entered the
fallback.

V8.8 seeds `19617..19620` and every later v8.8 gate remain prohibited. Any
correction must be separately versioned and must retain this failure
unchanged.
