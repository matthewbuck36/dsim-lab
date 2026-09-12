# M4v14 comparison: closed incomplete

The sole frozen batch, tool session40999, is terminal/reaped1 after2976.356462s
(49.61 minutes). Ten recordings are complete: four retained V13 development
recordings and six fresh V14 confirmations. Slot11 is incomplete; slots12–16
remain unstarted. No replacements, tuning, physical work, commits or pushes ran.
The full research goal is not complete.

## Full sixteen-slot disposition

All times below are simulation seconds. Arrival means entering the evaluator's
0.5m global region after local recovery; GOAL_HOLD is optional. The table keeps
native observed arrival separate from qualification of its recorded time.

| Slot | Population / condition | Arm | Recording | Global arrival | Other outcome |
|---:|---|---|---|---|---|
| 1 | Retained development / nominal | A | Complete | No | No local recovery |
| 2 | Retained development / nominal | B | Complete | 314.098 | Recovery passed |
| 3 | Retained development / nominal | C | Complete | 136.567 | Recovery, continuous motion and direction passed |
| 4 | Retained development / nominal | D | Complete | 147.998 | Recovery, continuous motion and direction passed |
| 5 | Fresh confirmation / nominal | A | Complete | No | No local recovery |
| 6 | Fresh confirmation / nominal | B | Complete | 286.132 | All11 runtime predicates passed |
| 7 | Fresh confirmation / nominal | C | Complete | 135.953, native only | Command consistency failed; qualified arrival join withheld |
| 8 | Fresh confirmation / nominal | D | Complete | 171.882 | All11 runtime predicates and all9 per-run measurement checks passed |
| 9 | Fresh confirmation / noise | A | Complete | No, native result | Block science not run |
| 10 | Fresh confirmation / noise | B | Complete | 329.232, native only | All11 runtime predicates passed; block science not run |
| 11 | Fresh confirmation / noise | C | Incomplete | Unavailable | Lifecycle recording-integrity failure |
| 12 | Fresh confirmation / noise | D | Unstarted | Unavailable | Withheld after slot11 |
| 13 | Fresh confirmation / delay | A | Unstarted | Unavailable | Withheld after slot11 |
| 14 | Fresh confirmation / delay | B | Unstarted | Unavailable | Withheld after slot11 |
| 15 | Fresh confirmation / delay | C | Unstarted | Unavailable | Withheld after slot11 |
| 16 | Fresh confirmation / delay | D | Unstarted | Unavailable | Withheld after slot11 |

A uses existing PDE detection with stationary sweeps. B uses recurrent_geometry_v3
with stationary recurrent verification. C uses PDE with rolling GESC and moving
angular-profile verification. D uses recurrent_geometry_v3 with the moving package
and authenticated recurrent_trapping_v1. All retain GESC+Gaussian and the frozen
V6 half-gain controller. These are integrated packages with diverging trajectories.

| Completed moving run | Direction median / P90, degrees | Usable / eligible targets | Mandatory stopped acquisitions |
|---|---:|---:|---:|
| Development C | 16.839 / 21.181 | 3 / 3 | 0 |
| Development D | 12.519 / 25.224 | 4 / 4 | 0 |
| Fresh nominal C | 19.578 / 21.163 | 3 / 3 | 0 |
| Fresh nominal D | 20.501 / 23.992 | 4 / 4 | 0 |

Each completed C/D reference retains all24 scheduled targets. The full comparison
retains48 development and144 confirmation target slots; unexposed, missing and
unstarted entries do not become usable observations. D nominal passes its combined
arrival/recovery/continuous/direction checks. D noise and delay remain unavailable.
The reference is observed-phase stationary GESC under the recorded augmented
objective, not a spatial gradient. No broad robustness or detector-speed claim is
inferred from arrival-time differences.

## Retained failures and reporting

Slot11's exact failed completeness checks are `v2_lifecycle_contract` and
`algorithm_event_source_causality`. The latter cascades from the lifecycle error:
`guidance approach hides an admitted collection`. Final zero, final readiness
false, readable bag, clean console, clean shutdown metadata, and native/outer
cleanup passed. The dispatcher did not reach its separate inner-cleanup audit
after the integrity rejection. Stage A separately expired after360.026 simulated
seconds, four verification attempts and no fill/escape/arrival. That native
behavioral observation does not make the incomplete recording qualified.
The exact rejected guidance record is absent from the validated projection;
its precise cause needs a targeted retained-data diagnosis. No repair is implied.

Fresh nominal labels and both numerical reference jobs completed successfully.
The native block summary timed out during final source hashing under its7s work
allowance. Its unavailable result remains unchanged. C7 additionally fails command
consistency, so its qualified recorded arrival time remains null. A zero prefix
counter in that failed direct-escape check does not mean GESC was zero throughout.

A separately planned cached supplement used the existing aggregate/formatting
owners once, without bags, normalized-array reads, labels, references or simulation
reruns. It attaches completed reference products to copies of completed label rows,
preserves every other check and arrival join, and retains original native block
failures. It is separate component evidence; it does not repair native block1.
Sole session99679 is terminal/reaped0:0.805374s,50 direct input/source pins stable.
Native final reporting also completed in7.560121s and remains unchanged.

## Exact evidence and recovery

External experiment base: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Pilot: `pilot/m4_pilot_v14/`. Work: `development/20260911/m4_v14_source_v1/`.

- Terminal execution: work `acquisition_execution_v1.json`, SHA256
  `98214067564e30d4d833c0f8ad01740e76402f294f120232b4d507c8c4a829ee`.
- Native ledger: pilot `acquisition/acquisition.json`, all16 dispositions.
- Native final: pilot `report/report_receipt.json`; result SHA256
  `9010fbc5a38a5c34e570c5d19176a908f9dd233afdd41062ce95800e9e907619`.
- Supplement: work `supplemental_cached_report_v1/report.md` and `result.json`;
  receipt SHA256 `434179ac2d85f609376a8eacb9f42b24fcebbbd631e67c39a92b86e6e1ed525d`.
- Slot11 diagnosis: work `slot11_integrity_diagnosis_v1.json`, nine cached checks,
  SHA256 `4aac8942780c1bf7ab8de5a1c1c188e9dd4c6e6dc2aa03535760f84145ad6ae1`.
- Source/preparation/release: unchanged [execution](validation/m4_v14_execution.md).
- In-flight evidence and prospectively adopted supplement bound: unchanged
  [runtime record](validation/m4_v14_runtime.md). It is now input-pinned by the
  supplement; subsequent closeout updates belong here and in live status/handoff.

Source validation remains776 focused tests passed, including131 V14 tests;
no new tests or runtime changes were made in closeout. Preserve source, helpers,
contract, root plan, original raw data and all failed versions. Current branch is
`feature/gesc-gaussian-robustness-v2` at
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`, with36 tracked modified files and the
existing task-owned untracked V2 work. No commit/push authorization is inferred.

The original independently labelled >=30% latency endpoint is unachieved:
0/12 observed confirmation endpoints and0/6 complete pairs. R10's finite selected
response/control evidence is separate. Nominal first residences last only
0.986/5.712/8.704/4.522s for A/B/C/D, below the unchanged12s requirement. No later
residence or arrival time is substituted. The full research goal remains open.

Next incomplete criterion: identify the rejected C11 guidance and its associated
admission ordering from retained evidence through existing owners, with a separately
bounded diagnostic plan before any scan or repair. No new matrix is scheduled.
Independent cached closeout/supplement review and material checkpoint are recorded
in the live status when complete; they prove evidence integrity, not qualification.

## Independent closeout verification

Terminal cached review PASS31 in0.271s: exact16ledger, retained references,
7freshattempts, native final receipt, summary timeout and absent science blocks
verified. All1129small frozen source pins match;28large/array/archive pins are
explicitly skipped. All308recorded fresh-case/science process identities are
absent by PID plus start_ticks, with no inspection errors or reused PIDs. Outer
driver161895 and dispatcher161928 are absent. Review SHA256
`07f3638f511360783237d4417e3642701b14f48d90b30f68186e039bce02e3a7`.

Separate supplemental review PASS28 in0.179235s; all50directpins remain current,
outputs match, only four direction fields were attached to each copied C7/D8
row, and all missing/failed outcomes and denominators remain unchanged. Review
SHA256 `6761417b7e452f4216f232cacdbe91e861a3ac5e8f677d5ebe4a500d132dff26`.
No scientific owner or source tests were rerun. Context validation and
`git diff --check` pass. These reviews establish the integrity of a closed
incomplete experiment and its separately labelled component report.

Material closure uses the existing `save_source_checkpoint.py` implementation
without changing it: only its exclusive OUT is redirected to
`checkpoints/m4_v14_closed_v1` and its manifest scope is labelled terminal
comparison closure. One command is bounded by30s. It copies and verifies each
dirty/untracked source member, retains Git patches, and hashes external evidence
files under the existing V14 work root. Raw bags are outside that scope. The
resulting manifest is recorded in live status after the checkpoint succeeds.

Material archive COMPLETE:684individually verified source members in0.975124s.
Manifest SHA256 `c93292e8121d1c1732cc035c531779e23ddc544ce545bbe6314909b8411ca5c5`
at `checkpoints/m4_v14_closed_v1/manifest.json`. The archive captures the source
and evidence before this receipt annotation. V14 closeout is complete; the full
research goal remains open. No acquisition process is running.
