# Phase 08.8 M4.1 Fixed V8.3 Primary Visible Probe

Date: 2026-07-30
Committed dispatch boundary: `77bb447`
Scenario: `phase08_v8_3_primary_visible_probe.yaml`
Case: `v8_3_primary_probe_r1p5_a45_h25_19101`
Seed: `19101`
Profile: `phase08_v8_3_counted_open_field_candidate_fill_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, candidate-informed amplitude-floor pass, strict second-candidate
raw ranking pass, Stage B pass, final-zero pass, analysis complete, and cleanup
pass.**

This was the one authorized execution of the fixed v8.3 visible probe. It ran
once from the committed isolated install with Gazebo GUI enabled and was not
retried.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_probe/
  scenario_summaries/
  20260731T065341485714Z_phase08_v8_3_primary_visible_probe.yaml
SHA-256:
  f9bc1e98ea5169e9e14c00564c189dc9f6ceaa61b1f96a578f646b73a037a511
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_probe/
  2026-07-31/
  20260731T065342440883Z_simulation_phase08_v8_3_primary_visible_probe-v8_3_primary_probe_r1p5_a45_h25_19101-robust__f966a38d
```

## Infrastructure and evidence

```text
record process return code: 0
record process timed out:   false
recording complete:         true
authoritative completeness: PASS
completeness failures:      none
completeness warnings:      none
final readiness false:      PASS
final commands zero:        PASS
cleanup:                    PASS
remaining nodes:            none
remaining processes:        none
analyze_run:                complete
analysis failures:          none
```

Evidence hashes:

```text
raw bag:
  7528317aebcaa7c9ddd2b277888b55b26e26cba4c78374764edae34f3685fce2
completeness.json:
  773b2345bd882c655b22d9c5f1d4a283f72716e9b9dacd119e5a5f5d9370c7ac
scenario_result.yaml:
  f7e0bd349863b35786d3c19404615e8b63fab1bcab47799e94dd993e80e8bd8e
analysis/phase07/analysis_completeness.json:
  28379327d17c4f60ddab4374afae3dd00c14ea5d495885d7f137b7ef2dde37e2
analysis/phase07/summary_metrics.json:
  70e536001c2d9f9914e62995d66867b9f0ec05eeadb70ffc0ff45101466c6836
```

The analyzer retained `53,516` synchronized samples. Cost, source, control,
and GESC streams matched at `1.0`; pose matched at `1.0` within `35 ms`; state
matched at `0.999851`. Phase 05 validation, topic counts, typed timestamps,
source-cost semantics, final-zero commands, final readiness false, and console
clean all pass.

## Behavioral path

The accepted complete path passed:

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

No in-readiness `RECENTER`, `FAILSAFE`, `TIMEOUT`, `FILL_REJECTED`,
`FILL_MERGED`, `FILL_SUPERSEDED`, or fill-design failure occurred. The
post-readiness explicit-stop transition is shutdown evidence and is outside
the accepted motion interval.

## Stage A and candidate-informed fill

Stage A completed at simulation time `286.917 s`, within its fixed `360.0 s`
budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (1.001126, 1.377488) m
convergence point:            (1.197768, 1.383094) m
distance to declared local:   0.350375 m
fill-to-convergence distance: 0.196723 m
fill merge/supersession:      none
```

Candidate one used the required bounded evidence pool:

```text
frozen pretrigger rotations:  6
verification rotations:       3
available rotations:          9
selected repeated rotations:  3
raw estimate:                 -2.066566928847218
MAD:                           0.10902512164576805
uncertainty:                   0.32707536493730416
lower bound:                  -2.3936422937845223
```

The versioned fill request carried that same interval into the Gaussian owner:

```text
candidate evidence lower:       -2.3936422937845223
amplitude scale:                 1.25
requested amplitude floor:       2.992052867230653
applied amplitude floor:         2.992052867230653
amplitude cap reached:           false
accepted amplitude:              2.992052867230653
sigma major/minor:               0.506211 / 0.506211 m
support radius:                  1.518634 m
escape exit radius:              1.366771 m
design escalation count:         0
```

The accepted amplitude equals the requested candidate-informed floor. The
short adaptive basin window reported only `0.029707` cost units of depth;
without the new floor its depth and curvature terms would remain below the
historical `0.10` amplitude minimum. This directly closes the scale mismatch
observed in the sealed v8.2 repeat failure.

The initial Gaussian repulsion crossed the fixed stall gate, so the already
allowed finite outward assist ran:

```text
escape outcome:           success
repulse stalled:          true
outward assist used:      true
escape duration:          29.000459 s
approximate escape orbit: 1.198016
maximum radial progress:  0.220497 m
```

## Strict ranking and Stage B

Candidate two also used the intended `6 + 3` evidence pool:

```text
raw estimate:                 -3.8372093023255816
MAD:                           0.0
uncertainty:                   0.0
lower/upper:                  -3.8372093023255816
retained candidate-one lower: -2.3936422937845223
strict separation margin:      1.4435670085410592
candidate ordinal:             2
filled candidate count:        1
known source count:            2
decision:                      GOAL_REACHED
```

The controller ranked candidate two at simulation time `415.8 s`. The first
valid later evaluator sample was:

```text
simulation time:       415.913 s
position:              (3.606833, 3.550034) m
declared global:       (3.5, 3.5) m
distance:              0.117969 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
ordering:              GOAL_REACHED before proximity sample
```

Stage B therefore completed about `128.996 s` after Stage A, within its fixed
`180.0 s` budget. The final retained distance is `0.117937 m`.

The robot entered the evaluator radius earlier while still in `SEARCH`, and
the run correctly continued. Proximity stopped simulation only after the
controller's strict ranking event. This coordinate-based stop remains
simulation-only; physical operation retains manual operator `Ctrl+C`
termination.

## Analysis metrics

```text
controller success:       true
counted ranked goal:      true
failsafe:                 false
timeout:                  false
fill count:               1
escape attempts:          1
escape successes:         1
escape failures:          0
path length:              25.320732 m
goal convergence time:    416.390855 s
readiness duration:       416.518355 s
terminal state:           GOAL_HOLD
```

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_probe/
  2026-07-31/
  20260731T065342440883Z_simulation_phase08_v8_3_primary_visible_probe-v8_3_primary_probe_r1p5_a45_h25_19101-robust__f966a38d/
  analysis/phase07/plots/
```

Available plots:

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

The trajectory plot visibly shows initial convergence around the local,
creation of one nearby fill, outward departure, transit across the open field,
and final convergence around the global. The candidate plot shows candidate
two strictly below candidate one's retained lower bound. The state plot shows
the complete assisted-recovery path and terminal `GOAL_HOLD`.

Machine-readable tables are beside the plots under:

```text
analysis/phase07/tables/
```

They include the candidate-fill amplitude evidence in
`algorithm_events.csv`, the accepted geometry in `gaussian_history.csv`, and
the full candidate comparison in `candidate_ranking.csv`.

## Gate disposition

The fixed v8.3 primary visible probe passes M4.1. This result authorizes the
sealed ten-run v8.3 primary repeat gate only after the retained evidence,
status, and report are checkpointed and committed.

This pass is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility claim,
a secondary-layout claim, a three-light claim, or a broad arbitrary-layout
claim.
