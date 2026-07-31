# Phase 08.8 M4.8 Fixed V8.7 Primary-Repeat Result

## Disposition

**CLOSED / FIXED POPULATION FAIL AT 3/4 FORMAL PASSES / ALL FOUR
DISPATCHED RUNS COMPLETED THE SCIENTIFIC BEHAVIOR / ASSIST-ENTRY EVIDENCE
DEFECT DIAGNOSED.**

The sealed v8.7 primary population executed seeds `19511`, `19512`, `19513`,
and `19514` exactly once and in order. Seeds `19511..19513` passed all
fourteen predicates. Seed `19514` reached the second/global source after a
complete local recovery but failed the required supervisor-owned-assist
predicate. The runner then stopped. Seed `19514` was not retried, and seeds
`19515..19520` were not dispatched.

The v8.7 secondary probe, secondary repeats, and broader matrix were not
authorized. This result does not overwrite the independently passing v8.7
visible probe or relabel seed `19514` as a formal pass.

## Frozen dispatch

Dispatch HEAD:

```text
308d8c9
phase 08.8: authorize v8.7 primary repeats
```

Installed scenario:

```text
/tmp/phase08_8_v8_7_release_qual.krosar/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_7_primary_repeats.yaml
SHA-256:
  f654f51a3cc445359b1f94c81512f25471d0c388267126bd8923791a1d2b542b
```

The source scenario had the same SHA-256. The execution used isolated
`ROS_DOMAIN_ID=232`, `ROS_LOCALHOST_ONLY=1`, serial headless Gazebo,
`stop_on_run_failure=true`, `stop_on_cleanup_failure=true`, no retry, a
`720.0 s` per-run simulation timeout, a `900.0 s` per-run wall timeout, and
an outer `10,500 s` timeout with bounded interrupt/kill handling. No external
ROS or DDS participant joined the domain during the sealed population.

The interactive console channel detached while the still-running suite was
between cases. It did not terminate, restart, or replace the original
process. The original runner continued and wrote its normal terminal scenario
summary after the first formal failure. Its outer-shell return code was
therefore not recoverable from the detached console channel. The
runner-written summary, retained per-run results, complete recordings, and
clean process audit are authoritative.

The truncated console capture is retained rather than repaired:

```text
/tmp/phase08_8_m4_8_v8_7_primary_repeats_dispatch.log
SHA-256:
  b2a2d6ccff54427cac5c6bba8048c871e4fe021bd52087175fbbdceba01e1963
```

## Retained population

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_7_primary_repeats/scenario_summaries/
  20260731T134126836619Z_phase08_v8_7_primary_repeats.yaml
SHA-256:
  fbf5ea9110fa1aef2fd585690a1bb9f7fa4658d6679e759eb8b93139c741c1ca
```

The runner recorded:

```text
started:   2026-07-31T13:41:26.836619Z
completed: 2026-07-31T14:04:40.613458Z
resolved:  10 seeds
executed:  4 seeds
formal:    3 pass / 1 fail
behavior:  4 pass / 0 fail
recording: 4/4 complete
cleanup:   4/4 pass
```

Per-run results:

| Seed | Formal | Stage A sim s | Stage B s | Exit alignment | Ranking margin | Global distance m |
|---:|:---:|---:|---:|---:|---:|---:|
| 19511 | PASS | 197.117 | 108.800 | 0.999655094 | 0.963365229 | 0.139960 |
| 19512 | PASS | 169.808 | 112.404 | 0.998795498 | 1.093912652 | 0.152056 |
| 19513 | PASS | 199.325 | 105.400 | 0.999909760 | 0.991836480 | 0.127582 |
| 19514 | FAIL | 173.919 | 119.884 | 0.999671269 | 0.991390033 | 0.112068 |

Every run had the exact required state path:

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

Every run created exactly one typed active fill at the first/local candidate,
completed one measured aligned assisted exit, resumed ordinary
raw-plus-Gaussian search, confirmed one distinct second candidate, ranked its
raw-cost interval strictly below the retained first-candidate bound, emitted
`GOAL_REACHED`, and then produced a valid noninterpolated evaluator sample
inside the fixed `0.50 m` simulation radius. No run entered `RECENTER`,
`FAILSAFE`, or `TIMEOUT`.

The evaluator coordinate was unavailable to controller motion and was used
only after controller-ranked `GOAL_REACHED`. Physical operation remains
coordinate free and manually terminated by the operator with `Ctrl+C`.

## Seed 19514 formal failure

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_7_primary_repeats/2026-07-31/
  20260731T135855335566Z_simulation_phase08_v8_7_primary_repeats-
  v8_7_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_238e5bb0
```

Thirteen of fourteen required predicates passed. The only failed predicate
was:

```text
supervisor_owned_escape_assist: false
reason: GESC leaked into the supervisor-owned command
```

All behavioral, recording, final-zero, readiness-false, and cleanup
predicates passed. The run's scientific result was:

```text
fill center:                         (0.895133, 1.157506) m
local convergence point:             (1.008934, 1.347349) m
selected revision-one direction:     (0.548904715, 0.835884929)
measured exit:                        (1.737013, 2.370570) m
fill-to-exit distance:                1.476580 m
selected/actual-exit alignment:       0.999671269
candidate-one retained lower bound:  -2.845819269747874
candidate-two interval:              [-3.8372093023255816,
                                      -3.8372093023255816]
strict separation margin:             0.9913900325777076
global-proximity sample:              (3.611844, 3.507075) m
global-proximity distance:             0.112068 m
final retained distance:               0.112039 m
```

### Message-level causal diagnosis

The schema-v11 predicate begins its strict assist interval at the later of the
first externally recorded `ESCAPE_ASSIST` state and first externally recorded
nonzero supervisor command:

```text
first recorded ESCAPE_ASSIST state:
  1785506493834865483
first recorded nonzero supervisor command:
  1785506493837615474
first evaluated control diagnostic:
  1785506493841327810
```

The first evaluated diagnostic was finite, arithmetically valid, and
correctly saturated. Its unsaturated combined command equaled the GESC
proposal and its supervisor contribution was exactly zero:

```text
GESC vx / wz:                 -0.185747350 / 12.589448298
combined vx / wz:             -0.185747350 / 12.589448298
supervisor contribution:       zero
fresh held supervisor command: zero
```

It was therefore ordinary previous-`ESCAPE_REPULSE` ownership, not a sum of
GESC and a nonzero supervisor command. Because the controller consumes state
and command on separate subscriptions, the recorder can receive the new
state and command before the controller consumes the new state. The
controller code can produce this exact diagnostic only while its latest
consumed state is still `ESCAPE_REPULSE`; after it consumes
`ESCAPE_ASSIST`, the enabled arbitration returns only the supervisor command.

The next diagnostic was already supervisor-owned:

```text
stamp:                              1785506493851741071
delay from authority command:       0.013125597 s
delay from recorded state:          0.016875588 s
combined command:                   supervisor command only
nonzero GESC proposal:              fully suppressed
```

The complete independently replayed interval contains:

```text
ordinary entry-transition samples:       1
GESC-plus-nonzero-supervisor samples:     0
supervisor-owned steady samples:      2,678
later fallback to GESC:                  0
unknown/nonfinite/arithmetic failures:   0
```

All `2,678` later assist diagnostics through the returned `SEARCH` boundary
matched a fresh supervisor command, suppressed the nonzero GESC proposal,
had correct contribution arithmetic and saturation, and retained revision-one
directional authority. The externally recorded transition settled in
`13.126 ms`, well inside the existing `150 ms` cross-topic evidence horizon.

The schema-v11 evaluator checks causal settling only at the assist-to-search
exit. At assist entry it still assumes that external bag publication order is
controller-consumption order and fails immediately on this one valid
previous-state diagnostic. The fixed v8.7 predicate remains failed exactly as
written; this diagnosis does not retroactively reclassify it.

## One-time offline analysis

The standard analyzer ran exactly once for each of the four dispatched runs
after the population closed. Every invocation returned zero, reported
`analysis_failures=[]`, passed fresh Phase 05 validation, and produced every
expected table plus all nine plots.

```text
seed 19511: analysis_status=partial, 9/9 plots
seed 19512: analysis_status=complete, 9/9 plots
seed 19513: analysis_status=complete, 9/9 plots
seed 19514: analysis_status=partial, 9/9 plots
```

The two `partial` labels are limited to optional generic analysis
applicability/gap handling. Neither has a missing critical input, failed
recording check, `analysis_failure`, missing plot, or incomplete scientific
event.

Analyzer log SHA-256 values:

```text
19511  f6d99980179383690f58d4aa5a3d4cde991a469676c66b184d7186c641c2e438
19512  f019a336d9ff25f4766de7db71e677ece5728b11314ca2812653596c99e6311f
19513  facd162a4ee470d80f99039800aba3f86e2fb46f23028bd5be32204626e764f7
19514  22a8092b89339d214e053741581fd59ead86f693420e1a4b42e7a7d749bf3c0f
```

Each run's plot directory is:

```text
<run>/analysis/phase07/plots/
```

and contains:

```text
trajectory_sources_fills.png
candidate_ranking.png
cost.png
components.png
state_events.png
weights.png
command_saturation.png
radial_escape.png
gaussian_history.png
```

Visual inspection of seed `19514` confirms start-to-local capture, one fill,
a direct northeast escape/transit, and final capture around the second/global
source. Its candidate plot shows candidate two strictly below candidate
one's retained bound, and its radial plot shows monotonic assisted exit after
the stalled repulse.

## Artifact hashes

```text
seed   raw bag                                                           completeness
19511  7ce556fcdeb99430bdd80907dbad73e14c24903d19d537560c0dfea9f8862a64  0f06ec4325955eb724f58c8778c6c1b5c43907c8fe4c0a39c7a80f6abfc1243c
19512  0ba7a71241c9898b721c5fd781f4b7fcd4eb16aa874899403b7a19bb6d03e3ad  2c4bfec415cd30161e00fbcf8356e36bcb23768fef365f50cbea78eda5bd0a17
19513  6f651a840b70c6fafa7bb2451150bd9a78ca6df9274a48a5b8415cce7ffd25ef  73910d1a2ab06498fd3bd3ee035a2595c1c6a23608730d69767ee5fa93272cf3
19514  5661e01c3cb3a4230bfe717e973d0b8fb52a51803f9606335897c52d1562c00d  17b4c9f8c36c19cf7e14ee9736eec9db34aa92a9896184d06a1aaa43af8fb1f3
```

```text
seed   scenario_result                                                   analysis_completeness
19511  5a0b9060d68c4aa6f7e4503665d3fedd939c01cdb82c3c800bde75457ef4a259  d5bdc950cd62a6fda3842f690a78b8391e5abe5c2249e36b7f81f6504532ce7e
19512  20acbf7df5efe07e8f465a574fff1da9591e36baedfdd694de484b86f070020c  00b7546e34fa72a6f3528b99fa6fd77b16cc4abde6e433c643178cb7631ef44e
19513  2aae08b138e8646b97f6311abc705b9a855fbbc1864c9b3cfc0e17fc2a1b5ed8  77767c687cd5d1a26d97ee05e110ed58d06cde3fa49bab80b0dccc75887bb5bd
19514  f18c70612ab8fec08f0bbac620dfc90152a33d5932cc37d39e01e271e13eee54  d9d58af1c57bef822a8cb5554251106032925361da36a4eb4cb0c374ce90a59c
```

## Fixed-version conclusion

The v8.7 primary-repeat gate is formally failed and closed at `3/4` formal
passes with four of ten declared seeds dispatched. The scientific behavior
passed `4/4`, and the only failed predicate is a bounded assist-entry
observation defect. V8.7 seeds `19515..19520` and every later v8.7 gate remain
prohibited.

A fresh evidence version may add a bounded causal assist-entry contract
analogous to schema v11's already-qualified assist-exit contract. It must
retain schema versions through v11 byte-for-behavior, continue to reject
GESC-plus-nonzero-supervisor commands, late/unknown/nonfinite transitions,
arithmetic or saturation errors, post-handoff fallback, persistent authority,
or cleanup failures, and change no controller, supervisor, detector, fill,
modified-cost, source, world, motion, ranking, timeout, or stop behavior.
