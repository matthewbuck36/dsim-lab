# Phase 08.7 M3 fixed spatial-suite report

Date: 2026-07-30

## Result

The fixed five-position M3 suite is retained as **FAIL (1/5 combined
successes)**.

All five attempts were valid completed experiments: recording, final-zero,
final-readiness-false, cleanup, independent validation, sqlite integrity, and
standard analysis passed for every run. The failure is behavioral, not an
infrastructure or evidence failure.

| Case | Stage A | Fill | 1.20 m approach | 1.00 m Stage B | Collision gate | Combined |
|---|---:|---:|---:|---:|---:|---:|
| `r1.0, 45 deg` | PASS | PASS | PASS | PASS | PASS | **PASS** |
| `r1.5, 22.5 deg` | FAIL | PASS | FAIL | FAIL | PASS | **FAIL** |
| `r1.5, 45 deg` | PASS | PASS | PASS | FAIL | FAIL | **FAIL** |
| `r1.5, 67.5 deg` | FAIL | FAIL | FAIL | FAIL | PASS | **FAIL** |
| `r2.0, 45 deg` | FAIL | PASS | FAIL | FAIL | PASS | **FAIL** |

The strict prospective gate required `5/5`; it therefore fails. No case was
retried and no threshold, seed, position, or algorithm value was changed
during M3.

## Frozen input

```text
qualified commit:
  d5d29aa2225c26d2bfa62f00a398b238b67a709b
suite:
  phase08_v7_m3_spatial_suite
experiment version:
  phase08-v7-m3
scenario SHA-256:
  1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae
seed:
  18101 for every case
local/global input:
  400.0 / 1600.0 relative units
known topology:
  1 declared local, 1 declared global, maximum fills 1
primary Stage B:
  first post-Stage-A sample within 1.00 m
non-gating approach diagnostic:
  first post-Stage-A sample within 1.20 m
execution:
  one serial headless attempt per fixed position
```

The source and isolated-install scenario hashes matched before dispatch. Every
run metadata file identifies the qualified commit above. Its `dirty=true`
field and common diff hash
`407af7bd428bb3c5c6165b2d3f6191ec3483adad265384ca405592ebc5208fbb`
refer only to the committed-dispatch entry appended to the live status after
the qualified commit; no algorithm, schema, launch, world, or scenario byte
changed.

## Invocation and retained runs

The exact batch ran on ROS domain `106`:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m3_qual/install/setup.bash
export ROS_DOMAIN_ID=106
export ROS_LOG_DIR=/tmp/phase08_7_m3_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m3_mpl
export TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 3000s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m3_spatial_suite.yaml \
  --operator phase08_7_m3 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3/\
phase08_v7_m3_spatial_suite_summary.yaml
```

The suite started at `2026-07-30T02:53:29.648468Z`, completed at
`2026-07-30T03:29:15.306672Z`, resolved all five cases, and retained no
unsupported case or early cleanup stop. The outer runner returned `1` because
four completed cases failed their required behavioral predicates; the
3000-second bound did not fire.

Evidence root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3
```

Retained run IDs:

```text
20260730T025330587588Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p0_a45_h25_18101-robust_gaussian_v1-75d0c27b_c2f44d09
20260730T025955944108Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p5_a22p5_h25_18101-robust_gaussian_v1-67d7c6_df90b76f
20260730T030714860870Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p5_a45_h25_18101-robust_gaussian_v1-0bbd09a8_5b3036e9
20260730T031432414753Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p5_a67p5_h25_18101-robust_gaussian_v1-474302_d759a5e3
20260730T032154202119Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r2p0_a45_h25_18101-robust_gaussian_v1-94deae52_63d99446
```

## Case outcomes

### Radius 1.0 m, angle 45 degrees — PASS

The detector confirmed convergence at
`(0.7163555082, 0.5501848122) m`, `0.1571942852 m` from the declared local and
`4.0558705969 m` from the global. One cluster was assigned to that local; its
fill center was `(0.8287007155, 0.5575358710) m`, `0.1125854505 m` from the
convergence point.

The direct accepted recovery path completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

The first noninterpolated approach sample was `1.1974712642 m` from the
global. The monitor correctly continued, and the first primary sample was:

```text
position:           (3.5494251203, 2.5025176543) m
distance to global: 0.9987060992 m
interpolation used: false
collision observed: false
```

Stage A, exact fill cardinality, Stage B, collision, and combined
classification all passed.

### Radius 1.5 m, angle 22.5 degrees — failed during local recovery

The detector and spatial association were valid. Convergence occurred at
`(1.6687908937, 0.7453881849) m`, `0.3308144703 m` from the declared local,
and one assigned fill was created at
`(1.6506953959, 0.8766304858) m`.

The first repulsive escape stalled after `3.406905075 s`. The predeclared
single redesign path then had only `39` valid synchronized samples against the
unchanged minimum of `40`; it emitted `FILL_REJECTED` with
`insufficient valid synchronized samples` and entered `FAILSAFE`. Recenter
never started, so Stage A did not complete. Stage B and the approach
diagnostic were consequently unavailable. Exact one-fill cardinality and
collision evidence still passed.

### Radius 1.5 m, angle 45 degrees — approach passed, primary arrival failed

This case completed the accepted redesign-assisted Stage A path:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> RECENTER
-> SEARCH
```

Convergence was `0.0436407311 m` from the declared local. The retained fill
revision stayed one unique cluster, so Stage A and exact cardinality passed.

The first noninterpolated approach sample was:

```text
position:           (3.5255816609, 2.3025833648) m
distance to global: 1.1976898679 m
interpolation used: false
```

That proves the additive diagnostic works independently. It did not rescue
the required result. No sample entered `1.00 m`; the minimum anywhere in the
complete post-Stage-A in-readiness trace was `1.0981376815 m` at
`(3.5254192867, 2.4021565561) m`. The run also retained a
wall-margin-inset failsafe and non-ground collision evidence. Primary Stage B,
the collision gate, and combined success failed.

### Radius 1.5 m, angle 67.5 degrees — lifecycle completed outside the local

The mechanical direct lifecycle returned to `SEARCH`, but its convergence
point `(1.1295130938, 1.8885353661) m` was `0.7491931004 m` from the declared
local, outside the committed `0.60 m` association tolerance. The fill at
`(1.0610451724, 1.9483750255) m` was therefore an unassigned cluster rather
than proof of recovery from the declared local.

Formal Stage A and exact local-fill cardinality correctly failed. After the
mechanical return to `SEARCH`, the robot got no closer than `2.5553421488 m`
to the global and entered `FAILSAFE` with
`no safe post-recovery direction candidate`. No collision occurred.

### Radius 2.0 m, angle 45 degrees — recenter timeout

Convergence was `0.4540322219 m` from the declared local and its one fill was
validly assigned. The repulsive escape reached its stable exit, but recenter
did not complete: after about `30.10 s` it emitted `TIMEOUT` and entered
`FAILSAFE` with `recenter timeout`.

Exact one-fill cardinality and collision evidence passed, but Stage A did not
return to `SEARCH`; therefore neither global-proximity result could arm.

## Aggregate interpretation

The fixed cross produced:

```text
infrastructure / recording / cleanup: 5 / 5
formal Stage A local recovery:         2 / 5
exact associated fill cardinality:    4 / 5
non-gating 1.20 m approach:            2 / 5
primary 1.00 m Stage B:                1 / 5
collision expectation:                 4 / 5
combined success:                       1 / 5
required M3 gate:                       5 / 5
```

The result is not explained by one universal failure mode:

- one case passed end to end;
- one failed the redesign sample floor by one sample;
- one proved recovery and global-region approach but met the wall/collision
  boundary before the stricter arrival radius;
- one completed a lifecycle around an extremum outside the declared local
  association tolerance and later exhausted safe post-recovery direction
  choices;
- one escaped but timed out during recenter.

The reporter changes are therefore qualified by real evidence: they preserve
successful Stage A independently, expose the looser approach without counting
it as arrival, and keep primary Stage B and combined success strict.

## Infrastructure and independent analysis

For all five runs:

- recorder return code was `0`, with no recorder timeout;
- `recording_complete` and cleanup were true;
- independent `validate_run` returned `0`, `passed=true`, with no failures or
  warnings;
- read-only sqlite `PRAGMA quick_check` returned `ok`;
- `analyze_run` returned `0` and status `complete`;
- fresh Phase 05 validation passed;
- eight plots and eleven tables were retained;
- recording and analysis failure lists were empty.

Each standard analysis carries the same three declared fallback warnings for
`channel_index`, `sync_tolerance_sec`, and `supervisor_publish_rate_hz`.
Those are analyzer provenance warnings, not integrity failures.

A bounded `sqlite3 -readonly` CLI audit could not start because this host does
not provide the `sqlite3` executable. The approved Python standard-library
fallback opened each bag through a `file:...?mode=ro` URI and returned
`[('ok',)]` from `PRAGMA quick_check` for all five bags.

A shell bookkeeping loop around the five validator invocations exited `1`
despite printing a child return code of `0` for every run. The five retained
logs independently contain `passed: true`, empty failure and warning lists,
and their individual commands returned `0`; the wrapper anomaly is retained
as a tooling note and is not relabeled as a run-validation failure.

Logs:

```text
/tmp/phase08_7_m3_validate_*.log
/tmp/phase08_7_m3_analyze_*.log
```

## Evidence identities

```text
0fe3d63b9223aac22ffe442cd78d7732f94f118504aee5463eab09d506610fe9  suite summary

d8c8b2895dded32311738fd1f715ca2839b1969433fb28b53edc91cb0085948f  case 1 scenario_result.yaml
d26a8a053c987fb81e05dd23917552d80fd3f1eb05b3d49f510dd46396139cae  case 1 completeness.json
f9621a7c073627ee5ce9a2cf0151ce656d3cdd0d3515388b2d6ca8a56a9ffea8  case 1 bag/bag_0.db3
2bd532f94ac185c6f7fe3eb00a8bf94dbb9b0eb00f58f53e06a2d4667072674d  case 1 summary_metrics.json
df781dd6a5c78b23c9dc7cccfec387d98eb1742b0b806ab6fed5b2f47e154f76  case 1 analysis_completeness.json

f7c1efdd75eee75c05423ac62b3f44d808cc306c9310b6b5e3cc426388d0666b  case 2 scenario_result.yaml
8d2a137f8d38af601edf409d3c037848b3da6cd2524eae6e6151427340456f65  case 2 completeness.json
474a62a10a4eeae170f0f28a4b2024482800dfe60c0a58d15e5d4fbc31c02f66  case 2 bag/bag_0.db3
d85e4d7ab11ec954b6273d547d9e2a83610b9a121c4ed73efc369eab838c6803  case 2 summary_metrics.json
0f48922bb832eb54051e60e5a9268d9f20fa945cba40c9b9f639e279c41e9cf0  case 2 analysis_completeness.json

56978dd166ce3e5393d32df1c2b62fe0e45ce6c10ec2c87c744c3e87e22598df  case 3 scenario_result.yaml
5faacb372c95eb067dc8a313b60230b8837ebfcd0fb27b95aea809da6903c778  case 3 completeness.json
1f2bc70557e9ff88db631528ef6cf55c8d9bdd5240d906dfabaf0aaa5b2211f6  case 3 bag/bag_0.db3
bc88df8c9b91c06731ad3b1d8c8d740206f49c7791da498b9e89a29165300fab  case 3 summary_metrics.json
0883b53f8875ceb4ea1466cdc5b33af5355bbdbf28893b1853a12ca86f78e69a  case 3 analysis_completeness.json

a32b6e3864e4b2c6bf4f922fa3cf1369664f921b8156c6db3501d1fe37fc6955  case 4 scenario_result.yaml
fcb042aaea7d8e81bb52d52b9a4ccf8e7e793ceaa5d4187dabf41d6ffbbfdbbb  case 4 completeness.json
368321263e62c27b05cbc1fa9c336d03bea21844242825b946f6e6634b4fcef7  case 4 bag/bag_0.db3
c22e50068e423d0eb8c1672b95b9e9d6893a1a62967cd94eff2e51adfe27ef97  case 4 summary_metrics.json
dea7b1fc2c620267e39357b03c4eb98b866689025d3705fbd3c22c5cd8f0c9c8  case 4 analysis_completeness.json

1f832bb7cb5e99be723b323e12cd78c7ca8c0cc66074a80ae3f6c645e83524d2  case 5 scenario_result.yaml
0de4f0fffed9b4426ccdd4b05f135fb9a474ea56692f8d190147ffe4881f6308  case 5 completeness.json
aafda5da7c1e0e3818c2516ea788166d9d1aa96bf70d28ae11048a3ebf9546ac  case 5 bag/bag_0.db3
192eaa82204ffcbcdbc8725d06233eb17e26e9748f645dd219c973bf80df1855  case 5 summary_metrics.json
5f84b55ef698e381473dd5667643fe8d12762045bb66c2842070740b80761fd1  case 5 analysis_completeness.json
```

## Boundary

M3 is closed and immutable as a failed fixed experiment. The passing case,
the four failures, and the diagnostic-only approach results are all retained;
none may be retried, relabeled, or counted toward a future version.

M2.3 remains its own successful one-case development result. V6 and every
historical scenario, world, case key, result, and evidence root remain
unchanged.

M3 does not establish spatial robustness, repeatability, simulation readiness,
or physical readiness. It does not authorize tuning, a replacement M3 suite,
M4, the 120-run campaign, Phase 09, or physical hardware.
