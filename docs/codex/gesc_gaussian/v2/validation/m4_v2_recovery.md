# M4 v2 recovery validation

Status: CLOSED_SOURCE_VALIDATION_PASS, 2026-09-10 UTC. Active amendment:
[m4_v2_recovery_plan.md](../m4_v2_recovery_plan.md). This record distinguishes
the source correction, finite process evidence and future simulation results.
No fresh pilot is released by this file.

## Verified entry state and authority

User resumed the full V2 goal with authority to make recommended changes
without additional questions. Existing Q7 source validation is retained; the
current correction addresses ownership proof, not detector or GESC retuning.
Branch `feature/gesc-gaussian-robustness-v2`, HEAD `3369cfc83a64ff5d8354827fd5310caaf0c8e945`.
Context validator PASS and all606 M4 v1 frozen source hashes matched before
edits. Read-only current procfs command inspection found no active Gazebo,
M4 dispatcher, scenario runner or recorder owner. Display0 socket and selected
Xauthority file exist; this is preparation information, not a launched graph.

The previous goal turn produced evidence/report/checkpoint and therefore counts
as progress. V1's terminal acquisition is INCOMPLETE,424.712260195s, with one
attempted A and15 unstarted. The immutable closure manifest remains
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m4_pilot_closed_incomplete_v1/manifest.json`,
SHA256 `31e01fcf9bfe5c341391a93f896ffc0ff4f33bc8371f3deecef25c5430409e4d`.
Do not use live amended source to replay or relabel its acceptance.

## Kernel proof rationale and limits

Linux reparents an orphan to its nearest living ancestor subreaper. The flag
persists through exec but is not inherited by a newly forked child, so each
selected inner/outer owner must establish its own scope before launching.
This supports a final adoption/reaping witness that survives intermediary exit.
[Linux PR_SET_CHILD_SUBREAPER manual](https://man7.org/linux/man-pages/man2/PR_SET_CHILD_SUBREAPER.2const.html).

A nonblocking wait that returns no exited child does not prove no live child.
The new path must require ECHILD after the direct Popen owner has consumed its
result, with an exclusive reaping scope, default SIGCHLD and no SA_NOCLDWAIT.
Linux __WALL includes clone children; waiting must cover owner threads.
This is a bounded implementation proof under the recorded launch/wait ownership
conditions, not protection against a hostile process changing those conditions.
[Linux wait manual](https://man7.org/linux/man-pages/man2/waitpid.2.html).

Procfs child lists can omit children while other children exit. Keep snapshots
as identity/context evidence, but do not treat an empty or retried child list as
complete final ownership proof. The old selected strict route remains unchanged.
[Linux proc_tid_children manual](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html).

Read-only host checks: Linux6.8.0-138, PR_GET_CHILD_SUBREAPER succeeds/current0;
user systemd249.11 and cgroupv2 delegation are available. No cgroup/systemd
mutation is selected. The implementation must reject unsupported ABI/reaper
conditions explicitly, preserve identity-bound signaling and all final-zero,
recording, graph and inclusive deadline gates.

## Validation sequence and external owners

New logs, original source copies, finite fixture receipts and integrated checks
belong to `/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v2_recovery_v1/`.
`root_source_validation.py` is the prepared integrated validation wrapper,
not a completed result. It retains exact commands, JUnit test identities,
actual installed console bindings, before/after source hashes and all failures.
`archive_boundary.py` creates exclusive material checkpoints and verifies their
tar bytes; it also hashes every fresh pilot file including bags when present.

Pending: old failure reproducer, new inner/outer/science process proof, explicit
version selection and rejection, focused regressions, independent adversarial
review, integrated held-source check, checkpoint, then one600s preparation.
All science definitions and720/900/15300 execution caps remain unchanged.

## Intermediate retained evidence

The old disappearing-child failure is reproduced in
`legacy_vanished_children_failure_v1.log`. The selected witness's first13
independent process fixtures passed; a subsequent slow-Popen test exposed a
relative-timeout restart (1.454817s versus the original1.2s end). Its failure is
retained in `adversarial_slow_setup_v1.log`, and source is being corrected to
apply the original work deadline after setup in both runner paths. These are
intermediate results, not a closed validation total.

The read-only preservation audit passes for all50 retained M4 v1 files
(264687338 bytes), the Q7 and M4A archives, and the M4 v1 closure archive.
Receipt: `retained_evidence_check_v2.json`, SHA256
`81070ee3f7cb6c07e83461ed52b5c086bf5b04c911e50ad9d45d6a16e10419fc`.
Exact command: `timeout 30s python3 -` with inline streaming-hash assertions;
0.555800s. Its first audit assumed one archive-manifest layout and raised
`KeyError: 'archive'`; `retained_evidence_check_v1.json` preserves that audit
error. Reading the actual named archive receipts resolved the schema mismatch;
no retained evidence bytes or scientific result changed.

Fresh version routing is source-validated: final105 focused checks PASS12.08s,
with v1 default/output parity, exact v2 population/IDs/root, selected ownership
flags and cross-experiment analysis rejection. Receipt:
`versions_source_receipt_v1.json`, SHA256
`8c50b511bd4844eb4218dd09d5e22e2296dd7e5f0f0c78d43cd2301f2fb25a20`.
The original versions_v1/v2 logs are retained; totals overlap and are not added.
Independent review confirms unchanged numerical/geometry/noise/reference owners
and identity-only changes to the metric/evaluator computation paths.

The corrected independent adversarial suite passes20 cases in18.89s, stable
source/test hashes; `adversarial_receipt_v1.json`, SHA256
`5a876ff6f857cb5c8026928006054c9018567afb8693521aefae5ec704a8112a`.
It includes live/zombie baseline rejection without stealing Popen status,
double forks/nested sessions/orphans, unrelated sibling sentinel, native
SIGCHLD flags, true kernel exhaustion with blind procfs observation, PID
substitution, interruption, permissions/malformed/capacity failures and the
original-end slow-start regression. Later owner glue/ABI edits require the
final composed run before release; this is not its result.

Independent native ABI verification compiles `sigaction_abi.c` with
`timeout 20s cc -Wall -Wextra -Werror`, then executes it under10s. Actual glibc2.35
headers report sigaction size152, handler/mask/flags/restorer offsets0/8/136/144,
sigset size128, SA_NOCLDWAIT2 and PR_SET/GET_CHILD_SUBREAPER36/37. All match the
selected binding. Receipt `sigaction_abi_receipt.json`, SHA256
`597921e18a96806313f2f13041ae5380a832cae39ac01909258c028060cbbffa`, retains
exact commands, C source and executable hashes. No signal or reaper state was
changed by this read-only probe; runtime separately rejects unsupported libc/ABI.


## Final source boundary

Final integrated validation passes **794 unique tests**, one predeclared Gazebo
E2E deselected, pytest118.94s / wrapper119.769728s. All610 collected source and
configuration pins are identical before/after. Receipt:
`root_final_v1_receipt.json`, SHA256 `ea4b3673ab5a4321558898e2f62cd08a2aea1678ee0f87090c4e8e0941a47c25`.
The receipt retains every JUnit identity, command, environment and installed
binding; `root_final_v1_junit.xml` and `root_final_v1.log` retain raw results.
Earlier focused totals overlap and must not be added to794.

The final ownership/routes/science invocation passed93 checks36.62s, including
24 selected-route checks,20 adversarial checks and49 inherited deadline/science
regressions. `ownership_routes_receipt_v1.json`, SHA256
`5ce37d72f70b1f44f2f1b1f9da28e3fdaf18de1ef5800932e392d2b7bb6a1e8a`,
records that its first hash sample occurred during that run. The integrated
receipt above supplies complete before/after binding and includes these checks.

Actual installed `run_scenario --help` and `record_run --help` pass under20s
per command. The selected runner exposes `--process-ownership-mode` with
`subreaper_v2`. `actual_entrypoints_v1.json`, SHA256
`65090b0713a2cb4afa7ec600ea5212159f0a26f7498c95679dbd85a3232b735f`,
binds commands and log bytes; integrated validation binds21 Q5 installed console
targets to live source. Historical Q1/Q2 installation-specific checks retain
their previously validated environments; they were not run under the wrong Q5
selection again. No IDL/entrypoint changes or rebuild were required.

Exact validation environment and outer command:

```bash
env -u PYTHONPATH ROS_DOMAIN_ID=182 ROS_LOCALHOST_ONLY=1 bash --noprofile --norc -c '
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/install/local_setup.bash
export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src"
timeout --signal=SIGINT --kill-after=10s 510s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v2_recovery_v1/root_source_validation.py root_final_v1'
```

Its exact subordinate pytest argv is saved in the receipt (480s work timeout,
10s kill grace,495s subprocess bound). All11 `test_m4*.py` files plus11 selected
runner/legacy/study/Q7 analysis regression files run in this same held context.

Implementation is optional `subreaper_v2` inside existing runner/science owners;
`observed_tree_v1` stays the default. Real fixtures establish direct-child
status preservation, selected plain/specialized/science routing, native SIGCHLD
admission, kernel ECHILD exhaustion, PID-safe bounded cancellation and the
original absolute deadline. Unperformed cleanup checks are explicitly unknown.
The earlier slow-Popen failure remains retained and now passes without renewing
the work end. Proof assumes the controlled caller retains exclusive reaping;
it is not protection against a foreign native waiter changing state.

Fresh `m4-pilot-v2` has an exact independent root, IDs, population and selected
ownership contract. Experiment identity is distinct from unchanged scientific
method `m4-pilot-v1`; v1 output/default parity and cross-version rejection pass.
Q7 detector, Q2/M3 controls, geometry/reference arithmetic and all science/gate
budgets remain unchanged. Old numerical owners are byte-identical to the v1
frozen contract. No fresh Gazebo case or real-bag science budget fit is measured
by source tests. Both original research targets remain unestablished.

Next: source checkpoint/archive, single600s preparation, independent frozen
contract audit and exact release, then four visible development cases and the
one-time twelve-holdout release. Read later receipts before recovery; never
repeat an existing fixed preparation or dispatcher.

Material source archive: `checkpoints/m4_v2_source_closed_v1/manifest.json`,
SHA256 `4f3d88fed0af4e473bde7bcc94432e489a37bc72f06fe5bf16f5de50ef32da0a`;
339 files,51 external artifact references,1346407-byte verified tar. Exact
commands: `timeout 30s .../tools/validate_phase_context.sh v2 implement`,
`git diff --check`, source-pin/local-link assertions, `timeout 30s .../tools/checkpoint_phase.sh v2`,
then `timeout 60s python3 builds/m4_v2_recovery_v1/archive_boundary.py m4_v2_source_closed_v1`
with the repository package and external experiment prefixes shown above.
All PASS. This receipt postdates the immutable archive; pinned source is held.

## Preparation and frozen audit

M4v2 preparation and independent frozen audit PASS,2026-09-10 UTC.
Single preparation completed43.516013s inside the600s cap; no acquisition.
Contract `pilot/m4_pilot_v2/preflight/contract.json`, SHA256
`f2bff98bab52b29e0d8cb6ae56a20dec62baa51c9b980b6cdb8e275c8617a352`;
prepared receipt SHA256
`48c1d447278ae766237dead8772125b4f8abe3aaf283ea80c1da0bd0fda4883f`.
External `builds/m4_v2_recovery_v1/preparation_v1_receipt.json` retains exact
command/log/time. The independent audit ran once under30s (2.898473s), without
bag decoding or field reevaluation, and matched all610 validated source pins,
all16 exact versioned slots/launch commands, Q7/Q2 selections, original geometry,
secondary topology/noise/delay/configuration receipts and all execution/science
budgets. `preflight/frozen_audit_v1.json`, SHA256
`82ec70831e6e5b845c0adfc5d39dcefb3f2fffb0e2e57b7fb367a6ad3836b603`.
Environment is clean Q2 then Q5 overlays, domain182/local-only, DISPLAY0.
Exact audit command is `timeout 30s /usr/bin/python3` on external
`builds/m4_v2_recovery_v1/frozen_audit_v1.py`, in the validation environment above.
No preparation retry, science result, holdout release or acquisition is implied.
Next: material preparation archive and exact dispatcher release, then the
single approved four-development/twelve-holdout comparison.

## Exact acquisition release

M4v2 DISPATCH RELEASED, single acquisition starting. Release
 `pilot/m4_pilot_v2/preflight/dispatch_release.json`, SHA256
 `4df11bdebb54831a2cab48f25293fba63dba21861ebcc79c3d4ed177f04a22e5`,
 binds contract/source validation/actual CLI/audit/archives and exact initial
 slots1-4. Preparation checkpoint SHA256
 `ca2d7dab98beadaa0704455f5e3fdd73a62f8247b5cc9c65db0a8808975dc865`.
 Exact outer command SIGINT15180s/kill-after120s caps15300s total; source is held.
 Console: `builds/m4_v2_recovery_v1/acquisition_dispatch_console_v1.log`.
 Read fresh `acquisition/started.json`, slot receipts and `acquisition.json`
 before recovery. Never restart or replace a slot; holdout release is separate.


Independent read-only review verified610 source pins and44 installed metadata/
wrapper/module pins. Seven prior files changed within planned ownership/version
scope;599 prior frozen files remain byte-identical. Legacy runner body/defaults,
numerics and scientific settings are preserved. Preparation archive contains
339 files/66 artifact references/1347885-byte verified tar. Bounded release
helper `builds/m4_v2_recovery_v1/release_dispatch_v1.py` independently requires
audit PASS and exact contract/source/environment, then calls the public release
validator under30s. It performs no acquisition itself.
