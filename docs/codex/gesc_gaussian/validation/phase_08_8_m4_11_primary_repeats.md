# Phase 08.8 M4.11 v8.10 primary repeats

Date: 2026-07-31
Committed dispatch boundary: `ccf75cd`
Scenario: `phase08_v8_10_primary_repeats.yaml`
Seeds: `19811..19820`
Profile: `robust_gaussian_v1`

## Result

**FORMAL POPULATION PASS — 10/10 seeds passed all fourteen predicates,
10/10 completed one local recovery with exactly one fill, 10/10 passed the
schema-v13 assisted command-ownership branch, 10/10 strictly ranked the
second candidate, 10/10 reached global proximity, 10/10 recordings and
cleanups passed, and all ten one-time analyses produced all nine plots.**

This was the one authorized installed suite invocation for the fixed v8.10
primary repeat population. It executed headlessly, serially, and in seed
order from `/tmp` on isolated domain `226`. It stopped on no failure, retried
no seed, changed no parameter, and was not externally monitored through ROS
or DDS.

One shell wrapper command exited before sourcing completed because
`/opt/ros/humble/setup.bash` does not support being sourced with Bash
`nounset` already enabled. The runner was never invoked, no process or file
was created, and the fresh run root and dispatch log remained absent. The
wrapper was corrected before the sole suite invocation. This is not a seed
attempt or retry.

## Frozen dispatch

```text
dispatch commit:
  ccf75cda3cd154737d02c619ad8ab60e30b827cf
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_primary_repeats.yaml
installed scenario SHA-256:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
ROS_DOMAIN_ID:
  226
Gazebo:
  headless, serial
per-run scenario timeout:
  720.0 s
per-run wall timeout:
  900.0 s
outer suite bound:
  9,600 s with bounded interrupt/kill escalation
stop on run or cleanup failure:
  true
retry:
  prohibited
```

The child wrapper captured runner return code `0`. The hosted execution
channel surfaced code `1` after printing that captured zero, but the
runner-emitted summary, ten per-run results, ten complete recordings, and
clean process audit are authoritative and internally consistent.

Dispatch log:

```text
/tmp/phase08_8_m4_11_v8_10_primary_repeats_dispatch.log
SHA-256:
  f13e57d74b3b4ee42eaa9d36930f73951fc0cc720191d06ee27a2325f6abda14
```

## Retained population

The exact runner-emitted summary is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats/
  phase08_v8_10_primary_repeats_summary.yaml
SHA-256:
  4689b2d225ebc707dd41408417a4156123b1f74afa9ee02f4e499c478cd91b91
```

It is the sole owner of the ten exact run-directory paths used for
validation and analysis.

```text
started:               2026-07-31T17:46:46.863081Z
completed:             2026-07-31T18:48:21.153945Z
resolved / executed:   10 / 10
unsupported:           0
stopped early:         false
formal:                10 pass / 0 fail
recording:             10/10 complete
authoritative checks:  10/10 pass
bag sqlite quick_check: 10/10 ok
cleanup:               10/10 pass
Git metadata:          10/10 pass
```

Every recorder metadata file proves:

```text
working_directory:    /home/mattb/dsim-lab
repository_root:      /home/mattb/dsim-lab
commit:               ccf75cda3cd154737d02c619ad8ab60e30b827cf
dirty:                false
untracked_paths:      []
```

## Per-run results

| Seed | Analysis | Stage A s | Stage B s | Global sample m | Final m | Rank margin | Exit alignment |
|---:|:---:|---:|---:|---:|---:|---:|---:|
| 19811 | complete | 294.024 | 107.984 | 0.109662 | 0.109629 | 0.990844 | 0.998635 |
| 19812 | partial | 194.024 | 106.998 | 0.124215 | 0.124183 | 0.991836 | 0.999433 |
| 19813 | complete | 223.519 | 127.704 | 0.139606 | 0.139584 | 1.681925 | 0.993043 |
| 19814 | complete | 191.912 | 100.402 | 0.128108 | 0.128098 | 0.991014 | 0.999119 |
| 19815 | complete | 220.732 | 124.678 | 0.188827 | 0.188818 | 2.475247 | 0.993983 |
| 19816 | complete | 128.432 | 114.478 | 0.106370 | 0.106346 | 0.094916 | 0.999946 |
| 19817 | complete | 121.634 | 115.668 | 0.148694 | 0.148694 | 1.147028 | 0.998430 |
| 19818 | complete | 182.732 | 107.984 | 0.137969 | 0.137949 | 0.989766 | 0.996740 |
| 19819 | complete | 232.115 | 127.194 | 0.167172 | 0.167133 | 2.257833 | 0.991816 |
| 19820 | complete | 176.606 | 121.210 | 0.117158 | 0.117126 | 0.991836 | 0.999799 |

Population ranges:

```text
Stage A completion:             121.634 to 294.024 s
Stage B duration:               100.402 to 127.704 s
global-proximity sample:          0.106370 to 0.188827 m
final retained distance:          0.106346 to 0.188818 m
strict ranking margin:            0.094916 to 2.475247
selected/actual exit alignment:   0.991816 to 0.999946
assist-entry handoff:             2.091 to 9.999 ms
assist-exit handoff:              4.004 to 11.238 ms
escape duration:                 17.801 to 24.877 s
path length:                     13.561 to 24.629 m
goal convergence time:          235.593 to 402.068 s
```

All Stage A completions were below `360.0 s`, all Stage B durations were
below `300.0 s`, and all entry/exit handoffs were below `150 ms`.

## Behavioral and ownership evidence

Every seed followed the same accepted path:

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

For all ten runs:

```text
completed local-recovery episodes:     1
created typed active fills:            exactly 1
repulse stall observed:                true
schema-v13 selected branch:            assisted
assist-entry ownership:                PASS
assist-exit ownership:                 PASS
ordinary GESC restored after exit:     true
candidate ordinal at goal:             2
filled candidate count at goal:        1
known source count:                    2
strict raw-cost separation:            PASS
noninterpolated post-ranking sample:   PASS
RECENTER / FAILSAFE / TIMEOUT:         absent
fill reject/merge/supersede/failure:   absent
final command zero:                    PASS
final readiness false:                 PASS
```

All ten runs used only onboard controller history for the assisted escape
direction. The simulator's declared local/global coordinates were used only
by the evaluator after the controller independently confirmed and strictly
ranked the second candidate.

The `0.50 m` global-proximity radius is evaluator-only. Physical operation
does not receive that coordinate or stop and remains under manual operator
`Ctrl+C`.

## One-time offline analysis

After the population and cleanup closed, all ten run directories were read
verbatim from the exact summary. Each was proven below the fresh v8.10 root
with a complete bag before its analyzer invocation. No run ID or path suffix
was manually reconstructed.

`analyze_run` ran exactly once per seed, serially. Every invocation returned
zero, reran Phase 05 validation successfully, reported
`analysis_failures=[]`, retained all critical inputs, and produced all
expected tables plus all nine plots.

```text
analysis invocations:       10 exactly
return code zero:           10/10
fresh Phase 05 validation:  10/10
analysis failures:          0
critical inputs complete:   10/10
analysis status complete:   9/10
analysis status partial:    1/10
plots:                      90/90
```

Seed `19812` is the one `partial` analysis. One algorithm-state sample gap
exceeded three nominal periods (`0.150000 s`), so only the optional generic
`state_durations` metric conservatively invalidated itself. All critical
inputs, typed state/event evidence, core scientific metrics, fresh
validation, formal predicates, and plots remain complete. The Phase 08.8
plan explicitly defines complete analysis as a successful one-time analyzer
invocation with the complete artifact bundle, all nine plots, and no
`analysis_failures`; optional generic metrics are not unstated acceptance
predicates. The analyzer was not rerun.

Analyzer logs:

```text
seed   SHA-256
19811  8de4e25cad532c9e1d89470df423ae2a1efdd57eb4bbe7a2ad88e7a1a3ab3e3e
19812  ce16da9d07701fa760bb785652e8814b24eea10e26f5df6d237240d63d6359e1
19813  49dbc8ab560d3c3b4943c942065e56325318795748a89a4d9704cfee6750319a
19814  ad0a76fa2a38a64e60ed7b2237bc444f854c930c9ec8b422ad5730fce044f852
19815  40a66d08512e4f30dff7ffc3f9b84e8cd9327fb35dcb46dc68c74e3f8a5da0d1
19816  7f6432aea11271f65479af358d02716a44546bb33c45e7270283c946abe8b595
19817  98a120788f5361c9ad361258f6d7b489ff061bd5b8e0dcf9fddbf80fbf641336
19818  29da06f01888309374047628a2a5b70defd577fc245a7457d5c37b96626af28e
19819  dc639c64927c3f2ab6de8076198973c7d2bee19a702e9ff433d34db7a0e3e440
19820  ae481ab10357fda89ede3c83254d84d633c918494e4b00f12c8876ca418c359f
```

Each run contains:

```text
analysis/phase07/plots/
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

All ten trajectory plots were visually inspected. Each shows start-to-local
capture, one nearby fill, an assisted exit, ordinary transit, and capture
around the second/global source.

## Artifact hashes

```text
seed   raw bag                                                           completeness                                                      metadata
19811  742291cee126b3e50e2cf2a79c8f7256212f5e2789ffe3fb4c0c829531f1e3a7  93991cfbe21a0f0a82d8550b9458a628254217c55695878ae6de5a405f7e5cbb  70043d51de71c590b62ae6f1d53c567c4ea6914a1f3d9c719cfe04925e0914ee
19812  68afdd30b7ad73d28e0bb3676897585a8ef3dac7d9e11e1f862fbf67e553208c  0d8d7abffd46defb2c0205c970bd56bc0c5f8e3e32214bfbe925eae6f26323e2  ea4a7d08630b0d7420786561096fd4aefa3dc612a278008dbc13db58ff03054b
19813  19e1f4202c0bd0c708588906e2ab88099f34aa4faf08dd8fccb3bac18f3bf4b1  8b82fcdbcec6d761c661c344fd4cd2f0de7137d102b08939dfb1c7dd89123677  ac9128620cae68770a17ff8be8451af83fa7ba5b7467bb4975c8c109e2411065
19814  3eb0054ad8b20efafc8f09064de73800b40dbdac3ee1e7220bad5be20993f019  72fc08628c4b3f8e0557789d9404d545b09865c96d4ffe5ecf8897fcbdd7651b  76db059260860e6fb1ae6cd16efd789ebe4124550a8c2b6a0b3f580691634aee
19815  a495d4fe6dd68e8ac7944d1c50a8d9754560bdae410c42eab18094af0383fc88  bcbab4246c375fe75d40303094864f5ef5c257541d9eb9aa7944467acc6ab966  483d16e97142d7f3dd13273fc48905d6d9749fe4119c9f8e71565e5de6af47ca
19816  6e6c6938d12c3b273cb62b747efacd3a8276fe2d3839f7dd87a3e1c6684bcb89  2a6e2ea975df7b7a6b20d86466eed0ba0656840504eaac1299cb78a7c88d04b7  2f92f8de9969a5881b2573d45beee75f2c6a0d04360518a2f0a2afa326f51c16
19817  929c7e693826ab2937e5a0a92e54a71f8041afd57ac854c6bbda69820b395a5f  d3017fa0a27c7c320c2769cc2e9efafa1956bef744ca14c4e5f45227e73a2b58  1987b09d7f2ee90a8ccd918fe414910168c21dc74f9f6cc9e3d6c3de5a607fea
19818  682362719aa6fe39e5aa4521f56d26deba1e718d842c879a15ce1a1aa5967367  abb426b69fe766bfd9efbeecf768a4c1c70568636b0d068fc4272f5af144a304  40e86188df18099389557550a2934d018c1994c9ef0a3dfb62be6960f85a6c2b
19819  2ee4160deaccb394c56e52a2534b1b7516e5d23845a8abd4ee32fe5791618b2c  40011a74ba683b0ed9c5ba4beec666cf4457efa886f3c8103a559a48c3893bba  46a508a5c1a6009ebf434e0691501678b82ebd1362b160763c3038709dc1a275
19820  dda002abe388d135ca1e71fb3d0f93ef456fdc522cdf0919dede37d28e1c8a33  85282b011aee62ed60d14637857d0ddf3d3f73e5cf1b08373ed4c32602ca6d56  06c1d603266b8d8530806d57c85e85e75d9aa9dae3bb273a4f8c335c739b7a9c
```

```text
seed   scenario_result                                                   analysis_completeness                                             summary_metrics
19811  04ddf4004b82d10766499ceb65aca7673f5d0d832f90b4ee929d8b537fba4dea  d500d7eb41b9172a6815485a3788938b3b24392a840e73b677cd85bf62d8f763  3e8905ea5fd1bbc4100e7149d581da54dc64559e2541d08c9b09ff31c6219332
19812  134668a57dcbf051b6b314c88b220c8e150fba6bedc266665576dac7335d2717  4d5d8364613582fde41276e2df14f146f0a6b00cca74d879c8e72398e085931c  ca2b42add5f1b2ede4580cc3d515811c8d5b832c53de17fda6d49c9b8367d429
19813  3df7eeb063f8683775ed4714db86d3b7079e079deae7e0dcf04abb2730dca589  d2b194d1e46e3a4e5940e169dede20ab23508fcbca6ee09fcf31e9a38eab89d9  36d437b7c9f963f7bea6cacc7ed48e6068b5ab0a77bd567fd754ebcac6a3f66d
19814  a01f7242ddbdcf8194d48c365502fca7b87035f514c564780a622bbdfe1a050a  9f9ec90800a31e3151a651049d00a104290a9d41e0c097f699cb873c78d61944  af890c187d478a4d8a208264f06ba8ac4516d547d2634a66308995c60ab24ffd
19815  59ab6672de0f4df9c9908757e42becea10a1361dffeb46e1752cdc54efb35827  53cbe353da4705a37a59636eea1aee03b562048cb6a8f05f7b22e2c893d4f883  5daef5d799c230e87697ceded07fe1ec014847b43b56f3751ded53feaf204cfb
19816  17cd1a3634b1e3a1a58e73c2c4db8358a9d56ea4fef99f9cba18e4d10bcf58ee  d91603496551313b540b5cc42edae6124d7018a1c22780347217019f70254f06  f9924eb0adcdbf4b46d091ec5056d2cd418ff583c1130e9d21484e045ed52fa7
19817  0bb3eb662efe0520195e2aed6ae98ae74b7040de602901545db8d7efbe4e2c24  d53464eeb741bccb8f1bc394a7a9c1b03070095a10726493421cdec18827e1fb  dee209aff2c7eb393fbe70e29b0f5d7cabe29b9464d7e1fb2aa678a17e43767d
19818  a5d1cfbc85f6b96d283d87198ab1ecb53b7e10dad4c72ef9475304958bc99e87  e4a495c0086dff2603269bfee5236c486528df8f51d6c49a073fb95e57653080  d8937a73a25d4f55bd6880f14e6da286c21d3a87f5f70aef6dafd57e63eeb58e
19819  36c00b2cf7dcfcef935f42eaa29796fd5f40e16b6d68d3c5aefd0b05f98ae9fe  b53ac3b9cbbe683db1c1c3fcf049a377df60f281993fdc32431beeff36d7b510  1498f21f8b0d70b16a6107c0f7351eab7d2bddbbd7302edf1e9cab3d90b96f06
19820  e269a3e3e87cd8343aab5fa66e22ecce7f4ff68756401653a88ced517d255422  303a29a81ebe06a47f3c7f7b69fa146df43e04752975c89788e131e21fe6f8e9  7fc1ea34f739e5777381f5f43ae221acd0e8995fe7568115ea26ea8fda5191a6
```

Trajectory plot SHA-256 values:

```text
19811  0a0c3a487d4adb85089554970400cf92a870746faa0748f4119ca71af81b50f7
19812  7f5bc8d35f78b326a1b377d1f86cf2c01d438d54f55403ab7a408e6b2922e83d
19813  f4449df853da8d6cc59aa7f118071d0aec549ffc1e586b6e24b50cd855277964
19814  b889bd1d0904512c824c1384b449cd7aedd4de7696ff02e44fa383666daecffd
19815  b629b36c5d1dafcd7bec5970084d21fa5d24ec5c98e20111feae2c05cda6f87d
19816  cca76ad69a9e65813d46514ce32db3184975c5b791180c60ba442d55a326ed3d
19817  89215b4d5403613732298f2eed229e152a39314086ddb132002bf6470b44fc30
19818  998a30653c84ed8e979d72cc62e0d962454ffc493d112f8c49b2b08bb1b9285d
19819  90572da77e27f061b8b775022ccf785907bb3811187b75deaa6526e172916e3e
19820  15ab1030c0e0e3a03c85189d1d56dc1bef0d394c7ed013644048af8400a78be2
```

## Gate disposition

The v8.10 primary repeat population passes M4.11 at `10/10`. The result and
analysis authorize a separately checkpointed and committed visible
secondary-layout probe for seed `19851`.

This result is evidence for repeatability in one fixed, obstacle-free,
two-source, `400/1600` simulator-relative primary layout. It does not claim
arbitrary positions or intensities, three sources, wall or obstacle
behavior, physical motion, or broad field robustness. Historical scenarios,
results, and failures remain unchanged.
