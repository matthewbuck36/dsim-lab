# Phase 09 Live Status

Last verified: `2026-08-01T03:49:09+00:00`
Status: `COMPLETE — SNAPSHOT STATIC INTEGRATION PASS; HARDWARE DEFERRED`

## Objective

Integrate the current terminal cumulative Phase 08 runtime through v8.12 into
the local physical TurtleBot3 source snapshot, preserve shared algorithm
parity and legacy selection, and statically qualify the selected physical
wrapper without accessing the live Pi or running hardware. The selected
wrapper enables the v8.12 interior-anchor fallback at `0.50 m`; shared legacy
and nonselected defaults remain disabled.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v1`
- HEAD: `c04c222dfeac525197bf0542cbde64f1421dc664`
- Working tree at start: intentionally dirty with nine pre-existing modified
  implementation-package files and the approved Phase 09 Plan untracked; no
  overlap with snapshot source edits. The generated Phase 09 status and M0
  validation artifacts are now additional untracked evidence.
- Plan: `docs/codex/gesc_gaussian/plans/phase_09_plan.md`
- Snapshot source:
  `/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src`
- Snapshot baseline: 306 regular files, 389 inventory entries, zero symlinks,
  zero nested `.git` directories, three packages (`ros_esc`,
  `ros_esc_interfaces`, `turtlebot3_vehicle_nodes`).
- Reserved live-Pi mount: absent; matching ROS/Gazebo/SSHFS/serial/physical
  processes: none.
- Implement context validator: PASS.
- M0 checkpoint:
  `docs/codex/gesc_gaussian/checkpoints/phase_09_checkpoint.txt`.

## Completed milestones

- Durable context recovery, current Git/snapshot inspection, status
  initialization, and `validate_phase_context.sh 09 implement`: PASS.
- M0 recoverable archive, exact before inventory/hash manifest, safe-path and
  gzip checks, same-permissions extraction proof, and source-stability
  comparison: PASS.
- M1 classified 52 planned paths. The frozen future transfer manifest has 51
  unique file paths; `config_parsing.py` is already byte-identical and remains
  excluded from transfer. All declared dsim sources exist and every declared
  new path is absent from the baseline.
- M1 owner audit found one selected source-cost owner (physical
  photoresistor), one modified-cost/filter/fill/supervisor/controller chain,
  one `/cmd_vel` owner in `controller_node`, and the existing Phase 05
  readiness/recorder/validator owners. The old physical launch currently
  starts a Vicon relay and legacy CSV collector; M3 must remove both from the
  selected path without changing their legacy files.
- M2 ported six typed messages, interface packaging, and all 18 declared
  cumulative v8.12 shared runtime files. All 27 shared/interface/config paths
  in `test_phase09_shared_parity.py` match current `dsim-lab` byte-for-byte.
- M2 added only physical package entry points/dependencies and the Phase 05
  recorder base; it did not copy the scenario runner, Gazebo dependencies,
  analyzer, worlds, or evaluator geometry.
- M2 isolated two-package build: PASS. Shared-owner focused tests: `300
  passed`; compatible observability subset: `13 passed, 2 deselected`;
  unchanged repository legacy regression: `34 passed`.
- Current snapshot delta is 35 declared files, zero paths outside the frozen
  transfer manifest, and zero generated roots.
- M3 extended the existing photoresistor owner with exact finite protocol
  parsing, preserved `raw_cost=-V`, bounded serial shutdown, stable-device and
  calibration gating, and dual legacy/typed physical publication. The
  adapter tests report `15 passed`.
- M3 extended the existing physical launch in place. The robust path uses
  `/odom`, has one controller `/cmd_vel` owner, starts neither the Vicon relay
  nor legacy CSV owner, contains no broad `pkill`, and keeps those legacy
  owners selectable only under `algorithm_profile=legacy`.
- M3 added the lower-speed `0.05 m/s`, `0.30 rad/s` controller configuration
  and managed selected wrapper. The wrapper passes metadata only to
  `record_run`, explicitly selects cumulative v8.12 including the `True`,
  `0.50 m` interior-anchor fallback, and refuses non-device-by-id or
  non-motion-ready calibration inputs. Adapter/launch tests report `22
  passed`; shared parity remains `28 passed`.
- Superseding M3 compatibility amendment: the user requires every pre-existing
  ESC Bash run file to remain working on the shared lab robot. The old launch
  must now be restored byte-for-byte, the selected graph moved to a new
  Phase 09-only launch, and all baseline wrappers/launch mappings statically
  audited before M5. The earlier in-place result above remains historical
  evidence, not the accepted final boundary.
- M3 compatibility amendment: PASS. The historical GESC+Gaussian launch, all
  26 pre-existing Bash entry points, all eight pre-existing launch files, and
  six legacy configurations match their M0 hashes. Phase 09 now has a separate
  selected launch; the old and new wrappers target only their respective
  launches. All 27 Bash files pass `bash -n`, all six referenced installed
  launch descriptions pass `--show-args`, all original console entry points
  remain present, the isolated three-package build passes, and the focused
  installed-overlay collection reports `69 passed`.
- M4 extended the sole Phase 05 manifest/recorder with physical operational
  heartbeats for typed source cost, `/odom`, `/imu`, filter output,
  timekeeper, robust algorithm state, and supervisor command. Each has a
  `0.50 s` freshness bound; a post-authorization fault now publishes
  readiness false, publishes stop true, and closes the run as failed.
- M4 resolved the recorded physical-time Level B gap through the existing
  recorder parameter-service preflight. It sets and immediately verifies
  `use_sim_time=False` on the seven byte-identical shared owners, then checks
  those values again in the full resolved-parameter snapshot before
  authorization. The shared sources remain unchanged.
- A focused validator test demonstrated that physical raw source data can be
  valid without an optional dimensionless score. The bounded
  `validate_run.py` amendment now requires finite single-channel `V` and
  `-V`, a valid physical timestamp/mode, and validates the score only when
  `source_score_valid=True`; simulation semantics are unchanged.
- M4 isolated three-package build: PASS. Snapshot physical tests: `36
  passed`. Snapshot M4 plus unchanged Phase 05 recording regressions: `84
  passed, 1 skipped`; the skip is the opt-in visible Gazebo smoke, which is
  outside this no-hardware milestone.
- M5 created an uncalibrated, measurement-empty calibration template; an exact
  cumulative terminal v8.12 audit profile; and primary/secondary evaluator-only
  metadata with the approved full-scale geometries. Both metadata files pass
  the existing recorder schema but retain `operator=UNASSIGNED`, calibration
  uncalibrated, every live-readiness field false, and no measured lamp setting.
- M5 extended the pure adapter preflight so the managed wrapper must validate
  calibration, operator assignment, measured response, hidden evaluator fields,
  manual stop policy, and all nine live-readiness flags before even checking
  the character device. Both shipped primary/secondary templates stop at this
  gate with exit `2`; no ROS target is started. M5 focused tests report `76
  passed` and all 27 Bash files still pass `bash -n`.
- M6 clean qualification: PASS under
  `/tmp/phase09_static_qual.vwhzo9`. Three packages build in `13.3 s`; Phase 09
  focused tests report `76 passed`; shared core reports `272 passed`;
  observability reports `13 passed, 2 deselected`; inherited recording reports
  `70 passed, 1 skipped`; repository legacy reports `34 passed`. All installed
  interfaces/entry points/assets and all six wrapper launch descriptions
  resolve. Both inert wrapper preflights stop with exit `2` before device or
  ROS target access.
- M6 snapshot-scope proof: exactly 51 paths differ from M0, exactly the 51-path
  transfer manifest; 33 are new and 18 modified. No baseline path is missing,
  no unexpected path exists, and no generated root/symlink/nested Git metadata
  exists. The backup rehash, no-live-mount, no-ROS/Gazebo/SSHFS-process, critical
  Python lint, authored-new-file whitespace, and repository diff gates pass.
- M7 sealed 339 after-file hashes and 425 after inventory entries. The
  reviewable Git-format patch contains all 51 transfer paths. Forward
  application to a fresh M0 extraction reproduces every after hash; applying
  the after inventory as the authoritative full-mode manifest reproduces the
  exact after inventory. Reverse application plus the before mode manifest
  reproduces every M0 hash and inventory entry. Temporary proof roots were
  removed; the real snapshot was not a patch target.
- M7 wrote the future read-only Pi comparison/scoped transfer/rollback
  procedure and the no-hardware handoff. M8 and M9 remain unexecuted. Phase 09
  prompt contracts now also require a dedicated Phase 09 launch and
  byte-identical legacy wrappers/launches/configurations so compaction or a
  fresh run cannot silently revert the shared-lab compatibility boundary.

## Current milestone

- Milestone: M7 — sealed no-hardware snapshot handoff.
- Implementation complete: `yes`
- Next acceptance criterion: none inside M0-M7. Any continuation begins at M8
  read-only live-Pi comparison under separate explicit user authorization.

## Current problem or blocker

- No Level A blocker is present.
- Level B amendment: the byte-identical shared controller, filter,
  modified-cost, PDE-history, convergence, and Gaussian owners set
  `use_sim_time=True` inside their constructors, overriding a launch/CLI
  `False` value. A host-only construction probe resolved `True`; changing the
  shared files would violate parity and adding a clock owner would violate the
  physical architecture. M4 therefore extended the existing sole
  `record_run` readiness owner to set and verify `use_sim_time=False` through
  each declared parameter service before readiness. Direct launch remains
  fail-closed through `recording_ready_required=True`.
- No unresolved M0-M7 acceptance blocker remains. The exploratory broad style
  diagnostic and all hardware-deferred checks remain explicit limitations, not
  hidden passes.

## Files currently relevant

- `docs/codex/gesc_gaussian/plans/phase_09_plan.md`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot_backup_receipt.md`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot_inventory_before.tsv`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot_before.sha256`
- `docs/codex/gesc_gaussian/validation/phase_09_shared_source_manifest.tsv`
- `docs/codex/gesc_gaussian/validation/phase_09_transfer_manifest.txt`
- `docs/codex/gesc_gaussian/validation/phase_09_legacy_compatibility.md`
- `docs/codex/gesc_gaussian/validation/phase_09_static_qualification.md`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot_inventory_after.tsv`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot_after.sha256`
- `docs/codex/gesc_gaussian/validation/phase_09_snapshot.patch`
- `docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_and_rollback.md`
- `docs/codex/gesc_gaussian/handoffs/phase_09_handoff.md`
- snapshot `config_files/gesc_gaussian/phase09_*.yaml` inert templates
- snapshot photoresistor owner, physical launch, physical package metadata,
  Phase 05 recorder/manifest/validator, and Phase 09 configuration/tests.

## Decisions and rationale

- Port one cumulative terminal v8.12 source boundary; do not blend three
  independent algorithms or copy evaluator/source geometry into control.
- Keep the shared interior-anchor default `False`; enable it only in the new
  selected physical wrapper with minimum displacement `0.50 m`.
- Preserve byte-identical shared runtime despite its inherited constructor
  time setting; enforce and snapshot physical time through the existing
  recorder parameter-service preflight.
- The Level B amendment is implemented, and the completed M6 isolated
  build/static gate plus final focused revalidation pass.
- M8 live-Pi transfer and M9 hardware commissioning remain deferred.
- The snapshot is non-Git state. Archive, manifests, patch, and reverse proof
  are mandatory recovery evidence; no snapshot file is described as committed.

## Validation checkpoints

- `validate_phase_context.sh 09 implement`: PASS; selected-scenario static
  integration only, no live-Pi or motion authority.
- M0 archive: PASS after exact extraction revalidation; archive SHA-256
  `8109c5c47789ce1d2bb2cf69ba82f6901b054193989c488fefcfb9cf507404b8`.
- Before inventory: 389 entries, SHA-256
  `4f7e130190441574a5663cc193be4fe1ac3b1a291e28fe98aaa3dee72ff25522`.
- Before regular-file manifest: 306 files, SHA-256
  `e38179695045e92cea03f023b6c7778d006c0df0a6c8f94ea1ce91c129999e17`.
- M1 shared-source manifest after the compatibility amendment: 52 rows,
  SHA-256
  `8e9446d438cfa4cb396540d028acd514b5e7eb57f2675f7d5c882e40e5f1798f`.
- M1 transfer manifest after the compatibility amendment: 51 unique paths,
  SHA-256
  `1db5c71cd3cf2b1071adb274b54cf6fa9259c4bdf7b2e9cd317e29739c87ccd1`.
- M2 isolated build root: `/tmp/phase09_m2_qual.4OWsT9`; two packages PASS.
- M2 shared snapshot tests: `300 passed in 7.05s`.
- M2 observability subset: `13 passed, 2 deselected in 0.55s`; the two
  simulation cost-source-owner tests are outside physical packaging.
- Repository legacy regression: `34 passed in 3.51s` at
  `/tmp/phase09_legacy_regression.3Jknxx`.
- M3 photoresistor and physical-launch tests: `22 passed in 0.07s`; shared
  parity recheck: `28 passed in 0.03s`.
- Historical pre-amendment M3 source hashes (superseded): launch
  `1774b4065183a9955c8f76efedf6855fb29ae8d45867c2fb45c61b291758c33f`,
  adapter
  `5ddfdf50afb7908936e4831bb95c0087e98426fa29d4d8fe6d7197f70734e6b1`,
  node
  `59e56389713522c075936edfb742e552765a8ff45b3a09258a1f122a18834ca7`,
  selected wrapper
  `60f98fbce5bbce65300641a1ec7a5b36dabc89e65cb84b5632bcba2876ca50cd`.
- M4 isolated build root: `/tmp/phase09_m4_build.PK4d69`; all three packages
  PASS in `13.4 s`.
- M4 built-overlay physical tests: `36 passed in 0.78s`.
- M4 focused plus inherited Phase 05 recording regressions: `84 passed, 1
  skipped in 2.42s`; skip reason: set
  `DSIM_RUN_GAZEBO_RECORDING_TEST=1` for the visible Gazebo smoke.
- Historical pre-compatibility M4 source hashes (recorder target later moved
  to the new launch): recorder
  `f42afec1c5168bc3c3507c74fb96794108bc1ca7a145e07c8824eaaae5b72d19`,
  manifest
  `a7deed1142d30f017eab4aa5fb89ab2113a94e9cdd810c405be8d46ef6c4710e`,
  validator
  `c4b33e3519940aec6942a4bff6767b390e25c4f387d018b7645e4ee99834c4ae`,
  focused test
  `5e30583ab67d72c176060bd29df7315de87ed262c44b719523cb91642b65e72b`.
- M3 shared-lab compatibility evidence:
  `docs/codex/gesc_gaussian/validation/phase_09_legacy_compatibility.md`.
  Old launch hash `542f26cc86f3ee06a8d6a6c8ee8a397fbadf2d8fc64aa39fcdf15eef8326bfaf`;
  new launch hash `a099bb8f4968861c4434e88e0cc7a140e7fe7ab7fae3cc628fb1dac15b6f630f`;
  selected wrapper hash after the M5 readiness gate
  `30be516fe6e7dea2f166de6a7d6667466f3918dec4fbfb918dd04a6875e5a677`;
  recorder target-contract hash
  `6c2da290c42324e21cd49b791e591e9f7f758bc6c9d0f4d8b3a8be96d62b7dea`.
- Compatibility build root: `/tmp/phase09_compat_build.zdGQKP`; three
  packages PASS in `12.6 s`. Focused installed-overlay tests: `69 passed in
  0.87 s`. All 27 Bash syntax checks, 40 baseline legacy-asset hashes, and six
  installed launch `--show-args` checks pass.
- M5 configuration hashes: calibration
  `cffa26462bff42157026f265aa2305b58b31ffdbca440dfd2af23d1f695bf78d`;
  selected profile
  `20f02c51660e838c5ab319b6bd9165a2b45da8b7864febb1235e4ccf76ce2752`;
  primary metadata
  `cb5dd258d5cb2cb37a077ef9e9f7ce9ca22af16b5e68fd7e0852c35b3af08029`;
  secondary metadata
  `af29921c669048ac5270c5df0b8ef39e88c09bccb8daaaaa3c6daa1eed742cc1`.
- M5 exact profile/geometry/schema/readiness tests plus shared parity and M4
  focused regressions: `76 passed in 0.95 s`. Recorder metadata load: primary
  and secondary PASS with `motion_ready=false`. Managed wrapper preflight:
  primary and secondary intentionally blocked with exit `2`; retained logs at
  `/tmp/phase09_compat_build.zdGQKP/inert_{primary,secondary}_preflight.log`.
- Snapshot generated build/install/log/cache roots after cleanup: zero.
- M6 report SHA-256 after final EOF diagnostic update
  `b8cafd5619343f864a5726329b0f5ad7f114042da9d57b935da5b4bcb7999144`;
  retained root `/tmp/phase09_static_qual.vwhzo9`.
- M6 exploratory broad style diagnostic: FAIL, retained and non-gating. The
  host plugin set reports 917 quote/docstring/import-order/79-column findings,
  predominantly 873 `Q000` quote preferences. Declared compilation, critical
  `E9,F63,F7,F82`, build, and test gates pass; the exploratory failure is not
  relabeled. See the static qualification report for exact logs and counts.
- M7 after inventory: 425 entries, SHA-256
  `ebb8534a8298092e813c54966e68069ec039a40e40d6cd5fb354633679257744`.
- M7 after regular-file manifest: 339 files, SHA-256
  `af470b19b3aae91518e45fd093dcbe6874f67cccdd4ca6cf26213659c865afe4`.
- M7 snapshot patch: 51 paths, 20,594 lines, SHA-256
  `8d56261f6857ff0f6f1bd83021202d32a3a13a0242fa7a9cb5011153b4393d1b`.
  Forward hashes/inventory and reverse hashes/inventory: PASS when paired with
  their authoritative full-mode inventory manifests.
- Future Pi transfer/rollback procedure SHA-256
  `bf9a447ff7c283ab38bd55fbefa06932e2745c900614a9f9b71ce9cf92b1d779`.
- Phase 09 handoff SHA-256
  `92031a21ec791cdc416619b86e2aceeb0afb707c54cf8f9b260ba73544dc0541`.
- Aligned Phase 09 Plan/Implement prompt hashes:
  `c30b0979087ad92927b359b7cf588d3e70bcfdff0bdcc385161dfda199a0cc38`
  and
  `bd28c730e487c5a04544a3a8c5c7b13ee9d37918941a5e37bf8d32da0481e965`.
- Final M7 seal revalidation at `2026-08-01T03:40:41+00:00`: context validator
  PASS; all 339 current hashes and all 425 inventory entries match the sealed
  after manifests; changed paths equal the 51-path transfer manifest exactly;
  the backup hash remains valid; the Phase 09 focused collection reports `76
  passed in 0.82 s`; all Bash syntax checks pass; repository `git diff
  --check` passes; the live-Pi path is not a mountpoint; and matching
  ROS/Gazebo/SSHFS/serial/physical processes are absent.
- Hardware/live-Pi/serial/ROS/Gazebo checks: NOT RUN by scope.
- At `2026-08-01T03:49:09+00:00`, the user authorized the bounded Phase 09
  closeout commit and post-commit receipt needed to return the repository to a
  clean worktree. Push remains a separate action and is not authorized.

## Attempts not to repeat

- Do not validate this archive with default extraction permissions: the host
  umask changes one historical mode `0777` to `0775`. Use
  `tar --same-permissions`; exact inventory and hashes then pass.
- Do not source `/opt/ros/humble/setup.bash` while `set -u` is active; the
  first M2 wrapper stopped before `colcon`. Temporarily disable nounset while
  sourcing.
- Do not run the complete repository legacy/observability collection against
  the physical overlay. It imports the deliberately excluded simulation
  `Multi_Light_Source_Cost`; the first collection failed, and a subsequent
  mixed invocation reported `306 passed, 9 failed` after that initial failure
  left the global rclpy context initialized. Use the separated shared-owner
  and repository-legacy invocations recorded above.
- A raw isolated colcon build root does not contain the Pi workspace's `src`
  layout, so a wrapper preflight first stopped on its required filter path.
  Use a temporary workspace view that links the isolated install and snapshot
  source when testing only the inert wrapper preflight; do not modify the
  snapshot with generated `build/install/log` roots.
- `--deselect` node IDs must be relative to pytest's selected root. The first
  M6 observability attempt used longer node IDs, ran both simulation-only tests,
  and reported `13 passed, 2 failed`; the clean retry used a name-based `-k`
  exclusion in a fresh process and reported `13 passed, 2 deselected`.
- Do not impose generic newline/trailing-whitespace rewrites on byte-identical
  shared files: one initializer is intentionally empty and the shared interface
  CMake file contains inherited whitespace. Apply authored-new-file hygiene and
  preserve shared parity.
- Plain `git diff` omits untracked new files. The first patch rehearsal
  contained only 18 modified paths and stopped on 33 missing after files. Use
  intent-to-add for every transfer path before generating the 51-file patch.
- Git patches retain only executable/non-executable state, not full snapshot
  modes. Forward proof first matched all hashes but exposed `0750/0755/0775`
  mode differences. Apply the after/before inventory modes during recovery;
  the combined proof matches exact inventories in both directions.

## Remaining work

1. M8 live-Pi read-only comparison/backup/transfer remains deferred and
   requires separate explicit authorization.
2. M9 stationary calibration and any hardware motion remain deferred and
   require another explicit authorization after M8.
3. The authorized bounded Phase 09 closeout commit and post-commit receipt are
   the only remaining repository-cleanup actions. Push remains a separate user
   choice.

## Stop conditions

- Stop before any live-Pi access, SSH/SSHFS, serial access, ROS hardware
  launch, motor/servo command, or physical process.
- Stop for a missing/invalid backup, snapshot overlap, cost sign/unit/topic
  change, controller-visible evaluator geometry/Vicon, duplicate owner,
  shared-runtime parity loss, legacy-selection loss, or final-zero/readiness
  regression.

## Compaction recovery

Before further changes, reread the plan and this file, inspect Git status and
the current diff, identify the next incomplete acceptance criterion, and
continue only from that verified state.
