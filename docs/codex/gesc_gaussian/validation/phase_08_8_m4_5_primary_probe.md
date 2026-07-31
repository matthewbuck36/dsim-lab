# Phase 08.8 M4.5 Fixed V8.5 Primary Visible Probe

Date: 2026-07-31
Committed dispatch boundary: `5113e5b`
Scenario: `phase08_v8_5_primary_visible_probe.yaml`
Case: `v8_5_primary_probe_r1p5_a45_h25_19301`
Seed: `19301`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, active-fill-transit escape pass, strict second-candidate raw
ranking pass, Stage B pass, final-zero pass, complete analysis and plot bundle,
and cleanup pass.**

This was the one authorized execution of the fixed v8.5 visible primary
probe. It ran once from the committed isolated install with Gazebo GUI enabled
and was not retried or changed in flight.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  scenario_summaries/
  20260731T101026602592Z_phase08_v8_5_primary_visible_probe.yaml
SHA-256:
  d6b0184d89dc768dff3894d74421c616f86bc2b6f8b9225cd909ddf6958d25e7
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  2026-07-31/
  20260731T101027547991Z_simulation_phase08_v8_5_primary_visible_probe-v8_5_primary_probe_r1p5_a45_h25_19301-robust__20e2e3be
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
remaining new nodes:        none
remaining processes:        none
analyze_run:                complete
analysis failures:          none
plots produced:             9/9
```

Evidence hashes:

```text
raw bag:
  6aa3fc901f5a31354517ba077d44b4bb6e7a18492048f51f6969afdeba3c9e7b
completeness.json:
  99723594a06b2ba620ddf600eec4231acc9929f3e5351d76ed143cdcaa937a28
scenario_result.yaml:
  d47cbf8f46f5bf9ec971a5277e2e65ab25a795dbb34498b4226d75a48f6c7bc3
analysis/phase07/analysis_completeness.json:
  57e852481b0449bee876054de47ac97b807f74bb01c9d97f4ebb53f9061d1f27
analysis/phase07/summary_metrics.json:
  202eb994e90e7b9537243dd75d6aad5ad69c67625ae2fb93ce461407f87caf07
```

The analyzer status is `complete`. Its only warnings identify the three
declared assumed fallbacks for `channel_index`, `sync_tolerance_sec`, and
`supervisor_publish_rate_hz`; they are not failures. Fresh Phase 05
validation, applicability integrity, critical inputs, typed timestamps,
source-cost semantics, final-zero commands, final readiness false, and
console checks pass.

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
post-readiness explicit-stop transition is shutdown evidence outside the
accepted motion interval.

## Stage A and candidate-informed fill

Stage A ran from simulation time `0.329 s` through `175.905 s` and completed
within its fixed `360.0 s` budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (0.963847, 1.239747) m
convergence point:            (1.069389, 1.324353) m
distance to declared local:   0.263837 m
fill-to-convergence distance: 0.135267 m
fill merge/supersession:      none
```

Candidate one used the required bounded evidence pool:

```text
frozen pretrigger rotations:  6
verification rotations:       3
available rotations:          9
selected repeated rotations:  3
raw estimate:                 -2.700046418293837
MAD:                           0.14532640388828177
uncertainty:                   0.4359792116648453
lower bound:                  -3.136025629958682
upper bound:                  -2.2640672066289915
```

The accepted typed fill retained the same raw interval:

```text
requested amplitude floor: 3.920032037448353
accepted amplitude:        3.920032037448353
amplitude cap reached:     false
sigma major/minor:         0.506211 / 0.506211 m
support radius:            1.518634 m
escape exit radius:        1.366771 m
design escalation count:   0
```

## V8.5 active-fill-transit escape

The escape event proves that the controller derived and latched one direct
direction from retained odometry and fill geometry:

```text
history anchor:               (0.336946, 0.024719) m
history anchor source time:   10.7 s
history displacement:         1.367223 m
history age:                  135.4 s
direct continuity direction:  (0.458521, 0.888684)
selected escape direction:    (0.458521, 0.888684)
selected rotation:            0.0 rad
direction revision:           1
active-fill transit enabled:  true
excluded active fill:         fill 1
retained other-fill count:    0
```

The selected vector exactly equals the direct continuity vector. The active
fill remained active at revision one in the typed registry and remained in
the modified cost. It was excluded only from collision-like direction
eligibility for its own escape episode.

The measured radial-progress gate entered finite assist after the initial
zero-translation repulsion stalled:

```text
escape outcome:           success
repulse stalled:          true
outward assist used:      true
escape duration:          29.935893 s
approximate escape orbit: 1.308037
maximum radial progress:  0.236130 m
failsafe:                 false
timeout:                  false
```

The published safe direction remained the same direct vector at revision one
through `ESCAPE_REPULSE` and `ESCAPE_ASSIST`; there was no tangent selection,
reselection, reversal, or accumulated turn. The recorded weights match the
v8.5 contract:

```text
ESCAPE_REPULSE: (raw, Gaussian, affine) = (0, 1, 1)
ESCAPE_ASSIST:  (raw, Gaussian, affine) = (0, 1, 1)
SEARCH:         (raw, Gaussian, affine) = (1, 1, 0)
```

At the measured `ESCAPE_ASSIST -> SEARCH` completion at source time `175.8 s`,
affine weight is zero and safe-direction validity is false on the first
recorded `SEARCH` sample. There is no persistent affine or route guidance
after recovery.

## Strict ranking and Stage B

Candidate two used the same intended `6 + 3` evidence pool:

```text
raw estimate:                 -3.8372093023255816
MAD:                           0.0
uncertainty:                   0.0
lower/upper:                  -3.8372093023255816
retained candidate-one lower: -3.136025629958682
strict separation margin:      0.7011836723668994
candidate ordinal:             2
filled candidate count:        1
known source count:            2
decision:                      GOAL_REACHED
```

The controller ranked candidate two at source time `300.2 s`. The first
valid later evaluator sample was:

```text
simulation time:       300.311 s
position:              (3.551734, 3.635997) m
declared global:       (3.5, 3.5) m
distance:              0.145504 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
ordering:              GOAL_REACHED before proximity sample
```

Stage B ran from `175.905 s` through `300.311 s`, or `124.406 s`, within its
fixed `180.0 s` budget. The final retained distance is `0.145494 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted its strict raw-cost ranking
event. The physical contract remains manual operator `Ctrl+C`; no physical
coordinate-distance stop is introduced.

## Analysis metrics

```text
analysis status:          complete
controller success:       true
counted ranked goal:      true
failsafe:                 false
timeout:                  false
fill count:               1
escape attempts:          1
escape successes:         1
escape failures:          0
path length:              17.941371 m
goal convergence time:    299.129229 s
readiness duration:       299.193616 s
terminal state:           GOAL_HOLD
```

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  2026-07-31/
  20260731T101027547991Z_simulation_phase08_v8_5_primary_visible_probe-v8_5_primary_probe_r1p5_a45_h25_19301-robust__20e2e3be/
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

The trajectory plot visibly shows local capture, one nearby retained fill,
direct northeast escape, open-field transit, and global capture. The
candidate plot shows candidate two strictly below candidate one's retained
lower bound. The radial plot shows the assisted measured exit, the weights
plot shows affine removal on return to `SEARCH`, and the state plot shows the
complete staged path and terminal `GOAL_HOLD`.

Machine-readable tables are retained beside the plots under
`analysis/phase07/tables/`.

## Gate disposition

The fixed v8.5 primary visible probe passes M4.5. It authorizes the sealed
ten-run v8.5 primary repeat gate only after this immutable evidence, report,
and live status are checkpointed and committed, followed by a separate
checkpointed and committed repeat-dispatch boundary.

This pass is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility claim,
a secondary-layout claim, a three-light claim, or a broad arbitrary-layout or
intensity claim.
