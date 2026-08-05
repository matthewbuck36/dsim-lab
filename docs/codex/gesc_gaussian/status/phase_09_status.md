# Phase 09 Live Status

Last verified: `2026-08-04T17:55:33-07:00`
Status: `M8E ON-PI CHECK-ONLY PASS, CLEAN BUILD, PI SOURCE PARITY PASS, AND LAB WALL-CLOCK INITIALIZATION PASS FOR CURRENT BOOT`

## Objective

Integrate the current terminal cumulative Phase 08 runtime through v8.12 into
the local physical TurtleBot3 source snapshot and the user-mounted Pi source,
preserve shared algorithm parity and legacy selection, and qualify the selected
physical wrapper through an explicitly authorized, nonlaunching on-Pi
`--check-only` without opening hardware or commanding motion. The selected
wrapper enables the v8.12 interior-anchor fallback at `0.50 m`; shared legacy
and nonselected defaults remain disabled.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v1`
- Terminal Phase 08 source reference: `c04c222dfeac525197bf0542cbde64f1421dc664`.
- Pre-M7.1 closeout HEAD: `1c01aa3` (`phase 09: seal snapshot integration receipt`).
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
- During M0-M7.1 the reserved live-Pi mount was absent. During M8A it is the
  user-mounted read-write SSHFS source at `/home/mattb/tb3-pi`; no direct Pi
  command or physical process was started.
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
- At the M2 checkpoint the snapshot delta was 35 declared files, with zero
  paths outside the then-frozen transfer manifest and zero generated roots.
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

## Historical M7 milestone

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
- `docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md`
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
- At the M7.1 decision boundary, M8 and M9 remained deferred. M8A has since
  completed the scoped source transfer only; on-Pi build and M9 remain
  deferred.
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

The four items in this subsection are the historical M8B sequence and are
superseded by the current M8C milestone at the end of this file.

1. M8B implementation, host qualification, rollback backup, scoped source
   transfer, and snapshot/Pi parity are complete.
2. The on-Pi build, installed-overlay checks, and inert selected-wrapper
   preflight remain unexecuted; the wrapper now performs the required build
   when a later authorized operator invocation occurs.
3. M9 must create mutable site copies, complete and separately approve the
   no-actuation stationary preflight, test the independent e-stop, complete a
   nontranslating/final-zero rehearsal, then calibrate before `--check-only`
   and the bare normal wrapper may pass.
4. Every live Vicon, serial, ROS graph, calibration, actuation, and motion step
   remains deferred and requires its appropriate authorization. Any Git push
   also remains a separate user choice.

## Stop conditions

These are the historical M8B agent-execution limits. They do not add an
operator gate to the current human-run M8C lab procedure.

- The authorized SSHFS source transfer is complete. Stop before any further
  remote/on-Pi command, build, source, ROS graph, serial access, motor/servo
  command, calibration, or physical process without a new authorization.
- Stop for a missing/invalid backup, snapshot overlap, cost sign/unit/topic
  change, controller-visible evaluator geometry/Vicon, duplicate owner,
  shared-runtime parity loss, legacy-selection loss, or final-zero/readiness
  regression.

## Compaction recovery

Before further changes, reread the plan and this file, inspect Git status and
the current diff, identify the next incomplete acceptance criterion, and
continue only from that verified state.

## Phase 09 M7 closeout post-commit receipt — 2026-08-01

The bounded no-hardware snapshot integration and its durable recovery evidence
were committed:

```text
5b4c162047e2bae4c8f9fc742fa5ebd0c322e6f5
  phase 09: close no-hardware snapshot integration
```

Immediate post-commit verification:

```text
branch:
  feature/gesc-gaussian-robustness-v1
ahead of matching origin branch:
  178 commits
tracked and untracked worktree changes:
  none
Phase 09 implement context validator:
  PASS
all 339 sealed snapshot hashes:
  PASS
active simulation/analysis/physical runtime:
  none
handoff sha256:
  92031a21ec791cdc416619b86e2aceeb0afb707c54cf8f9b260ba73544dc0541
checkpoint sha256 in the closeout commit:
  984e06849d4f027057622dc64182cb3e7fe3be8438bbfb01246fbb4c3ae73a24
snapshot patch sha256:
  8d56261f6857ff0f6f1bd83021202d32a3a13a0242fa7a9cb5011153b4393d1b
after-file manifest sha256:
  af470b19b3aae91518e45fd093dcbe6874f67cccdd4ca6cf26213659c865afe4
```

The final staged generic whitespace check identified only the exact recovery
payload: historical source whitespace represented inside
`phase_09_snapshot.patch`, plus the intentionally empty final symlink-target
column in both inventory TSVs. One unrelated extra blank line at the end of
the backup receipt was corrected before commit. The staged check excluding
only those three byte-preservation artifacts passed, their sealed hashes were
unchanged, and the immediate clean-tree `git diff --check` passed. Do not
normalize those recovery files; doing so would change the reviewed patch or
inventory contract.

## Historical M7 closeout milestone

**PHASE 09 M7 COMPLETE / SNAPSHOT STATIC INTEGRATION PASS / SHARED-LAB LEGACY
COMPATIBILITY PRESERVED / CLOSEOUT COMMITTED / HARDWARE DEFERRED.**

## Next criterion

There is no remaining M0-M7 criterion. M8 live-Pi read-only comparison may
begin only under separate explicit authorization. Transfer and M9 hardware
commissioning each retain their own later authorization boundaries.

## Phase 09 M7.1 operator-entry and recording amendment — 2026-08-01

The user requested a final implementation audit, renamed the new-only selected
wrapper to `gesc_gaussian_two_source_voltage.bash`, renamed its new-only launch
to `gesc_gaussian_two_source.launch.xml`, and requested useful live terminal
diagnostics while retaining complete recording in the existing recorder.

Initial read-only audit confirmed that the cumulative terminal v8.12 shared
algorithm parity and M0 legacy hash guards still pass. It also found one real
physical-startup defect: the then-current `record_run.git_state(Path.cwd())`
required the Pi workspace to be a Git checkout, but the reviewed source-only
snapshot has no Git metadata. That call could fail before rosbag or the target
started. M7.1 added and tested an explicit non-Git provenance fallback without
weakening capture when Git is available.

The same audit confirmed that subprocess output was retained only in
`console.log`, so the invoking terminal was nearly silent. M7.1 added an
opt-in, bounded asynchronous tee and rate-limited summaries inside the existing
recorder. It does not start `ros2 topic echo`, the legacy CSV collector, or a
second recorder. The sqlite3 rosbag remains authoritative and declares both
the legacy streams and the additional GESC/Gaussian typed diagnostics.

The recording audit also found that the legacy collector embedded the exact
controller/filter/rotation inputs in its `comments.txt`, whereas the managed
rosbag run resolved ROS parameters but did not preserve every file-backed
physical input. M7.1 added validated, hashed evidence-file copies for the
calibration, selected profile, scenario metadata, controller, filter, rotation,
wrapper, launch, topic manifest, and QoS files under the same unique run
directory. This preserves reproducibility without reviving the legacy CSV
recorder.

## M7.1 implementation and final audit

- Renamed only the two Phase 09-owned operator paths to
  `gesc_gaussian_two_source_voltage.bash` and
  `gesc_gaussian_two_source.launch.xml`; the superseded names are absent from
  source, installed assets, manifests, and documentation.
- Preserved byte-for-byte parity for all 27 declared terminal v8.12 shared
  runtime/interface/config paths. The selected profile retains the counted
  two-source,
  maximum-one-fill behavior and enables only the cumulative v8.12
  `interior_farthest` fallback at `0.50 m`; shared and legacy defaults remain
  disabled.
- Retained `raw_cost=-voltage` in volts, one source-cost owner, one cost/filter/
  fill/supervisor/controller chain, one `/cmd_vel` owner, and one recorder.
- Fixed non-Git physical startup with explicit `git.available=false`
  provenance while preserving commit/branch/diff/untracked hashing when Git is
  available; unexpected Git errors remain fatal.
- Added mandatory, unique, in-run configuration evidence with source and
  retained SHA-256 verification. The physical validator now recomputes every
  required retained hash and treats missing, escaped, duplicate, or corrupted
  evidence as a completeness failure.
- Added selected-only one-second passive diagnostics and terminal streaming.
  `console.log` is written before a nonblocking, bounded 256-line terminal
  queue, so a slow/broken display cannot block the ROS executor or managed
  process capture.
- Added exact CLI guard coverage for truncated valued options and retained
  cleanup for only the two new temporary runtime configuration copies.

Final source receipts:

```text
wrapper:
  19871669f078b76d4a44a796624e2daf8d4cc3acf66c500fba2efacf54fe24fb
launch:
  a099bb8f4968861c4434e88e0cc7a140e7fe7ab7fae3cc628fb1dac15b6f630f
record_run.py:
  c885d2e43857a7158da318d9f84122a8908954ef4c93e4c415b4cbddf7a438ae
validate_run.py:
  d788b57818ef864e2024c6056c3c0768b933ec8d418f3f1e91332932e9c24b93
```

Three independent final reviews of algorithm parity/ownership,
wrapper-launch-Ctrl+C lifecycle, and recorder-validator-data behavior found no
unresolved defect after the bounded corrections. This is not a claim about
unrun hardware.

## M7.1 clean qualification and reseal

Fresh root: `/tmp/phase09_m71_final.bmS5g9`.

```text
isolated ros_esc_interfaces + ros_esc + turtlebot3_vehicle_nodes build:
  PASS, 3 packages in 13.1 s
Phase 09 focused:
  93 passed in 1.72 s
shared core:
  272 passed in 8.20 s
inherited recording:
  70 passed, 1 skipped in 2.88 s
compatible observability:
  13 passed, 2 deselected in 2.36 s
repository legacy behavior:
  34 passed in 3.73 s
```

The skip is the existing opt-in visible-Gazebo recording smoke. A first legacy
attempt sourced a stale repository install and stopped during collection; the
fresh corrected source-owner invocation above passed all 34 tests. All six
unique installed wrapper launch descriptions pass `--show-args`; the inert
selected wrapper exits `2` before device/ROS access and leaves zero temporary
configuration directories.

The final snapshot remains `339` regular files and `425` inventory entries,
with zero symlinks/generated roots. Its exact M0 delta is `33` new plus `18`
modified, `0` deleted, and equals the sorted unique 51-path transfer manifest.

```text
transfer manifest:
  5f60d69adc5d0feb87cb2fa2dd7c16cdc3bab846d3ec84fee181cb1dce9661f5
after regular-file manifest:
  3bca5cf1845311a2cedc40081f055f1bb51333184a195488f823c130fee33373
after inventory/modes:
  522a1440de034c1538181db9792214432c237d162b323ba065542da582c7f37c
51-path, 21,950-line patch:
  c92d0f96578ca28883b8c173f05411ca1a4b8d6e68cccd4e4f6b1ae667066723
```

Fresh forward application plus after modes reproduces all 339 hashes and 425
entries. Reverse application plus before modes reproduces all 306 M0 hashes
and 389 entries. Temporary proof roots were moved to Trash; the real snapshot
was never the patch target.

## Historical M7.1 milestone

**PHASE 09 M7.1 COMPLETE / FINAL SNAPSHOT STATIC INTEGRATION PASS /
SHARED-LAB LEGACY COMPATIBILITY PRESERVED / HARDWARE DEFERRED.**

## Next criterion

There is no remaining M0-M7.1 snapshot criterion. The bounded repository
closeout commit is the final administrative action under the user's prior
clean-tree authorization. M8 live-Pi read-only comparison may begin only under
separate explicit authorization; transfer and M9 hardware commissioning retain
their own later authorization boundaries.

## Phase 09 M8A live-Pi source transfer — 2026-08-01

The user mounted `pi@192.168.1.36:/home/pi` at `/home/mattb/tb3-pi` and
explicitly authorized applying the completed snapshot changes to the physical
Pi source tree. The mount was already read-write. No direct SSH command, Pi
build/source, ROS launch, serial access, mechanism command, or motion ran.

### Read-only preflight and overlap result

- Pi source packages: the expected `ros_esc`, `ros_esc_interfaces`, and
  `turtlebot3_vehicle_nodes` only.
- Pi baseline hashes: `306/306` M0 files PASS.
- Pi baseline metadata: `389/389` type/mode/size entries PASS.
- Transfer classification: 51 unique paths = 18 existing M0-identical targets
  plus 33 absent new targets; zero overlap/source errors.
- Independent second audit: same result.
- Legacy selection assets: 26 wrappers + 8 launches + 6 baseline physical
  package configuration assets = `40/40` M0 hash/mode PASS. The complete
  baseline also proves all `ros_esc` controller/filter/rotation configs.
- Existing out-of-manifest generated state: four `__pycache__` directories and
  six `.pyc` files. They were excluded and remain untouched.
- Pi `.bashrc` evidence: ROS 2 Humble, Burger model, domain ID 36.
- SSHFS capacity before transfer: approximately 1.5 GiB free.

### Backup and transfer

The exact rollback root is:

```text
/home/mattb/tb3-pi/phase09_backups/20260801T230325Z
```

It contains all 18 pre-transfer files, the 33-path absent list, sealed
manifests, and a verified archive. Backup checks: `18/18` file hashes,
`18/18` extracted archive hashes, and `25/25` backup-manifest entries PASS.

```text
backup manifest:
  17859e95c590c78abc8fb015229d825ae7f10d167d1ac86afb20d24e283f2561
existing-target archive:
  d3ccc408259b172162927c2da47db2ff5fc7ab0484b99d32511c1533a8b38366
```

The first dry run used the Plan's plain `rsync -a` shape and showed unnecessary
existing-directory time/group updates. It wrote nothing. The reviewed Level B
transfer-hygiene correction added `--omit-dir-times --no-owner --no-group`.
Its dry run and transfer resolved to 18 modified files, 33 new files, three
required new directories, zero deletions, and zero unrelated changes.

### Manual-wrapper build/source correction

The transfer audit found that M7.1's selected wrapper sourced an existing
install but did not run the build expected by the user's manual Bash workflow.
The bounded correction changed only three existing manifest paths:

- selected wrapper: commented `MBuck 2026-08-01` three-package build before
  source;
- selected wrapper regression: exact package set and build-before-source
  assertion; and
- physical package README: operator behavior documented.

The full snapshot Phase 09 collection passed `93` tests after the correction,
then the same three files were copied through the existing no-delete manifest.
The final snapshot-to-Pi dry run is empty. No historical entry point changed.

### Final evidence

```text
snapshot hashes: 339/339 PASS
Pi hashes: 339/339 PASS
snapshot inventory: 425/425 PASS
Pi inventory: 425/425 PASS
post-transfer legacy selection: 40/40 PASS
all Pi Bash entry points: 27/27 bash -n PASS
direct mounted-source Phase 09 tests: 93 passed in 28.34 s
direct parity/launch subset: 44 passed
Python compileall: PASS
structured parse: 11 XML, 7 YAML, 68 JSON PASS
final generated Pi state: unchanged at four cache dirs/six pyc files
```

One earlier direct full-test invocation returned only progress output through
the command-yield boundary and no final captured status. It was not treated as
a pass or failure; the fresh fully captured retry above passed `93/93`.

Resealed evidence:

```text
transfer manifest:
  5f60d69adc5d0feb87cb2fa2dd7c16cdc3bab846d3ec84fee181cb1dce9661f5
after-file manifest:
  1d86d9ebceffbef49df06a53470f972f1897fc7488fd0fa315abd2a47004cd36
after inventory:
  8eacf7b7f36cd67979688cf168ae5fd3c4e8274ebdffa149e76b12c737c647ee
51-path patch:
  8985b4b2f5a33383a9abe4b6dc48a48a999c4da9dec5dfc24b88e9b324708939
aligned Phase 09 Plan prompt:
  e103301417819a3d2231ee37d80bd30de333a0c8010b97d521917ab05eab5fdd
aligned Phase 09 Implement prompt:
  c46b8a43e2f59fa16ac2446e7864fb4c4d31a60df033824d94482722bfe5ea60
```

Forward patch recovery reproduces all 339 final hashes; reverse recovery
reproduces all 306 M0 hashes. Exact commands and rollback boundaries are in
`docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md`.

## Historical M8A milestone

**LIVE-PI SOURCE TRANSFER PASS / SNAPSHOT-PI BYTE PARITY PASS / LEGACY
SELECTION PRESERVED / ON-PI BUILD NOT RUN / HARDWARE AND MOTION DEFERRED.**

## Historical next M8 criterion

Under separate authorization, run the three-package build on the Pi, installed
launch/interface/entry-point checks, and only the motion-blocked wrapper
preflight. Do not start a ROS graph or access a device as part of that gate.

## Phase 09 M8B evaluation-only Vicon and single-entry amendment — 2026-08-01

The user clarified that the selected algorithm must continue to use
wheel/IMU-backed `/odom` exclusively, while Vicon is required only for
ground-truth collection, trajectory analysis, and evidence completeness. The
local Vicon SOP requires Vicon Tracker and its Python server to be ready before
the robot-side experiment starts. The ONR report separately describes Vicon as
the system used to capture position data for plotted experimental trajectories.

The accepted M8B boundary is therefore:

- all controller, supervisor, PDE/history, modified-cost, Gaussian-fill, and
  escape pose inputs remain `/odom`;
- Vicon publishes only as `geometry_msgs/msg/PoseStamped` to
  `/gesc_gaussian/evaluation/vicon_pose` and is recorded as a required physical
  evidence heartbeat;
- recorder readiness may fail closed on missing/stale Vicon evidence, but no
  Vicon value enters a control calculation;
- every legacy odometry/Vicon source remains byte-identical; a new
  Phase-09-only evidence publisher is isolated inside the existing odometry
  package and cannot publish `/odom`;
- the dedicated Phase 09 wrapper defaults to the primary scenario, resolves
  the commissioned serial device from calibration, requires one typed per-run
  safety/Vicon confirmation, and retains a run-specific metadata copy;
- `--check-only` audits configuration without a ROS graph, device, Vicon
  client, run directory, or command; and
- historical wrappers, launches, configurations, and their mappings remain
  byte-identical.

Current authorization covers planning/evidence updates, offline snapshot
source/configuration edits and tests, and a separately backed-up, scoped
SSHFS source transfer after qualification. It does not authorize a direct
SSH/on-Pi command, workspace build on the Pi, ROS hardware graph, serial/GPIO
access, Vicon client execution, calibration, lamps, rotating mechanism, or
motion.

### M8B implementation and host qualification

The fresh pre-edit snapshot backup remains at:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260802T001406Z_m8b_preedit
```

It contains the 339-file before manifest, 425-entry inventory, 41 MiB archive,
and retained checks proving the current snapshot, mounted Pi reviewed paths,
and a same-permissions archive extraction each match all `339/339` sealed M8A
hashes. Archive SHA-256:
`dfe7cc95b70c33f7d99ef65b32c1bdba136df17ced251f4525f304125e416136`.
The temporary extraction was moved to Trash after verification.

The final implementation adds only selected-path Vicon evidence, staged
rotation authorization, the passive stationary timekeeper, stricter physical
calibration/metadata, the sole recorder/validator extensions, and regression
guards. It retains wheel/IMU-backed `/odom` as the only algorithm pose and
records Vicon only as required evaluation evidence. The wrapper's eventual
normal entry remains the bare
`gesc_gaussian_two_source_voltage.bash`, with primary-scenario and commissioned
serial defaults plus one typed `RUN operator | observer` confirmation.

The final adversarial pass corrected bounded evidence defects before source
freeze:

- coercible bool/string Vicon identity, pose, status-age, and rotation-command
  fields are now rejected as wrong wire types;
- Vicon readiness requires at least two same-session advancing samples;
- rotation requires fresh passive `WAITING_AUTHORIZATION` evidence before
  GPIO ownership, permanently latches any pre-gate nonzero command, and
  requires an exact revoked-authorization terminal zero status;
- invalid `ControlDiagnostics.final_command_valid=false` cannot establish
  final zero, and the recorder keeps rosbag active for stable zero dwell before
  and after target termination;
- operational evidence covers the full readiness-true interval, including
  zero-command holds, and enforces each retained `0.6 s` bound at both
  endpoints and every interior gap; and
- offline validation independently freezes all 12 physical operational
  manifest aliases so a retained artifact cannot remove its own gap check.

Final host evidence under `/tmp/phase09_m8b_final3.DhSBng`:

```text
fresh three-package host build: PASS in 13.0 s
Phase 09 focused: 309 passed in 5.09 s
shared core: 272 passed in 7.53 s
inherited recording: 70 passed, 1 skipped in 2.85 s
physical-compatible observability: 13 passed, 2 deselected in 0.85 s
repository legacy behavior: 34 passed in 2.71 s
Bash syntax: 27/27 PASS
structured parse: 11 XML + 7 YAML + 68 JSON PASS
critical Python lint: 111/111 files PASS
formal legacy selection: 40/40 M0-identical
expanded legacy configuration set: 68/68 M0-identical
```

The skip is the opt-in visible-Gazebo recording smoke. The two exclusions are
simulation cost-owner tests deliberately absent from physical packaging. An
initial local test command overwrote `PYTHONPATH` and hid `rclpy`; the corrected
fresh process prepended source paths and produced the result above. No hardware
or behavior result is claimed for the environment-only failed collection.

### M8B snapshot seal and live-Pi source sync

Final recovery evidence:

```text
snapshot: 345 regular files / 432 inventory entries / 0 symlinks
M0 delta: 39 new + 18 modified + 0 deleted = 57 paths
transfer manifest:
  f015285fa8b618f985d7257ac1471fe02c61e4ba17bc4701457ba36411931ff6
after-file manifest:
  97af95a46bc8161f83a6776d609eb2480c0af0584b09ac62d5d60b9f2f638053
after inventory:
  602c2c9fa1f31fa7bd29692a07127e65b72c8570b1dcb6273226367db38643d2
57-path patch:
  6fd166368449f33cff85d5e1422a414199171b27d8420e9ea1364cb2f5090885
forward hashes/inventory: 345/345 and 432/432 PASS
reverse M0 hashes/inventory: 306/306 and 389/389 PASS
```

The mounted Pi first matched M8A (`339/339`, `425/425`). The reviewed M8B dry
run contained 15 existing replacements, six new files, one new directory, and
zero deletions. The verified rollback root is:

```text
/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b
archive:
  a88dab7d51832f634558af9f886767a82c19c60ae7ff9a4b1c38764444a6fdbc
backup manifest:
  c2fc028ba28bfb4244e706256a7b84c08654a112398987be808ae331bd7cb459
```

The actual itemization matched the dry run. Both the final manifest-scoped and
complete source-tree dry runs are empty. The Pi matches all `345/345` final
hashes and `432/432` type/mode/size entries. Its four pre-existing cache
directories and six `.pyc` files remain unchanged. No command, build, source,
ROS graph, serial/GPIO device, Vicon client, calibration, actuator, or motion
ran on the Pi.

The authored-document `git diff --check` passes when the generated recovery
patch, full-mode inventory, and checkpoint are excluded. The generic check's
remaining findings are confined to those byte-preservation artifacts: 14
patch lines, 22 changed inventory rows with an empty symlink-target column,
and their 36 verbatim checkpoint echoes. They must not be normalized apart
from the sealed recovery contract.

## Historical M8B terminal milestone (superseded by M8C)

**M8B SNAPSHOT AND PI SOURCE PARITY PASS / EVALUATION-ONLY VICON AND STAGED
ROTATION STATIC CONTRACT PASS / LEGACY SELECTION PRESERVED / ON-PI BUILD NOT
RUN / NOT PHYSICAL READY.**

## Historical M8B next workflow (superseded; do not execute)

1. Under separate authorization, run the bounded three-package build on the
   Pi and inspect the installed interfaces, entry points, launch arguments,
   and `--check-only` behavior. Do not start the graph or access a device in
   this gate.
2. Create mutable site calibration and primary/secondary metadata copies under
   `${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09` before stationary
   preflight; leave the installed selected profile frozen.
3. With live serial and evaluation-only Vicon data but calibration still
   unreviewed, run `--stationary-preflight`; readiness and both actuation gates
   remain false.
4. Review the retained PASS, then hash-couple the same site metadata bytes with
   `--approve-stationary RUN_DIR --reviewer NAME`.
5. Test the independent emergency stop, then run the separately authorized
   nontranslating/final-zero rehearsal.
6. Perform and independently review the rotating-photoresistor calibration.
7. Run `--check-only` until the complete commissioning audit passes.
8. Only then run bare `gesc_gaussian_two_source_voltage.bash` for the primary
   scenario and type `RUN operator | observer` when the floor, e-stop, and
   Vicon server are ready.

Steps 1-8 are not completed merely because the source is synchronized. M8B is
not a live Vicon, hardware, calibration, or motion pass.

## M8C lab-SOP one-command simplification — 2026-08-03

<!-- MBuck 2026-08-03: Replace the M8B commissioning ceremony with the existing lab SOP and one selected wrapper; preserve M8B results above as history. -->

The user approved a simpler physical-test contract matching the attached
`DSIM - TurtleBot3 Vicon Setup.pdf` and the lab's unchanged
`vicon-tracker-server.py`. The historical M8B progression above remains useful
as provenance, but it is no longer an operator procedure and must not block the
selected experiment.

Current operator contract:

- on the Windows Vicon computer, follow the lab SOP, make sure Vicon Tracker is
  streaming, and run the unchanged `vicon-tracker-server.py`;
- on the Pi, invoke bare `gesc_gaussian_two_source_voltage.bash` from its normal
  `voltage_cost_values` Bash directory;
- the selected wrapper builds only `ros_esc_interfaces`, `ros_esc`, and
  `turtlebot3_vehicle_nodes`, sources the workspace, and starts `pigpiod` only
  when it is not already running;
- no separate build command, site-configuration copy, calibration approval,
  stationary preflight, `--check-only`, typed `RUN`, subject/segment selection,
  server-file SHA-256, handoff authorization, or `PHYSICAL READY` tag is part of
  the operator path;
- wheel/IMU-backed `/odom` remains the sole algorithm pose;
- the legacy Vicon `7f` stream is converted by the existing odometry owner to
  `nav_msgs/msg/Odometry` on
  `/gesc_gaussian/evaluation/vicon_odom` for passive evaluation only;
- absent, stale, or incomplete Vicon evidence must remain visible in terminal
  diagnostics and retained validation, but may never inhibit, stop, steer, rank,
  or otherwise gate robot motion; and
- operator `Ctrl+C` remains the normal end condition. The managed shutdown must
  command readiness false/final zero, retain the zero dwell in the bag, finalize
  the bag and metadata, run bounded validation, and print the retained run
  directory.

The selected experiment remains an exploratory physical test of the cumulative
terminal v8.12 algorithm, not a claim of broad physical robustness. Normal lab
safety still applies: clear the floor, arrange the two lamps, keep the robot in
view, and remain ready to press `Ctrl+C`.

### Current evidence state

- M8B host qualification, rollback evidence, and snapshot/Pi parity above remain
  valid historical evidence.
- M8C snapshot source edits are complete: `16` reviewed replacements and three
  obsolete Phase-09-only JSON/stationary-gate files removed. Every other M8B
  source path, including all legacy ESC selections and the historical Vicon
  client/server, is byte-identical.
- The final isolated host build passed all three selected packages in `12.6 s`.
  The focused M8C suite reports `196 passed`; the functional package suites
  report `153 passed, 3 deselected` and `71 passed, 3 deselected`.
- All `27` Bash files pass syntax. Nine changed Python files, nine XML files,
  seven YAML files, and 68 JSON files parse. The selected launch
  `--show-args` check passes.
- The real wrapper's host-only `--check-only` path rebuilt all three packages in
  `12.6 s` and passed with scenario `primary` and `/dev/ttyUSB0`, without
  starting pigpio, serial, Vicon, a ROS graph, the recorder, or motion.
- Snapshot recovery artifacts are retained at
  `/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T003650Z_m8c_pre_simplification`
  and
  `/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T010757Z_m8c_post_simplification`.
- The reviewed Pi rollback is
  `/home/mattb/tb3-pi/phase09_backups/20260804T011049Z_m8c_pre_simplification`.
  The final snapshot and Pi match `342/342` regular-file hashes and `430/430`
  inventory entries; the final checksum dry run is empty.
- No on-Pi build, ROS graph, live Vicon connection, serial/GPIO access, lamp
  response, actuator command, or robot motion has been run by Codex for M8C.

## M8D familiar runtime CSV export — 2026-08-03

<!-- MBuck 2026-08-03: Derive familiar CSVs from the finalized authoritative bag; do not add a live collector or second recorder. -->

The selected wrapper now automatically writes familiar, headerless CSV files
into its retained run root after the sole sqlite3 rosbag finalizes. The export
runs inside the existing `validate_run` owner and is atomic and idempotent; it
does not alter the selected launch graph, add a live CSV collector, or affect
any legacy ESC wrapper.

Finalized run artifacts now include:

- `encoder.csv`: `[timestamp, angle]` from the `encoder` alias;
- `cost_value.csv`: `[timestamp, augmented_cost]` from
  `augmented_cost_legacy` (`/cost_modified`);
- `filter_value.csv`: timestamp plus the exact two-value legacy filter row;
- `control_value.csv`: timestamp plus the exact six-value final-command row;
- `odometry.csv`: evaluation-only Vicon in the legacy
  `[timestamp, x, y, z, qw, qx, qy, qz]` layout;
- `raw_cost_value.csv`: legacy raw cost with `raw_cost = -voltage`;
- `algorithm_odometry.csv`: the algorithm's independent `/odom` pose; and
- `legacy_csv_manifest.json`: resolved sources, semantics, row counts, file
  sizes, SHA-256 values, and bounded export errors.

Final write-enabled validation requires the export to be complete. Dry
validation does not mutate the run directory and prints a warning that CSV
export was skipped. The CSV columns are compatible with the legacy low-level
plot reader; its one-level `Test_*` browser does not auto-discover the selected
wrapper's nested dated run root, so a retained run directory must be supplied
directly to that reader.

M8D changed exactly two existing snapshot/Pi source files,
`validate_run.py` and `test_phase09_physical_recording.py`, and added
`legacy_csv_export.py`. Scoped SSHFS transfer used no delete behavior.
Pre-transfer recovery artifacts are retained at:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T023735Z_m8d_legacy_csv_export
/home/mattb/tb3-pi/phase09_backups/20260804T023735Z_m8d_legacy_csv_export
```

The verified post-change source seal is retained at
`/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T030145Z_m8d_post_legacy_csv_export`.
Its 343-file manifest hashes to
`49f969c72021242f25eaa4b2b87993904a9c0a5decd79278385d1d35bcf5b9af`,
its 431-entry inventory hashes to
`88b84d44dd478a09da610f75f9caf98619b71d5017f2f3d5a123cbd8f18a5bf7`,
and its verified source archive hashes to
`e713a243daa6c5e687494798fd0ed76096d5000904108716bf2106f22c95a23c`.

Current M8D evidence:

- source focused/full five-file Phase 09 regression: `209 passed`;
- isolated build: all three selected packages finished in `12.6 s`;
- installed-overlay five-file Phase 09 regression: `209 passed`;
- `ros_esc` functional regression: `159 passed` with the three inherited style
  meta-tests excluded;
- vehicle-node functional regression: `71 passed` with its three inherited
  style meta-tests excluded;
- mounted Pi-source recording regression: `131 passed`; the remaining Phase 09
  files then passed `78` tests;
- exact snapshot/Pi parity: `343/343` regular-file hashes and `431/431`
  type/mode/size inventory entries; and
- generated cache files and source-tree symlinks: `0`.

The first attempted test shell enabled `set -u` before sourcing ROS and stopped
on the setup script's unset `AMENT_TRACE_SETUP_FILES`. Reordering the shell to
source ROS before enabling `set -u` passed; this was a shell-environment attempt,
not a source or behavior failure.

The first retained-manifest verification attempt ran from the repository root
instead of the source root, so all relative paths were reported missing. The
same manifest then passed all 343 entries from its correct source root; the
archive hash check also passed. No source changed during that correction.

No on-Pi build/source, live Vicon connection, calibration, safety rehearsal,
serial/GPIO access, lamp response, actuation, or robot motion was run for M8D.

## M8E milestone at that point

**M8D FAMILIAR CSV EXPORT PASS / M8C LAB-SOP ONE-COMMAND CONTRACT RETAINED /
HOST QUALIFICATION PASS / SNAPSHOT-TO-PI PARITY PASS / LEGACY SELECTION
PRESERVED / NO LIVE HARDWARE RUN BY CODEX.**

## Exact next workflow

1. In the human-operated lab session, follow the attached Vicon SOP, start the
   unchanged Windows `vicon-tracker-server.py`, arrange the two lamps, and clear
   the floor.
2. SSH to the Pi and invoke bare `gesc_gaussian_two_source_voltage.bash` from
   its normal `voltage_cost_values` directory. The wrapper performs its own
   build/source and conditional `pigpiod` startup; no additional repository
   gate or authorization file is required.
3. Watch the printed run directory and one-second diagnostics. Keep the robot
   in view and press `Ctrl+C` if the behavior or hardware is not acceptable.
4. On normal completion or interruption, wait for final-zero/rosbag validation
   and the automatic familiar CSV export, then retain the reported run
   directory. Diagnose any evaluation-incomplete Vicon, CSV-export
   incompleteness, or physical behavior result from that evidence.

## M8E real-Pi runtime repair and check-only — 2026-08-04

<!-- MBuck 2026-08-04: Repair the real-Pi startup path, force a clean selected-package build, and preserve every historical experiment entry point. -->

The first bare wrapper attempt is retained as failed commissioning evidence at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/
  2026-08-04/
  20260804T152851316144Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_df84804a
```

It started the recorder but failed before readiness because the wrapper omitted
the Pi's established `~/turtlebot3_ws` underlay and the selected installed
Python copies were stale. `turtlebot3_bringup` was unresolved, the installed
photoresistor console entry rejected the current serial flags, readiness stayed
false, and no command or motion occurred. The run was shut down and retained.

M8E corrected the bounded runtime path:

- the wrapper resolves its own evidence path before changing directory;
- it sources `/opt/ros/humble` and then
  `/home/pi/turtlebot3_ws/install/setup.bash` before the selected build;
- it builds exactly the three selected packages with `--symlink-install`;
- it constructs the selected base and experiment launches before recorder
  ownership and verifies installed Python/source parity;
- it requires distinct readable/writable photoresistor and OpenCR devices;
- a selected-only no-lidar helper retains OpenCR motors and wheel/IMU `/odom`
  while avoiding the historical photoresistor/LDS-02 `/dev/ttyUSB0` collision;
  all historical launches retain the complete unchanged vehicle bringup; and
- the missing historical `sound_profile_experiment_node_script.py` was
  restored byte-for-byte from the retained generated install so a clean build
  does not break that legacy launch/entry point.

M8E changed no `ros_esc` algorithm source. Six existing selected/documentation/
test files were replaced and two files were added. The scoped snapshot-to-Pi
transfer used no delete behavior. Pre-repair rollback roots are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T224607Z_m8e_runtime_repair
/home/mattb/tb3-pi/phase09_backups/20260804T224607Z_m8e_runtime_repair
```

The Pi backup contains the moved stale selected build/install state under
`generated_before`; it remains recovery evidence and is not the corrected
install.

Final host qualification:

```text
Phase 09 implement context: PASS
Bash/Python/XML syntax: PASS
focused wrapper/launch/compatibility: 22 passed
isolated selected build: 3 packages PASS in 15.1 s
selected base and complete launch --show-args: PASS
installed-overlay Phase 09/device suite: 233 passed
vehicle functional suite: 74 passed
new selected helper focused flake8: PASS
```

The operator repaired the pre-existing interrupted `linux-firmware` package
configuration. Final package-manager evidence was `dpkg` exit zero, empty
`dpkg --audit`, passing `apt-get check`, running kernel
`5.15.0-1079-raspi`, and no reboot requirement. The
`ros-humble-turtlebot3-bringup` APT package remains absent by design; the lab
source underlay is the accepted owner.

The operator then confirmed:

```text
usb-1a86_USB_Serial-if00-port0 -> /dev/ttyUSB0
usb-ROBOTIS_OpenCR_Virtual_ComPort_in_FS_Mode_FFFFFFFEFFFF-if00 -> /dev/ttyACM0
```

and ran the strengthened `--check-only`. The intentionally moved stale install
prefixes produced one-time missing-prefix warnings before the clean rebuild.
The final result was:

```text
ros_esc_interfaces: PASS in 1 min 20 s
ros_esc: PASS in 11.8 s
turtlebot3_vehicle_nodes: PASS in 5.32 s
3 packages: PASS in 1 min 39 s
installed Python parity: PASS (ros_esc=63, turtlebot3_vehicle_nodes=21)
scenario: primary
turtlebot3 underlay: /home/pi/turtlebot3_ws/install/setup.bash
turtlebot3 model: burger
photoresistor: /dev/ttyUSB0
OpenCR: /dev/ttyACM0
selected lidar: disabled
launch construction: PASS
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Earlier in the same commissioning sequence, the low-battery robot was powered
down. The stale SSHFS mount was detached without deleting data, the Pi was
powered from the wall and booted, and the source was remounted. Post-power-cycle
verification reports `345/345` source hashes, `433/433` type/mode/size entries,
all three `colcon_build.rc` files zero, current install links, and the rollback
backup present. The final strengthened check-only output above was captured
after the Pi was back online.

The final M8E source seal is:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T234034Z_m8e_post_runtime_repair
```

with zero source caches/symlinks and these SHA-256 values:

```text
source manifest: 5469c772d0649d42cee3581d207d19a29a16d6df1f13d30620e1a10ce301c66d
inventory:       3775454cb80812501495c4315b6ce696302960d580ba7750d550be3a9bfb6fd2
verified archive: 2a2b81cef6e1156890191e0667795c9ddfbca111cffa5e9d88fc2a9e3bdb659a
```

Full evidence and rollback details are in
`docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md`.

### Offline clock finding and correction

The successful check printed `2026-08-04T16:27:57+00:00`, about seven hours
behind absolute UTC. A later reboot restored the stale
`2025-06-04T14:59:08+00:00`; `timedatectl` confirmed `RTC time: n/a`, UTC,
active but unsynchronized NTP. DSIMOVERWATCH has no internet access. This
matches Nick's package README, which requires `sudo date -s` before experiments.

The first correction copied the Linux tower's Unix epoch and produced
`2026-08-05T00:02:42+00:00` while the lab remained on August 4. No run started
under that superseded setting. Review of Nick's README, both legacy collector
owners, and the selected recorder confirmed that the established convention is
to enter Pacific wall-clock fields literally into the UTC-configured Pi.

The Linux tower reported `2026-08-04 17:54:22 PDT -0700`; the corrected Pi
reported `2026-08-04T17:54:22+00:00`. That is a PASS for this powered session
and preserves the historical folder date. No timezone or NTP configuration
changed. Repeat the literal wall-time step after each reboot and before ROS,
never during a run and never with a Unix epoch, timezone label, or offset. The
recorder's `...Z`/`*_utc` labels follow this established Pi lab clock and are
not an external true-UTC synchronization claim.

## M8E final milestone before M8F

**M8E CLEAN ON-PI BUILD AND CHECK-ONLY PASS / INSTALLED-SOURCE PARITY PASS /
SELECTED DEVICE AND NO-LIDAR BASE SEPARATION PASS / LEGACY SELECTION PRESERVED /
OFFLINE LAB WALL-CLOCK INITIALIZATION PASS FOR CURRENT POWER SESSION / NO ROS
GRAPH OR MOTION RUN.**

## Exact next workflow after M8E

1. If the Pi has rebooted since the successful
   `2026-08-04T17:54:22+00:00` initialization, repeat Nick's literal
   wall-clock `sudo date -s` step from the lab computer before starting ROS.
   Do not copy a Unix epoch or timezone/offset. Otherwise the current clock is
   already valid.
2. Follow the attached Vicon SOP, start the unchanged Windows
   `vicon-tracker-server.py`, arrange the two lamps, clear the floor, and keep
   `Ctrl+C` immediately available.
3. Invoke bare `gesc_gaussian_two_source_voltage.bash`. The successful M8E
   check-only does not need to be repeated before each experiment.
4. Watch the printed run directory and one-second diagnostics. Stop if sensor,
   odometry, command, rotation, or physical behavior is unacceptable.
5. After `Ctrl+C`, wait for readiness false, final-zero dwell, bag finalization,
   validation, familiar CSV export, and the final retained run directory.

## M8F first selected runtime-graph repair — 2026-08-04

The first bare selected attempt is retained as a failed commissioning run:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T201250796597Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_6d9b4ac3
```

Both strict legacy CLI owners rejected `--ros-args -p
use_sim_time:=False`; controller and filter exited 2, readiness never became
true, and `/cmd_vel` had zero messages. The 3,187-message bag closed cleanly
and retains `/odom`, IMU, encoder, and evaluation-only Vicon evidence. Its 18
completeness failures and empty familiar CSVs are correct consequences of the
startup failure. No algorithm motion ran.

The accepted source repair adds a native `--use-sim-time` option to controller
and filter with legacy default `True`, selects `False` only in the Phase 09
launch, and validates the complete parsers inside `--check-only`. Signal-safe
cleanup now covers filter, selected rotation, photoresistor, and the existing
Vicon UDP client. The Windows Vicon server, endpoint, packet format, units,
topics, and evaluation-only role remain unchanged; `/odom` remains the sole
algorithm pose. Historical ESC wrappers and launches remain byte-pinned.

Verified results:

```text
canonical focused tests: 10 passed
canonical legacy regression: 37 passed
focused Vicon/launch tests: 35 passed
complete six-file Phase 09 physical suite: 238 passed
critical changed-file lint and static syntax/XML/Bash checks: PASS
fresh isolated host build: 3 packages passed in 12.5 s
mounted Pi source static checks: PASS
snapshot/Pi regular-file parity: 345/345
snapshot/Pi symlink parity: 0/0
```

Pre-repair backups and receipts exist under
`20260804T202726-0700_m8f_runtime_graph_repair` in both snapshot and mounted Pi
`phase09_backups`. Eleven unique reviewed files were transferred with no
delete operation. The Pi source is current, but its post-M8F build/install has
not yet been rebuilt or qualified.

## Current milestone

**M8F SOURCE REPAIR HOST-QUALIFIED / SNAPSHOT-PI SOURCE PARITY PASS / ON-PI
POST-REPAIR BUILD, INSTALLED PARITY, PARSER COMPATIBILITY, AND CHECK-ONLY PASS /
NEXT PHYSICAL ALGORITHM RUN NOT STARTED.**

### Exact next action after M8F

The operator completed the one-time post-repair command from the standalone
Linux-tower SSH terminal:

```text
ros_esc_interfaces: PASS in 2.61 s
ros_esc: PASS in 5.19 s
turtlebot3_vehicle_nodes: PASS in 5.31 s
three packages: PASS in 14.4 s
installed Python parity: PASS (63 + 21 files)
selected CLI parser: PASS (physical=False, legacy default=True)
scenario/launch: primary, PASS
devices: /dev/ttyUSB0 photoresistor, /dev/ttyACM0 OpenCR
selected lidar: disabled
current time: 2026-08-04T20:52:29+00:00
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Read-only SSHFS inspection confirmed all three `colcon_build.rc` files are
zero. The one-time M8F rebuild gate is closed. If the Pi has not rebooted and
source has not changed, follow the established Vicon/lab SOP and invoke bare
`./gesc_gaussian_two_source_voltage.bash`; do not repeat check-only as a ritual.
The next retained run must still prove sensor, `/odom`/IMU, Vicon, command,
motion, Ctrl+C/final zero, bag/validation/CSV, and physical two-light behavior.
See
`docs/codex/gesc_gaussian/validation/phase_09_first_physical_run_repair.md`.

## M8G second selected-run diagnosis and startup-grace repair — 2026-08-04

The second bare selected run is retained failed evidence at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T205606472031Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_d4f0178d
```

The M8F runtime repairs held: the three-package build passed, OpenCR and
wheel/IMU `/odom` came up, evaluation-only Vicon became live, the 10,234-message
bag finalized, and every process shut down cleanly. Readiness remained false,
all 1,202 `/cmd_vel` samples were zero, and no motion occurred. The selected
supervisor's 5-second startup grace expired before the recorder's passive
graph/parameter stage could authorize rotation, causing `SEARCH -> FAILSAFE`.
No Timekeeper or source-cost messages were published.

M8G changes exactly the new selected wrapper plus its focused test. The wrapper
now passes explicit recorder bounds of `45.0 + 45.0` seconds and a selected-only
algorithm startup grace of `100.0` seconds. Recording readiness remains the
motion gate. Shared controller/supervisor defaults, the launch default, all
historical ESC wrappers/launches, algorithm tuning, cost sign/units, `/odom`
ownership, and evaluation-only Vicon remain unchanged.

Verified results:

```text
focused selected wrapper/launch: 23 passed
complete six-file Phase 09 suite: 239 passed
canonical legacy behavior: 37 passed
Bash syntax/XML parse/critical lint: 27/27, 9/9, PASS
isolated selected build: 3 packages PASS in 15.2 s
mounted-Pi focused suite: 23 passed
snapshot/Pi regular files: 345/345 PASS
snapshot/Pi inventory: 433/433 PASS
source caches/symlinks: 0/0 on both sides
```

Matching recovery and transfer receipts are under
`20260804T210435-0700_m8g_startup_grace_repair` in both snapshot and mounted-Pi
`phase09_backups`. No Pi build, ROS graph, serial/GPIO access, Vicon client,
recorder, or motion was started by Codex for M8G.

## Current milestone

**M8G SELECTED STARTUP-GRACE SOURCE REPAIR HOST-QUALIFIED / SNAPSHOT-PI SOURCE
PARITY PASS / SECOND FAILED NO-MOTION RUN RETAINED / ON-PI POST-REPAIR BUILD AND
CHECK-ONLY NOT YET RUN / PHYSICAL ALGORITHM BEHAVIOR NOT YET DEMONSTRATED.**

### Exact next action after M8G

From the standalone Linux-tower SSH terminal, run exactly one post-source-change
check:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash --check-only
```

Review its three-package, installed-parity, parser-compatibility, launch, and
final PASS output before another bare run. It must start no runtime or hardware.
After it passes, do not repeat check-only as a ritual; return to the ordinary
Vicon/lab SOP and bare wrapper. The next retained run still must prove live
Timekeeper, voltage/raw cost, filter/control, readiness, authorized motion,
Ctrl+C/final zero, bag/CSV completeness, and physical two-light behavior.
