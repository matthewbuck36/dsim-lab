# M4 pilot v1: closed incomplete

Verified 2026-09-09. The single authorized dispatcher stopped after its first
development case because outer process-ownership inspection failed. The fixed
version is CLOSED_INCOMPLETE: one INCOMPLETE slot and fifteen UNSTARTED slots.
The full V2 objective remains IN_PROGRESS. Neither research improvement is
established; this is an honest interrupted comparison, not a completed 16-run
experiment or an algorithm-performance failure.

## Alignment with the two goals

The user's email attachment describes slow/missed convergence while circling
and the need for robust direction estimation during continuous search. The
approved [parent plan](../plan.md) retains both goals. Q7's user-selected
two-block means address positional settling detection. M2/Q2 direction work
and M3 moving verification/design address continuous search without mandatory
stopped acquisition. The email is methodological context, not separate
authorization or evidence that the exact Q7 formula came from its author.

Q7 is implemented and source-validated: 400 integrated checks, including
actual detector/stationary/moving DDS, with PDE and five-shift modes retained.
M4 preparation/dispatch/evaluation source validation covers 767 unique passing
tests in their correct installation contexts. These are source results, not
measured faster detection or better moving directions. See
[Q7 validation](q7_two_block_method.md) and
[M4 source validation](m4_source_validation.md).

## Attempt and retained inner result

External paths below are relative to
`/home/mattb/Experiments/GESC-Gaussian/v2/`.

- Root: `pilot/m4_pilot_v1/`; one dispatcher, 424.712260195 s elapsed.
- Slot 1: A, primary visible development, seed 26090801, inherited detector
  and stationary search. Actual run directory:
  `runs/2026-09-09/m4-pilot-v1-slot01-A-26090801/` beneath that pilot root.
- Existing `scenario_result.yaml` classification: 14/14 required predicates
  PASS; local fill -> escape (including assist) -> SEARCH -> ranked GOAL_HOLD.
  The live evaluator's post-recovery proximity sample is at simulation time
  309.709 s, distance 0.149797183 m. This is a retained existing-run observation,
  not the unavailable M4 science time-to-goal metric.
- `metadata.yaml`: recording finalized, infrastructure completed, complete and
  final zero observed; target and bag clean exits 0, no run/cleanup errors.
  `completeness.json`: PASS with no failures or warnings. Inner strict cleanup
  and inner process-ownership inspection PASS.
- Outer child: exit 0, not timed out. Its periodic ownership tracker recorded
  `ProcessLookupError: [Errno 3] process disappeared before child enumeration`.
  Consequently outer `inspection_complete=false` and cleanup FAIL.

The outer cleanup error text is `inner recorder ownership is absent or
incomplete`; that generic helper message refers here to the outer tracked
child. The early ownership gate skips the final inspection loop. Its empty
`remaining_*` arrays are initialized defaults, **not evidence that the outer
graph/process/session inspection found nothing**. This establishes incomplete
outer proof; it does not establish that a process actually remained alive.

The failure occurred before the dispatcher admitted slot 1's inner result and
recorded binding into M4 science. The immutable auto-report therefore correctly
leaves its behavior/science unavailable. The separate inner success above does
not override that disposition. Slots 2–16 were never dispatched; the repeated
failure reason on their ledger rows is the stop reason, not fifteen additional
failed runs. B/D's new detector and C/D's moving policy were not exercised by
this M4 attempt. No block science job or holdout release occurred.

## Research report and denominators

The dispatcher wrote `report/report.md`, `report/result.json` and
`report/report_receipt.json` under the pilot root. Preserve these exact files.

| Target | This version |
| --- | --- |
| Confirmation latency >=30% lower without additional wrong fills/goals | EVIDENCE_UNAVAILABLE; 0/12 observed holdout endpoints, 0/6 pairs |
| Direction median <=30 degrees, p90 <=60 degrees, availability >=80% | EVIDENCE_UNAVAILABLE; 0 informative eligible holdout targets out of 144 scheduled |
| Zero mandatory stopped acquisition | EVIDENCE_UNAVAILABLE; no accepted C/D recording |
| Combined fill/escape/SEARCH/stronger candidate in each holdout condition | EVIDENCE_UNAVAILABLE; all holdouts unstarted |

All 192 unique direction slots remain explicit: 24 fixed offsets for each of
eight C/D runs, 48 development plus 144 holdout. Every row is analysis-unavailable.
Time-to-goal, path, jitter, lag and fallback science metrics remain unavailable,
never zero. Wrong-fill/goal counts and stopped-acquisition attribution are not
inferred from the baseline or missing recordings.

## Execution and verification receipts

The exact dispatched command, in the frozen Q2/Q5 overlay environment with
`ROS_DOMAIN_ID=181`, `ROS_LOCALHOST_ONLY=1`, `DISPLAY=:0`, was:

```bash
timeout --signal=SIGINT --kill-after=120s 15180s /usr/bin/python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/run_m4.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v1/preflight/contract.json
```

Exit 1; no renewed deadline, rerun or replacement. Console:
`builds/m4_pilot_runtime_v1/acquisition_dispatch_console_v1.log`.
The earlier noclobber console-name collision occurred before any dispatcher
started and is retained in `preflight/console_destination.json`.

| Receipt | SHA256 |
| --- | --- |
| `pilot/m4_pilot_v1/preflight/contract.json` | `b6366e66a8d2bfc8c05e428a2214dbfe5b0e5578164f5b1328d8dc36a50a9e77` |
| `pilot/m4_pilot_v1/acquisition/acquisition.json` | `3100668df800072184ec370735a8753e697c9ef41dd0e4c3de9c8415571ca2e7` |
| `pilot/m4_pilot_v1/report/result.json` | `507ba41f16f89d79fa40670b1a6f89f64c5acda4cd13e843506ed668c10259c5` |
| `pilot/m4_pilot_v1/report/report.md` | `f3ac4a97a3efa50dd8a529503d55a69d23e53822176fbdd5d277e4aaec50228a` |
| `pilot/m4_pilot_v1/report/report_receipt.json` | `20b1ce77268511b635316502a41196680d4c5d8d8a06ed177bb88ae30e622cf5` |
| `builds/m4_pilot_runtime_v1/first_slot_observation_receipt_v1.json` | `4af58eb20d25840e2128b659f82f5d59214f041c584ce8edb894f26867bd8a28` |
| `builds/m4_pilot_runtime_v1/pilot_closure_audit_v1.json` | `5e84418252b2a95aa7d2a646bdbc2f0bc2b10b19a18ee0c92b3f0df2d0f53c6e` |

The bounded closure audit (`timeout 60s python3 -`, inline read-only hash/JSON/
YAML assertions) completed in 0.836127 s. It verified all 606 frozen source
hashes unchanged, the 16-slot disposition and 192 direction rows, no block
analysis/replacements/release, and retained all 50 pilot file hashes including
the bag (264687338 bytes total). The independent review also verified all 20
referenced contract/slot/final hashes, exact frozen row identities, summary-to-
scenario equality and actual launch argv against recorder metadata. No bag was
decoded again, simulation repeated or scientific budget renewed for closeout.

Closeout checks PASS: `timeout 30s
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
v2 implement`, `git diff --check`, and the bounded read-only local-link/source
audit (22 resolved links, 606 unchanged pins, expected branch/HEAD). The existing
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh
v2` wrote `checkpoint.txt`. No new runtime tests were needed for these
documentation-only changes. The material archive receipt is appended to current
status after creation; source validation remains the existing pinned result.

## Next boundary

Preserve v1 exactly and diagnose the disappearing-process race in the existing
runner's optional ownership tracker. Do not just ignore the exception or mark
empty default arrays as a cleanup pass: a vanished parent can leave descendants.
A bounded source correction needs a separately saved amendment, a finite
reproducer and strict error/cancellation/identity regressions before fresh
runtime evidence. The fixed v1 cannot resume or accept replacements under
[the adopted execution plan](../m4_execution_evaluation_plan.md).

Read-only source diagnosis narrows the uncertainty: `_process_children` read
a process identity, failed to read that process's child list and confirmed
the identity had disappeared. `_snapshot_process_tree` attached its partial
snapshot to the exception, but `_track_owned_processes` retained only a generic
error. The failing PID and observation time cannot be recovered from the
receipt. Retaining bounded PID/identity/operation/time/partial-snapshot context
and explicitly reporting skipped inspections as unknown would improve future
diagnosis while still failing closed. A passing route for this race requires
a prospectively reviewed ownership witness that survives intermediary exit;
retrying enumeration or substituting prior observations is insufficient under
the existing M4A requirement. No such correction or witness is implemented by
this closeout, and no source gate has been relaxed.

A fresh comparison would require a separate experiment/version and reviewed
release; it cannot borrow slot 1 or silently expand the approved 16-run budget.
No fresh acquisition is released by this report. Source remains held at the
failed attempt's 606 pins. Q7, Q5, Q6, M4A and older retained failures stay intact.
Branch remains `feature/gesc-gaussian-robustness-v2`, HEAD `3369cfc83a64ff5d8354827fd5310caaf0c8e945`,
with saved uncommitted changes. No commit, push, V1, physical snapshot, Pi or
hardware action occurred.
