# Root environment guidance validation — 2026-09-08

Result: **PASS**, documentation complete on
`feature/gesc-gaussian-robustness-v1`, base HEAD `dca77ba`. The user explicitly
reopened the branch for these root guides, then authorized the local commit
`docs: close V1 with environment guidance` as its final change. The containing
commit is the final boundary; it replaces the earlier closure at `dca77ba`.

## Delivered scope

- Updated simulation root `README.md` and `AGENTS.md`.
- Added `docs/environment_parameters.md` with source-backed environment rules,
  selected tuning, hardware settings, effective configuration owners, and
  mount/instruction-discovery limitations.
- Added four versioned external-root documents and their index in
  `docs/environment_guides/`; installed exact copies as `README.md`/`AGENTS.md`
  in `/home/mattb/physical_TB3_files_snapshot` and `/home/mattb/tb3-pi`.
- Updated the Phase 10 plan/status/handoff and current checkpoint for this
  documentation amendment. The frozen report and historical results are intact.

The mount point was checked with `findmnt --mountpoint /home/mattb/tb3-pi`:
exit 1, no exact mount. Guide writes used an open directory descriptor verified
on the laptop filesystem and exclusive new-file creation. No mount/unmount,
SSH session, transfer, Pi build, device access, Gazebo, or robot graph occurred.
Physical code evidence is the offline source refreshed earlier on 2026-09-08.
The guides accurately state that local mount-point files are hidden by SSHFS.

## Source review and checks

Independent read-only simulation and physical audits traced the selected
scenario/wrapper, launch defaults/overrides, node constructors, controller JSON,
recorder contract, and hardware adapters. Cross-review verified the resulting
tables. Shared geometry/gains/equal selected values are omitted; tuning is not
presented as a universal environmental invariant.

The one-off documentation audit passed **55 assertions**, **25 local links**,
and balanced fences in **12 Markdown files**, including all four deployed
copies. It verified parsed XML defaults, selected controller JSON speeds,
parsed heartbeat contracts, physical wrapper clock/startup/evidence selection,
shared clock/Gaussian source parity, the unmounted destination, exact deployed
bytes, and zero runtime Git changes. Its structured results and external-file
SHA-256 hashes are retained in
[`environment_guidance_checks.json`](environment_guidance_checks.json).
Untracked guide paths were inspected explicitly; `git diff --stat` alone does
not include those files.

Corrections during the audit were documentation/checker corrections only:
the shared helper, not the bare rclpy default, controls absent clock overrides;
serial port uses the wrapper CLI rather than an exported variable;
startup timeout applies to controller and supervisor; rotation initialization
has different owners/units. The first one-off assertion expected an unquoted
shell assignment; parsing the actual quoted value fixed the checker, with no
source edit. The physical PDE cost-history difference was traced to retained
history/legacy fitting, while selected robust estimation uses typed raw samples.

## Exact validation commands and outcomes

From `/home/mattb/dsim-lab`:

```bash
timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 implement
timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh 10
timeout 30s python3 /tmp/dsim_environment_guidance_validation/check_guidance.py
git diff --check
```

All exit 0. Context reports `Phase 10 implement context is complete.` The
required-doc helper reports `All Phase 00 audit documents exist.` This is not
a rerun of the original report coverage/PDF validation.

Existing clock tests, each independently bounded:

```bash
timeout 120s bash /tmp/dsim_environment_guidance_validation/run_clock_configuration.sh /home/mattb/dsim-lab/ros2_ws/src/ros_esc
timeout 120s bash /tmp/dsim_environment_guidance_validation/run_clock_configuration.sh /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ros_esc
```

The helper sources `/opt/ros/humble/setup.bash` and the canonical
`ros2_ws/install/setup.bash` for generated interfaces; prepends its `$1` source
root to `PYTHONPATH`; asserts clock/fill/PDE imports are under that source root;
sets `PYTHONDONTWRITEBYTECODE=1`, `ROS_DOMAIN_ID=214`, `ROS_LOCALHOST_ONLY=1`,
and a temporary `ROS_LOG_DIR`; then runs:

```bash
/usr/bin/python3 -m pytest -q -p no:cacheprovider "$1/test/test_clock_configuration.py"
```

- Canonical source: **16 passed in 0.86s**, exit 0.
- Physical snapshot source: **16 passed in 0.79s**, exit 0.

Exact helper and commands: `/tmp/dsim_environment_guidance_validation/` contains
`run_clock_configuration.sh`, `clock_commands.txt`, `check_guidance.py`,
`clock_canonical.log`, `clock_physical_snapshot.log`, and `guidance_checks.json`.
These temporary logs supplement the committed results here. No new tests were
added. These existing tests instantiate isolated host ROS nodes; they do not
launch either experiment graph or access hardware.

Final administrative checkpoint:

```bash
timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh 10
```

The generated `checkpoints/phase_10_checkpoint.txt` is the current precommit
documentation boundary. No simulation matrix, physical run, hardware readiness
check, source transfer, report recompilation, or broad regression was needed
for these prose-only changes. None is claimed as performed.

## Final V1 commit checks

The closeout review found exactly the 14 intended documentation/validation
files and no unrelated or runtime changes. Existing 32 passing clock tests
remain applicable: the final edit only adds closure wording. Final context
validation passed; documentation review passed 30 local links, balanced
fences, four recorded guide hashes, and the exact 14-file scope. Staged
diff/scope checks run before the final local commit. The commit is followed by `git status --porcelain`
and a check that the final commit subject matches the recorded boundary.
No push is included; do not create a follow-up commit merely to insert the
new commit hash or postcommit status into these records.
