# R11 retained diagnosis validation

Adopted [plan](../r11_retained_diagnosis_plan.md); simulation-only retained inputs,
no production changes or new simulations. Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r11_retained_diagnosis_v1/`.

## Import-only diagnosis

Root session 35163 terminal/reaped exit 0. Selected environment unchanged;
clean PYTHONPATH/RMW_IMPLEMENTATION, domain 201, localhost 1, DISPLAY :0,
source stationary_recurrent_pairing_v1/runtime_environment_v2.sh then
`/usr/bin/python3 -B import_probe.py` under outer SIGINT 15s + kill 5s.
No ROS initialization, bags, numerical work or production source edits.

Import completed in 1.408771661 seconds. Six source/helper/plan pins remained
stable. The audit hook recorded exactly one subprocess at 1.385899148 seconds:
`git rev-parse --show-toplevel`, from run_scenario.py::_repository_root during
module initialization. This confirms the current single-process import defect.
It does not retrospectively identify the unrecorded V12 child command or change
its failed verdict. Exact caller stack and source hashes: `import_result.json`.
Verification and B/noise arrival diagnoses remain pending.

Result SHA256 `484a0c038f9618d91728cadf62c9205dcb657675d6d9f58fb26f84a802a3dd21`.

## B/noise arrival diagnosis

Cached/static evidence suffices; the conditional 30-second filtered read was
SKIPPED because no further read is needed to identify the rejection. Existing
_arrival_metrics requires the independently selected recorded and live first
arrival poses/distances to match exactly. Retained positions differ:
recorded (3.3274862671, 3.0326022809), 0.4982184419 m; live
(3.3301101736, 3.0345959993), 0.4954426677 m. Both existing owners report
valid noninterpolated samples within 0.5 m and both routes use /odom.
These exact-equality predicates necessarily reject this pair.

The precise delivery difference and recorded pose ROS timestamp remain unknown.
Do not substitute the live 283.201 seconds for the unavailable recorded endpoint.
Small static result: `arrival_static_result.json`; source and cached metrics
hashes were stable. No helper, bag read, source correction or study rerun.

## Noisy verification diagnosis

Root session 55523 terminal/reaped exit 0. The selected clean environment ran
`/usr/bin/python3 -B verification_probe.py` under SIGINT 55s + kill 5s,
with the helper's 52-second work limit. Actual total 3.032655172 seconds;
C/D filtered reads 1.319336777 / 1.180960491 seconds, exactly one each.
Selected counts matched metadata: C 18,168 rows, D 18,203 rows across events,
state, guidance and automatic readiness. All 129 source/small-input hashes
remained stable. Raw hashes were inherited from immutable acquisition receipts;
bag stat stability was checked, not represented as a fresh raw hash.

All four VERIFY-to-SEARCH returns in each noisy moving arm carry the exact
reason `verification_deadline; last_evidence=uninformative_raw_profiles`.
At cancellation, every signal_margin is negative, from -0.0291201250 to
-0.0192972054; each has at least four eligible cycles and positive sector
trajectory, baseline-negative and upper-cost-negative margins. These are
terminal snapshots, not a claim that every instant of each attempt had the
same rejection reason. They identify the final failed signal-quality condition.

Full selected boundary/event payloads: `verification_result.json` (354,362 bytes).
Compact exact cancellation projection: `verification_summary.json`.
No source correction, numerical reference or simulation was executed.

## Completion

R11 COMPLETE; no production changes. Independent source/cached review confirms
the owner selects only the latest three eligible revolutions and compares RMS
averaged centered-profile amplitude to 3 times RMS pairwise disagreement.
This is not a calibrated three-sigma test. All eight cancellations occur at
12 seconds after admission, but the appended evidence is the prior evaluation:
its exact evaluation timestamp and earlier trajectory of causes are not retained.
See [handoff](../r11_retained_diagnosis_handoff.md) for justified next work.

Context validator, git diff --check, 12 current local links and the existing
checkpoint tool PASS. Material archive `checkpoints/r11_retained_diagnosis_v1/`
verified 603 source members in 0.849301 seconds; manifest SHA256
`5ac24e647705426067b14b9a4b64c1011b73b5dfb1d3cbae583529daf5a7929b`.
This receipt postdates the immutable archive. No runtime remains active.
The broader research goal remains incomplete; no production correction,
profile-method study or new comparison is silently authorized by this result.
The existing user authorization permits a separately documented next iteration.
