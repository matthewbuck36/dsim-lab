# Phase 08.8 M4.4 Fixed V8.4 Primary Repeats

Date: 2026-07-30 PDT (artifacts dated 2026-07-31 UTC)
Committed dispatch boundary: `31a99ed`
Scenario: `phase08_v8_4_primary_repeats.yaml`
Case: `v8_4_primary_repeat_r1p5_a45_h25`
Profile: `phase08_v8_4_counted_open_field_approach_continuity_v1`

## Result

**FIXED POPULATION FAIL — seed `19211` passed; seed `19212` passed Stage A,
exact one-fill cardinality, and measured escape, but failed Stage B after the
escape direction revalidator reversed the initial direction. Seeds
`19213..19220` were not dispatched, as required by the committed
first-failure rule.**

The committed scenario resolved ten seeds, `19211..19220`, for serial,
headless, fresh-process execution. Exactly two executed once. There were no
retries, outcome-based parameter changes, cleanup failures, or later-seed
dispatches after the first formal failure.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_repeats/
  scenario_summaries/
  20260731T090629163024Z_phase08_v8_4_primary_repeats.yaml
SHA-256:
  5b464fa8c405c4651d863949839d161d00dfd4bd44bc415d4d54cf02fa4ee381
```

Committed scenario SHA-256:

```text
ef822e73c13f1e78d94c60ae10a11438caae8137507aae837495d84109699407
```

Run root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_repeats/
  2026-07-31/
```

## Dispatch accounting

| Seed | Run suffix | Formal result | Stage A | Stage B | Final global distance |
|---:|---|---|---:|---:|---:|
| 19211 | `cda49cce` | PASS | `193.419 s` | `165.988 s` | `0.119298 m` |
| 19212 | `8ffaac16` | **FAIL** | `167.513 s` | `180.030 s`, expired | `4.679383 m` |
| 19213–19220 | — | **NOT DISPATCHED** | — | — | — |

Both executed runs passed recording completeness, final-zero, final readiness
false, cleanup, exact one-fill cardinality, and Stage A. Seed `19211`
completed:

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

Seed `19212` completed the same path through assisted escape, then remained in
ordinary `SEARCH` until the independent Stage B budget expired:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

It emitted no in-readiness `FAILSAFE`, `TIMEOUT`, forbidden fill event, second
fill, or invalid ranked-goal event. The runner stopped it gracefully for the
failed Stage B gate. The later explicit-stop transition is shutdown evidence
outside the accepted motion interval.

## Infrastructure and analysis

Both recorders returned `0` without timing out. Both authoritative Phase 05
completeness results passed, and both cleanups passed with no remaining new
node or session process. The serial runner exited `1` with
`stopped_early_reason: run_failure`.

| Seed | Analyzer | Synchronized anchors | Path length | Escape time | Goal time | Analysis note |
|---:|---|---:|---:|---:|---:|---|
| 19211 | partial | 46,062 | `20.901905 m` | `23.683461 s` | `357.204499 s` | one state gap invalidated only duration reconstruction |
| 19212 | complete | 44,556 | `13.773860 m` | `24.575067 s` | none | behavioral failure retained separately |

Both analyses have `analysis_failures: []`, all nine plots, all tables, and
fresh Phase 05 validation. Contacts and generic aggregate-target metrics are
unavailable by design in both open-field runs. Seed `19211` is `partial`
because one state gap exceeded `0.15 s`; its formal scenario result remains
passed.

## Direction-reversal diagnosis

Fill amplitude, detector behavior, and recovery completion are not the
differentiators:

| Seed | Candidate-one lower | Fill amplitude | Escape duration | Stage A |
|---:|---:|---:|---:|---:|
| 19211 | `-3.470387` | `4.337984` | `23.683461 s` | PASS |
| 19212 | `-2.845373` | `3.556716` | `24.575067 s` | PASS |

Seed `19212` failed after the new approach-continuity intent was correctly
derived. The controller recorded:

```text
fill center:
  (1.069488, 1.314025) m
frozen onboard-history direction:
  (0.401588, 0.915820)
evaluator-only alignment with fill-to-global:
  +0.911010
```

The global coordinate in that alignment is offline diagnostic evidence only.
It was not available to the supervisor, controller, detector, or fill owner.

The active-fill hard-avoidance rule rejected the direct frozen direction at
escape start because the robot was only about `0.001758 m` from the estimated
fill center and the direct direction momentarily reduced that millimetric
offset. The selector therefore chose a tangent:

```text
initial selected direction, revision 1:
  (0.915820, -0.401588)
evaluator-only global alignment:
  +0.412383
```

During the three-second Gaussian-only repulse interval, the robot drifted to
the opposite side of the estimated center. At the stall sample, the initial
direction's projection on the new fill-center radial vector was negative, so
revalidation rejected it. The selected sequence became:

```text
revision 1 at 142.9 s:
  ( 0.915820, -0.401588)
revision 2 at 146.0 s:
  (-0.363617,  0.931549)
revision 3 at 146.5 s:
  (-0.915820,  0.401588)
```

Revision three is the exact negative of revision one. Its evaluator-only
global alignment is `-0.412383`. The robot completed a formally valid radial
escape on that northwest/west direction, returned to `SEARCH` near
`(-0.380863, 1.327148) m`, and ended at
`(-0.731250, 1.501713) m`.

Seed `19211` did not reverse:

```text
frozen direction:
  (0.689090, 0.724676)
revision 1:
  (0.689090, 0.724676)
revision 2:
  (0.999683, 0.025164)
frozen-direction evaluator-only global alignment:
  +0.999928
```

It escaped east/southeast, resumed raw-plus-Gaussian `SEARCH`, strictly ranked
candidate two, and stopped `0.119298 m` from the declared global.

The defect is therefore the integration of the correct frozen intent with an
active-fill rule intended as hard collision-like avoidance:

1. the active Gaussian fill is mathematical basin memory, not a physical
   obstacle;
2. the robot necessarily begins escape inside that fill;
3. a millimetric estimator offset can make the forward direction look
   momentarily “inward”;
4. the hard rule replaces it with a tangent;
5. later revalidation may choose the other tangent and reverse the affine and
   supervisor directions;
6. a valid radial escape can consequently carry the robot away from the
   unvisited basin.

Increasing Stage B or weakening the fill does not correct this reversal.
Increasing affine gain alone also cannot guarantee direction continuity when
the supervisor changes the typed affine direction itself.

## Bounded correction implication

A fresh version should treat the active fill differently from a prior fill
during this one escape episode:

- latch the frozen direct approach-continuity direction;
- do not treat the active mathematical fill as a hard obstacle while the robot
  transits its own estimated center;
- continue checking every other retained fill and all finite/stale-input
  contracts;
- keep the direction fixed through `ESCAPE_REPULSE` and `ESCAPE_ASSIST`;
- fail explicitly rather than reverse it;
- clear it at measured escape completion exactly as v8.4 already does.

This uses no source/global coordinate, Vicon pose, room dimension, wall model,
route map, waypoint, or persistent post-recovery guidance. It is valid only
for the already declared route-blocking/local-first demonstration envelope;
it is not a general guarantee for arbitrary basin order.

## Evidence hashes

Hashes are ordered as raw bag, `completeness.json`, `scenario_result.yaml`,
`analysis_completeness.json`, and `summary_metrics.json`.

```text
seed 19211 / cda49cce
49cb731241d515990aff1499632799ed174af1b502490d76a47f3da4a49386d7
b763e2546316933e538fe9014c60ac12db0e8ab26b70fe3e30ec54234eddf74d
27d3f48c63a889dcf6ec3cc9a3d5e8997e5837bd5fb70d9f0bf274a582230999
dc3ae65c9138a98586fdf4bdc391a32e4172bd5607f3ecf98031e5e6a9dcbdc3
7543a25c37e33b8bcc81bd2791472c7c4920d82978aabf2d6f6fa132d15f5576

seed 19212 / 8ffaac16
16958a533a1b53cf78ceeaf35de15ae93db5b4af54b605ca7923705456104167
493932b4d97b2a2495f149b62cc8d1bbd444c1ede4c5d002fbdb3efe12990550
1f35f3f08bc36b07bceb506f5c3eac64f44db740748db45f6edc88c986c10f65
27cf63ff163a1e5f81ff8b6d1b2f269f516aa793fe3685a27a94f9e2d63f5c55
6161fb3f45dac9a02c54015334f4f805ba80c9d96b10799e6ac8a8f6cc6ac724
```

## Plots

Each retained run has the complete nine-plot bundle under:

```text
<run>/analysis/phase07/plots/
```

The failed seed's `trajectory_sources_fills.png` visibly shows local capture,
one fill, westward escape, and post-recovery search away from the global. Its
`radial_escape.png` shows that Stage A was a real measured escape rather than
a stuck recovery. Seed `19211`'s trajectory shows the corresponding passing
local-fill-escape-global sequence.

## Gate disposition

The fixed v8.4 primary population is closed failed. No v8.4 secondary or broad
run is authorized. The evidence must be checkpointed and committed before a
fresh default-off correction amendment is implemented or dispatched.
