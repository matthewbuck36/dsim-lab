# M1a fixed calibration outcome

**The complete 36-setting calibration failed; no detector setting was selected.** Fifteen settings passed all 79 synthetic traces, but every setting had zero uncensored retained positive opportunities. Three settings also triggered during independently labeled negative travel. The nonempty retained-positive gate remains enforced.

## Preserved execution and provenance

- [Full calibration](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_calibration_v1/calibration.json>) completed with process exit 0 and scientific status failed. SHA256: `a7d83b70fcf664432c4bb881fd7a7a59486378ec827e00b2274702b88cbddd67`.
- [Complete recovered labels](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1_recovery1/labels.json>) were frozen before detector evaluation; their hash is `2ae8c6e53446ec2ce176f43436d47b726c7c5d8107990a486f021ff787e9620b`.
- [Compact manifest](m1a_calibration_manifest.json) binds the contract, inventory, unchanged synthetic data, all 36 grid receipts, exact executed commands, logs and recovery chain.
- [Source enclosure audit](m1a_enclosure_audit.md) independently checked all six qualified enclosures and 8,625 point receipts without reevaluating the field.

The original label attempt remains incomplete with exit 124 at its 600-second cap. Its completed geometry and log are retained unchanged. The separately frozen technical recovery completed with exit 0 in approximately 32 seconds (31.818 seconds from started-receipt to final-manifest file timestamps), verifying 8,642 old JSON receipts and reusing all 8,625 points with zero new field evaluations. The recovery changed repeated segment-query work; scientific geometry, labels, grid and acceptance rules remained fixed.

Exact executed command records, including source overlays, timeouts, function arguments and log paths:

- [Original 600-second label command](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_label_command.json>).
- [600-second recovery command](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_command.json>).
- [300-second calibration command](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_calibration_command.json>).

Their immutable log and artifact hashes are in the compact manifest. The same eight development inputs and 79 synthetic traces were used; the thirteen retrospective holdout inputs remained excluded.

## Retained spatial labels and censored opportunities

The frozen input-only geometry produced seven positive residence intervals and 24 directed-progress intervals. Positive residence durations were 12.070–34.136 seconds; none met the fixed 54-second common support requirement even before runtime eligibility masking. The common positive denominator is therefore **zero in every grid row**.

| Seed | Positive intervals | Negative intervals | First opportunities censored | Later fragments censored | Supported opportunities |
| --- | ---: | ---: | ---: | ---: | ---: |
| 19801 | 2 | 3 | 1 | 5 | 0 |
| 19811 | 3 | 2 | 1 | 8 | 0 |
| 19851 | 0 | 3 | 0 | 0 | 0 |
| 19901 | 0 | 4 | 0 | 0 | 0 |
| 19911 | 0 | 3 | 0 | 0 | 0 |
| 19931 | 0 | 1 | 0 | 0 | 0 |
| 20001 | 1 | 4 | 1 | 0 | 0 |
| 20031 | 1 | 4 | 1 | 0 | 0 |

Four first opportunities were short or interrupted. Thirteen later eligibility/residence fragments were censored under the unchanged one-opportunity-per-SEARCH rule. These 17 records are not 17 independent trials; counts are identical across the grid. There were no additional no-eligible-SEARCH-support records.

At W=3 seconds, epsilon=0.36 m, all three radius choices produced the same negative-travel response on seed 20031 at source time 65.455 seconds (score 0.3550410402 m, radius 0.1891879350 m). These are three configuration outcomes observing one retained event, not three independent failures.

At W=3 seconds, epsilon=0.48 m, R=0.50/0.75 m, one event per setting occurred inside a positive spatial residence on seed 20001 at 49.025 seconds. That residence is censored and contributes no uncensored detection. Unknown-event counts range 0–12 per setting. Unknown outputs are not true positives, and no-output settings do not establish sensitivity.

## All 36 frozen configurations

Synthetic columns count detections: positives should be 27/27 and negatives 0/52. Retained P/N/U counts mean events inside positive spatial intervals / negative intervals / unknown intervals; P remains censored here. Every row has supported-positive count 0, qualifies=false and no selection.

| W(s) | epsilon(m) | R(m) | Synthetic positive detections | Synthetic negative detections | Retained P/N/U |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 0.24 | 0.25 | 10/27 | 0/52 | 0/0/7 |
| 3 | 0.24 | 0.50 | 10/27 | 0/52 | 0/0/7 |
| 3 | 0.24 | 0.75 | 10/27 | 0/52 | 0/0/7 |
| 3 | 0.30 | 0.25 | 10/27 | 2/52 | 0/0/7 |
| 3 | 0.30 | 0.50 | 10/27 | 6/52 | 0/0/7 |
| 3 | 0.30 | 0.75 | 10/27 | 6/52 | 0/0/7 |
| 3 | 0.36 | 0.25 | 14/27 | 2/52 | 0/1/7 |
| 3 | 0.36 | 0.50 | 14/27 | 6/52 | 0/1/7 |
| 3 | 0.36 | 0.75 | 14/27 | 6/52 | 0/1/7 |
| 3 | 0.48 | 0.25 | 14/27 | 2/52 | 0/0/12 |
| 3 | 0.48 | 0.50 | 14/27 | 6/52 | 1/0/12 |
| 3 | 0.48 | 0.75 | 14/27 | 6/52 | 1/0/12 |
| 6 | 0.24 | 0.25 | 22/27 | 0/52 | 0/0/1 |
| 6 | 0.24 | 0.50 | 22/27 | 0/52 | 0/0/1 |
| 6 | 0.24 | 0.75 | 22/27 | 0/52 | 0/0/1 |
| 6 | 0.30 | 0.25 | 27/27 | 0/52 | 0/0/1 |
| 6 | 0.30 | 0.50 | 27/27 | 0/52 | 0/0/1 |
| 6 | 0.30 | 0.75 | 27/27 | 0/52 | 0/0/1 |
| 6 | 0.36 | 0.25 | 27/27 | 0/52 | 0/0/2 |
| 6 | 0.36 | 0.50 | 27/27 | 0/52 | 0/0/2 |
| 6 | 0.36 | 0.75 | 27/27 | 0/52 | 0/0/2 |
| 6 | 0.48 | 0.25 | 27/27 | 0/52 | 0/0/2 |
| 6 | 0.48 | 0.50 | 27/27 | 0/52 | 0/0/2 |
| 6 | 0.48 | 0.75 | 27/27 | 0/52 | 0/0/2 |
| 9 | 0.24 | 0.25 | 19/27 | 0/52 | 0/0/0 |
| 9 | 0.24 | 0.50 | 19/27 | 0/52 | 0/0/0 |
| 9 | 0.24 | 0.75 | 19/27 | 0/52 | 0/0/0 |
| 9 | 0.30 | 0.25 | 21/27 | 0/52 | 0/0/0 |
| 9 | 0.30 | 0.50 | 21/27 | 0/52 | 0/0/0 |
| 9 | 0.30 | 0.75 | 21/27 | 0/52 | 0/0/0 |
| 9 | 0.36 | 0.25 | 27/27 | 0/52 | 0/0/0 |
| 9 | 0.36 | 0.50 | 27/27 | 0/52 | 0/0/0 |
| 9 | 0.36 | 0.75 | 27/27 | 0/52 | 0/0/0 |
| 9 | 0.48 | 0.25 | 27/27 | 0/52 | 0/0/0 |
| 9 | 0.48 | 0.50 | 27/27 | 0/52 | 0/0/0 |
| 9 | 0.48 | 0.75 | 27/27 | 0/52 | 0/0/0 |

The 15 settings passing all synthetic cases are W=6 seconds with epsilon 0.30/0.36/0.48 m and W=9 seconds with epsilon 0.36/0.48 m, each at all three radii. This finite synthetic result does not qualify a retained-data setting. No threshold was chosen or changed after this grid.

## Evidence limits

There is no retained sensitivity, true-positive-rate or detection-latency improvement claim. The recorded median delay field comes from detected synthetic positives because the retained common-positive population is empty; it is not a retained latency measurement or comparison. Historical convergence_time keeps its existing goal-event meaning.

The enclosures are finite sampled model regions, with explicit annular holes and numerical/spatial-resolution limits. Recorded readiness and source-age masks remain timing proxies rather than exact callback reconstruction. This replay does not establish counterfactual robot motion, broader robustness or operational readiness. The fixed M1a failure and original timeout remain preserved. No Gazebo, physical-hardware action, source edit or replay rerun was performed to prepare this report.
