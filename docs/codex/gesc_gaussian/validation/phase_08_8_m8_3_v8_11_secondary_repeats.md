# Phase 08.8 M8.3 v8.11 Secondary Repeats

Date: 2026-07-31
Committed dispatch boundary: `13ccb8b`
Scenario: `phase08_v8_11_secondary_repeats.yaml`
Case: `v8_11_secondary_repeats_r1p5_a67p5_h25`
Seeds: `19911..19915`
Profile: `robust_gaussian_v1`

## Disposition

**PASS — 5/5 FIXED NO-RETRY RUNS, 70/70 FORMAL PREDICATES, FIVE
TOPOLOGY-BOUND ONE-FILL RECOVERIES, FIVE STRICT SECOND-CANDIDATE RANKINGS,
FIVE GRACEFUL GLOBAL-PROXIMITY STOPS, COMPLETE RECORDING/CLEANUP, AND 45/45
PLOTS.**

The one authorized installed suite ran all five seeds serially and stopped
normally. No seed was skipped, retried, replaced, or tuned. Every run treated
the first confirmed extremum as an unknown candidate, created exactly one
typed fill, completed an accepted recovery path, restored ordinary GESC
search, strictly ranked candidate two from raw rotational cost, entered
`GOAL_HOLD`, and stopped on the first valid evaluator-only post-recovery
global-proximity sample.

Four seeds completed direct repulse. Seed `19912` exercised the separately
gated supervisor-owned assist branch before returning authority to ordinary
GESC. This population therefore qualifies both accepted escape paths in the
fixed secondary layout.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  13ccb8b4c890c93d4363f1f2e7609a3b5f473168
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_11_secondary_repeats.yaml
installed/source SHA-256:
  01466b3c350b4e37693eaffb0c40fe15591d28a8d09ee14f4b60aa00f200ce1d
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  221 / 1
presentation / execution:
  headless Gazebo / serial
attempts / retries per seed:
  1 / 0
```

Frozen layout:

```text
start:   (0.0, 0.0) m
local:   (0.5740251485476348, 1.38581929876693) m, input 400
global:  (3.5, 3.5) m, input 1600
ratio:   1:4
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_repeats/scenario_summaries/
  20260731T211244723799Z_phase08_v8_11_secondary_repeats.yaml
SHA-256:
  a05e6d4de1863324af1cd09178b7a0b7165e9f2776e76bb626481018b0b16f5c
started / completed:
  2026-07-31T21:12:44.723799Z / 2026-07-31T21:37:40.960812Z
resolved / unsupported:
  5 / 0
```

Exact summary-owned runs:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/
  2026-07-31/
  20260731T211245658756Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_b9e46a70
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/
  2026-07-31/
  20260731T211723714744Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_15c56eee
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/
  2026-07-31/
  20260731T212352071223Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_96457b4e
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/
  2026-07-31/
  20260731T212828990981Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d39b9a91
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/
  2026-07-31/
  20260731T213307752047Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d014dc3c
```

Every recorder captured the clean committed checkout at `13ccb8b`, with
`dirty: false` and no untracked paths. The retained dispatch log is:

```text
/tmp/phase08_8_v8_11_secondary_repeats_dispatch.log
SHA-256:
  1492855ed5ffca22ce88dfa27a19b7d7b08762aecfc3fdada4d288ab580ec240
```

## Per-seed behavioral evidence

| Seed | Stage A sim s | Escape branch | Convergence-to-local m | Fill-to-convergence m | Strict raw-cost margin | Stage B sim s | Final global m |
|---:|---:|---|---:|---:|---:|---:|---:|
| `19911` | `115.722` | `direct_repulse` | `0.763386` | `0.009788` | `3.607655` | `237.306` | `0.165580` |
| `19912` | `201.122` | `assisted` | `0.073659` | `0.153164` | `0.991836` | `327.534` | `0.128708` |
| `19913` | `116.035` | `direct_repulse` | `0.760524` | `0.013867` | `3.595674` | `235.613` | `0.130621` |
| `19914` | `115.834` | `direct_repulse` | `0.763032` | `0.018295` | `3.597580` | `236.704` | `0.124299` |
| `19915` | `115.718` | `direct_repulse` | `0.772215` | `0.018902` | `3.605789` | `232.610` | `0.135716` |

Candidate/fill geometry:

| Seed | Confirmed candidate m | Fill center m | Created / typed / active |
|---:|---|---|---|
| `19911` | `(1.212976, 1.803550)` | `(1.204969, 1.797921)` | `1 / 1 / 1` |
| `19912` | `(0.622905, 1.330715)` | `(0.774464, 1.308601)` | `1 / 1 / 1` |
| `19913` | `(1.209367, 1.803835)` | `(1.196639, 1.798331)` | `1 / 1 / 1` |
| `19914` | `(1.210126, 1.807238)` | `(1.192664, 1.812694)` | `1 / 1 / 1` |
| `19915` | `(1.228848, 1.795114)` | `(1.219289, 1.778807)` | `1 / 1 / 1` |

Seeds `19911`, `19913`, `19914`, and `19915` confirmed the shifted
aggregate-field basin about `0.76..0.77 m` from the individual local lamp.
The individual-lamp distance was correctly diagnostic rather than gating.
Seed `19912` explored longer, confirmed close to the declared local lamp,
and required supervisor-owned escape assistance. Its smaller strict ranking
margin reflects a substantially lower first-candidate raw cost, but candidate
two remained strictly better.

Direct path, observed four times:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
-> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

Assisted path, observed for seed `19912`:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
-> ESCAPE_ASSIST -> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

All direct and assisted ownership predicates passed. Escape durations were
`21.765091`, `19.530430`, `21.644877`, `21.667825`, and `21.460704 s` in seed
order. Fill-to-exit alignment ranged from `0.952097` through `0.994069`.
Every run returned to ordinary GESC before candidate-two ranking.

The shared topology qualification hash was:

```text
eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71
```

Each run passed all `14/14` predicates, including exact one-fill cardinality,
strict counted-candidate ranking, and the first valid noninterpolated
post-recovery sample inside the `0.50 m` evaluator radius. The Stage B sample
distances were `0.165590`, `0.128741`, `0.130629`, `0.124310`, and
`0.135716 m` in seed order.

## Recording, shutdown, and analysis

Population result:

```text
formal classification:          5/5 PASS
recording complete:             5/5 PASS
authoritative completeness:     5/5 PASS
fresh Phase 05 validation:      5/5 PASS
final command zero:             5/5 PASS
final readiness false:          5/5 PASS
cleanup:                        5/5 PASS
SQLite PRAGMA quick_check:      5/5 ok
analysis status / failures:     5/5 complete / []
plots:                          45/45
```

Each summary-owned run was analyzed exactly once. Its analysis directory is
the exact run path above followed by `analysis/phase07`.

The first shell wrapper used `set -euo pipefail` and exited `1` while sourcing
`/opt/ros/humble/setup.bash` because ROS referenced the unset
`AMENT_TRACE_SETUP_FILES` variable. It stopped before invoking
`analyze_run`; zero analysis directories existed afterward. The corrected
bounded wrapper retained `set -eo pipefail`, then invoked each analyzer once.
This is a recorded shell-orchestration correction, not a retry of any
analysis or simulation.

Raw bag and analysis log hashes are:

| Seed | Raw bag SHA-256 | Analysis log and SHA-256 |
|---:|---|---|
| `19911` | `546994fbcaac62875ca55e5ab2929a37b61a9c8f4a64d0f5e893850ed70f2d79` | `/tmp/20260731T211245658756Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_b9e46a70_analysis.log` — `ad6a0745b44c483bdc41c621bcab5d4e2f6ae0ca973d1f2c36ea810da40edeb4` |
| `19912` | `df0a1ca7396fd07d5fb4b796c282aa45ac6899e924d577f67a4dac41a1eaa50b` | `/tmp/20260731T211723714744Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_15c56eee_analysis.log` — `00f82726d0d4192e3963094609effdabaab345385775b2442f085e5e18119639` |
| `19913` | `a671bf02d7be930c0d2dc108b8bafd81fcfdaeef0c04beb2067aceb1bad549d1` | `/tmp/20260731T212352071223Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_96457b4e_analysis.log` — `22bc83ae58777c750e9a5a73477e2207a9c09a80780f79d6c1fdecfe38fb713d` |
| `19914` | `2c51fa18aad4d8a9944b5ae5fd343f9c97673c59005312f530ff01c38defa780` | `/tmp/20260731T212828990981Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d39b9a91_analysis.log` — `2e3737694528880a4b345e9985eff84bb5b808dd5a300f5ecb629f75ea269bc7` |
| `19915` | `847645a380e1a2fc704959492a0aa199c576df069552b886c90dd531a60a142c` | `/tmp/20260731T213307752047Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d014dc3c_analysis.log` — `a1b5c7162cdae5a142ef77f3e27268fbec77196c251b9a9d5c0882b8ef504f2d` |

The analyzer emitted the same three non-gating fallback warnings for every
run: assumed `channel_index`, `sync_tolerance_sec`, and
`supervisor_publish_rate_hz`. Critical inputs, applicability integrity,
stored validation, fresh validation, recording failures, and analysis
failures all passed or were empty.

## Plot manifest

Each path below is relative to that seed's exact run directory followed by
`analysis/phase07/plots/`.

| Seed | Plot | SHA-256 |
|---:|---|---|
| `19911` | `candidate_ranking.png` | `8a29462cbc97f25e432a47cedcb22264a17040d570c313c3fd4d31da7d2bf3f1` |
| `19911` | `command_saturation.png` | `4a725e8cd58cf4cb74dc79620f7a30055167486158d8e3561bb569dcecdbd00c` |
| `19911` | `components.png` | `85c2c3a4777b29ae98a71dbd05a3e218b67a5d42fa1bc2d78a8670e9723d3ba8` |
| `19911` | `cost.png` | `426b60da9927ff14c1df71b5b1e56cc8f0f8987f872815d978513e4764c702ce` |
| `19911` | `gaussian_history.png` | `53323f2f63d6385eb239f85800ba0be92fa1337bf0d1658e0158db05899fb278` |
| `19911` | `radial_escape.png` | `6f85ae77d221e5e6a5fc57162445b6f891a481c13802618559ad10950491edff` |
| `19911` | `state_events.png` | `4510d31e1d592a173bf8eb2eb09705eb50b4ade72b60e9b2c0a46d4a45bcc544` |
| `19911` | `trajectory_sources_fills.png` | `c95e4a68478bd2dd38da2f96473ccfe23466c261923088b812aed8778b41b6e7` |
| `19911` | `weights.png` | `1d30bfae5efd67f7ce92582ff24439374bddc009dfd6251138fbaf02edd07926` |
| `19912` | `candidate_ranking.png` | `b5430b3e724b98f5e4af29b15591c647a04f6fb0dfd919afce3f8682d4a412f9` |
| `19912` | `command_saturation.png` | `ced26551590f3454c6e06b5bf645c6fd850c4865bb311a2f1ae69b2f55a07914` |
| `19912` | `components.png` | `2b2ce13c8e39016bb8d9461d024c35cb48ea09da48c39b5e64c5c19b921285ec` |
| `19912` | `cost.png` | `c8a4e1ec96b9821f0153cb1e095e33ee53f427a9c07d250cfbd3bfd6d3de36cb` |
| `19912` | `gaussian_history.png` | `723727f05fdc02f54fac4b3bfdfb92f17f5e02f5257d5daf2a4a3f227b61223e` |
| `19912` | `radial_escape.png` | `74c279867c03bd61a6245676076ebbd46cc960a695c579e85a72df0104781c9a` |
| `19912` | `state_events.png` | `30a19707dac0c8f41ef54440f0602971f02aa53a4dc953f0aaafb2556a360a66` |
| `19912` | `trajectory_sources_fills.png` | `e9e7998bb618bbba4b1c91378d950ad15bd828ce2dd6b079eaeddc4fb06940be` |
| `19912` | `weights.png` | `d81b5513179878f695696e61d9aa9107d56379c177caa71c29b439f7ea135730` |
| `19913` | `candidate_ranking.png` | `cdf33ab0587d988f200101d603b9396ac1d1f951c8aca95adcbfa72bc92f5dae` |
| `19913` | `command_saturation.png` | `807b330054f3045a3e907870e6fc91a8812d3f10a1490076e64d013b57dce016` |
| `19913` | `components.png` | `b297b6405d038d2f382586741ab95fcc03d44df9dd0e875df2241b1bfd4d2c37` |
| `19913` | `cost.png` | `7dbb9590d3d4978f5d36e699e20e36cea5a6ca3c2aa58fefb243c2feb716d415` |
| `19913` | `gaussian_history.png` | `32d995a04f8a2713f0b66aa53eb42b56ba78b8ea26bcd311234955a307a71f33` |
| `19913` | `radial_escape.png` | `1182cd1156cd7634f2cbfbdd5ba9dda00ce76661769b7f8acebfb15494a8f86e` |
| `19913` | `state_events.png` | `842aaa7077aae5bef32401b60ff15a32e3496f4f0765178518ffb906701d054c` |
| `19913` | `trajectory_sources_fills.png` | `9e6e027b04957e418dec806e95f5b8ce22e7c5243e1ad3ab9f16658d1448e645` |
| `19913` | `weights.png` | `9d977a0a2232a4245ca5ca92f3ab28a1bf52e87decfca461cb72891b274fe693` |
| `19914` | `candidate_ranking.png` | `cb7bb6a3e13048695fcc6378cc46697fd9052fff09c737273dbb4ee2fece04c8` |
| `19914` | `command_saturation.png` | `55af106d6b519f5336862c8fbe75eab30f5e0b3513ef3fea511f9a919c6ca9bc` |
| `19914` | `components.png` | `4a70af9402da4ec44bd1ae2a2b851484982537d45ac551daf6fd32221cbad6c6` |
| `19914` | `cost.png` | `ca9e68e5a0dac8bbab4d736b5da2babb113b159f154c08972ec4e4069e2cd1be` |
| `19914` | `gaussian_history.png` | `f5dd18a4c8ce009caac66499250d9cacbfc9623126e6b3a0fdfbbd1dbb6b4173` |
| `19914` | `radial_escape.png` | `8508bceb03b79c0a1d6f0cfddf378b085588b351a2433554181376941126b727` |
| `19914` | `state_events.png` | `83e9e581df6a0aa4dfec95bda3d89cbc7a484242ec90cb062ea2255b56c15e7f` |
| `19914` | `trajectory_sources_fills.png` | `5c3e6212cb7d6fe853a40364a33d4a7e9c6b3a461f09ae98c0229663740f67e4` |
| `19914` | `weights.png` | `7157a52300c7a4ed5d7a48895b96027715cbf8315128e59d8582fec72fee3013` |
| `19915` | `candidate_ranking.png` | `4892a21a5a2478dc232d8dcd601bd01ec133280ff69a00476f54a85e69096cf1` |
| `19915` | `command_saturation.png` | `6d653eb6ae4db379140e06d97fc15eb28fdd5339bfcf33fc549805ecc450ea26` |
| `19915` | `components.png` | `ae79652369a7f9c0df75175ac3c87f8bfba703a174de803e1bc98f12c152681d` |
| `19915` | `cost.png` | `bf10d3e7c64d966d088a9d83537b16c3f7a786556982be2d7bcbc700d2401cf1` |
| `19915` | `gaussian_history.png` | `1f009eee137ce110ae7e03d593cc5905e1c11e1b2691a8be64b63fd3ebcbbb89` |
| `19915` | `radial_escape.png` | `342f0c2bafb12eb398c186552115e6eb0cf7386f7dabc8805ddb8f6defe3fd2d` |
| `19915` | `state_events.png` | `24a668e0deee7c9d281ffaa47fb037735bd3c35d2904a50fdef2ddc6cf94fd36` |
| `19915` | `trajectory_sources_fills.png` | `af6f5e8553ff3faab406bc91d7a972c4f5f1028e75f3354cc19984c55f44a72f` |
| `19915` | `weights.png` | `58db131c3430187f4c6534631e39ef2b1a327605f643a18afde796420371d69e` |

Visual inspection of all five trajectory plots and representative ranking
plots confirms one fill, outward escape, ordinary transit, global capture,
and strict candidate ordering. Seed `19912` visibly includes its longer
local orbit and assisted exit; the other four show the shifted-basin direct
route.

## Runtime boundary and claim

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. All five runs, bags, results, analyses, and plots are
retained. This result qualifies repeatability only for the exact admitted
secondary two-source, obstacle-free, zero-disturbance layout. It does not
claim unknown source count, arbitrary light fields, walls, obstacles, three
lights, or physical coordinate stopping. Physical arrival remains manual
operator `Ctrl+C`.

The population gate now authorizes a separately checkpointed and committed
dispatch boundary for the fixed four-case v8.11 varied-layout/intensity
matrix. The matrix has not been dispatched by this result.
