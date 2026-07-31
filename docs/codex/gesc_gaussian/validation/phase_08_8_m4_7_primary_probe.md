# Phase 08.8 M4.7 Fixed V8.6 Primary Visible Probe

Date: 2026-07-31
Committed dispatch boundary: `378804f`
Scenario: `phase08_v8_6_primary_visible_probe.yaml`
Case: `v8_6_primary_probe_r1p5_a45_h25_19316`
Seed: `19316`
Profile: `robust_gaussian_v1`

## Result

**FORMAL PASS — infrastructure complete, Stage A pass, exact one-fill
cardinality, supervisor-owned assisted escape pass, measured exit alignment
pass, strict second-candidate raw ranking pass, Stage B pass, final-zero pass,
complete analysis artifact bundle with one non-gating generic metric
limitation, all nine plots, and cleanup pass.**

This was the one authorized execution of the fixed v8.6 visible primary
probe. It ran once from the committed isolated install with Gazebo GUI
enabled and was not retried or changed in flight.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  scenario_summaries/
  20260731T122709562239Z_phase08_v8_6_primary_visible_probe.yaml
SHA-256:
  de5b739c2aeb57750655c391dd427b25fef54f80a30cd7de1d8c5ac9d1fdfdb3
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  2026-07-31/
  20260731T122710523689Z_simulation_phase08_v8_6_primary_visible_probe-
  v8_6_primary_probe_r1p5_a45_h25_19316-robust__c4156158
```

## Infrastructure and formal evidence

```text
scenario runner return code:      0
record process return code:       0
record process timed out:         false
graceful global-proximity stop:   true
recording complete:               true
authoritative completeness:       PASS
completeness failures:            none
completeness warnings:            none
final readiness false:            PASS
final commands zero:              PASS
cleanup:                          PASS
remaining new nodes:              none
remaining processes:              none
formal scenario classification:   PASS
required predicates:              14/14
analyze_run return code:          0
analysis failures:                none
plots produced:                   9/9
```

Evidence hashes:

```text
raw bag:
  eef7417aac054bc9e534369c9e0654a40e5afbbb860f85e8ae2519c7d167aa4e
completeness.json:
  51818876d3b2eb47299d5bd3794e7936339fde1de4569ada19c223c854f12663
scenario_result.yaml:
  89ae6f2adc7e2ba490917900dcb3902fdd0bcf3bea4f5ef8e3b449a5d00d318f
analysis/phase07/analysis_completeness.json:
  171dcc92eb7c8d35d3dc4da4f42da15aa971a0560ac73236b7a9ce194a9cee13
analysis/phase07/summary_metrics.json:
  59d2257f126d1e157f65c8bafabb3bad2280fd44c474972e147bbce5a01b20bc
dispatch log:
  /tmp/phase08_8_m4_7_primary_probe_dispatch.log
  654048ce58a582bbb493d0e70f12d57c21ae1037b98612e1850052710f582cd6
analysis log:
  /tmp/phase08_8_m4_7_primary_probe_analysis.log
  5a7fc487957433b0235390b9517f5db62d82e07c99bf22bace0a9cd421222f0d
```

## Behavioral path

The exact required path passed:

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

Stage A ran from simulation time `0.524 s` through `184.532 s`, or
`184.008 s`, within its fixed `360.0 s` budget.

```text
completed recovery episodes: 1
created clusters:             [1]
typed clusters:               [1]
active clusters:              [1]
fill count:                   exactly 1
fill center:                  (1.296031, 0.933131) m
convergence point:            (1.196543, 0.978328) m
distance to declared local:   0.158880 m
fill-to-convergence distance: 0.109273 m
fill merge/supersession:      none
```

Candidate one used the required bounded evidence pool:

```text
frozen pretrigger rotations:  6
verification rotations:       3
available rotations:          9
selected repeated rotations:  3
raw estimate:                 -2.8453728221821186
MAD:                           0.0
uncertainty:                   0.0
lower/upper:                  -2.8453728221821186
```

The accepted typed fill retained the same raw interval:

```text
requested amplitude floor: 3.5567160277276484
accepted amplitude:        3.5567160277276484
amplitude cap reached:     false
sigma major/minor:         0.506211 / 0.506211 m
support radius:            1.518634 m
escape exit radius:        1.366771 m
design escalation count:   0
```

## V8.6 direction and command ownership

The escape event proves that the supervisor derived and latched one direct
direction from retained odometry and fill geometry:

```text
history anchor:               (0.267193, 0.032539) m
history anchor source time:   8.6 s
history displacement:         1.367324 m
history age:                  158.2 s
direct continuity direction:  (0.752446653, 0.658653198)
selected escape direction:    (0.752446653, 0.658653198)
selected rotation:            0.0 rad
direction revision:           1
active-fill transit enabled:  true
excluded active fill:         fill 1
retained other-fill count:    0
```

The measured radial-progress gate entered finite assist after repulsion
stalled:

```text
escape start source time:     166.8 s
assist start source time:     169.9 s
escape complete source time:  184.4 s
escape outcome:               success
repulse stalled:              true
outward assist used:          true
escape duration:              17.681432 s
approximate escape orbit:     0.699071
maximum radial progress:      0.309885 m
failsafe:                     false
timeout:                      false
```

The schema-v10 command-owner predicate passed:

```text
assist state samples:                  290
evaluated assist control samples:      1,876
fresh matching supervisor commands:    1,876
nonzero GESC proposals suppressed:     1,876
positive supervisor linear samples:    1,876
selected direction revision:           1 throughout
fill-to-exit distance:                  1.478864 m
measured exit position:                (2.415237, 1.899785) m
selected/actual-exit alignment:         0.999977987
post-exit supervisor zero:              PASS
post-exit ordinary GESC ownership:      PASS
```

The actual escape therefore followed the selected onboard-history vector
nearly exactly. This directly corrects the retained v8.5 seed-`19316`
wrong-side exit, whose measured alignment was `-0.925`.

Recorded state weights match the intended contract:

```text
ESCAPE_REPULSE: (raw, Gaussian, affine) = (0, 1, 1)
ESCAPE_ASSIST:  (raw, Gaussian, affine) = (0, 1, 1)
SEARCH:         (raw, Gaussian, affine) = (1, 1, 0)
```

The first synchronized post-exit sample has no valid safe direction, zero
supervisor command, zero supervisor contribution, and combined command equal
to the ordinary GESC proposal. There is no persistent affine, supervisor, or
route authority after recovery.

## Strict ranking and Stage B

Candidate two used the same intended `6 + 3` evidence pool:

```text
raw estimate:                 -3.8372093023255816
MAD:                           0.0
uncertainty:                   0.0
lower/upper:                  -3.8372093023255816
retained candidate-one lower: -2.8453728221821186
strict separation margin:      0.9918364801434629
candidate ordinal:             2
filled candidate count:        1
known source count:            2
decision:                      GOAL_REACHED
```

The controller ranked candidate two at source time `291.4 s`. The first
valid later evaluator sample was:

```text
simulation time:       291.530 s
position:              (3.607557, 3.569383) m
declared global:       (3.5, 3.5) m
distance:              0.127995 m
radius:                0.50 m
interpolation used:    false
ranked goal required:  true
ordering:              GOAL_REACHED before proximity sample
```

Stage B ran from `184.532 s` through `291.530 s`, or `106.998 s`, within
its relaxed simulation-only `300.0 s` budget. The final retained distance is
`0.127973 m`.

The evaluator coordinate did not direct motion. It stopped this simulation
only after the controller independently emitted its strict raw-cost ranking
event. The physical contract remains manual operator `Ctrl+C`; no physical
coordinate-distance stop is introduced.

## Offline analysis disposition

`analyze_run` executed exactly once, returned zero, produced every expected
table and all nine plots, reported all critical inputs present, passed fresh
Phase 05 validation, and has:

```text
analysis_failures: []
applicability integrity: PASS
formal scenario acceptance: PASS
analysis artifact bundle: complete
summary analysis_status: partial
```

The summary is `partial` only because the optional generic
`state_durations` metric conservatively invalidated itself after three
isolated pre-Stage-A `SEARCH` gaps exceeded three nominal supervisor periods:

```text
0.220447 s
0.162486 s
0.338401 s
```

The complete typed state path, Stage A episode, assist interval, post-exit
handoff, terminal state, event sequence, recording completeness, and all
formal acceptance predicates remain valid. No critical stream is missing,
and the analyzer reports no analysis failure. This limitation is retained
and reported; the analyzer was not rerun and no evidence gate was weakened.

For the v8.6 runtime gate, “complete analysis” means the analyzer completed
successfully with its full artifact bundle, no `analysis_failures`, and all
nine required plots. It does not require every optional generic metric to be
valid when that metric is independent of the formal recorded predicates.

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
escape time:              17.681432 s
path length:              17.421318 m
goal convergence time:    291.070090 s
readiness duration:       291.190027 s
terminal state:           GOAL_HOLD
```

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  2026-07-31/
  20260731T122710523689Z_simulation_phase08_v8_6_primary_visible_probe-
  v8_6_primary_probe_r1p5_a45_h25_19316-robust__c4156158/
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

The trajectory plot visibly shows local capture, one nearby retained fill, a
straight northeast supervisor-owned exit, ordinary search transit, and
global capture. The candidate plot shows candidate two strictly below
candidate one's retained lower bound. The radial plot shows the measured
assisted exit, the weights plot shows affine removal on return to `SEARCH`,
and the state plot shows the complete staged path and terminal `GOAL_HOLD`.

Machine-readable tables are retained beside the plots under
`analysis/phase07/tables/`.

## Gate disposition

The fixed v8.6 primary visible probe passes M4.7. It authorizes the sealed
ten-run v8.6 primary repeat gate only after this immutable evidence, report,
plan clarification, and live status are checkpointed and committed, followed
by a separate checkpointed and committed repeat-dispatch boundary.

This pass is evidence for one fixed two-source, `400/1600`, radius-`1.5 m`,
angle-`45 deg` open-field case. It is not yet a ten-run reproducibility claim,
a secondary-layout claim, a three-light claim, or a broad arbitrary-layout or
intensity claim.
