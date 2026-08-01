You are planning Phase 09 inside the existing `dsim-lab` Git repository.
Phase 09 will integrate the current terminal, cumulative Phase 08 GESC +
Gaussian algorithm through v8.12 into the local source-only snapshot of the
physical TurtleBot3. Planning and later snapshot implementation do not
authorize physical motion.

## Read before doing anything

Read completely:

- `AGENTS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`;
- `docs/codex/gesc_gaussian/implementation_sequence.md`;
- `docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md`;
- `docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md`;
- `docs/codex/gesc_gaussian/status/phase_08_status.md`; and
- `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.

Reconstruct the current state from code, Git, the final reports, and retained
interfaces. Do not rely on chat memory or reopen a failed Phase 08 version.
The final Phase 08 closeout commits are `9335da2` and `c04c222`.

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 plan
```

If required durable context is missing, stop and report it. The absence of the
historical broad `simulation_ready=true` tag is not a blocker for this
selected-scenario, no-hardware Plan. Do not alter or relabel the historical
Phase 08 result.

## Current user authority and evidence boundary

The user accepts the demonstrated simulation evidence as sufficient for a few
selected physical scenarios:

- v8.10 primary fixed two-light layout: `11/11` formal passes;
- v8.11 secondary fixed two-light layout: `6/6` formal passes; and
- v8.12 interior-anchor visible probe: `1/1` formal pass.

The v8.12 matrix remains formally failed on its first case, despite complete
local-to-global scientific behavior. Do not claim arbitrary layout/intensity,
three-light, wall, obstacle, or broad simulation readiness.

## Cumulative v8.12 algorithm-selection rule

Do not cherry-pick, blend, or independently merge v8.10, v8.11, and v8.12.
They are successive experiment/evidence versions in one cumulative Git
history:

- v8.10 retained the counted-candidate controller profile and corrected the
  scenario runner/recorder working-directory boundary;
- v8.11 changed the simulation evaluator/schema for shifted aggregate-basin
  association but did not change the controller, filter, Gaussian-fill,
  modified-cost, convergence-detector, or supervisor runtime owners; and
- v8.12 added the opt-in `interior_farthest` odometry-history fallback to the
  three existing supervisor files.

The shared core runtime did not change between the qualifying v8.12 source
commit `0263f1c` and Phase 08 terminal commit `c04c222`. Plan one exact port of
the current terminal shared runtime files. The selected physical wrapper must
explicitly enable:

```text
open_field_escape_interior_anchor_fallback_enabled=True
open_field_escape_interior_anchor_min_displacement_m=0.50
```

Keep the shared node/launch default `False` for legacy and nonselected paths.
The original `outside_radius` anchor retains priority. Preserve the historical
v8.12 `13/14` formal result without treating its completed scientific behavior
as excluded from the user-selected physical algorithm. V8.11 evaluator
topology remains recorder/evaluator metadata and must never enter control.

This authority permits Phase 09 planning and, after an approved Plan,
snapshot-only implementation and static qualification. It does not authorize
mounting or writing to the live Pi, commanding motors, or running physical
hardware. Later physical motion requires a separate explicit user
authorization plus live calibration, emergency-stop, final-zero, recording,
and operator-readiness checks.

### Shared-laboratory compatibility authority

The TurtleBot3 is shared. Plan strict nonregression for every pre-existing ESC
method and its Bash run file. The historical
`light_gesc_gaussian_fill_experiment.launch.xml`, all pre-existing Bash
wrappers, and their legacy configurations must remain byte-identical to the
sealed snapshot baseline. Put the selected Phase 09 graph in a new dedicated
launch file and point only a new managed Phase 09 wrapper at it. Plan static
`bash -n`, wrapper-to-launch argument resolution, installed `--show-args`,
entry-point preservation, and baseline hash checks for every legacy wrapper.

## Exact physical snapshot boundary

The physical Pi-home snapshot is:

```text
/home/mattb/physical_TB3_files_snapshot/pi
```

The physical ROS source target is:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

It contains the existing `ros_esc`, `ros_esc_interfaces`, and
`turtlebot3_vehicle_nodes` packages. The snapshot is not Git-controlled.
Plan a recoverable pre-edit backup, source manifest, and SHA-256 baseline
before any later implementation edit.

Do not mount, read from, or write to `/home/mattb/tb3-pi` in this Phase 09
Plan or snapshot implementation. That path is reserved for a later,
separately authorized SSHFS transfer after the robot is available.

## Controller and experiment constraints

The physical controller may consume only:

- the rotating photoresistor and derived raw minimization cost;
- wheel odometry;
- IMU data already required by the physical stack;
- active typed Gaussian fills; and
- the configured total source count.

It may not consume GPS, Vicon pose, source coordinates, source roles, declared
lamp intensities, room dimensions, a global start position, or evaluator
proximity. Vicon may be recorded later for external evaluation only; it must
not enter control, classification, fill design, escape direction, or stopping.

Preserve the Phase 08 algorithm contract:

- every confirmed extremum begins as an unknown candidate;
- raw complete-rotation cost owns candidate comparison;
- the adaptive Gaussian is persistent visited-basin memory;
- affine/approach direction is temporary local-recovery assistance;
- direct and supervisor-assisted escape remain supported;
- known source count two permits exactly one local fill before terminal
  ranking;
- the physical arrival decision is manual operator `Ctrl+C`;
- shutdown must publish readiness false and final zero before recording and
  scoped cleanup finish; and
- the initial field is open, obstacle-free, and operator-managed, with no
  autonomous wall or obstacle-avoidance claim.

## Planning rules

1. Do not edit source code in this Plan task.
2. Do not run or command physical hardware.
3. Preserve simulation/physical algorithm parity; only adapters, launch,
   calibration, and physical configuration may differ.
4. Reuse existing owners. Do not create a second controller, supervisor,
   recorder, validator, or message owner. Isolate orchestration in a dedicated
   Phase 09 launch without editing the historical launch.
5. Preserve every legacy Bash entry point/launch/configuration, legacy
   behavior, cost sign/units, canonical topics, message semantics, and the
   existing physical `/cmd_vel` owner.
6. Do not introduce Heavy-Ball ESC, SLAM, route planning, or a coordinate-based
   physical global stop.
7. Inspect the snapshot and current `dsim-lab` source before naming exact
   files, topics, interfaces, or dependencies.
8. Apply the Level A/B/C policy. Missing motion authority is a hard stop only
   for physical motion, not for safe Plan work or static snapshot integration.

## Required Plan content

Plan one reviewable milestone at a time, including:

1. snapshot baseline, backup, manifest, and recovery procedure;
2. current `dsim-lab` versus snapshot package/interface/launch audit;
3. exact current terminal cumulative v8.12 algorithm-source integration,
   without version cherry-picking or a simulation/physical fork;
4. photoresistor, odometry, IMU, command, stop, and readiness adapters;
5. a dedicated Phase 09 launch/configuration with conservative inactive
   defaults and byte-identical historical launches/wrappers;
6. source-response calibration and the two selected scenario definitions;
7. Phase 05 recorder/validator reuse and run metadata;
8. manual `Ctrl+C`, emergency stop, stale-input, and final-zero behavior;
9. host-side static tests, syntax/interface checks, launch construction, and
   build checks that are possible without the Pi;
10. explicit hardware-required checks that must remain unexecuted;
11. later SSHFS read-only diff, Pi backup, scoped source transfer, on-Pi build,
    and rollback procedure; and
12. exact stop conditions, checkpoints, commits, and handoff evidence.

Do not plan a blind whole-home mirror. The later transfer must use a reviewed
source/configuration manifest and exclude generated `build`, `install`, `log`,
cache, editor, Git-metadata, and runtime paths.

## Required durable artifact

Write one self-contained Plan suitable for review at:

```text
docs/codex/gesc_gaussian/plans/phase_09_plan.md
```

It must include the objective and nonclaims, repository and snapshot findings,
exact files to modify/create, ownership/interface effects, parameter defaults,
compatibility strategy, milestone sequence, tests and commands, checkpoint
boundaries, stop conditions, risks, hardware-deferred checks, SSHFS transfer
boundary, and assumptions requiring implementation-time verification.

End after the Plan, context validation result, Git state, and a clear statement
that no snapshot source, live Pi file, or physical process was changed.
