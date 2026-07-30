# Phase 08.7 M4.2 visible-probe report

## Authority and immutable boundary

The user authorized one fresh visible two-light probe after the complete
M4.2 post-recovery liveness correction passed no-Gazebo qualification. The
implementation was committed at
`a1f58fb8b706181823877de35ff029fa812402bb`; the dispatch checkpoint was
committed at `232ac03d29e7513da6222b5c90e1f61c7808ca98`.

M4.2 did not overwrite, retry, relabel, or reuse M4.1 or any earlier case,
seed, run ID, evidence root, or completeness document. The fixed eight-case
suite and optional three-light probe were not run.

## Fixed input and execution

```text
suite:       phase08_v7_m4_2_visible_probe
version:     phase08-v7-m4-2-probe
case:        v7_m4_2_probe_r1p5_a45_h25_18208
case key:    d4aaa0d2d7e4af20c7721d2912620fe2a0a2f9f16004c462a0299e235f2866c8
seed:        18208
scenario:    e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973
ROS domain:  160
GUI:         visible
```

The one run is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe/
  2026-07-30/
  20260730T081058251159Z_simulation_phase08_v7_m4_2_visible_probe-
  v7_m4_2_probe_r1p5_a45_h25_18208-robust_gaussian_v_56b72dfe
```

The runner started at `2026-07-30T08:10:57.281166Z`, completed at
`2026-07-30T08:18:20.539562Z`, and returned `1`. It stopped gracefully on the
live `1.20 m` global-proximity sample, did not reach the post-Stage-A timeout,
and completed cleanup with no remaining new ROS nodes or session processes.
The recorder returned `1` only because its offline completeness result had
one failed evidence check; it did not time out.

## Formal result

The formal M4.2 visible-probe result is **FAIL: recording evidence invalid**.
The complete behavioral result independently passed.

```text
recording completeness:                   FAIL (47/48 checks passed)
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         PASS
post-Stage-A 120 s budget:                PASS (not expired)
collision expectation false:              PASS
required state path and events:           PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined formal result:                    FAIL
```

The non-gating `1.00 m` closer diagnostic was not reached. It cannot rescue
or fail the primary result.

## Stage A evidence

The accepted in-readiness path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Key ROS simulation times were:

```text
convergence confirmation:  309.3 s
VERIFY_EXTREMUM:            309.4 s
DESIGN_OR_MERGE_FILL:       318.5 s
ESCAPE_REPULSE:             318.7 s
RECENTER:                   327.0 s
resumed SEARCH:             340.0 s
```

Exactly one cluster was created:

```text
cluster/fill ID:             1
convergence point:           (1.3518537117, 1.3340700116) m
distance to declared local:  0.3994328707 m
distance to global:          3.0505385083 m
fill center:                 (1.2801842025, 1.4269760881) m
fill-to-convergence:         0.1173373667 m
```

Pure Gaussian repulsion escaped successfully in `8.362181527 s`; no redesign,
assisted escape, stall, timeout, collision, or in-readiness `FAILSAFE`
occurred. Recenter completed `0.1349758792 m` from its fixed safe-proxy target,
inside the new `0.15 m` tolerance.

## M4.2 post-recovery behavior

The new epoch started at simulation time `340.0 s`:

```text
anchor:                       (1.7340487379, 1.9017207353) m
fill center:                  (1.2801842025, 1.4269760881) m
anchor-to-fill distance:      0.6567918213 m
guidance outward hold:        0.60 m
affine taper distance:        0.50 m
recenter already attempted:   false
```

Guidance completed normally at `359.1 s`:

```text
epoch path length:            1.6420006682 m
epoch net displacement:       1.1386958164 m
outward progress:             1.1087168804 m
12 s window path:             1.0305195589 m
12 s window displacement:     0.7656182086 m
direction refresh count:      0
liveness recenter attempted:  false
```

The high net displacement correctly avoided the loop-recovery ladder. This is
the intended distinction from M4.1, which traveled substantially but gained
little net translation.

Stage B began on the first valid post-Stage-A odometry sample at
`340.022 s`. The live runner stopped at `361.918 s`, only `21.896 s` into the
independent `120.0 s` budget:

```text
global:                   (3.5, 3.5) m
qualifying pose:          (2.9001106472, 2.4628184159) m
global distance:          1.1981706364 m
valid post-A samples:     645
invalid post-A samples:   0
interpolation:            false
```

The behavioral correction therefore succeeded on the one fixed M4.2 attempt.

## Evidence failure and root cause

All required topics, exact publishers, `/clock`, singleton timestamps,
multi-publisher `/joint_states`, source causality, event freshness, motion
coverage, final-zero, readiness, parameters, metadata, notes, and cleanup
checks passed. Only this check failed:

```text
algorithm_event_producer_identified
```

The two unidentified records were valid supervisor-owned
`AlgorithmEvent.EVENT_CONFIGURATION` messages:

```text
post-recovery guidance epoch started
post-recovery outward progress completed
```

`validate_run.algorithm_event_producer_stream()` identifies shared-bus
configuration-event producers by a closed prefix table. The supervisor's
previous configuration prefix, `measured escape`, is present, but the new
M4.2 `post-recovery ` prefix was not added. The messages are fully typed,
finite, fresh, and nonregressing; the defect is attribution coverage, not
timestamp content or runtime ownership.

A read-only in-memory replay mapped only
`EVENT_CONFIGURATION + detail.startswith("post-recovery ")` to the existing
`supervisor` stream. It returned:

```text
patched_read_only_passed:             true
failures:                             []
algorithm_event_producer_identified:  PASS
typed_timestamps_nonregressing:       PASS
algorithm_event_emission_fresh:       PASS
```

The replay used `write_report=False`. It did not modify or relabel the
retained M4.2 `completeness.json`, which remains failed.

## Bag and standard analysis

Read-only Python sqlite `PRAGMA quick_check` returned `ok`; the bag contains
`772,486` messages. Standard analysis returned `0` with no analysis failure,
eight plots, and eleven tables under:

```text
analysis/phase07
```

Its status is correctly `partial` solely because both the stored and fresh
Phase 05 validation see the same unidentified-producer check. Its three
warnings are existing assumed fallbacks for channel index, synchronization
tolerance, and supervisor publish rate.

## Smallest fresh correction

M4.2 remains a formal evidence failure and must not be retried or relabelled.
A fresh, explicitly authorized version should:

1. add `("post-recovery ", "supervisor")` to the existing closed
   configuration-prefix map in `validate_run.py`;
2. extend the existing producer-signature and per-producer timestamp tests to
   cover the new M4.2 event family and continue rejecting unknown signatures;
3. prove with read-only replay that M4.2 would otherwise pass while preserving
   its immutable failed completeness file;
4. replay M4 and M4.1 read-only so their formal outcomes and completeness
   hashes remain unchanged;
5. run focused/broad recording plus M4.2 behavioral regressions, an isolated
   build, installed dry-run, checkpoint, and commit before a fresh visible
   attempt;
6. use a fresh version, case ID, seed, and evidence root. No eight-case suite
   or three-light run may start until that fresh visible probe passes every
   evidence and behavioral predicate.

This correction changes neither navigation nor any acceptance threshold.

## Retained hashes

```text
9d296d50c203804f3938bcb22379b6b6bc6c5636d9c5880bded51ee4a75043ad  suite summary
4abaecc2dacf8fb544de01ba198e4e26792566c5cc44c059e6d99e4802d746d0  completeness
b7f4a57a973f79ff9e2b07c5ad7c8968f341b7ee0d3fa6b3b2c9029fd07984fe  scenario result
2cc3596a31d938e50be94db1d10fadf0d2ffebcc1e7875340a6a1dd0c3ad101a  resolved scenario
58075c7f39941df1a0a452c3a4fc45344e22396fc1a6ee16fe5c6af4c5ba683f  resolved topics
6f674c5aae80b469378342d1e8666b6220edc548c007025b7e82300834a90960  metadata
7dd10ccd0231cd9e17eb8b9e1a76d8dbba5779d19d7c8fd2e1dc2f3d8093af66  sqlite bag
414a9537a888adc30fc0b586b8c5832cb1039c6271913639c0264d0d7eb537cc  analysis completeness
2da54701a71a5ee4befe788461af766f19f1333107b928730d286032d5d736d4  summary metrics
```
