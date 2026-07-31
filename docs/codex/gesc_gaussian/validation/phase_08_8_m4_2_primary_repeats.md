# Phase 08.8 M4.2 Fixed V8.3 Primary Repeats

Date: 2026-07-30 PDT (artifacts dated 2026-07-31 UTC)
Committed dispatch boundary: `ec21cda`
Scenario: `phase08_v8_3_primary_repeats.yaml`
Case: `v8_3_primary_repeat_r1p5_a45_h25`
Profile: `phase08_v8_3_counted_open_field_candidate_fill_v1`

## Result

**FIXED POPULATION FAIL — four of five dispatched seeds passed; seed `19115`
passed Stage A and exact one-fill cardinality but failed Stage B after escaping
through the arrival-side corridor. Seeds `19116..19120` were not dispatched,
as required by the committed first-failure rule.**

The committed scenario resolved ten seeds, `19111..19120`, for serial,
headless, fresh-process execution. Exactly five were executed once. There were
no retries, outcome-based parameter changes, cleanup failures, or later-seed
dispatches after the first formal failure.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_repeats/
  scenario_summaries/
  20260731T070914746817Z_phase08_v8_3_primary_repeats.yaml
SHA-256:
  596b93d0fa07a63be2bc9b38691fb879b017ff8e1b5d21ade9bfffc8a99c2ec8
```

Committed scenario SHA-256:

```text
51456d960af47a1942033e80e38a049a74b848345c091e1cda257b04c0ac30bc
```

Run root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_repeats/
  2026-07-31/
```

## Dispatch accounting

| Seed | Run suffix | Formal result | Stage A | Stage B | Final global distance |
|---:|---|---|---:|---:|---:|
| 19111 | `7c1017e5` | PASS | `191.010 s` | `115.294 s` | `0.141761 m` |
| 19112 | `1f25b3b1` | PASS | `200.825 s` | `121.006 s` | `0.155023 m` |
| 19113 | `5f655ca5` | PASS | `202.227 s` | `133.382 s` | `0.119478 m` |
| 19114 | `18a12d0e` | PASS | `190.634 s` | `164.390 s` | `0.185826 m` |
| 19115 | `f501f968` | **FAIL** | `346.924 s` | `180.030 s`, expired | `5.167727 m` |
| 19116–19120 | — | **NOT DISPATCHED** | — | — | — |

All five executed runs passed recording completeness, final-zero, final
readiness false, cleanup, exact one-fill cardinality, and Stage A. The four
passing seeds followed:

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

Seed `19115` followed the same path through the completed assisted escape, then
remained in `SEARCH` until the independent `180.0 s` Stage B budget expired:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

It emitted no in-readiness `FAILSAFE`, `TIMEOUT`, forbidden fill event, or
second fill. The runner stopped it gracefully for the failed Stage B gate, and
the later explicit-stop transition is shutdown evidence outside the accepted
motion interval.

## Infrastructure and analysis

Every executed recorder returned `0` without timing out. Every authoritative
Phase 05 completeness result passed, every cleanup passed with no remaining
new node or session process, and the serial batch stopped with
`stopped_early_reason: run_failure`.

| Seed | Analyzer | Synchronized anchors | Path length | Goal time | Analysis note |
|---:|---|---:|---:|---:|---|
| 19111 | complete | 39,235 | `18.773845 m` | `304.372910 s` | none |
| 19112 | complete | 41,317 | `19.587510 m` | `320.470383 s` | none |
| 19113 | partial | 43,159 | `20.420976 m` | `334.864602 s` | one state gap exceeded `0.15 s`; formal scenario result passed |
| 19114 | complete | 45,566 | `20.452050 m` | `353.314944 s` | none |
| 19115 | partial | 67,923 | `24.741314 m` | none | behavioral failure and one state gap exceeded `0.15 s` |

Both partial analyses have `analysis_failures: []`; their available metrics,
plots, candidate evidence, odometry, and fresh Phase 05 validation remain
usable. The state-gap limitation is reported separately from the scenario
classification and does not turn seed `19115` into an infrastructure failure.

## Failure diagnosis

Candidate-informed fill strength is not the differentiator. The failed seed's
accepted amplitude was `3.556827`, equal within recorded precision to three
passing seeds. It completed a valid assisted escape, retained the fill, and
did not return to the filled local basin.

The differentiator is the outward direction chosen after the Gaussian-only
escape became radially stalled. The following diagnostic uses the declared
global coordinate only offline, after execution. It was never available to
the supervisor, controller, detector, or fill owner.

```text
escape alignment =
  unit(fill center -> assisted exit)
  dot unit(fill center -> declared global)
```

| Seed | Fill amplitude | Candidate-one lower | Assisted exit `(x,y)` | Escape alignment |
|---:|---:|---:|---:|---:|
| 19111 | `3.557` | `-2.846` | `(2.281, 1.599)` | `+0.906` |
| 19112 | `3.557` | `-2.845` | `(2.748, 1.210)` | `+0.751` |
| 19113 | `3.557` | `-2.845` | `(2.734, 0.792)` | `+0.559` |
| 19114 | `4.390` | `-3.512` | `(2.431, 0.198)` | `+0.159` |
| 19115 | `3.557` | `-2.845` | `(-0.214, 0.369)` | **`-1.000`** |

The four positive-alignment escapes reached and strictly ranked the stronger
second candidate. Seed `19114`, with the weakest positive alignment, passed
closest to the Stage B limit. Seed `19115` escaped almost exactly opposite the
remaining stronger basin, crossed back through the side from which the robot
had entered the local region, and ended at `(0.11484, -0.40462) m`.

This is a controller/supervisor symmetry-breaking defect:

1. both `ESCAPE_REPULSE` and open-field `ESCAPE_ASSIST` set the raw-cost weight
   to zero;
2. the Gaussian centered on the filled basin supplies radial repulsion but no
   preferred world direction;
3. the open-field supervisor freezes whichever radial side stochastic
   dynamics occupy at the stall sample;
4. the stronger source's sensor signal is therefore excluded precisely while
   the escape direction is selected.

The evidence rejects weakening the fill or merely extending Stage B. A weaker
fill risks restoring the local minimum; a longer timeout permits more travel
along an already wrong heading. A fresh correction must preserve v8.3 and
restore a sensor-derived directional asymmetry without source coordinates,
global pose, room geometry, Vicon, or a route planner.

## Evidence hashes

Hashes are ordered as raw bag, `completeness.json`, `scenario_result.yaml`,
`analysis_completeness.json`, and `summary_metrics.json`.

```text
seed 19111 / 7c1017e5
2444cc506c077ff8ea111bee96f250247fc40550e71b434de432aef6efac0f6d
3c3280ed65ba7bdd572a5e5e12f0a9d3ef4c3ca14d6bee1b38104b8563c69937
d486d8f7e10d2319d0368090118ce8c1f87df9ab413bb5f238eac180d891a0d7
811dd41136b7e66ad080c4e7976ec95ae92a0976b41b775f946ab936e755824f
50a06aea28c4af6ed5aad1152cbbd77bb7df37d31ae3aadd7ff1a540c6a3709a

seed 19112 / 1f25b3b1
5259eaa301ac716ce51a9067e8cfc2f9d1c61defa885d0334265fe04a6457519
246f198276563c70aaaf055e22d409514447f7cbc89d22f4f47997dc7ac021c3
fdc7dca4c8d4d7c6e9daa7edf19cd79a2505ff51235ef41d9ebaa86bfa972b3e
4d6098dcc7fe392843b1662452a5803e629a54d2dd14f6bb46cfbbe3d342610d
9d37d61051113cee220bab53ae3eb6d85154405c6c7d2bcfb98dd3153ca889f2

seed 19113 / 5f655ca5
164ad37a02a34e760a7c80fb04a9d62f63bdfb399fa614fa56c9720e07e0831c
09e273f3cd6a1851ba113ce2598a11ad78a2fd75c43586ae5e8d726dbe747e0c
0a094690bb0a94ca168f9a94cc68c6000884771db80dde967640e6ede095103b
6507efef2a28337578e043967630bb3ab66dafd3c6b1d39c31140a462c377da3
a6c9d8254413721f7750676dffcbb58dbbbd2b10220973ba650c09680f0928c9

seed 19114 / 18a12d0e
acb4bced7d667ddf84a18446a166602505ae6c900132a8cac1ad39a8256d0bbe
f6c4773038fdee09336a83246dbd165dd447a4b08f30b763e8118ee440c310c6
35291af3d95d39c1f3d2bd927d9551447fd129ec8a66bd048e6994e505bbbbab
cef4da45a1b2d0a758ca6fba353fc0da83e2220ed6a72374f2878651f732efc4
4cabfd47bf7eb9f07bef69958b584c9d88b973a2e2a477cc716714c96c11bb1f

seed 19115 / f501f968
f641f7ad5f6cb34bc13cdd0322baff11192ec99800dde0b4bdf866005c3ea109
f10458f9e6b56d60490224edcf8fdc953d5b33705696cdc0b690842c18230d0f
c2870ec7ba10c910f12616d2e59505839d34de36e4c3c2b74a4a22bfb726ca29
6cfc6da45222a2076443b27d94ceb32d4400d73a84339d49b6115b10552bfc4b
526d0152c6005d54f9115fd531f8d4e9fd37c54a6b4cc63a105e2cd05a2898e6
```

## Plots

Each run retains the nine standard Phase 07 plots under:

```text
<run>/analysis/phase07/plots/
```

The most diagnostic comparison is:

```text
7c1017e5/analysis/phase07/plots/trajectory_sources_fills.png
f501f968/analysis/phase07/plots/trajectory_sources_fills.png
```

The first shows a positive-alignment escape and global convergence. The second
shows the mirrored arrival-side escape and southwest search. Cost,
candidate-ranking, Gaussian-history, radial-escape, state, component, weight,
and command plots remain beside them, with machine-readable tables under
`analysis/phase07/tables/`.

## Gate disposition

The fixed v8.3 primary population is **CLOSED / FAIL**. Its secondary visible
probe, secondary repeats, and broader matrix are prohibited. No v8.3 case may
be retried, changed, relabelled, or counted in a fresh gate.

A continuation requires a separately planned, default-off, versioned
correction; complete no-Gazebo qualification; a material checkpoint and
commit; fresh scenario identities, roots, and seeds; then a new visible
primary probe.
