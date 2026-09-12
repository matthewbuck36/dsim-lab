# R23 guidance/admission correction: complete

R23 identified and corrected the timestamp-ordering validator defect that stopped
V14 at C11. No runtime algorithm changed and no old recording/report was rewritten.
The broader research goal and remaining noise/delay comparison conditions stay open.

The retained C11 stream has exactly one original predicate violation: valid
APPROACH publication3234 followed by valid COLLECT3235 at the same162.0-second
simulation tick, candidate2/epoch2, accepted161.9s. The first reports admitted_at=0;
the second reports162.0s, matching the unique stage event. State companion and pose
match; each phase retains its correct deadline. No subsequent phase regression
occurred. The runtime publication sequence establishes the earlier/later order;
cross-topic receipt order is not used as proof.

The existing validator now defers only equal-timestamp approach rows after every
original identity/state/pose/deadline check passes. Only the FIRST fully validated
COLLECT for that candidate/epoch/admission can resolve it, and that witness must
have a higher sequence, the admission timestamp and VERIFY state. Missing, invalid,
later-timestamp or earlier-sequence witnesses cannot rescue it. Unresolved rows
retain the original error and are omitted from accepted metrics. Each row still
requires its own exact state companion; identical state hashes are not required.

Only v2_lifecycle_validation.py and test_v2_lifecycle_recording.py changed. Exact
before bytes, source hashes and the reviewed patch remain under external
`development/20260911/r23_guidance_admission_v1/` in the V2 experiment root.

| Evidence | Result |
|---|---|
| One filtered retained capture, session56208 | Terminal0,2.945496s;14small pins and raw file stats stable |
| Independent capture review | PASS31;18,183 records and all payload hashes checked |
| Independent source review | PASS;all old test functions unchanged |
| Focused tests, session32887 | Terminal0;187passed in48.55s,including13new cases;0failures/skips |
| Source/test inputs | All four focused input hashes stable through execution |
| Runtime/scientific work | No simulation, numerical reference or full bag revalidation |

The focused command used the existing sourced R21 environment and
`timeout --signal=INT --kill-after=5s 60s /usr/bin/python3 -B -m pytest -q -p no:cacheprovider`
for test_v2_lifecycle_recording.py, test_v2_lifecycle_contract.py and
test_r21_trapping_recording.py. Complete output is retained in focused_v1/pytest.log.
These are serialized-wire/contract tests, not a new empirical recovery success.

Exact SHA256 receipts:

- Capture: `50eabf33b48f642806227a9585e54d1384b5c7353a6cabebc6a50669440d99fd`.
- Capture review: `068c325842cf2c6081ad8f561b313753b13155ac773960f67541bc4692d82fa1`.
- Source review: `0a4a5bb9fa3a56bd5bda2acaf24c1594c550a68ad924fd031e80f4e7a8bb31c0`.
- Focused source validation: `5628194dc82f6a520b132306871fed28e987941fc533f51da428559b7cb79413`.
- Exact validated patch: `3d3b06f2f6536770eb7f56af0cd167c24dc976f24758a2c8a331b12ac04089f2`.
- Corrected validator: `f18906fce8e6994f5d803995ad7b78c427b9d965024476069010ddb9d8d92710`.

Original C11 remains INCOMPLETE; its separate360.026s Stage A nonarrival and V14's
five UNSTARTED slots remain unchanged. R23 does not claim that every C11 integrity
check has now passed: the single filtered capture was not a full revalidation.
V14 source pins refer to its archived validator bytes; do not reopen its dispatcher.

Next incomplete criterion: through existing owners and a prospective bounded plan,
establish whether retained C11 can supply a separately qualified baseline failure
under the corrected validator, then finish the missing noise/delay comparisons
with explicit provenance and preserved original failures. Avoid rerunning complete
recordings or building another comparison-version infrastructure loop. No new
simulation is released by this handoff. Original30% independent latency remains
unachieved/unavailable; arrivals and R10 component responses do not replace it.

Git remains feature/gesc-gaussian-robustness-v2 at3369cfc with existing task changes.
No commit/push, physical/Pi/snapshot or V1 work. Source material checkpoint and
context/diff checks are recorded in live status before the next milestone.

R23 source correction COMPLETE: focused187PASS (13new), independent source review
PASS. Validation receipt5628194dc82f6a520b132306871fed28e987941fc533f51da428559b7cb79413.
Material archive688verified members,1.002444s, manifest
91e4e9f3f885a76d24b4ca1c93413a3019064ef15fc33fc92fa90db4431d91f2
at checkpoints/r23_guidance_admission_closed_v1/. The unchanged existing
save_source_checkpoint.py implementation was scoped to this exclusive OUT and
the R23 EVIDENCE directory under a30s bound; no helper source was modified.
Current phase plan updated after V14 closure; V14 archived plan/source unchanged.
Context and diff checks pass. This annotation follows the archived source snapshot.
No simulation is running; full goal and missing comparison conditions stay open.
