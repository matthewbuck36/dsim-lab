# Phase 08.8 baseline audit

Date: 2026-07-30

## Result

**PASS — the remembered simple GESC-plus-Gaussian behavior was recovered from
Git history without reverting the current architecture.**

The current implementation starts from:

```text
branch: feature/gesc-gaussian-robustness-v1
starting HEAD: bc25fef phase 08: close final report boundary
```

The last pre-phased boundary used for semantic comparison is:

```text
e0c693e6c9f954d3e7061c90089b7b2a2c6a1d4c
Update .gitignore and add Experiment Storage Protocol documentation
```

The first commit unique to this branch after `main` is:

```text
2af90644602e9a990fbbb4cfa6e079f94746e7fc
Add heavy-ball ESC work and supporting ROS nodes
```

`2af9064` is not a valid rollback target. It explicitly adds Heavy-Ball
configuration and supporting code, while this project retained the ordinary
GESC controller and retired Heavy-Ball as the active algorithm. Phase 08.8
therefore extends the current owners and leaves both historical commits
unchanged.

## Useful behavior at `e0c693e`

The old graph already demonstrated the minimal mechanism the user wants to
reproduce:

- a convergence metric and resettable three-crossing counter;
- an event-centered Gaussian fill derived from raw PDE cost history;
- persistent Gaussian modification of the controller cost;
- optional PDE-history affine exploration;
- ordinary GESC motion after a fill.

That implementation had no typed fill identity, no explicit supervisor state
contract, no source-count reasoning, no rotation-stable comparison between
extrema, and no complete recorder/validator lifecycle. Its apparent simplicity
is useful as a behavioral reference, but not as a safe code rollback.

## Current owner delta

The current tree replaces the implicit old flow with explicit, selectable
owners:

| Concern | Pre-phased behavior | Current retained owner |
|---|---|---|
| convergence | timing-sensitive crossing counter | detector with historical crossing default and opt-in qualified dwell |
| extrema | every event looked fill-ready | supervisor classifies a candidate before fill or terminal hold |
| fill | untyped four-value Gaussian output | adaptive typed fill, cluster identity, revision, validation, and association |
| memory | centers in process-local lists | active typed fill registry plus retained candidate summaries |
| escape | cost modification implicitly drove departure | explicit fill, repulse, optional assist, recenter, and search states |
| comparison | no local/global comparison | complete-rotation raw-cost median/MAD intervals |
| evidence | console topics | typed events, recorder completeness, final zero, offline validation, and plots |

Across the detector, fill, modified-cost, supervisor, scenario, recording,
analysis, and central launch owners, the semantic comparison from `e0c693e`
to the implementation boundary contains 71 added files and five modified
files. The size reflects the completed phased validation infrastructure; it is
not justification to duplicate or replace any owner.

## Adopted Phase 08.8 design consequence

Phase 08.8 keeps the useful simple flow while retaining the validated current
architecture:

```text
qualified candidate
-> raw-cost rotation summary
-> one adaptive typed fill
-> direct Gaussian repulse
-> SEARCH without recenter or affine guidance
-> second candidate
-> strict raw-cost interval ranking
-> GOAL_HOLD
```

The new path is opt-in. Historical defaults remain absolute source-score
classification, crossing-count confirmation, enabled operating bounds, and
their existing recenter/affine selections.

No controller input was added for declared source coordinates, source roles,
room center, Vicon pose, or evaluator global proximity. Existing `/odom`
continues to support PDE history and fill geometry, but Phase 08.8 introduces
no route map, waypoint planner, room map, or second pose estimator.
