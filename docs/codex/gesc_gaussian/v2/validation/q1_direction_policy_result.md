# Direction-policy diagnostic result

Status: CLOSED COMPLETE_DIAGNOSTIC; **development nominee: mean weight 0.75**
with the predeclared current-cycle coherence threshold 0.25. Qualification is
NOT_EVALUATED. The original confirmation data remain SEALED and M4 unreleased.

The single arithmetic job completed in 10.18 wall seconds, exit 0, under its
60-second cap. All 24 original targets, reference vectors and first recorded
outputs are retained. No field/reference evaluation, filter replay, bag read
or new trajectory occurred. All 556 original source files remained unchanged.

| Output | Median error (degrees) | P90 error (degrees) | Averaging applied | Development rule |
| --- | ---: | ---: | ---: | --- |
| Actual recorded policy | 55.342800 | 103.692391 | 4/24 | Unchanged control |
| Proposed weight 0.50 | 23.012355 | 71.986722 | 24/24 | Fails P90 |
| Proposed weight 0.75 | 20.526919 | 34.946685 | 24/24 | Nominated |
| Proposed weight 1.00 | 15.530607 | 62.278098 | 24/24 | Fails P90 |

All three candidates have 24 finite errors, no fallback and no missing slot.
Every current-cycle coherence value passes the fixed threshold, so gated and
ungated vectors coincide for these particular targets. Their separate records
remain in the result. The 0.50 candidate exactly reproduces the completed D2
control. The lower median for weight 1 does not override its failing P90.

The nominee's residence/approach medians are 21.041567/20.526919 degrees and
P90 values are 34.951518/32.853326 degrees. Its frozen ranking key is
`[34.95151795301875,21.041566806766056,20.52691894242276,0.75]`.
It improves error versus actual output at 23 targets and worsens one:
residence seed26090911 target8 rises from 11.025841 to 34.953935 degrees.
Compared with the old 0.50 sensitivity it improves 18 and worsens six.
Its maximum error is 53.085303 degrees.

Direction accuracy is only one effect. The nominee's magnitude divided by the
actual output magnitude has minimum/median/maximum
0.235195/0.846257/5.070189. No command was applied by this arithmetic. Existing
speed ceilings must remain effective in implementation, and fresh trajectory
tests must examine changed gain and historical-average lag.

## Support and numerical evidence

All 24 rolling means reconstruct exactly at saved floating precision; maximum
component discrepancy is 0. All current support and three covered warmup-cycle
receipts pass, including the permitted pre-readiness warmup. Coherence spans
0.414461520741 to 0.725018001801. The independent segment norm integration used
58,905 calls total, 1,995–3,045 per anchor, below the fixed 20,000 cap. Maximum
normalized denominator error estimate is 4.746885260089446e-12 cost/metre,
below 1e-10. No unavailable numerical value, warning or partial target occurred.

The quadrature estimates and reconstruction bounds govern the diagnostic;
they are not formal numerical certificates or statistical confidence intervals.
Coherence does not establish correctness under synchronous interference or
arbitrary washout transients. These repeatedly studied trajectories are
development evidence, not independent qualification. The nominee is one
fixed candidate for a subsequent runtime amendment and fresh simulation.

## Exact execution and receipts

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/`.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 /usr/bin/time -p -o /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/process_time.txt timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/preflight/diagnostic.py evaluate --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/preflight/contract.json --output /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/analysis --release /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/dispatch_release.json > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/console.log 2>&1
```

Primary SHA256 receipts, paths relative to that root:

- `preflight/contract.json`: `917d10eb90effac6005593448ae324e2b63bfbb74d62dffef4fbecb0a5315a41`.
- `dispatch_release.json`: `7b12815b05aedc926827ad4f526182e7cf44c8d028884fd7ce0738e397231185`.
- `analysis/result.json`: `fe6cb53f7017c4be6b60d244eb14402fd5e1388235d848c97cff9ff8d3999899`.
- `console.log`: `fdae3cb578c6472b8af142601f1690ebc451a8eb229c09f3eb95658b55e9a250`.
- `process_time.txt`: `7d550a9bbdd254c906dafb913fa1093f3102ded11c12b0a5f6876a12f98c3329`.
- `diagnostic_closed.json`: `88a1767f80135c98dbec416a7768206b1b046e20100828aa37146723a4b231df`.

The preflight material checkpoint is
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q1_direction_policy_preflight_v1/manifest.json`,
SHA256 `efb543720fc2bcecb956de6f25f9f43ac2cbf16508cbdf60c806fac061acb0e5`:
230 files, 967785-byte verified archive and 304 retained artifact hashes.
It precedes release and arithmetic. The primary closure verifies source/input
lineage and equality of each of the 24 individual receipts with its final row.
Its sourced domain191 command was `timeout 60s python3` with the external
`close_diagnostic.py`, redirected to external
`builds/initial/q1_policy_close_v1.log`. Later independent audits are excluded
from primary closure and bound by the final material checkpoint.

## Independent saved-result audit

PASS: 607 file hashes unchanged, including 556 prior source files and six
diagnostic source/plan/test receipts. The independent audit verifies every
original target/first-diagnostic/control join, saved support numerator and
denominator sums/error bounds, all three weight vectors, errors and magnitudes,
per-run/pooled counts and exact nomination. It performs saved arithmetic only;
no segment norm integration, field evaluation, filter replay or bag read.
The nominee increases magnitude at eight targets and decreases it at sixteen.

Final artifacts live under the external diagnostic's
`diagnostics/result_audit_v1/`. Both root and independent reviewer visually
checked `paired_errors_and_magnitude_v2.png`: all 24 targets, the single worsened
case, common logarithmic magnitude scales and evidence limits are visible.
The CSV retains all candidate/control values. SHA256 receipts:

- `manifest.json`: `caab8a832d16c09e1cfa70768159d26fc53324406a5c9bebe4eef10337432708`.
- `result.json`: `1034067fa584d39ea681f0ef30fb20ed3ed8896202c6a7fb985df14e02dce39d`.
- `paired_errors_and_magnitude_v2.png`: `55151b87b01d954329c8baaf03131eb8c843e65122bcfb6831e09723cb890733`.
- `targets.csv`: `4e27170d0131973b79c55dcad7eaf04a125fabd00d6f1049f460d15950e9a865`.

The first audit helper stopped before publication because it compared receipt
objects including optional byte-count fields. Its script/log remain retained.
The corrected helper compares the common path/SHA identity; the successful
bounded read-only audit took approximately 1.9 seconds. Exact successful
commands, with the external directory above as prefix, were
`timeout 60s python3 extract_v2.py > command_v2.log 2>&1` and
`timeout 60s python3 render_v2.py > render_v2.log 2>&1` using absolute paths.
Both exited 0. The latter only refines labels/layout from the saved CSV. No
primary source, candidate, parameter, numerical result or experiment was retried.
