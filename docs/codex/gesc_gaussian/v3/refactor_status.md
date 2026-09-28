# ESC/V3 refactor status

Active implementation authorized 2026-09-28. See [accepted plan](refactor_plan.md).
Branch: `refactor/esc-v3`. Goal remains the full refactor, not a compatibility
shim or a documentation-only change. No Pi changes or physical operations.

## R1 — preservation and build hygiene

- PASS: 2930 pre-refactor tracked/untracked working-tree entries archived with
  content hashes, modes and symlink targets verified against the archive.
- Archive/evidence: `/home/mattb/Experiments/GESC-Gaussian/v3/refactor_20260928T195707Z`.
- Archive SHA256: `eea8ffecf5fbc9a21038b3e74d7c160dfb11c7ad0f606ea9f50177ee68ee4a3e`.
- Frozen ref `archive/pre-v3-refactor-20260928` points to original HEAD
  `e7267740fc64f1a1c06bcb09ad25a60c57d1f72e`; original V1/V2 refs unchanged.
  Uncommitted comment renames/planning documents are preserved in the archive.
- Existing build/install/log directories moved under evidence
  `generated_workspace/`; these are never new build inputs.
- Inherited context check: `timeout 20s bash
  docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
  v2 implement` PASS. The accepted plan defines the V3 checkpoint equivalent.
- One Git index cleanup invocation rejected option ordering before index
  changes; corrected invocation succeeded. Exact hygiene receipt is external.

## R2 — active runtime implementation, complete

- Profiles: 19 short aliases, six Gazebo launch options, installed module-based
  configuration with custom-file compatibility. Original interactive Matplotlib
  plots retained; physical/headless plotting off. Physical package not imported.
- Selected V3 numerical helpers extracted with portable original-source golden
  fixtures; 13 focused numerical cases passed. Selected run05 k_vx=0.5 retained,
  while the physical-target velocity caps are deliberately 0.05 m/s, 0.30 rad/s.
- One local V3 control owner now connects observation, GESC/rolling direction,
  recurrent detection, moving verification, fill preparation/registry and escape.
  Numerical work is in a single private process; fill commits and escape objective
  changes are applied at a new real observation rather than replaying old data.
- Original adapters/filter/controller rewritten without V2 readiness/recorder
  protocols. Filter refinement has a 64-total-evaluation budget and recoverable
  reset. Lie-bracket input dimensionality repaired to its intended scalar cost.
- Fresh eight-message interface build PASS (10.7 s); see `interfaces_build.log`.
- Optional bag/plot/observer and legacy controller scoped tests: 28 PASS (2.55 s).
  Ordinary SQLite bag analysis, V3 messages, Agg plots and signal cleanup covered.
- Profile/adapters/filter scoped tests: 54 PASS (1.36 s), plus 19 Bash syntax
  checks and all-profile finite-object smoke; receipts copied into evidence.
- Pure observation/worker tests: 5 PASS. Worker timeout and new-process recovery
  tested; source/receipt age is never renewed by completion or duplicates.
- Actual isolated local ROS graph tests: 2 PASS (5.28 s), no hardware or Gazebo.
  A two-second numerical worker job did not block command cadence; duplicates
  expired to zero, fresh input recovered; subprocess SIGINT delivered final zero.
  Exact command uses ROS_LOCALHOST_ONLY=1, DDS domain189 and a 50 s outer timeout;
  receipt `control_ros_tests.log`. This is not proof of physical stopping.
- First combined source suite: 136 PASS / 1 FAIL (9.17 s), retained in
  `r2_combined_first.log`. The failing test still expected positive forward
  velocity after restoring selected GESC repulsion; reverse translation is valid.
  The settled installed reruns below pass; the intermediate failure is retained.

## R3 — installed software qualification, complete

- PASS: fresh complete symlink workspace build, all three packages (3.25 s).
  A subsequent dependency-update build passed in 2.23 s. Receipts:
  `workspace_build.log`, `final_build_and_tests.log`.
- PASS: installed active suite **196 tests**, no skips, 9.04 s; receipt
  `final_installed_entrypoint_tests.log`, with actual test bags/rendered images in
  `final_installed_entrypoint_artifacts/`. Existing NumPy matrix deprecation warnings are
  reported (372); no warning was converted into a qualification claim.
- Exact final command from repository root:
  `timeout 75s bash -c 'source /opt/ros/humble/setup.bash; source
  ros2_ws/install/setup.bash; export ROS_LOCALHOST_ONLY=1; python3 -m pytest -q
  ros2_ws/src/ros_esc/test --basetemp=/home/mattb/Experiments/GESC-Gaussian/v3/refactor_20260928T195707Z/final_installed_entrypoint_artifacts'`.
  ROS subprocess/transport tests use local domains187–190; no physical devices.
  The SIGINT test invokes the installed `controller_node --v3` entrypoint.
- Installed inventory: 11 intended console entries, eight interfaces, 19 Bash
  aliases; code/resources resolve to the current build/source. Retired owner
  modules are unavailable. See `installed_interfaces_profile.txt` and final audit.
- Core review restored selected gain0.5, repulse-before-assist behavior,
  original centered phase, full odometry detector rate and detector boundary
  timestamps. Both current pose and incoming observation must remain in the
  candidate neighborhood before a commit. Known-fill suppression and the
  retained mathematical fill-sweep guard are tested.
- Optional-worker Queue allocation failure initially escaped construction;
  expanded the existing error boundary and added a passing regression. Fresh
  basic control is independent of unavailable optional numerical work.

## R4 — cleanup and handoff, complete

- 523 obsolete active source/test/documentation files moved into external
  `retired_active_sources/`, with every destination hash checked. Old phase
  source/firmware/run evidence is preserved; frozen references are unchanged.
- Final structure audit found75 additional generated tracked entries under
  `extremum-seeking` after the initial1362 removal. These build/install/log and
  generated documentation trees were archived and verified too. Total1437
  generated entries removed from tracking; final tracked-generated count0.
  Receipt: `additional_generated_hygiene.json`.
- Current root/package READMEs and concise usage, architecture, environment,
  software-test and history guides replace stale active directions. Historical
  phase documents keep their original status; no new phase framework added.
- Active documentation check:14 files /71 local links, no missing targets;
  `final_documentation_check.json`. `git diff --check` passes.
  Active simulation source has no phase09 reference;
  historical documents/reports remain unchanged in meaning.
- [Requirement-by-requirement completion audit](refactor_completion_audit.md)
  maps all nine accepted implementation items and explicit corrections to
  current source, installation, tests and archive receipts.
- Branch `refactor/esc-v3`; the completed implementation is recorded in the
  refactor commit containing this status update. No push, Pi changes,
  deployment, hardware action or Gazebo research runs were made.

## Git checkpoint before Gazebo testing — 2026-09-28

- User requested a clean Git tree before testing. Generated-file cleanup is
  committed separately as `24d4a29` (`chore: stop tracking generated build
  artifacts`); the following refactor commit records the runtime, profiles,
  tests, documentation and retirement together.
- Read-only cleanup audit reverified all 523 retired-file hashes, the full
  pre-refactor archive digest and the four frozen reference hashes. The 93 new
  files contain only source, configuration, tests and documentation.
- Staging exposed extra blank lines at EOF in three numerical helper files;
  removed them and verified identical Python ASTs before/after. Runtime logic
  is unchanged. `git diff --check` and `git diff --cached --check` then pass;
  the installed 196-test result above remains the latest validation. No
  Gazebo or physical tests were started.
- External `git_cleanup_receipt.json` records the resulting commit IDs, final
  clean status and unchanged frozen references. Ignored local build/install/log
  products remain available; they are not part of either commit.

## Handoff / subsequent work

The software refactor is complete. Next is a separately scoped Gazebo V3
observation-model and behavioral test milestone using realistic acquisition,
arm-speed, timing, loss and resource constraints. Preserve working physical V1.
The selected V3 algorithm is not yet behaviorally or physically qualified.
Software tests do not establish continuous measured base translation, full
Gaussian escape, global convergence, Raspberry Pi headroom or hardware stopping.
The inherited optional ADC matcher is not a faithful validated UNO quantizer;
V3 currently disables it. Keep this limitation in the next simulation plan.
