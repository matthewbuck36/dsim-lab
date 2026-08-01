You are implementing the approved Phase 09 Plan in the local physical
TurtleBot3 source snapshot. This implementation is strictly no-hardware and
must not mount, write to, launch, or command the physical Raspberry Pi or
TurtleBot3.

## Recover the durable boundary

Read completely:

- `AGENTS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`;
- `docs/codex/gesc_gaussian/plans/phase_09_plan.md`;
- `docs/codex/gesc_gaussian/status/phase_09_status.md`, if already present;
- `docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md`;
- `docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md`;
- `docs/codex/gesc_gaussian/status/phase_08_status.md`; and
- `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.

Inspect current code, Git state, the saved Plan, and the physical snapshot
before editing. The saved Plan is authoritative unless current evidence
requires a bounded, documented correction under the Level A/B/C policy.

Initialize the live status without overwriting a nonempty file, then run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 09
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 implement
```

The historical absence of a broad `simulation_ready=true` tag does not block
the approved selected-scenario snapshot implementation. It also does not
become a passing Phase 08 claim. Missing Plan/status context, an interface or
ownership conflict, loss of simulation/physical parity, or any attempt to
command hardware remains a stop.

## Exact edit and hardware boundary

Implement physical source changes only under:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

Keep Phase 09 Plan, status, validation, manifests, checkpoints, and handoff in
`/home/mattb/dsim-lab/docs/codex/gesc_gaussian/`.

The snapshot is not Git-controlled. Before its first edit:

1. create the approved recoverable source backup;
2. record an exact source inventory and SHA-256 manifest;
3. prove `/home/mattb/tb3-pi` is not mounted or accessed; and
4. record the baseline paths and hashes in the live Phase 09 status.

Do not edit `/home/mattb/tb3-pi`, use SSH/SSHFS, command motors, invoke a
physical launch, or perform a physical sensor test. Do not copy generated
`build`, `install`, `log`, cache, editor, Git-metadata, or runtime content.

## Required implementation contract

Integrate the current terminal, cumulative Phase 08 counted-source GESC +
adaptive Gaussian behavior through v8.12 into the existing physical owners.
Reuse or extend the snapshot's `ros_esc`, `ros_esc_interfaces`, and
`turtlebot3_vehicle_nodes`; do not create a parallel algorithm or duplicate
controller/recorder stack.

The TurtleBot3 is shared laboratory equipment. Preserve every pre-existing ESC
Bash run file, historical launch, and legacy configuration byte-for-byte
against the sealed baseline. Do not extend the historical
`light_gesc_gaussian_fill_experiment.launch.xml` in place. Put the selected
Phase 09 orchestration in a new dedicated launch and point only the new managed
Phase 09 wrapper and physical recorder target contract at it. A change that
breaks or silently reroutes any legacy wrapper is a hard compatibility stop.

### Cumulative v8.12 source-selection rule

Do not cherry-pick, blend, or independently merge v8.10, v8.11, and v8.12.
They are successive experiment/evidence versions in one cumulative Git
history. V8.10 retained the counted-candidate profile; v8.11 changed the
simulation evaluator/schema without changing core runtime owners; and v8.12
added the `interior_farthest` odometry-history fallback to the three existing
supervisor files. The shared core runtime did not change between qualifying
v8.12 commit `0263f1c` and Phase 08 terminal commit `c04c222`.

Port the current terminal shared runtime files exactly and prove their
source-to-snapshot hashes. Do not copy the v8.11 simulation evaluator or its
source geometry into physical control. The selected physical wrapper must
explicitly set:

```text
open_field_escape_interior_anchor_fallback_enabled=True
open_field_escape_interior_anchor_min_displacement_m=0.50
```

Keep the shared node/launch default `False` for legacy and nonselected paths;
the original `outside_radius` anchor retains priority. Preserve the historical
v8.12 `13/14` formal result, while implementing the complete scientific
behavior the user accepted. Stop if the saved Plan or implementation diff
selects an older runtime boundary, disables the fallback in the selected
wrapper, or introduces evaluator geometry into control.

Preserve:

- rotating photoresistor raw minimization cost and timestamp semantics;
- wheel odometry and permitted IMU inputs;
- known source count and counted-candidate raw-cost ranking;
- adaptive typed Gaussian fill lifecycle and exact one-fill behavior for two
  sources;
- temporary affine/approach-continuity assistance, including the v8.12
  interior-anchor fallback explicitly enabled by the selected physical wrapper
  while remaining default-off for legacy/nonselected paths, plus direct and
  assisted escape paths;
- persistent Gaussian memory after affine assistance is cleared;
- legacy profile selection plus byte-identical legacy Bash/launch/config entry
  points;
- canonical topics, public message semantics, cost sign/units, and the sole
  physical `/cmd_vel` owner;
- Phase 05 recording/final-zero contract; and
- simulation/physical algorithm parity.

Do not add GPS, Vicon, source position/role/intensity, room dimensions, global
coordinates, SLAM, route planning, autonomous wall avoidance, or a physical
coordinate-distance stop to control. Vicon files may remain for external
evaluation, but no Vicon value may affect control or stopping.

Physical arrival remains operator `Ctrl+C`. The selected field assumption is
open, obstacle-free, and human-managed. A future physical run must still prove
stale-input stop, readiness false, final-zero ordering, recorder finalization,
emergency stop, and scoped cleanup before motion is authorized.

## Execution discipline

Work one Plan milestone at a time. Before moving on:

- run the milestone's focused static/offline tests;
- record exact commands, outcomes, skips, and retained paths in
  `docs/codex/gesc_gaussian/status/phase_09_status.md`;
- inspect snapshot and repository diffs for unintended scope;
- run `bash -n` for every Bash entry point, resolve every wrapper launch and
  supplied argument, run installed `--show-args` for every unique referenced
  launch, and verify all pre-existing wrapper/launch/config hashes;
- update the before/after snapshot manifest and recoverable patch evidence;
- run `checkpoint_phase.sh 09` at material boundaries; and
- create only bounded, authorized `dsim-lab` commits for durable Phase 09
  documentation/manifests. Never imply that external snapshot files were
  captured by Git unless a retained patch or manifest proves them.

Use bounded host-side checks only: static imports where dependencies exist,
unit tests, syntax/YAML/XML parsing, interface comparison, launch construction
without hardware, source-package builds that are compatible with the host,
and recorder/configuration validation. Report Pi-only, hardware-only, serial,
GPIO, Arduino, motor, live-topic, emergency-stop, and physical-motion checks as
unexecuted—not passed.

Do not weaken acceptance or safety checks merely to make host qualification
green. Preserve every failed attempt and distinguish source integration,
static readiness, and physical readiness.

## Required closeout

Write:

```text
docs/codex/gesc_gaussian/handoffs/phase_09_handoff.md
```

Also retain the final snapshot inventory, before/after SHA-256 manifests,
reviewable source patch/diff, static validation report, future SSHFS transfer
manifest, Pi backup/rollback procedure, and exact hardware-deferred checklist.
The static report must include shared-lab legacy hash, entry-point, Bash syntax,
and wrapper-to-launch compatibility evidence.

Close Phase 09 snapshot implementation only when the declared static criteria
pass, every skip is explicit, the snapshot is recoverable, runtime is inactive,
the live status and checkpoint are current, and Git plus external snapshot
state are reported. Do not declare physical readiness or run the robot.

Recommended bounded commit message:

```text
phase 09: integrate physical snapshot workflow
```
