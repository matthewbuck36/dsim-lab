# Phase 08.7 M4.3 Two-Light Suite Report

## Verdict

The fixed M4.3 serial two-light qualification is **CLOSED / FAIL at 6/8**.
The visible probe and all eight suite attempts have valid, complete evidence,
but the readiness rule requires every attempt to pass.

The fixed suite produced:

- spatial cases: `3/5` passed;
- central spatial/repeat cases: `4/4` passed;
- fixed visible plus central spatial/repeats: `5/5` passed;
- repeatability cases: `3/3` passed;
- all-case recording completeness: `8/8`, each `48/48`;
- all-case cleanup: `8/8`;
- all-case collision expectation: `8/8`;
- Stage A local recovery: `7/8`;
- Stage B post-recovery global proximity: `6/8`;
- combined result: `6/8`.

This is a behavioral qualification failure, not an infrastructure,
recording, collision, final-zero, cleanup, or M4.3 event-attribution failure.
No case was retried or changed, and the optional three-light probe did not
run.

## Fixed execution

The exact committed suite input had SHA-256:

```text
37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc
```

It ran once, serially and headlessly, on ROS domain `162` from the isolated
M4.3 install:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_3_qual/install/setup.bash
export ROS_DOMAIN_ID=162
export ROS_LOG_DIR=/tmp/phase08_7_m4_3_suite_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_3_suite_mpl
export TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 5400s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_3_two_light_suite.yaml \
  --operator Codex \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3/\
phase08_v7_m4_3_two_light_suite_summary.yaml
```

The suite started at `2026-07-30T09:00:39.750638Z`, completed at
`2026-07-30T09:41:46.322069Z`, and returned `1` because two fixed behavioral
contracts failed. The outer timeout did not fire. All eight cases executed
exactly once in committed order.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3/
  phase08_v7_m4_3_two_light_suite_summary.yaml
```

## Per-case result

| Fixed case | Stage A | Stage B | Combined | Recording | Cleanup | Primary observation |
|---|---:|---:|---:|---:|---:|---|
| `v7_m4_3_r1p0_a45_h25_18309` | fail | fail | fail | 48/48 | pass | `RECENTER -> FAILSAFE`; no recenter completion |
| `v7_m4_3_r1p5_a22p5_h25_18309` | pass | fail | fail | 48/48 | pass | 120.02 s Stage B budget expired at 3.277 m |
| `v7_m4_3_r1p5_a45_h25_18309` | pass | pass | pass | 48/48 | pass | 1.200 m boundary reached |
| `v7_m4_3_r1p5_a67p5_h25_18309` | pass | pass | pass | 48/48 | pass | 1.199 m boundary reached |
| `v7_m4_3_r2p0_a45_h25_18309` | pass | pass | pass | 48/48 | pass | 1.200 m boundary reached |
| `v7_m4_3_repeat_r1p5_a45_h25_18310` | pass | pass | pass | 48/48 | pass | 1.200 m boundary reached |
| `v7_m4_3_repeat_r1p5_a45_h25_18311` | pass | pass | pass | 48/48 | pass | 1.200 m boundary reached |
| `v7_m4_3_repeat_r1p5_a45_h25_18312` | pass | pass | pass | 48/48 | pass | 1.198 m boundary reached |

The passing cases reached the primary global boundary after Stage A at:

```text
central spatial:  1.1997458447 m
67.5 degree:      1.1990206857 m
radius 2.0:       1.1995476577 m
repeat seed 18310: 1.1999846419 m
repeat seed 18311: 1.1997574121 m
repeat seed 18312: 1.1983970714 m
```

The non-gating `1.00 m` diagnostic was not required for the combined result.

## Failure 1: corner-fill recenter dead end

Case `v7_m4_3_r1p0_a45_h25_18309` correctly found the declared corner local,
created exactly one fill, and completed pure Gaussian escape. Its accepted
geometry was:

```text
declared local:        (0.7071067812, 0.7071067812) m
convergence point:     (0.6654436996, 0.9542455084) m
fill center:           (0.5447780037, 0.8569669278) m
convergence-to-local:  0.2506259421 m
fill-to-convergence:   0.1549946206 m
fill support radius:   0.5086747487 m
avoidance radius:      0.6086747487 m
```

The path reached:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> FAILSAFE
```

At simulation time `253.1 s`, the supervisor emitted:

```text
RECENTER->FAILSAFE: no safe recenter direction candidate
```

The terminal robot center `(0.4455714550, 0.3016966342)` remained inside the
physical room. The robot was still inside the conservative fill-avoidance
circle near the southwest corner. The recenter selector required every
candidate endpoint to remain safe for the full fixed `0.50 m` direction
lookahead. Directions that increased fill distance crossed the wall-margin
inset over that full horizon, while directions toward the room center first
crossed the fill circle. Consequently, the fixed-horizon candidate set was
empty even though a shorter physically in-bounds outward segment existed.

This is a recoverable local-planner resolution defect. It should not have
been classified as an immediate physical-room or collision failure.

## Failure 2: post-recovery direction opposed the global route

Case `v7_m4_3_r1p5_a22p5_h25_18309` passed Stage A and exact one-fill
cardinality. It retained the accepted verified-trap geometry:

```text
fill center:             (2.3230366975, 1.5706901453) m
convergence point:       (2.2294059233, 1.5744524517) m
fill-to-convergence:     0.0937063329 m
convergence-to-global:   2.3069769545 m
```

Nearest declared-local distance was `1.3086226278 m`. Under the committed
`verified_trap` contract this remains diagnostic, while the verified
below-threshold decision, global exclusion, fill association, lifecycle, and
exact topology are gating.

The Stage A recenter completed at simulation time `144.0 s`, near room
center:

```text
post-recovery anchor:  (1.7300872541, 1.7399268693) m
fill center:           (2.3230366975, 1.5706901453) m
anchor-fill distance:  0.6166280169 m
```

The current selector chose:

```text
safe direction:  (-0.9615999066, 0.2744551323)
```

That direction was hard-safe and maximized clearance and outward fill
distance, but its dot product with the evidence-only anchor-to-global
direction was approximately `-0.49`. It therefore pointed west, away from
the northeast global source. Both the supervisor translation and the robust
affine term used that same direction.

The retained liveness sequence was:

```text
144.0 s  post-recovery guidance epoch started
165.7 s  post-recovery liveness direction refreshed
192.2 s  post-recovery liveness requested recoverable recenter
204.4 s  second post-recovery guidance epoch started
229.5 s  liveness released guidance to ordinary search
```

The first epoch accumulated `2.693 m` of path for only `0.810 m` net
displacement. The second epoch accumulated `1.808 m` for `0.729 m` net and
released at only `0.692 m` outward progress. The robot never recovered the
lost global direction. Its independent Stage B budget ran from simulation
time `144.103 s` through `264.123 s` with `3,533` valid, `0` invalid,
noninterpolated odometry samples and no qualifying sample. It stopped
gracefully on the fixed timeout at:

```text
pose:                (1.2672143994, 1.1016695200) m
distance to global:  3.2767851058 m
```

This is a detector/topology/supervisor integration defect: fill-distance
clearance was treated as the primary navigation objective after known local
topology was exhausted. The accepted Gaussian already preserves the old
basin; an unconstrained “farthest from fill” direction can reverse
source-led progress. A longer timeout or looser global stop would not correct
this trajectory.

## Cross-case comparison

The fixed visible probe, central spatial case, and all three central repeats
passed (`5/5`). Their first post-recovery directions generally pointed into
the northeast half-plane. The failed `22.5 degree` case was the only retained
case whose first post-recovery direction had strongly negative alignment
with the evidence-only global route and then required both direction refresh
and recenter.

This comparison supports two separate bounded corrections:

1. recenter direction evaluation must adapt its finite lookahead near a
   physical wall/fill pinch and treat a temporarily empty candidate set as
   recoverable while the robot remains physically valid;
2. post-recovery SEARCH must give raw-plus-Gaussian GESC a source-led handoff
   before authorizing affine or supervisor translation, and any later
   guidance direction must be derived from observed source-led displacement
   rather than maximizing fill clearance alone.

Physical room faces, non-ground collision, nonfinite/stale input, graph
ownership, explicit stop, and final-zero remain hard gates. The proposed
correction does not supply global coordinates to the algorithm and does not
weaken the primary `1.20 m` stop boundary.

## One-time standard analysis and evidence health

Each of the eight retained bags was analyzed exactly once with the installed
M4.3 analyzer, using a bounded `180 s` wrapper and a run-local
`analysis/phase07` output. All eight invocations returned `0`; every analysis
reports `complete` with no analysis failure and retained eight plots and
eleven tables.

Read-only sqlite `PRAGMA quick_check` returned `ok` for every bag:

| Case | Messages |
|---|---:|
| `r1p0_a45` | 1,045,730 |
| `r1p5_a22p5` | 558,756 |
| `r1p5_a45` | 502,212 |
| `r1p5_a67p5` | 344,680 |
| `r2p0_a45` | 437,928 |
| repeat `18310` | 531,850 |
| repeat `18311` | 460,930 |
| repeat `18312` | 481,970 |

All eight completeness files passed all `48/48` checks with no failures,
including the M4.3 post-recovery producer attribution, per-producer
timestamps, final zero, final readiness false, collision evidence, and
publisher ownership.

## Retained hashes

Suite summary:

```text
40babf08ce27f22d23e5ccfbbf3913e1627e9d092ad7be602fafbe234377e367
```

Per-case hashes are ordered as:

```text
completeness.json
scenario_result.yaml
bag/bag_0.db3
analysis/phase07/analysis_completeness.json
analysis/phase07/summary_metrics.json
```

```text
v7_m4_3_r1p0_a45_h25_18309
435ad9f757ace41a2a386280d240222dea0bcb9da7e180f4d12943298f493ab7
a6e8d1b86969642a8059ed56965d0f0a9699c4bd72572a6e7b14cd5964dfaa43
97aab1e5138bd4f045dbbcfdb2109cdfd27d66a2e498c53377c8ab0975196217
c2638c6df4bb191a786196c0a16813d0716eb0d6890bfc486cceb48733446fca
58a2d9ad5cf374496fdd110dbc72d5c36635a3b307bad5b7f26bec2045e0e3e5

v7_m4_3_r1p5_a22p5_h25_18309
7c23ec5d6e1d3c8d97bf87adc9d4849ecd21ac10fad2280d2ad88aca85913091
91ac5b29dd9fb34513f7daff2b1e75232cc5073bed1abd24edf64e2c6653ec37
97f091c39225e33c711b54e123e31756ddbf208a73b535340069b6658abd3ea7
c9e67a213b67307aa75077e8e3403e2cf0bebcb0c94bd8ea7bf6e53e2597c29f
d7e69861c080f5059bd7c3487bfecda02a8fd9b5272d4461fbea3a780df56d38

v7_m4_3_r1p5_a45_h25_18309
6e14ae65896db599ebb45b69b3fe931e622a447f2fd51c314d21b4eb8cbdf4b7
e135dc050db7939f883df17c621dda8310abea653b20911e0415cd26c2e49b16
c6bef26d98dfd8d6aeccb3cbfd7b913b57cb237700669da1a741e93d6d2af24e
8f7502e2b8fdb1c8e1ca65c39d0287e9f5d935d0be3eed4f2b4efe3b36d21cbc
6dbbbbf20b79441e58158f15376c39e6354cb6f27657b2d2892eb2507cc2393c

v7_m4_3_r1p5_a67p5_h25_18309
74c3a3bf30f3db30d35d382b1586c196c6cdcc510daf5dc9b038798eccbb1237
24f4401bd54aa972d2bb231df9109180ab8d96fd03204d59d8a2f0e7cbc2371d
8cedda9e177cbacaa5d56c2ecfab72c725c4bcd5fe1b4c105dae1c89477ce61a
d350531cc43857a102a60e94621bd7a22428f13495c42957686b6ef38bf1b9ee
c7e8024342004e01987be89ab5b95200fbe8c54433302f70ca20cd539ace2284

v7_m4_3_r2p0_a45_h25_18309
5b4be05d6e16c69e6eead13ac53fe19a35266e1c1140dc02d6542f6a03907efc
c57bcaf3eb6c5f8b103ca931171759d9633103ca6b4e104d6955e9cb75375d4d
95ed5307ef95d947d1bdc8d6a4e404688de1aee335cc4a7ad3cb50656b6a3091
45c876d4f263dd3d5e1ac1183de91cfc227d7307f55abfb2f2c7bc13febbc34c
42455b087b0d6679343e37d126fbf861d4fedc4c2479901139dd9eda716c372a

v7_m4_3_repeat_r1p5_a45_h25_18310
b576b11957d8be329fdd303799e8102aa2c109fac218c83ebeaf675f7e1a085a
1ac1f9d5ace322b6a974372b21113273bf855969329ac9f7c4407b1dc1432d0f
8ca3d3bb8afbbc64801d26501ebf37e7a0b4185c36d984d42b90b1d0fedb1aa9
4d27d71df421d73646b3f60bc25bf6a8151d5cafb9b5801bb9ef186afc97a883
4e12d1152f8e472893466d4885525d0c71b24e41d2d3aec92aa3105b28a68a53

v7_m4_3_repeat_r1p5_a45_h25_18311
7326b908a6c8c01ccb392af9cd5b0f431e010537c7dd2c31546661797d093140
cfe21322a6ae374fe889e68376d8fc631ff64c4c175e0e892b23ac3ece886bdb
e81bab3685750976e8235c27668ec1b91c2e21fea49ccb021d3ccdd5a5b34224
6588bedbccef5bfc0d2ab1bd537626493c844db36b3fd7cdfcc238ced9a172a8
9e04f30a9da312325184c6b4b9899ebeec73e6c5b7d42f6f77db073d8811a6ea

v7_m4_3_repeat_r1p5_a45_h25_18312
a45140f2876094d0729ae687d50404c6060ac075b9a6f6e640358fbfe0bc81c9
1d6e60719ebfe765ca512f60c2ee67a9b57f04c081e89638d3dd9899a65807cb
0030615b3f957a8c563dad04951406d07199ad4ebab19e04891aef406e2ca263
4ca501d3c2c249e09eae2d212d7061d3cdda6c5abdf3dbd4680131844b85c5ad
08456d95598af42046d1dda1052f6d329bf7f5254010ec05870673fa0db9339c
```

After suite cleanup and analysis, `gzserver`, `gzclient`, `run_scenario`,
`record_run`, and matching launch processes were inactive. M4.3 remains
immutable and is not simulation-ready.
