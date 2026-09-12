# M2 fixed reference v1 — EVIDENCE_UNAVAILABLE

The fixed retained-input reference version is closed with **EVIDENCE_UNAVAILABLE**.
The corrected `v1b` invocation exited 0 after **79.666100286 seconds**,
but all eight input normalizations rejected source ordering before producing
observations. The 192 fixed anchor slots therefore have no causal anchors,
field/reference values, or matched direction outputs. Averaging availability
and angular-error statistics are **unavailable (`null`)**, not measured zero
percent performance. This does not qualify M2 direction performance, waive a
gate, select a detector, or authorize a new empirical run.

The [completed summary](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_references_v1_recovery1/references.json) has SHA256
`1e40fb153b01933bff798e245129838e15ea496892b0a78d930300492c26e6df`. The companion
[byte-hash manifest](m2_reference_v1_manifest.json), SHA256 `e7eb58a380758078739c38ebb0f70cb19011302984ce790f44f24493456a6a96`,
retains all 211 JSON receipt hashes, complete exact launch scripts, log hashes,
configuration identities, input IDs and source-owner checks.

## Preserved execution versions

| Launcher | Exit | Exact script / retained log | Outcome |
| --- | ---: | --- | --- |
| v1 | 1 | [m2_reference_command_v1.sh](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1.sh) / [log](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1.log) | ROS setup rejected unset optional variable before Python |
| v1a | 1 | [m2_reference_command_v1a.sh](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1a.sh) / [log](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1a.log) | Python configuration preflight rejected incorrectly scoped robot_description lookup |
| v1b | 0 | [m2_reference_command_v1b.sh](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1b.sh) / [log](/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_reference_command_v1b.log) | Finite fixed reference completed with all source inputs unavailable |

Each scientific launcher contains the exact same `freeze_v2_direction_references`
call under `timeout 300s`; `v1b` uses the fresh output directory
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m2_references_v1_recovery1`. The reproducible launcher entrypoint is `bash SCRIPT > LOG 2>&1`. Exact
absolute workload arguments and complete script contents are in the manifest;
an additional outer tool wrapper is not asserted from these retained files. No launcher or log was
overwritten. The original `m2_references_v1/` directory remains absent.

The shell failure and initial Python preflight failure are retained in
[m2_reference_launcher_note.md](m2_reference_launcher_note.md). The separately
planned [reader correction](../m2_reference_preflight_recovery.md) restricted
robot-description lookup to captured parameter values while retaining its
conflict and geometry checks; [validation](m2_reference_preflight_recovery.md)
records 100 passing tests and all eight configuration-only binding preflights.
No numerical rule, target population, missing-data rule, or denominator changed.
The pre-correction and corrected source archives and patches are retained in
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_pre_reference_v1/manifest.json` and
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_pre_reference_recovery1/manifest.json`. Their manifest/archive/patch byte hashes
were checked while writing this record.

## Fixed population and observed outcome

The unchanged inventory SHA256 is `eae9b60fc2f6f3e638f7ee9e56fd52174176fb4495de78bb145640eddb93e90d`.
Only its eight development bags were read by this job; the thirteen
retrospective holdouts remain excluded. This report read retained JSON/logs and
source bytes only; it opened no bags and constructed no models.

| Seed | Normalized observations | Missing anchor slots | Retained input qualification reason |
| ---: | ---: | ---: | --- |
| 19801 | 0 | 24 | source regression or conflicting duplicate |
| 19811 | 0 | 24 | source regression or conflicting duplicate |
| 19851 | 0 | 24 | source regression or conflicting duplicate |
| 19901 | 0 | 24 | source regression or conflicting duplicate |
| 19911 | 0 | 24 | source regression or conflicting duplicate |
| 19931 | 0 | 24 | source regression or conflicting duplicate |
| 20001 | 0 | 24 | source regression or conflicting duplicate |
| 20031 | 0 | 24 | source regression or conflicting duplicate |

Every input has `qualified=false`, `origin_ns=null` and an empty observation
array. Consequently all 192 target records retain their bag/seed/slot identity
but have `target_ns=null` and `observation_index=null`; the planned numeric
source-time targets could not be instantiated. Every per-anchor result says
`missing_causal_anchor`. This record does not infer which source stream or
conflict subtype caused the generic qualification failure; separate read-only
forensics may establish that cause without changing this closed result.

The 211 receipts comprise one append-only `started.json`, one `targets.json`,
eight empty input traces, eight empty method-output arrays, 192 anchor receipts,
and one final `references.json`. `started.json` intentionally retains its
initial `status=incomplete`; final process completion and the closed unavailable
outcome are recorded here and by the final summary. All 192 individual anchor
receipts equal their corresponding final-summary rows, and every target's input
trace digest matches its exact retained bytes.

Causal anchors, reconstructed objectives, complete/rate-qualified cycles,
numerically qualified references, informative references, eligible informative
anchors and matched method outputs all have count zero. These are unavailable
stages after input rejection. There was no anchored objective/harmonic result;
no measured angular error, averaging availability, lag, jitter, trajectory
improvement or comparison pass follows. The ordinary per-bag control flow may
initialize model objects even with no anchors; no claim of instrumented zero
model constructions is made.

## Configuration and source provenance

The successful configuration preflight bound each bag's recorded launch defaults
and overrides, selected filter/model/transform configuration hashes, historical
URDF, and captured live robot-description XML. All eight use selected raw cost
`/turtlebot3/cost_value_chatter`, source cost `/gesc_gaussian/source_cost`, and pose
`/odom`. The verified geometry is joint `(0,0,.355)` m, axis `(0,0,1)`, identity
mount rotation and sensor offset `(.18,0,.015)` m. Per-run captured XML digests
and complete selected configuration bindings remain in `started.json` and the
companion manifest. Passing these configuration checks did not establish valid
source ordering or exact historical model-input provenance.

The following nine owner/configuration/protocol hashes match `started.json`,
`references.json`, and current source bytes at report generation:

| Owner | SHA256 |
| --- | --- |
| `gesc_gaussian_bag_analysis.py` | `17b9231d0d8ada8835a61574f15d3492d3c4b780b153be9873b7e283260df7cb` |
| `v2_direction_reference.py` | `614332ebbaa0d654b11b8f0c7304bf980ea3e7d693172e471dc999d703f51aed` |
| `aggregate_field_truth.py` | `b9b0e8b483dc4d7ac2fd392b7ef7ed57a8cb95ebb600124dc5d964b4cf0190c5` |
| `cost_function_objects.py` | `b54cf0baa3e068c471c424b2f629d3fa896c30187040769ca27808d5c7f77886` |
| `config_parsing.py` | `d158915f459681a8955df1b7940526b0148d4aae2463125c27b586df58287555` |
| `rolling_gesc.py` | `6800641655b2967cd7a53f4daca3f20317f5787c888355fc29e67ee80afec775` |
| `base_filters.py` | `c7e47ecac2b1d334319fd2c7941e2c043e57b4c5490b38f31c6ec55c0eb455a8` |
| `gesc_filter_full_rotation.json` | `f1cfd23a9c60e08780a4477f23cacc80a9e0c75b127448291e321756de7a2dce` |
| `m2_reference_plan.md` | `cb1493928c5bbb03f9ca787156c55b0a380bdfc2b445295d21d7a65cbda4a225` |

The retained bags predate exact V2 model-input provenance. Even a successful
future proxy reconstruction would remain separate from bounded typed runtime
transport evidence. Preserve this version and all unavailable anchors; any
corrected evidence attempt requires its own prospective version and retained
provenance. No source edit, replay, model evaluation or experiment occurred
while producing these two validation files.
