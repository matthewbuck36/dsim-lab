# M4 V8 retained incomplete result

Status: CLOSED_INCOMPLETE, 2026-09-10 UTC. Full V2 remains IN_PROGRESS.
The sole dispatcher (root session 94339) returned 1 after 4.740011331996357 s;
its internal acquisition receipt measures 1.0280601029953687 s. All 16 slots
are UNSTARTED. No scenario, ROS graph, recording, bag, block science or holdout
release was launched. Preserve this version and all 35 pilot files; never resume
or replace a reserved slot. The source and preparation passes retain their
source-only scope; they are not experimental acceptance.

## Outcome and research scope

The existing finalizer retained all 16 outcomes and all 192 scheduled direction
targets (48 development, 144 holdout). All are unavailable; there are 0/12
latency endpoints, 0/6 latency pairs and 0/144 eligible holdout direction targets.
Missing direction statistics, stopped-sweep counts and combined-sequence results
are unavailable, not zero. No replacements or development-to-holdout release
occurred. Both original goals remain open: earlier detection including circling
and oscillation, and better GESC direction during continuous movement.

## Verified admission defect

Failure: `TimeoutError: M4 remaining case/science envelopes do not fit suite deadline`.
The existing run_m4.py SHA256
621af734f0b182ee166d594b22c90ada16721feca7a6ec232d6dc065393b9093
checks admission before ensure_ros_daemon, graph inspection and child launch.
Its source was unchanged from V7. V8 started_monotonic=60906.478755597,
suite_end=76206.478755597 and first case_end=61806.478755597. Subtraction
returns 14399.999999999993 instead of the required 14400 s: a deficit of
7.275957614183426e-12 s, one ULP at the start value. This falsely rejects the
first reserved case before acquisition. The retained V7 start56063.905715417
produces exactly14400 and admitted its first case. Root and independent review
agree on this pure arithmetic reproduction; no dispatcher or simulation replay
was used to diagnose it. The new outer timeout placement is not the cause.

A separately adopted correction can compare elapsed time with the exact integer
remaining allowance, preserving every absolute case/suite/cleanup deadline and
science reservation. It requires actual dispatcher baseline/fault tests and a
fresh experiment identity. No correction has yet been applied at this closure.

## Retained evidence

Paths below are absolute external references. No original receipt is rewritten.

| Evidence | SHA256 |
| --- | --- |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/preflight/contract.json` | `76bc335518f936e26f2d5f8cac1591d3f28cdfee0e37b94467a4e3ea777a1a9a` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/preflight/dispatch_release.json` | `6ff1953fb21ee2a3a94528abfdab28acb2c341bd3c33f5802f41ee8a7baa22d9` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/acquisition/started.json` | `14e6271867363a7fdc972f85fe4775481d9141ef3111183f35d4fd9831b6c724` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/acquisition/acquisition.json` | `8fa63547100fa671b1c1301cd961dc1318004fe8ffb390cfaba2b01fbbcf8f46` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/report/result.json` | `273efd3b5fd58c08a60bb19aab02ee78287267d83333cd452db62e075b72835f` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/report/report.md` | `26f982002b2e5a0c9e0056379eb3f927faa07e749309ea54c94a301230666793` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8/report/report_receipt.json` | `6a613419474ce82d994bd75268d393db8f7dd7f6beb0c0bbc53301f2f9ce4742` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v8_stationary_causality_comparison_v1/acquisition_owner_v1.json` | `10db998cdc8cbc0d57063222bf0176adee07d68c2822a5b30cb6b09e7bdf106b` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v8_stationary_causality_comparison_v1/acquisition_execution_v1.json` | `32d390080c6a1c434f5bad35d6b35f2346e66b4bf0c2bfe8955c4d121a1ae326` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v8_stationary_causality_comparison_v1/acquisition_dispatch_console_v1.log` | `55d12a50bea77301d9210677aca03d4ecdf15240a9903044ab45790acc577561` |

V8 source evidence: 1232 unique PASS cases, 641 unchanged source pins and
21 installed bindings; actual CLI PASS. Source aggregate SHA256
 ae68f367d4df0142c4b44e171d9837677500491e0527c5db62a99fafa8b61867.
Preparation PASS54.248191949 s/600 and frozen audit PASS4.752669608 s/30.
Source archive6570e90809e5745d6d1543b51879a51c697c78b0b388f521a719627790359ae8;
prepared archive9533fd0a01d722e5e9dba826d92367c81bbbad4577bef2a9fc017251cb7c45ab.
Independent terminal closure audit and material archive are the remaining closure
steps. No tests, ROS graph, bag decode or numerical model job is needed for them.

Git: feature/gesc-gaussian-robustness-v2 at3369cfc, saved uncommitted task changes.
No commit/push, V1, physical snapshot, Pi or hardware action occurred.

Independent closure audit PASS, 0.177930467 s under30 s: external
builds/m4_v8_stationary_causality_comparison_v1/closure_audit_v1.json,
SHA2561e470d3da35035f092a57a7973853ae4a4ef581752a5f835e63185e2ab48751c.
All641 current pins and receipt references match; terminal owner PIDs are absent;
all16 slots/192 targets and35 pilot files remain retained. No cleanup/behavior
pass is inferred for unstarted rows. Context validator, diff check and existing
checkpoint tool PASS. One60s material closure archive follows.

V8 material closure PASS5544a2cf123c69fc77a0bb1e04550ac87f7a1640e193f09167b470ee68502ed5:
411 repository files/200 external references/1614974-byte verified tar,
1.058293623s under60. Independent closure audit PASS; V8 stays all16 UNSTARTED.
The combined [V9 amendment](../m4_v9_budget_comparison_plan.md) is now adopted.
Next: preserve pre-edit source, capture V1-V8 outputs and execute one actual
dispatcher budget baseline before changing production. One source milestone
combines the elapsed-budget correction and freshV9 routes. No acquisition or
preparation is released; both original research goals remain open.
