# Q2 snapshot serialization source validation

Status: SOURCE VALIDATION PASS; CDR timing v1 stays failed, structural v2 passes.
Read `../q2_snapshot_structural_clone_plan.md`. The three
existing runtime owners now use scoped generated-message cloning and avoid a
discarded canonical traversal. Freshness, deadlines, evidence identities and
transaction ownership are unchanged. Timing, actual transport and1167 held
integrated checks pass; material closeout is recorded in the live status.
No scientific acquisition or M4 release.

All external paths below are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/`.

## Focused ownership and parity

Actual supervisor/Gaussian ownership regressions plus existing focused tests:
**106PASS in15.47s**, `snapshot_serialization_focused_v1.log`. The publication
spy retains the exact supplied object; it cannot hide aliasing by copying.
Checks verify independent source/candidate/publication/command/pending support,
unchanged original deadlines and preserved worker inputs after caller mutation.
The pure owner fixture controls time explicitly; actual DDS will retain original
ROS and steady-clock freshness checks.

Independent generated-wire checks: **38PASS in10.49s**,
`snapshot_clone_contract_v2.log`, SHA256
`22540b825abe5328b8e6cb35878ddc632e35f03f2da6a22ecd4cde1c80026420`.
The original D3 manifest, archive and lifecycle source are SHA-verified before
loading the old hash owner. Synthetic sizes0,1,363,4000 cover exact old hashes,
declared field types/arrays/integers/times, IEEE bits including NaN/infinities/
signed zero and subnormals, Unicode, embedded-NUL rejection before native
conversion, nested two-way mutations and malformed excluded publication stamps.
Both original/deepcopy/clone and decoded serialized messages are checked.

Independent test source SHA256:
`8609b644575df1c57393d5f59bf08f7de5e553223979a46a33fffe7e61470b4f`.
Held lifecycle source SHA256:
`2f0981ff8f6829ca0caabc8d505f399f8402204c25f23b6750888be4cdb1cf41`.

Exact independent invocation, from repository root:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q2_snapshot_clone_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/snapshot_clone_contract_v2.log 2>&1
```

## Retained initial byte-comparison failure

The first independent invocation used the same command and `v1.log`, yielding
**36PASS/2FAIL in52.93s**. Log SHA256
`ff3ce7aa392fcbdd68af2a8f02d917d551caddca07e8a06261bacd5cac5c9d3a`.
Differences were at CDR alignment padding after strings. Local installed
FastCDR `Cdr.h:3513–3519` advances over alignment bytes; `FastBuffer.h:161–165`
advances the position without writing field values. Header SHA256 values:
`9a52c56422b8168f43c8e43f33aa9efc7e1e993077de93e569e808cb4c959294`
and `b0fbd4d37df5b49efb80a91417c7a979746bc96b38acdab71098d98d0cb44290`.

The plan explicitly clarified this before the second test and before any
timing job. Complete field/float-bit/hash/ownership equality remains mandatory;
raw buffer padding is diagnostic, not canonical lifecycle identity. The final
38 tests verify the two bulk cases that stopped early in the first run.
Runtime source did not change between these independent test invocations.

## Fixed CDR timing version: CLOSED FAILED_TIMING_GATE

The single fixed10x363/3x4000 job completed all26 method receipts with unchanged
source hashes and exit1. There was no timeout or parity exception. Retained
`serialization_preflight_v1/results/result.json` SHA256:
`a39aa03dfdfda444738a7e9e41f37bd6f467deb3c74a4d62ab65dfc6b2e18eaf`.
`dispatch_release.json` binds the reviewed script, exact timeout60s command,
fixed population/gates,106/38 test logs and preflight source checkpoint.

Selected363-observation maximum163.631029ms PASSES the200ms gate. Median
old221.797584ms/new150.344311ms gives1.4752642286544517x, FAILING the unchanged
2x improvement requirement. New stage medians: assembly32.218310ms,
publication31.303118ms, command snapshot31.726979ms, send31.607631ms and
hash22.775783ms. The four cloning stages dominate; even removing the hash cost
would not reach2x. Gaussian pending clone median31.917524ms is separate.
At4000 observations, supervisor median1701.142608ms and maximum1715.763749ms
remain unsuitable for a general real-time claim. No4000 timing gate was set.

This fixed version stays failed and must not be rerun. A subsequent source
correction requires a prospective amendment and new timing identity, retaining
the same performance/field/hash/detachment gates. Actual pipeline callback and
readiness evidence, held integrated checks and source closeout remain pending.
The prepared `pipeline_timing_diagnostic_v3` has not executed.

Before timing, the material checkpoint was saved at external
`checkpoints/q2_serialization_preflight_v1/manifest.json`, SHA256
`65e615d2e36aeb6763bfb87a74c5b168c1d9966d87229fb24be415c1f719c093`:
250files,1035187-byte verified archive,400 retained artifact hashes. It is a
preflight boundary, not a passed timing or scientific result.

## Structural correction preflight

`../q2_snapshot_structural_clone_plan.md` was adopted after saved-stage review.
Before changing source, the failed CDR boundary was saved at
`checkpoints/q2_serialization_cdr_failed_v1/manifest.json`, SHA256
`b57b7c2b936973e38687efa4c7a73fd0e2c1ebe2fc13e8ce3f6047a0196b3165`:
251files,1038312-byte verified archive,435 retained artifact hashes. The later
CDR closure receipt `serialization_preflight_v1/closed.json`, SHA256
`6e1690fea4510a7969547f0a6a081f3399f188dbdcec22df21fe17138c690a51`,
binds its completed outputs and failed gate. No CDR timing rerun occurred.

Only `v2_lifecycle.py` changed for the structural correction. Four ordered
schema digests, explicit slots and normalized generated SLOT_TYPES bind the
supported types; a warm plan cache still checks schema drift. Explicit primitive
types/ranges, UTF8/NUL strings and canonical list/array representations precede
private-slot storage. Mutable nested values detach per occurrence. All hash,
envelope and registry functions are AST-identical to the CDR checkpoint; the
supervisor/Gaussian call sites remain held. Source SHA256:
`79658a9203c330cb7de417195549ecb87b8a723a1f656cb27def7ef5cc1008ab`.

Focused owner/lifecycle regressions: **106PASS13.43s**, timeout90s,
`snapshot_structural_focused_v1.log`, SHA256
`1a855a83a347f6bcdad7eae9d3932b9d59db5f0bcba9f121e3f0637924860ed2`.
Exact pytest argv: `python3 -m pytest -q` plus test files
`test_q2_snapshot_serialization.py test_v2_lifecycle_contract.py
test_v2_fill_transactions.py test_v2_supervisor.py` under the usual test directory.
Use env-uPYTHONPATH, Humble then Q2 overlay, append extremum-seeking/src as in
the retained independent invocation; stdout/stderr go to the named log.

Independent contract: **97PASS10.65s**, timeout90s, same invocation pattern as
above with only `test_q2_snapshot_clone_contract.py`; log
`snapshot_structural_contract_v1.log`, SHA256
`4f9218da10ba8f2206bdc954f036eadf87f913d20d556372f318b8244e726872`.
The original38 tests/comparator remain unchanged and59 adversarial cases add
schema drift, private-slot corruption, scalar/array/range rejection, unpaired
surrogates, repeated aliases, distinct quiet-NaN bits and representable Time
extrema. Test source SHA256:
`8df65d2c7ca9e745f9a6c6de63de80f14a8d63027dff352cc83bb72f514eb56d`.

New exclusive `serialization_preflight_v2/measure_serialization.py` is derived
from v1 by changing only version and source pins; fixed population, ordering,
timing/parity code and gates remain identical. It is prepared, not yet run.
Actual DDS `pipeline_timing_diagnostic_v4` is also prepared, not released:
it refreshes source pins, additionally pins the executed lifecycle tests,
fails process status on source drift and retains unexpected pytest exceptions.
Original owner logic and actual pipeline assertions/source allowances remain.

## Structural fixed timing: CLOSED PASS

The one structural timing execution completed all13 pairs/26 method receipts,
with all5 source pins unchanged and exit0. Result
`serialization_preflight_v2/results/result.json`, SHA256
`96c99dd3b29a7ff524644433ebeebdea57031b8b817b2b3f0e5c190927c38502`:
selected363 median old210.222075ms/new45.871822ms, speedup4.582815073083593x;
new maximum46.180069ms. Both unchanged2x and200ms gates PASS. Gaussian pending
copy median6.149783ms is separate. At4000 observations, median590.751988ms and
maximum615.394943ms are reported without general real-time qualification.

The source checkpoint before this job is
`checkpoints/q2_structural_preflight_v1/manifest.json`, SHA256
`03562b82ce8a6947256e708cb904cc6cbe65890952060aa1df236ae20101c81f`:
251files,1042564-byte verified archive,440 retained artifact hashes. Reviewed
timing script SHA256
`c8a687d774894af8fc064bc34665d3f531288e31991db09b34939a3c15df0091`;
AST comparison confirms only source pins and version differ from failed v1.
`dispatch_release.json` binds this checkpoint, script, tests, caps and gates;
`closed.json` binds the completed output files. The single exact command is
the v1 timing invocation with `serialization_preflight_v2` substituted;60s outer
and58s internal caps, Q2 overlay, no ROS nodes or extra warmup repetitions.

The reviewed actual DDS diagnostic v4 is now dispatched once under120s after
this PASS. Its result is pending. Passing synthetic timing alone does not close
Q2 or establish scientific direction/convergence improvement.

## Actual DDS correction check

The single reviewed v4 diagnostic completed **21PASS21.17s** (21.310157s wrapper),
exit0, no exception, all8 source/test hashes unchanged. Test log
`pipeline_timing_diagnostic_v4/pytest.log`, SHA256
`89479e4dab84fe30bfd8a19115d54d9b1538bbf3b99e0ba6886f88f30b4daca9`;
timing receipt SHA256
`926002066bebd3fc4741d1ca0484fc674b120ccee869840a12440cd5f88f5341`.
The normal case prepared at generation0, activated at generation1 and passed
the actual composer/ESCAPE assertions. Departure during the worker cancelled
the preparation, leaving both registries at generation0 as asserted.

Maximum snapshot53.920525ms, begin-preparation25.139439ms and entire supervisor
timer79.667692ms. This includes actual publisher work, beyond the synthetic
copy-only benchmark. Direct context/readiness events are retained for audit.
The original50s case/120-source allowance and120s diagnostic outer cap remain.
Script SHA256
`39c47c14609b3e6fc0b0d36626f6318fda3405feace8e6961147255e4f53fcfb`;
its release receipt records the exact timeout120s argv and timing prerequisite.

Source/install receipts refreshed after this check:21 console targets and6
generated Python message bindings resolve to the declared environment, without
ROS/node startup (`installed_binding_v2.json`). D3 comparison finds17 changed
earlier source owners,539 unchanged and12 additive policy/copy files
(`source_scope_v2.json`, SHA256
`d2c33c9be762308b641b96ac95bd69f0d62c320819c517b5f90384e73de89fd8`).
The three additional changed owners are the scoped lifecycle/supervisor/Gaussian
copy correction. Controller, source acquisition and numerical reference remain
unchanged from D3. Held40-file integration is now dispatched with426 source
pins,300s pytest/310s outer cap, Q2 overlay and domain192; its result is pending.

Independent saved-event audit PASS, four exact publication/Gaussian-entry/
retained-context joins: normal-case timer74.370340ms, valid context sequences
188/189 at readiness ages58.640987/78.009802ms; departure-case timer79.667692ms,
valid sequences188/189 at56.584940/82.150036ms. Gaussian retained these at source
ages25/175ms and25/200ms respectively. Original readiness receipts did not
change during either callback and recorded readiness decisions remained true.
This directly verifies freshness through the corrected callbacks; the precise
invalid bit in the old failure remains unobserved, as originally recorded.
`pipeline_timing_diagnostic_v4/result_audit.json`, SHA256
`5f84f5a585a003115e37597647f503590c301e053d4eb00fa8c0d5028cc684a5`,
retains exact joins and outcome assertions; its read-only audit script/command
are beside it. Refreshed installed-binding receipt SHA256:
`9d446ac6ab68f810a6db0157b206039f058d418fc34703f212cb1d0be4158868`.

Final held integration PASS1167 in162.63s, no failures/skips/errors, one inherited
sqrt warning. All426 pins unchanged; `integrated_receipt_v3.json` SHA256
`0f6b70c83588e7d262b48decbb87978b35814b5255d64291c1667179f3aaaf56`.
See `q2_policy_runtime.md` for exact integration argv and source-closeout scope.
