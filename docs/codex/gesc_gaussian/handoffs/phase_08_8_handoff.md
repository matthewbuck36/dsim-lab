# Phase 08.8 Handoff

## Terminal disposition

**PHASE 08.8 CLOSED / PRIMARY FIXED LAYOUT `11/11` FORMAL PASS /
SECONDARY SCIENTIFIC PASS BUT FORMAL EVALUATOR FAIL / SECONDARY REPEATS
AND BROADER MATRIX NOT RUN / NO PHYSICAL MOTION.**

Read first:

- [Phase 08.8 final report](../validation/phase_08_8_final_report.md)
- [Phase 08.8 Plan](../plans/phase_08_8_plan.md)
- [Phase 08 live status](../status/phase_08_status.md)

The earlier
[whole-Phase-08 final report](../validation/phase_08_final_report.md) remains
the authoritative history through Phase 08.7. Phase 08.8 is an additive,
separately versioned development iteration and does not relabel the earlier
broad simulation-ready failure.

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
