# START HERE — DSIM GESC + Robust Gaussian Implementation Package

This package is designed to be copied into the root of the existing `dsim-lab` Git repository and used with the Codex extension in VS Code.

## Current entry point — Phase 10 V1 closeout

Start with the LaTeX-typeset
[`FINAL_PROJECT_REPORT_V1.pdf`](../docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf)
for the complete V1 architecture, mathematics, interfaces, parameters,
chronology, results, limitations, and reproducibility record. The
[`FINAL_PROJECT_REPORT_V1.tex`](../docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex)
source and [Markdown audit companion](../docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md)
are retained beside it. Its companion
[coverage matrix](../docs/codex/gesc_gaussian/validation/phase_10_report_coverage.tsv)
shows which implementation-package and phase artifacts were considered.

The terminal V1 evidence boundary is deliberately narrow: broad simulation
readiness and broad physical readiness failed. Selected simulation evidence is
v8.10 primary `11/11`, v8.11 secondary `6/6`, v8.12 visible `14/14`, and the
first varied v8.12 case `13/14`; the remaining three varied cases were withheld
without retry. The eighth physical run is the first retained two-basin
behavioral success, but it ended before a second convergence or `GOAL_HOLD`
and retained `61/62` completeness. Manual operator `Ctrl+C` remains the normal
physical stop; `GOAL_HOLD` is not a physical process terminator.

The dated Phase 08 and Phase 09 checkpoint sections below are preserved as
historical navigation and provenance. The final report, latest handoffs, and
live source supersede them where they describe an earlier "current" state.
Phase 10 authorizes no Gazebo rerun, hardware command, physical transfer, or
creation of `feature/gesc-gaussian-robustness-v2`.

## The intended outcome

Implement a backward-compatible **GESC + robust Gaussian local-minimum escape system** that:

1. Uses the existing GESC implementation as the baseline.
2. Keeps raw light-sensor data measured and logged continuously.
3. Separately switches the controller contributions from:
   - the raw sensor cost,
   - Gaussian repulsion,
   - the affine/directional term.
4. Detects an undesired local minimum.
5. Estimates the basin center and size from recent data without requiring many complete orbits.
6. Creates or enlarges one smooth fill for the entire basin instead of repeatedly creating narrow overlapping fills.
7. Temporarily disables raw-cost attraction while escaping.
8. Retains past fills so the robot does not return to known minima.
9. Uses a deterministic assisted-escape fallback when pure repulsion stalls.
10. Supports a selectable, simulation-tested bounded-indoor recenter strategy
    before resuming search; the exact strategy remains a provisional research
    policy rather than a fixed invariant.
11. Records every important input, output, parameter, event, command, and state with synchronized ROS timestamps.
12. Uses the same algorithm and logging interfaces in Gazebo and on the physical TurtleBot.
13. Does not proceed to new physical trials until the simulation acceptance gates are met.

Heavy-Ball ESC is outside the scope of this implementation.

---

## Where to put this package

Extract this folder into the repository root so the structure resembles:

```text
dsim-lab/
├── ros2_ws/
├── ...
└── DSIM_GESC_Gaussian_Codex_Implementation_Package/
```

Do not move individual prompt files into source packages. Keep this package intact as the implementation record.

---

## Git setup

From the repository root:

```bash
git status
git switch -c feature/gesc-gaussian-robustness-v1
```

Inspect a dirty working tree before editing. Preserve and work around
non-overlapping user changes; stop only when intended edits overlap or cannot
be preserved safely.

---

## How to use Codex

For every phase:

1. Inspect current code, tests, Git, the active Plan/status, retained evidence,
   and latest relevant dependency handoffs.
2. Run the phase's Plan context validator.
3. Create or amend the durable Plan at
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`; a manual verbatim chat
   export is not required.
4. Review the file-level Plan and remain on the same Git branch.
5. Initialize or resume
    `docs/codex/gesc_gaussian/status/phase_XX_status.md`; verify it against Git,
    then run the implementation preflight.
6. Implement milestone by milestone in the same or a new chat. Update live
   status continuously and create a checkpoint at material evidence, expensive
   empirical, or independently reviewable implementation boundaries.
7. Run the tests named in the Plan and write
    `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.
8. Close the live status and commit the coherent phase before beginning the
   next one.

Use the phases in numeric order. Do not skip Phase 00.

Treat each new chat and every post-compaction continuation as fresh context.
Experimental Codex memory may be useful, but `AGENTS.md`, the version-controlled
audit documents, saved phase plan, live phase status, implementation handoffs,
current repository state, and Git history are the source of truth.

For Phases 06-10, use these as the default historical summary:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

The bridge is the current cross-phase summary; the Phase 00 audit remains the
historical baseline. Read older audits and handoffs through targeted
dependency/conflict lookup rather than reloading all of them by default.

---

## First prompt

Open:

```text
prompts/00_repo_audit_PLAN.md
```

Paste its entire contents into Codex Plan mode.

Phase 00 is intentionally read-only. It forces Codex to discover the repository's real packages, topics, nodes, launch files, message types, tests, and naming conventions before any implementation is attempted.

The completed Phase 00 Plan has been saved at:

```text
docs/codex/gesc_gaussian/plans/phase_00_plan.md
```

The Phase 00 Implement chat must read and verify that file before creating the
audit documents.

## Current checkpoint after Phase 08.8

Phases 00-07.5 are implemented. Phase 08 is closed as a development and
diagnostic phase; its broad simulation-ready objective failed. The final
Phase 08.7 retained-success reproduction produced `13/17` formal and `14/17`
behavioral passes under evidence-selected two-light conditions, not an
unbiased acceptance denominator.

The separately approved Phase 08.8 counted-source iterations subsequently
qualified the primary fixed two-source layout at `11/11` formal passes and the
secondary fixed two-source layout at `6/6` formal passes. V8.12 qualified the
default-off interior approach-anchor fallback and passed its visible probe.
Its first broad-matrix case completed the scientific local-recovery-to-global
behavior but failed one frozen direct-exit alignment predicate at `13/14`, so
the remaining three cases did not run. V8.12 is terminally closed; there is no
v8.13 and no broad simulation-ready claim. Read first:

```text
docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md
docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md
docs/codex/gesc_gaussian/validation/phase_08_final_report.md
docs/codex/gesc_gaussian/handoffs/phase_08_final_handoff.md
docs/codex/gesc_gaussian/status/phase_08_status.md
docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt
```

The user accepts the selected primary and secondary evidence as sufficient for
Phase 09 physical-interface integration. The next work is a separately
reviewed, no-hardware Plan and static implementation under
`/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src`, centered first on the
known-good two-light `1:4` response condition. A historical broad
`simulation_ready=true` tag is not required for that snapshot-only work.

Planning or snapshot implementation alone does not authorize Codex to start a
live Pi graph or hardware motion. Do not resume or relabel historical Phase 08
evidence, infer arbitrary layout/intensity or three-light readiness, route
Vicon/GPS into the controller, or enable an automatic physical global-distance
stop. The current M8C procedure below separately defines the human-operated lab
run and requires no repository readiness tag or authorization file.

### Historical Phase 09 M8B checkpoint (superseded by M8C)

Phase 09 M0-M7.1 completed and statically qualified the source-only snapshot.
On 2026-08-01, under separate explicit user authorization, historical M8A
verified a scoped live-Pi rollback backup and transferred the then-reviewed 51
source/configuration paths. M8B now adds the selected-only Vicon evaluation
evidence path, stationary no-actuation preflight/approval contract, strict
calibration evidence, and single-entry operator workflow. The M8B snapshot
implementation, host-side isolated build/regression qualification, and reviewed
real-Pi source sync passed. The verified rollback backup is
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`; snapshot and Pi
match `345/345` regular-file hashes and `432/432` inventory entries. This is
source parity, not an on-Pi build or hardware result.

Wheel/IMU-backed `/odom` is the sole algorithm pose. Vicon is required for an
accepted selected two-source run only as evaluation evidence on
`/gesc_gaussian/evaluation/vicon_pose` and
`/gesc_gaussian/evaluation/vicon_status`; it can gate evidence completeness but
cannot affect controller, fill, escape, ranking, or stopping calculations.
Legacy ESC wrappers, launches, configurations, Vicon paths, and rotating-frame
paths remain isolated from the selected Phase 09 owners.

No direct on-Pi command, build, launch, serial/GPIO access, live Vicon identity,
calibration, actuator command, emergency-stop rehearsal, or motion has run.
Resume from the current Phase 09 Plan/status/handoff and
`docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md`. Follow
the exact next sequence: separate on-Pi build/installed-static gate; create
mutable calibration and primary/secondary metadata copies under
`${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`; uncalibrated/readiness-
false/no-actuation `--stationary-preflight`; review and
`--approve-stationary RUN_DIR --reviewer NAME` against the same metadata bytes;
independent emergency-stop then safe nontranslating/final-zero rehearsal;
calibration; `--check-only`; then the bare
`gesc_gaussian_two_source_voltage.bash` with assigned operator/observer and
typed `RUN`. The bare wrapper is the eventual normal primary entry point, not a
currently authorized physical command.

### Current Phase 09 M8C checkpoint — 2026-08-03

<!-- MBuck 2026-08-03: Current physical operator path follows the lab SOP and one bare selected wrapper. -->

The attached `DSIM - TurtleBot3 Vicon Setup.pdf` is the controlling lab setup
procedure. On Windows, run the unchanged `vicon-tracker-server.py`; on the Pi,
run bare `gesc_gaussian_two_source_voltage.bash` from the selected
`voltage_cost_values` Bash directory. The wrapper owns the selected
three-package build/source step, starts `pigpiod` only if absent, launches the
managed recorder/graph, prints the run directory, and shows live diagnostics.

The current operator path has no separate build, site configuration,
calibration approval, stationary preflight, `--check-only`, typed `RUN`, Vicon
subject/segment entry, server-file SHA-256, handoff approval, or
`PHYSICAL READY` tag. Wheel/IMU-backed `/odom` remains the sole algorithm pose;
legacy `7f` Vicon data is passive evaluation-only
`/gesc_gaussian/evaluation/vicon_odom`. Vicon absence must be visible and makes
evaluation incomplete, but never gates motion.

Pressing `Ctrl+C` is the normal experiment stop. The recorder/wrapper must retain
readiness-false and final-zero evidence through a stable bag dwell, finalize and
validate the run, and print its retained directory. M8C source implementation,
host validation, snapshot reseal, and reviewed Pi transfer passed with exact
`342/342` file-hash and `430/430` inventory parity. The current rollback is
`/home/mattb/tb3-pi/phase09_backups/20260804T011049Z_m8c_pre_simplification`.
Codex did not perform an on-Pi build or live hardware run; the next step is the
ordinary human-operated lab SOP and bare wrapper, with no additional repository
gate.

### Current Phase 09 M8D recording amendment — 2026-08-03

<!-- MBuck 2026-08-03: Add familiar post-bag CSVs without adding a recorder or changing any legacy experiment path. -->

For the selected wrapper, the runtime data directory is
`${HOME}/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/<UTC-date>/<run-id>/`.
The terminal diagnostics described above remain live while the sole managed
sqlite3 rosbag records. The familiar headerless CSVs are not live streams: after
a clean `Ctrl+C` shutdown finalizes the authoritative bag, the existing
`record_run` finalizer invokes their atomic, idempotent export as part of final
validation. An incomplete export makes that validation fail.

The post-bag export writes these familiar files into the same run directory:

- `encoder.csv`: `[timestamp, angle]`;
- `cost_value.csv`: `[timestamp, augmented cost]` from `/cost_modified`;
- `filter_value.csv`: `[timestamp, two filter values]`;
- `control_value.csv`: `[timestamp, six command-array values]`; and
- `odometry.csv`: `[timestamp, x, y, z, qw, qx, qy, qz]`, retaining the legacy
  Vicon/evaluation plotting semantics.

It also writes `raw_cost_value.csv` as `[timestamp, raw_cost]`, where
`raw_cost=-voltage`, and `algorithm_odometry.csv` as
`[timestamp, x, y, z, qw, qx, qy, qz]` from the algorithm's `/odom` input.
`legacy_csv_manifest.json` records each mapping, row count, file hash, and any
export error. The existing `extract_test_data` column reader can consume these
files directly. Its old top-level `Test_*` browser does not automatically find
the nested run directories, and no synthetic `comments.txt` is created.

The rosbag remains the sole recorder and source of truth; M8D adds no second
recorder or live CSV collector. This selected-only post-bag compatibility
amendment supersedes the earlier no-CSV-equivalence statement only for these
exports. Every legacy wrapper, launch, node, and experiment path remains
unchanged, and no safety or hardware-readiness claim is broadened.

### Current Phase 09 M8E Pi runtime checkpoint — 2026-08-04

<!-- MBuck 2026-08-04: Retain the real-Pi clean-build/check-only evidence and selected no-lidar device separation. -->

The first bare selected attempt is retained as failed commissioning evidence.
It never reached readiness or motion because the wrapper omitted the Pi's
established `~/turtlebot3_ws` underlay and selected installed Python was stale.
M8E repaired that runtime path without changing any `ros_esc` algorithm source
or historical ESC launch/wrapper.

The wrapper now restores the source underlay, performs a selected three-package
`--symlink-install` build, constructs both selected launches, verifies
installed-source parity, and checks distinct photoresistor `/dev/ttyUSB0` and
OpenCR `/dev/ttyACM0`. A new selected-only base helper starts OpenCR plus the
standard state publisher without LDS-02 because the open-field algorithm has
no `/scan` consumer. The historical full vehicle bringup remains unchanged.
The exact missing historical sound-profile module was also restored so clean
builds preserve that legacy entry point.

The human-operated Pi `--check-only` passed all three packages in `1 min 39 s`,
installed parity (`ros_esc=63`, `turtlebot3_vehicle_nodes=21`), device
separation, and launch construction. It did not start pigpio, open serial,
connect Vicon, create a ROS graph, record, actuate, or move the robot. Following
the earlier power cycle, the mounted source still matches the snapshot
`345/345` files and `433/433` inventory entries, with all three build return
codes zero; the final strengthened check-only was captured after the Pi was
back online.

Read the authoritative validation at
`docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md`. The Pi has
no RTC or reachable internet NTP on DSIMOVERWATCH, so preserve Nick's literal
wall-clock `sudo date -s` procedure after every reboot and before starting ROS.
Do not copy a Unix epoch or timezone/offset. The accepted initialization passed
for the current powered session at `2026-08-04T17:54:22+00:00`; the earlier
August 5 epoch-copy attempt started no run and is superseded. Follow the M8C lab
SOP and invoke the bare wrapper; the successful check-only is not a repeated
gate.

---

## Non-negotiable rules

- Reuse and extend existing nodes rather than creating parallel duplicate systems.
- Preserve legacy behavior behind an explicit legacy profile or feature flag.
- Do not silently change the sign or units of the existing cost.
- Do not stop measuring the sensor when its controller weight is zero.
- Do not rely on terminal text as the experimental record.
- Do not let Gazebo and physical runs use different algorithm logic.
- Do not hard-code topic names that already have a repository convention.
- Do not launch the physical robot during Phases 00–08.
- Stop safely and publish zero velocity on exceptions, invalid data, or timeouts.

## Contradiction policy

- **Level A — hard contradiction:** stop before further edits when cost sign or
  units, the research objective, public compatibility, dependency availability,
  physical safety/authorization, preservation of unrelated changes, shared
  simulation/physical algorithm behavior, or the approved architecture would
  be violated, or when major redesign/scope expansion is required.
- **Level B — bounded implementation correction:** continue only for a local,
  testable runtime or implementation correction that preserves the research
  objective and public architecture and does not weaken acceptance criteria.
  The handoff must record the original assumption, observed contradiction,
  exact correction, files, tests, and scope justification.
- **Level C — acceptance or research failure:** finish the current declared
  stage, obey predeclared early-stop gates before later expensive stages,
  report the failed gate honestly, preserve failed runs, and name the smallest
  justified next step. Do not relabel failure as incomplete work or weaken a
  threshold without a versioned justification.

## Test reporting contract

Every Implement handoff reports the global build/test result and baseline
trend, focused changed-package tests, tests added by the phase,
`git diff --check`, modified-Python syntax/import checks, focused lint/style
checks when global lint has inherited debt, and exact skipped or unexecuted
tests with reasons. A phase is not described as fully tested when a required
test was not executable.

---

## Addendum

Reuse or extend an existing node when that node already owns the responsibility. A new node may be created only when
the repository audit shows that no existing node is an appropriate owner, the feature has a distinct ROS responsibility
and interface, and the new node follows the repository’s established architecture. Do not create duplicate,
simulation-specific, physical-specific, or replacement implementations of existing algorithm behavior.
