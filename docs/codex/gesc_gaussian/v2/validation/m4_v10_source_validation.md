# M4v10 comparison source and retained-motion validation

SOURCE_VALIDATED, 2026-09-10, under the
[prospective comparison plan](../m4_v10_arrival_comparison_plan.md).
No M4v10 preparation or acquisition has run. This source boundary follows the
successful [stationary B02 acquisition/analysis](r4_stationary_integrated_02.md).

## Result and scope

The existing comparison owners now select PDE/recurrent detection and
stationary/rolling-centered acquisition in four matched arms, use the adopted
arrival criterion, and require usable four-arm development science before
confirmation. V10 has a distinct method identity, fresh reserved seeds and
consistent budgets:240s labels,40s freeze/report,1400s science,15800s suite;
case900s, recorder720s, Stage A360s and Stage B300s remain. Historical V1–V9
contracts/results remain unchanged. Exact old V9 scenario byte parity passes.

Only seven production owners changed since the verified R4 archive:
`m4_scenario.py`, `scenario_schema.py`, `run_scenario.py`, `m4_pilot.py`,
`run_m4.py`, `evaluate_m4.py` and `m4_workflow.py`. No detector numerical,
controller, filtering, stationary/centered verification, Gaussian, topic/IDL or
physical source changed in this milestone. New focused tests and documentation
accompany these owner changes. Nine old future-version test sentinels advance
from V10 to V11; old accepted populations and outputs stay intact.

Owner details: [scenario/dispatch](m4_v10_scenario_dispatch.md),
[science/motion](m4_v10_science_validation.md),
[workflow/release](m4_v10_workflow_source.md). Independent reviews checked the
actual B02 arrival/pose join, retained C label representations, D02/D03 complete
reference-row shapes and producer/release field agreement. A final exact-key
disagreement was corrected before testing. None of these reviews decoded bags.

## Source checks and preserved failure

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/`.

The first coordinated bundle selected25 module/test targets and completed608
unique checks in131.639977s (pytest129.36s): **607 passed, one failed**. All757
source/helper/input pins and all21 installed entry-point bindings remained
stable. Session14599 is terminal/reaped, exit1. Failure was confined to the new
test's V9 exact-byte parity fixture: sorted JSON topology maps reordered YAML
keys relative to the original scenario. All four topology mappings were
semantically identical; the pre-V10 builder also preserves supplied insertion
order. This was not an old scenario or production-code change.

The fixture now uses the hash-verified original YAML topology maps and keeps
exact byte equality. The original failed log/JUnit/receipt and correction
diagnosis remain. Only the affected version module was rerun: **32 passed** in
9.894771s (pytest7.71s), session5593 terminal/reaped, exit0. All757 pins and
installed bindings stayed stable. Across the two jobs, the sole changed shared
pin was this test file; every production/runtime/installed binding was identical.

`source_validation_combined.json` retains the two original receipts, changed
test path and latest passing outcome for each of608 unique checks. Its counts
are the union, not607+32 distinct tests. It supplies the existing dispatch
validator's passing source receipt while preserving the initial failure.

Exact invocations (each existing driver internally bounds pytest to230s plus5s
termination and records before/after pins, JUnit identities and full logs):

```sh
timeout --signal=INT --kill-after=5s 260s env -u PYTHONPATH ROS_DOMAIN_ID=219 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/tests_v2.json'
timeout --signal=INT --kill-after=5s 260s env -u PYTHONPATH ROS_DOMAIN_ID=219 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/validate_source.py --version focused_v2 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/tests_v3.json'
```

## Retained empirical motion check and real CLI smoke

The new motion owner passed on D02's original closed exports in4.244722s,
session72036 terminal/reaped, exit0. All764 source/input pins remained stable.
The published original analysis receipt hash, all selected export artifact
sizes/hashes, original scenario pin and canonical generated-message round trips
were verified. The prior complete/valid lifecycle is explicitly prior evidence;
this check does not repeat that validation or create a new comparison run.

The actual adapter paired all9419 Twist/ControlDiagnostics vectors exactly,
using3616 states,3615 guidance messages and5314 measured poses. It reports
`OBSERVED_CONTINUOUS_ACQUISITION`, complete authority/coverage/pairing:
VERIFY78.2–92.3s contains415 poses and0.513372m planar travel; DESIGN92.3–92.9s
contains18 endpoint-inclusive poses and0.016116m travel. Both phases have zero
observed sustained stationary duration and zero ROS-time zero-command dwell.
All178 zero publications in those phases remain in the output with timestamps
and bag-receipt gaps. These are source-sample measurements, not a claim about
every instant between samples. No bag decode, field model or simulation ran.

```sh
timeout --signal=INT --kill-after=2s 60s env -u PYTHONPATH ROS_DOMAIN_ID=219 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/check_retained_motion.py retained_motion_v1'
timeout --signal=INT --kill-after=2s 90s env -u PYTHONPATH ROS_DOMAIN_ID=219 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/check_cli.py'
```

The final CLI check completed in5.850403s, session93843 terminal/reaped, exit0.
Real installed scenario/recorder help and workflow prepare/dispatcher/evaluator
help all returned0 under individual15s caps; V10 appears as an explicit choice.
All756 source/helper pins and21 installed entry-point bindings stayed stable.
No node main, preparation or dispatch was invoked by these help commands.

## Receipts and next boundary

SHA256s relative to the external root:

- `focused_v1/source_validation.json`: `a68cf39ade6305471152324aceea29c55b1bf1b438ffaa45b0f95b17ba14a50e`.
- `focused_v2/source_validation.json`: `66918ecd467939371b294dee4feba070c01b67a092c3efcea2c007872aea5753`.
- `source_validation_combined.json`: `3de8cde1884801d566102b9d1c33da1159417b36afdf3a9027a03ea11cf23109`.
- `retained_motion_v1/receipt.json`: `483a217448974b4d64d5b65bd50a23eb9068562b78c1c5e724968dc421afccd1`.
- `cli_v1/receipt.json`: `b361c98a2a48d3544df33b88f8b581ad4cab1492d244a55d9ee0acb03822e1a8`.
- `detector_v9_fixture_correction_v1.json`: `c4328375524d2ade3ecb259b456ca2c9fa5d35ded9dcff3a6c314ecafb0a8ccc`.

Next: material checkpoint/source archive, then separately recorded exclusive
V10 preparation and resolved-contract review. The full comparison is not yet
released. Its four visible development recordings must yield usable completed
science and credible integrated behavior before twelve headless confirmation
slots. All exposed geometry/data remain development context. Research accuracy,
the original30% paired latency target and broad robustness are not established
by a source pass. No process remains active at this boundary.
