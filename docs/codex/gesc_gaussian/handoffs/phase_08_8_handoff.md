# Phase 08.8 Handoff

## Terminal disposition

**PHASE 08.8 TERMINALLY CLOSED AFTER V8.12 / V8.10 PRIMARY FIXED LAYOUT
`11/11` / V8.11 SECONDARY FIXED LAYOUT `6/6` / V8.12 VISIBLE `1/1` /
V8.12 MATRIX FIRST CASE SCIENTIFICALLY COMPLETE BUT FORMAL `13/14` FAIL /
REMAINING MATRIX CASES NOT RUN / NO V8.13 / NO PHYSICAL MOTION.**

Read first:

- [Phase 08.8 final report](../validation/phase_08_8_final_report.md)
- [Phase 08.8 Plan](../plans/phase_08_8_plan.md)
- [Phase 08.8 v8.12 Plan](../plans/phase_08_8_v8_12_plan.md)
- [v8.12 terminal matrix result](../validation/phase_08_8_m8_9_v8_12_broad_matrix.md)
- [Phase 08 live status](../status/phase_08_status.md)

The earlier
[whole-Phase-08 final report](../validation/phase_08_final_report.md) remains
the authoritative history through Phase 08.7. Phase 08.8 is an additive,
separately versioned development iteration and does not relabel the earlier
broad simulation-ready failure.

The v8.10 empirical boundary retained below is its immutable historical
snapshot. The [current terminal amendment](#current-v811v812-boundary) at the
end of this handoff is authoritative for the completed Phase 08.8 goal.

## Final controller boundary

The selected behavior is opt-in and preserves historical defaults:

```text
extremum_classification_mode: counted_candidates
known_source_count:           2
max_fill_clusters:            1
operating_bounds_enabled:     false
recenter_after_escape:        false
```

The controller:

1. treats the first confirmed candidate as unknown;
2. summarizes complete-rotation raw-cost minima;
3. creates exactly one adaptive typed Gaussian fill;
4. escapes by either measured direct repulse or causal supervisor-owned
   assist;
5. restores ordinary GESC with the retained fill and affine weight zero;
6. rejects revisits associated with that fill;
7. summarizes the second candidate from raw cost;
8. accepts it only when its uncertainty interval is strictly lower.

It receives the integer source count but no source position, source role,
declared intensity, global coordinate, Vicon pose, room map, or evaluator
proximity. Existing relative odometry remains in use for Gaussian placement
and local motion history; no new route map, planner, or global
dead-reckoning system was added.

## Empirical boundary

### Primary layout — qualified

```text
start:        (0.0, 0.0)
first lamp:   (1.0606601718, 1.0606601718)
second lamp:  (3.5, 3.5)
inputs:       400 / 1600 simulator-relative
environment:  open field
```

Evidence:

```text
visible:                         1/1 formal pass
fresh headless repeats:         10/10 formal pass
local recovery and one fill:    11/11
strict second-candidate rank:   11/11
global convergence:             11/11
recording/final-zero/cleanup:    11/11
```

Reports:

- [primary visible](../validation/phase_08_8_m4_11_primary_probe.md)
- [primary repeats](../validation/phase_08_8_m4_11_primary_repeats.md)

### Secondary layout — not formally qualified

```text
start:        (0.0, 0.0)
first lamp:   (0.5740251485, 1.3858192988)
second lamp:  (3.5, 3.5)
inputs:       400 / 1600 simulator-relative
environment:  open field
```

Seed `19851` created one fill at the observed aggregate basin, completed the
direct-repulse recovery branch, strictly ranked the second candidate, entered
`GOAL_HOLD`, and finished `0.105549 m` from the global.

It remains a formal failure because the observed aggregate basin was about
`0.75 m` from the declared first lamp, outside the frozen evaluator's
`0.60 m` lamp-association limit. The five secondary repeats were not
authorized.

Report:

- [secondary fixed result](../validation/phase_08_8_m4_11_secondary_probe.md)

Do not quote this as `1/1` formal secondary success or two-layout
repeatability.

## Plots

Every final v8.10 run retains these nine plots under its run-local
`analysis/phase07/plots/` directory:

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

Use the exact run directories owned by:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/
  phase08_v8_10_primary_visible_probe_summary.yaml

/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats/
  phase08_v8_10_primary_repeats_summary.yaml

/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/
  phase08_v8_10_secondary_visible_probe_summary.yaml
```

Do not reconstruct a run suffix manually.

## Preserved compatibility

- V6 and every historical scenario/world/result remain preserved.
- `algorithm_profile=legacy` and historical defaults remain selectable.
- Cost sign, units, canonical topics, and message semantics are unchanged.
- `custom_controller` remains the sole `/cmd_vel` owner.
- The same algorithm owners remain shared by simulation and physical paths.
- The Phase 05 recorder/validator and Phase 07 analyzer remain the only
  owners of their responsibilities.
- All fixed Phase 08.8 failures remain failed evidence.

## Explicit nonclaims

- no arbitrary layout or intensity guarantee;
- no formally passing secondary repeat population;
- no M6 broader matrix;
- no three-light Gazebo result;
- no unknown-count behavior;
- no global-first recovery;
- no wall, collision, or obstacle-avoidance claim;
- no broad simulation-ready tag;
- no physical run.

The known-count three-source state-machine path is unit-tested, but physical
or Gazebo three-light behavior is not demonstrated.

## Physical contract

The simulation-only `0.50 m` evaluator stop is prohibited in physical
operation. The physical robot must continue until the operator decides it is
close enough and presses `Ctrl+C`.

That interrupt must retain:

```text
readiness false -> stop -> final zero -> bag finalization -> scoped cleanup
```

The field assumption is open, obstacle-free, and operationally bounded by a
human. Wall and obstacle avoidance are future work.

The simulator `400/1600` values are not a physical calibration. Do not
hard-code those values as lux, lamp wattage, or voltage.

## Next permitted work

A separate Phase 09 Plan may inventory and statically qualify the real
TurtleBot3 launch, rotating photoresistor, odometry/IMU, recording,
emergency-stop, and manual-termination path. Physical motion still requires
explicit authorization.

Use the primary fixed layout as the first commissioning target. If a second
formal simulation layout is required, first create a fresh evaluator-only
Plan that predeclares aggregate-field basin association. Do not widen the
secondary `0.60 m` gate retroactively or expose evaluator geometry to the
controller.

## Git boundary

The final report, this handoff, navigation updates, live-status closeout, and
Phase 08 checkpoint are committed as a bounded closeout. The post-commit
status receipt names the exact commit and clean worktree state.

## Current v8.11/v8.12 boundary

V8.11 corrected the evaluator-only shifted-basin association without passing
source geometry into the controller. Its secondary visible seed `19901` and
repeat seeds `19911..19915` passed `1/1 + 5/5`, including five direct escapes,
one assisted escape, exact one-fill cardinality, strict raw-cost ranking, final
global proximity, complete recording, final zero, cleanup, and `54/54` plots.

That is now the qualified second fixed-layout simulation demonstration:

```text
start:        (0.0, 0.0)
first lamp:   (0.5740251485, 1.3858192988)
second lamp:  (3.5, 3.5)
inputs:       400 / 1600 simulator-relative
environment:  obstacle-free open field
formal:       6/6
```

V8.11's first varied-matrix seed `19931` then failed before escape because no
recorded approach pose lay outside the data-derived fill exit radius. V8.12
added a default-off `interior_farthest` odometry-history fallback with a
`0.50 m` minimum displacement. No-Gazebo qualification passed the full
`1012 passed, 3 skipped` functional suite, retained-history replay, historical
scenario/V6/world hashes, isolated install, graph construction, and installed
scenario parity.

The v8.12 visible seed `20001` passed `14/14`. It exercised an
`interior_farthest` anchor, assisted local recovery, strict candidate-two raw
ranking, and final global proximity at `0.116707 m`; all nine plots are
retained.

The one authorized v8.12 matrix invocation stopped on seed `20031`. That run
completed the full scientific path:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
-> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

It created one fill, used an `interior_farthest` anchor at `1.318198 m`,
cleared the `1.366771 m` fill exit radius, strictly ranked candidate two by
`2.518884`, and stopped `0.127721 m` from the global. Recording, final zero,
readiness false, SQLite integrity, cleanup, one-time analysis, and all nine
plots completed.

It remains a formal `13/14` failure because the direct exit curved
`42.6452 degrees` from its initial anchor direction while the frozen evaluator
allowed at most `36.8699 degrees` (`0.735563 < 0.80`). This is one formal
evidence-contract failure after successful behavior. Do not relabel it as a
formal pass or weaken the fixed gate.

The serial suite stopped as required:

```text
seed 20031:       dispatched once / formal fail / behavior complete / no retry
seeds 20032-34:   not dispatched
v8.12 matrix:     population gate not met
```

Reports:

- [v8.11 secondary visible](../validation/phase_08_8_m8_3_v8_11_secondary_visible_probe.md)
- [v8.11 secondary repeats](../validation/phase_08_8_m8_3_v8_11_secondary_repeats.md)
- [v8.11 matrix failure](../validation/phase_08_8_m8_4_v8_11_broad_matrix.md)
- [v8.12 no-Gazebo qualification](../validation/phase_08_8_m8_7_v8_12_no_gazebo_qualification.md)
- [v8.12 visible pass](../validation/phase_08_8_m8_8_v8_12_visible_probe.md)
- [v8.12 terminal matrix result](../validation/phase_08_8_m8_9_v8_12_broad_matrix.md)

## Current usable simulation demonstrations

Use only these exact repeatable populations for a confident claim:

```text
primary:
  local (1.0606601718, 1.0606601718)
  global (3.5, 3.5)
  400 / 1600 simulator-relative
  11/11 formal

secondary:
  local (0.5740251485, 1.3858192988)
  global (3.5, 3.5)
  400 / 1600 simulator-relative
  6/6 formal under evaluator-only schema-v14 topology evidence
```

Both assume start `(0.0, 0.0)`, local-first encounter, known source count two,
an obstacle-free open field, no controller access to light positions or roles,
and evaluator-only coordinate stopping. The simulator-relative inputs are not
a physical calibration.

Do not claim arbitrary position/intensity robustness. The planned `1:5` and
alternate-placement v8.12 cases were not run. Three-light Gazebo behavior,
unknown source count, global-first return-to-best behavior, walls, obstacles,
disturbances, and physical transfer remain unproven.

## Current physical and next-phase rule

There is no physical coordinate-based arrival stop. A future physical run
continues until the operator judges the robot sufficiently close and presses
`Ctrl+C`; final readiness false, zero command, recording finalization, and
scoped cleanup remain mandatory.

Phase 08.8 authorized no physical motion. V8.12 is final, and no v8.13 is
planned or authorized. The next action is a separate Phase 09 Plan for static
physical-interface and calibration qualification, followed by separate
explicit authorization before any physical motion.
