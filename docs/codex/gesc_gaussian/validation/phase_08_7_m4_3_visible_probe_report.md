# Phase 08.7 M4.3 visible-probe report

## Authority and fixed boundary

The user authorized the fresh M4.3 evidence-attribution correction and its
passing-gated two-light sequence on 2026-07-30. The Plan amendment was
committed at `6f7a5fa`, the qualified implementation at `85fdd6f`, and the
visible dispatch checkpoint at `b278209`.

M4.3 did not retry, overwrite, relabel, or count M4.2 or any earlier result.
The M4.2 failed completeness file and every tracked historical hash remained
immutable.

## Fixed input and execution

```text
suite:       phase08_v7_m4_3_visible_probe
version:     phase08-v7-m4-3-probe
case:        v7_m4_3_probe_r1p5_a45_h25_18308
case key:    a5ea7f8b3d12aa01be4018ba059d12f9366f722687f95403e1c47c6929fc4655
seed:        18308
scenario:    cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658
ROS domain:  161
GUI:         visible
```

Exactly one attempt ran:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe/
  2026-07-30/
  20260730T085116266752Z_simulation_phase08_v7_m4_3_visible_probe-
  v7_m4_3_probe_r1p5_a45_h25_18308-robust_gaussian_v_91c59c52
```

The suite started at `2026-07-30T08:51:15.319251Z`, completed at
`2026-07-30T08:56:09.342914Z`, and returned `0`. The internal live
global-proximity boundary stopped the run; the outer timeout did not fire.
Cleanup passed with no remaining new nodes or session processes.

## Formal result

The fixed M4.3 visible probe is **PASS**:

```text
recording completeness:                   PASS (48/48)
required state path and events:           PASS
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         PASS
post-Stage-A 120 s budget:                PASS (not expired)
collision expectation false:              PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined result:                           PASS
```

The optional non-gating `1.00 m` closer diagnostic was not reached. It did
not rescue or fail the primary result.

## Stage A evidence

The accepted direct path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Key simulation times were:

```text
convergence confirmation:  181.6 s
VERIFY_EXTREMUM:            181.7 s
DESIGN_OR_MERGE_FILL:       190.8 s
ESCAPE_REPULSE:             191.0 s
RECENTER:                   199.7 s
resumed SEARCH:             216.1 s
```

Exactly one cluster was created:

```text
cluster/fill ID:             1
convergence point:           (1.3727925110, 1.1298208642) m
distance to declared local:  0.3197026721 m
distance to global:          3.1847701388 m
fill center:                 (1.3617698434, 1.2560695726) m
fill-to-convergence:         0.1267289847 m
```

Pure Gaussian repulsion escaped successfully in `8.735487521 s`. No redesign,
assisted escape, stall, timeout, collision, or in-readiness `FAILSAFE`
occurred. Recenter completed `0.1452067367 m` from its fixed safe-proxy
target, inside the committed `0.15 m` tolerance.

## Post-recovery behavior and Stage B

The new guidance epoch started at `216.1 s`:

```text
anchor:                       (1.8824607739, 1.6835514429) m
fill center:                  (1.3617698434, 1.2560695726) m
anchor-to-fill distance:      0.6736911715 m
guidance outward hold:        0.60 m
affine taper distance:        0.50 m
recenter already attempted:   false
```

Guidance released normally at `236.7 s`:

```text
epoch path length:            1.7596027588 m
epoch net displacement:       1.1082037413 m
outward progress:             1.1045059990 m
12 s window path:             1.0635155091 m
12 s window displacement:     0.8501738801 m
direction refresh count:      0
liveness recenter attempted:  false
```

The high net displacement correctly avoided the loop-recovery ladder.

The independent Stage B clock started at `216.111 s`. The first qualifying
noninterpolated sample arrived after approximately `25.36 s`:

```text
global:                   (3.5, 3.5) m
qualifying pose:          (2.9945190974, 2.4141474035) m
global distance:          1.1977423781 m
valid post-A samples:     747
invalid post-A samples:   0
interpolation:            false
```

The operator-equivalent stop then finalized readiness false and zero command
evidence. The resulting explicit-stop state/event records occurred after the
readiness interval and did not violate the in-readiness forbidden contract.

## Corrected evidence and standard analysis

The two M4.3 supervisor configuration events were identified, fresh, and
nonregressing:

```text
post-recovery guidance epoch started
post-recovery outward progress completed
```

All `48` recording checks passed, including exact publishers,
multi-publisher timestamp scope, event attribution, event freshness, source
causality, final zero, clean shutdown, and strict finite JSON.

Read-only sqlite `PRAGMA quick_check` returned `ok`; the bag contains
`513,328` messages. Standard analysis returned `0` and reports `complete`
with no analysis failures, eight plots, and eleven tables under
`analysis/phase07`. Its three existing assumed-fallback settings are channel
index, synchronization tolerance, and supervisor publish rate.

## Retained hashes

```text
38565f76dc00424fecc6a4ac032ba9376a8cd8eb90e400f3fe2410ee6a5a93de  suite summary
a8a3c54c11028c7746ae4739f9357e7bb2245fc69c5b51cd5793a82c36d60390  completeness
6065e89a36628df5fa79bd04f3c6dbdeeb04fca137968c77d575c60ea94312e4  scenario result
d481c9fadd59faf8b1c64175decd725fb3bac520921148ac10fe97585f74e4c0  resolved scenario
6bebef88500af68bca09e423d2365f99a99a153091de9c0780862e186f0b1d05  resolved topics
85bdbc95107858d9c6377b41ab15832a18cffa4bd1453c7240d060ea4c320677  metadata
5346b6d8b2cbaa6bcfeedfe6abd071fbcca57291abb80cbbf2d9bdc7654566b9  sqlite bag
eeac4d8f77d0dd5f94723f9f95f9edb760fa18670b4edb84be19fc238bdb6ba3  analysis completeness
5e0700b9410c02a18bfed7808bb6c1b52b255bf03f7c2316d88d3333cd424b8b  summary metrics
```

The visible pass opens, but does not itself satisfy, the fixed M4.3
two-light-readiness gate. The serial eight-case suite may run only from its
committed bytes and fresh evidence root. The optional three-light probe
remains unauthorized.
