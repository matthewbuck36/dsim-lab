# M4 v2 result and shutdown-delivery postmortem

Status: CLOSED_INCOMPLETE,2026-09-10 UTC. Full V2 remains IN_PROGRESS.
The single released dispatcher exited1 after536.403020s, within the15300s
suite and900s first-case limits. One baseline A slot is INCOMPLETE;15 slots
are UNSTARTED. No replacement, block science or holdout release occurred.

## Verified outcome and evidence limits

The new inner/outer subreaper ownership witnesses both pass all eight kernel
flags, including actual ECHILD, root reaping and restored state. Existing
inner and outer graph/session/identity cleanup checks were performed and pass.
The later independently repeated inner check in the dispatcher was not reached
because recording validation failed; do not imply that skipped check passed.

Recorder completeness is false: `completeness.json` remains the initial
`run did not finalize` result; metadata remains `recording`, `complete:false`.
The retained401125376-byte `bag/bag_0.db3` has no final bag metadata. The ordinary
analyzer could not initialize storage, so behavioral outcomes and final-zero
integrity are unavailable. No reindex, recovery, relabeling or analysis retry
was performed on this fixed evidence.

Live monitor evidence separately recorded local recovery, fill cardinality,
ranked GOAL_HOLD and a noninterpolated global-proximity sample at306.217sim s,
distance0.127911730m. Those are retained live receipts, not admitted M4 science
or proof of finalized recording/final zero. The console's `operator requested
shutdown` is recorder wording for its signal path; no human intervention was
performed by this continuation.

All16 slots and192 scheduled direction rows are present in the immutable report
(48 development,144 holdout). Latency has0/12 observed endpoints and0/6 pairs.
Both primary targets, mandatory-stop evidence and combined holdout sequence
remain EVIDENCE_UNAVAILABLE. Missing error counts are not zero. The report lists
the abort cause on unstarted slots as a reason; those slots did not each suffer
a separate recording failure.

## Measured shutdown delivery defect

The selected inner root is the installed `ros2 run` wrapper PID29702; actual
recorder Python is its child PID29703. Saved pidfd signal receipts show SIGINT
only to29702, then SIGTERM to29702 and adopted29703, followed by SIGKILL to
29703 and surviving bag/target descendants. Recorder shutdown acknowledgement
appears at04:25:54.743UTC, followed by partial target shutdown. It never writes
final recording metadata or completeness. Inner root returns-15; outer CLI1.

The selected ownership proof correctly establishes complete cleanup, but its
direct-child-only graceful delivery does not preserve the recorder owner's
normal shutdown opportunity through the extra CLI wrapper. This is a Level B
runner correction, not evidence for retuning detector/GESC or weakening gates.
A follow-up must target the correct graceful recipient with verified identity/
ancestry and preserve the recorder's ordered target-stop/bag-finalization path,
absolute deadlines, legacy defaults and this failed version. Exact installed
wrapper semantics and a matching finite process fixture must precede source
release; no automatic dispatcher restart is authorized within M4v2.

## Immutable receipts

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Run: `pilot/m4_pilot_v2/runs/2026-09-10/m4-pilot-v2-slot01-A-26090801/`.

| Artifact | SHA256 |
| --- | --- |
| `pilot/m4_pilot_v2/preflight/contract.json` | `f2bff98bab52b29e0d8cb6ae56a20dec62baa51c9b980b6cdb8e275c8617a352` |
| `pilot/m4_pilot_v2/acquisition/acquisition.json` | `313dbf1a625f02ff3499cdeffe87789189f733b39428dc13fe08719a8006df0f` |
| `pilot/m4_pilot_v2/acquisition/slot_1.json` | `9b4615522a9f3b6d2d7d894e191a4073233ac1ba9659fb7195ce9d725c6e55da` |
| `pilot/m4_pilot_v2/report/result.json` | `918d162b51f036d48b411323dc3c7ba8d24f220c0c52e62899c27c7589b6dcb7` |
| `pilot/m4_pilot_v2/report/report.md` | `174e305f9a65aa4f42da0f7d6eb36c2e001815a9b577a6af5aa7e741e8ef08c4` |
| `pilot/m4_pilot_v2/report/report_receipt.json` | `eeddd6ce71f3b1441e43336c867960a0ea4399dc9fd9656287b40e4736035eab` |
| `builds/m4_v2_recovery_v1/pilot_closure_audit_v1.json` | `28c0bfd8e276aeed54700915bacf9ca073e89ee4e82ed1c32f3e91f38d80af34` |

Closure audit verifies all610 frozen source pins, report/result hashes, exact
slot/target counts and every46 pilot files/403938081bytes including raw bag.
It performs no scientific reevaluation. Runtime session92843 is terminal exit1,
not an observation timeout. Earlier M4v1 and Q7/M4A/older evidence is preserved.
Branch remains `feature/gesc-gaussian-robustness-v2` at3369cfc with saved
uncommitted task edits; no commit/push, hardware/Pi or V1 change occurred.

Next: material closure checkpoint/archive, then a separately recorded bounded
graceful-delivery amendment and fresh source/process evidence. Full16-run
comparison/report goal remains active; this failed version stays immutable.

## Material closure

M4v2 material closure archived: external
 `checkpoints/m4_v2_closed_incomplete_v1/manifest.json`, SHA256
 `846f535e46e86389fd632cbb1dcf094d9d640f9dc2596ded374b65bd2765f492`;
 341 dirty/untracked files,102 retained artifact references,1351984-byte
 verified source archive. All610 source pins held through closure;46 pilot
 files/403938081bytes including raw bag independently hashed. Context/diff/
 checkpoint PASS; read-only procfs confirms no active case owner. This receipt
 postdates the immutable archive. Next bounded correction needs its own plan.
