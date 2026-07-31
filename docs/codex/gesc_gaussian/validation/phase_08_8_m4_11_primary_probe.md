# Phase 08.8 M4.11 v8.10 primary visible probe

Date: 2026-07-31
Implementation commit: `77dd443`
Committed dispatch boundary: `f96edfd`
Scenario: `phase08_v8_10_primary_visible_probe.yaml`
Case: `v8_10_primary_probe_r1p5_a45_h25_19801`
Seed: `19801`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — recorder-CWD correction pass, complete infrastructure,
Stage A pass, exact one-fill cardinality, supervisor-owned assisted escape
pass, schema-v13 dual-topology command ownership pass, strict second-candidate
raw ranking pass, Stage B pass, final-zero pass, complete one-time analysis,
all nine plots, and uncontaminated cleanup pass.**

This was the one authorized execution of the fixed v8.10 visible primary
probe. It ran once from `/tmp` against the committed isolated install with
Gazebo GUI enabled. It was not retried, modified, or externally monitored
through ROS or DDS.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/
  phase08_v8_10_primary_visible_probe_summary.yaml
SHA-256:
  f37e9cab4ab790e647897118c576635ad6011bba211d882da84f2ba7c78b6a73
```

The summary contains exactly one selected and resolved case, seed `19801`,
no unsupported case, and this exact run directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/2026-07-31/
  20260731T173056885644Z_simulation_phase08_v8_10_primary_visible_probe-
  v8_10_primary_probe_r1p5_a45_h25_19801-robus_d984451c
```

The analyzer target was read verbatim from that summary. No run ID or
directory suffix was manually reconstructed.

## Recorder-CWD correction

The runner was deliberately invoked from `/tmp`. The finalized recorder
metadata proves that the child used the resolved checkout working directory
and captured the clean committed dispatch tree:

```text
working_directory: /home/mattb/dsim-lab
git.repository_root: /home/mattb/dsim-lab
git.commit: f96edfd302fbd6fed7f48263ace766d0b425a20a
git.branch: feature/gesc-gaussian-robustness-v1
git.dirty: false
git.untracked_paths: []
```

This directly closes the v8.9 failure mode in which `record_run` inherited
`/tmp` and failed its Git lookup before Gazebo. No recorder, metadata, or
scenario logic was weakened.

## Infrastructure and formal evidence

```text
scenario start:                    2026-07-31T17:30:55.946255Z
scenario completion:               2026-07-31T17:36:48.717776Z
scenario runner return code:       0
record process return code:        0
record process timed out:          false
graceful global-proximity stop:    true
recording complete:                true
authoritative completeness:        PASS
completeness failures:             none
final readiness false:             PASS
final commands zero:               PASS
cleanup:                           PASS
remaining new nodes:               none
remaining run-session processes:   none
formal scenario classification:    PASS
required predicates:               14/14
analyze_run invocations:           exactly 1
analyze_run return code:           0
analysis status:                   complete
analysis failures:                 none
plots produced:                    9/9
bag sqlite quick_check:            PASS
```

The cleanup baseline contained only the runner-observed ROS daemon for
isolated domain `225`. No new node or run-session process remained.

Evidence hashes:

```text
bag/bag_0.db3:
  b2345ebbe3b94f4aa6fdf6affe6a3bbb34d43f5b765b32ded8b09bcca1306e9d
bag/metadata.yaml:
  afe887929b65d93ef6676d96534c7e2437f835075d0ab04dbe32cb88771fa84a
metadata.yaml:
  df696317d94a1cfb93a412f14d754c8a43f977f259d11a153f5e1015e54a8563
completeness.json:
  b682ef11f86afeea191a20af919c098b9afe288a0e41a1861050f91caa460c45
scenario_result.yaml:
  7e0db1ef246f2647765f2e1a87cb84503834765ac33b5099f31285ca533c3865
resolved_scenario.yaml:
  9c4a56e7793780124c2384b00a18a7706d0be256fc372a3aaf39783b91cae05a
analysis/phase07/analysis_completeness.json:
  95a3a7cc5b512e2ebcc042598758789ed85b7c81836dbed290c90deb772b6d11
analysis/phase07/summary_metrics.json:
  c66853cc2a2daaa0ebc6d5162fd5731811c4677142f395f741c45c4d418980ee
dispatch log:
  /tmp/phase08_8_m4_11_v8_10_primary_visible_dispatch.log
  637ca8a18a618536f10aae08aa7ee0b594599730100a7844b8d2efefeb86a632
analysis log:
  /tmp/phase08_8_m4_11_v8_10_primary_visible_analysis.log
  4d3c1fa9b383d5f273b81e1a2c5b7c804a5ddf8f9e504cf8029de1a65d89e08d
```

## Behavioral path

The exact accepted assisted path passed:

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

Required event counts were:

```text
CONVERGENCE_CANDIDATE x2
CONVERGENCE_CONFIRMED x2
FILL_CREATED          x1
ESCAPE_STARTED        x1
ESCAPE_STALLED        x1
GOAL_REACHED          x1
```

No accepted-motion `RECENTER`, `FAILSAFE`, `TIMEOUT`, fill rejection,
fill merge, fill supersession, or fill-design failure occurred.

## Stage A and candidate-informed fill

Stage A completed at simulation time `168.713 s`, within its fixed `360.0 s`
budget.

```text
completed recovery episodes:       1
created clusters:                  [1]
typed clusters:                    [1]
active clusters:                   [1]
fill count:                        exactly 1
fill center:                       (0.988985, 1.347271) m
convergence point:                 (1.140476, 1.392573) m
distance to declared local:        0.341375 m
fill-to-convergence distance:      0.158120 m
fill merge/supersession:           none
```

Candidate one used the required bounded `6 + 3` rotation evidence:

```text
raw estimate:       -2.422265897599617
MAD:                 0.17209430671240034
uncertainty:         0.516282920137201
lower bound:        -2.938548817736818
upper bound:        -1.9059829774624162
candidate ordinal:   1
```

## Assisted escape and dual-topology ownership

The controller first attempted Gaussian/affine repulsion, detected the
declared stall, and entered the supervisor-owned assist branch. The assist
selected one revision-one onboard-history direction and produced a
well-aligned escape:

```text
selected direction:             (0.380276873, 0.924872694)
fill center:                    (0.988985, 1.347271) m
measured exit:                  (1.394502, 2.761538) m
fill-to-exit distance:           1.471256 m
selected/actual alignment:       0.993861949
escape duration:                24.281332 s
repulse stalled:                true
assisted:                       true
failsafe:                       false
timeout:                        false
```

The schema-v13 conditional ownership predicate passed both relevant
handoffs:

```text
assist state samples:                      422
assist control samples:                  2,731
fresh matching supervisor commands:      2,731
nonzero GESC proposals suppressed:       2,731
positive supervisor linear samples:      2,057
assist-entry transition samples:             0
assist-entry steady owned samples:       2,731
assist-entry delay:                       0.003215288 s
assist-entry deadline:                    0.15 s
assist-entry evidence mode:               bounded_causal_schema_v12
post-exit transition samples:                1
post-exit ordinary control samples:      15,024
post-exit ordinary GESC restored:          true
post-exit delay:                          0.011156662 s
post-exit deadline:                       0.15 s
post-exit evidence mode:                  bounded_causal_schema_v11
schema-v13 branch:                        assisted
```

There was no persistent supervisor, affine, safe-direction, or
escape-geometry authority after recovery.

## Strict ranking and Stage B

Candidate two used the same fixed raw-cost evidence policy:

```text
raw estimate/lower/upper:       -3.8372093023255816
retained candidate-one lower:   -2.938548817736818
strict separation margin:        0.8986604845887634
candidate ordinal:               2
filled candidate count:          1
known source count:              2
decision:                        GOAL_REACHED
```

The first valid post-ranking evaluator sample was:

```text
simulation time:       293.935 s
position:              (3.598174, 3.536081) m
declared global:       (3.5, 3.5) m
distance:              0.104594 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
```

Stage B lasted approximately `125.222 s`, within its simulation-only
`300.0 s` budget. The final retained distance is `0.104573 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted strict raw-cost
`GOAL_REACHED`. Physical execution remains manually stopped by the operator
with `Ctrl+C`; the simulation proximity stop is not in the physical path.

## Offline analysis and plots

`analyze_run` executed exactly once after the sealed run closed, using the
summary-owned run directory. It returned zero, reran the authoritative
validator successfully, produced every expected table and plot, and
reported:

```text
analysis_status:       complete
analysis_failures:     []
controller_success:    true
counted ranked goal:   true
fill count:            1
escape attempts:       1
escape successes:      1
escape failures:       0
escape time:           24.281332 s
path length:           17.028679 m
goal convergence time: 293.693059 s
terminal state:        GOAL_HOLD
```

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/2026-07-31/
  20260731T173056885644Z_simulation_phase08_v8_10_primary_visible_probe-
  v8_10_primary_probe_r1p5_a45_h25_19801-robus_d984451c/
  analysis/phase07/plots/
```

Available plots and SHA-256 hashes:

```text
candidate_ranking.png
  b264b7acbc3059ac0f46b29c4399102b5eaca9ee7590b4917e4acde80684f133
command_saturation.png
  392a46fc054e2cf0d1f0d42da9cf0c20ec52907d5445ee57364389b625515576
components.png
  86b748555814ffadfe22de07f1cf7f22c374b470d27fa00b01bae54706ef2498
cost.png
  d2cfc08b03538c2e19a026fdd4c7a99de6a4d31810673911b1f99e1ca75215d0
gaussian_history.png
  9ca9e6c49a32c81b238e0bbb0c2c05fabd33fde2a40b79b757fa8eb2d3d2aeec
radial_escape.png
  0e78245274b7d62e45a7b4acad04f82d5aed0c494307561848cea6c61630031c
state_events.png
  0aa39016cd9faa3619657f5b362a272648a42b23179195ecd1bfa6f051bac9ba
trajectory_sources_fills.png
  b86526c85fc79a8275b08116ac2d346b2b06ef2430e9b038f695672c5083bd25
weights.png
  49b93e18786fc848238a0f6310ca8a87b6ec2672aef8d35d864ca9462b5d59e6
```

The trajectory was visually inspected. It shows start-to-local capture, one
nearby typed fill, assisted exit, ordinary GESC transit, and capture at the
declared global. The other plots agree with the formal evidence.

## Level B evidence erratum

The committed dispatch-boundary text asked the recorder metadata to identify
`77dd443` as the "committed dispatch HEAD." That hash is the qualified
implementation commit; the subsequently committed dispatch boundary is
`f96edfd`. Runtime metadata correctly captured the actual clean dispatch
HEAD `f96edfd302fbd6fed7f48263ace766d0b425a20a`.

This is a bounded documentation correction. It changes no dispatched input,
runtime state, code, metadata, controller behavior, acceptance predicate, or
retained artifact and does not invalidate the result.

## Gate disposition

The v8.10 primary visible probe passes M4.11. It authorizes a separately
checkpointed and committed ten-run primary-repeat dispatch boundary for
seeds `19811..19820`.

This is evidence for one fixed, obstacle-free, two-source, `400/1600`
simulator-relative primary layout. It is not evidence for arbitrary source
positions or intensities, three sources, wall or obstacle behavior, physical
motion, or broad field robustness. Historical scenarios and results remain
unchanged.
