# M1 retained replay and fixed calibration v1

**The fixed calibration failed: none of the 36 configurations qualifies, and no setting was selected.** The complete grid was executed once. Its synthetic positive contract is not satisfied; independently, the frozen evaluator geometry does not supply any qualified retained spatial labels. These are distinct limitations.

## Exact evidence

- [Frozen label contract](m1_labels_contract.md), written before detector evaluation.
- [Small manifest with hashes and all 36 row summaries](m1_replay_calibration_manifest.json).
- [Retained publication failure](m1_label_publication_failure.md); its directory and incomplete manifest remain unchanged.
- [Complete v1a labels](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a/labels.json>).
- [Complete calibration](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_calibration_v1/calibration.json>), with per-row grid_01.json through grid_36.json beside it.

All eight development/diagnostic inputs were read from the M0 freeze. Thirteen retrospective holdout bags were excluded. Full selected bag, input-affecting metadata/config and recorded geometry hashes were checked. Label freezing reads no convergence/fill/state output; runtime state/readiness masks are added only after the immutable spatial labels exist.

## Synthetic result

79 deterministic traces per configuration: 27 positional-settling positives and 52 negatives. All 52 negatives were rejected at every grid point. No configuration detected every positive. This finite result does not establish general false-positive performance.

| Window W | Best total passing | Positive detected | Representative unresolved positives |
| --- | ---: | ---: | --- |
| 3 s | 62/79 | 10/27 | 4.5/6-second circles and fore/aft oscillations; changing-rate circle |
| 6 s | 74/79 | 22/27 | 4.5-second circles, both phases/sample rates; changing-rate circle |
| 9 s | 71/79 | 19/27 | 6-second circles and fore/aft oscillations |

At W=6 s, epsilon=0.24 m, each tested radius gives 74/79. That best observed count is still a failure, not a selected or accepted setting. All original W, epsilon and radius candidates remain unchanged.

## Independent geometry and retained data

The full input streams are available and mostly align within the declared 50 ms tolerance. Duplicate source timestamps are frequent and explicitly do not add elapsed time. No qualified basin was produced by the fixed stationary-cycle mean/ring contract in any of the three distinct geometries. Accordingly all retained spatial labels and the common positive denominator are zero.

| Geometry | Source | Successful starts agreeing | Ring depth | 72/144-angle disagreement | Qualified |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | local | 1 | 0.002438213 | 0.012258986 | no |
| 1 | global | 1 | 0.004694209 | 0.007923006 | no |
| 2 | local | 1 | 0.001924970 | 0.012252195 | no |
| 2 | global | 1 | 0.004781714 | 0.007931538 | no |
| 3 | local | 2 | 0.016692169 | 0.012704663 | no |
| 3 | global | 1 | 0.004679472 | 0.007923157 | no |

Every best point was interior and every ring fit within bounds. Ring depth was below the fixed 0.025 raw-cost-unit requirement in all six cases; local quadrature disagreement exceeded 0.01, and most agreeing-start counts were one rather than two. These approximate optimizer receipts do not show that real trapping is absent. They show that this frozen oracle construction is unqualified. Its failures cannot be repaired by borrowing old convergence flags or changing labels after seeing detector outcomes.

Recorded eligibility contains 68 to 139 history-invalidation generations per run and 2,191 to 10,690 eligible pose samples, detailed in the small manifest. Generations also include readiness changes outside SEARCH; they are not a measured in-SEARCH reset rate. Recorded-time freshness and source-origin exclusions can censor numerical support, and do not by themselves establish a runtime defect.

The retained numerical replay produced 0 to 7 candidate events per grid row. Every such event is unknown under the available independent labels. There is no verified retained false-positive rate, true-positive rate, or detection-latency improvement.

## Implementation and validation

The canonical reader now accepts an optional resolved-alias filter while its default continues to read the original full bag contract. The canonical analyzer owns full-stream input qualification, prospective geometry/label freezing, common one-opportunity-per-SEARCH support, and fixed-grid replay. Existing convergence_time remains the historical first-goal metric. No parallel recorder/node/analysis pipeline was introduced.

The replay preserves state receipt order, same-SEARCH latch behavior, invalidation pulses between poses, source/frame/gap validity, epoch starts and conditional readiness. Recorded clock/receipt timing is a proxy for runtime callback and wall-monotonic freshness; exact callback races are not reconstructed. New outputs are numerical detector responses, not proven authorized runtime publications.

Focused tests: **33 passed** in the final retained command. Coverage includes timekeeper offset, bounded publication skew, unsorted regressions, frame breaks, independent residence/progress/unknown labels, segment crossings, one opportunity per epoch, short-first censoring, invalid pulses, pose-before-epoch exclusion, geometry well/flat distinction, safe JSON publication, and reader-filter/default compatibility. Existing analyzer tests pass in the same invocation.

Exact executed command strings, including the source-patch retention setup, are retained in [m1_executed_commands.json](</home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_executed_commands.json>); its SHA-256 is recorded in the small manifest. All commands ran from the repository root. The two main invocations were:

```bash
timeout 300s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a.log 2>&1 <<'PY'
import json
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import freeze_v2_replay_labels
r=freeze_v2_replay_labels('docs/codex/gesc_gaussian/v2/validation/baseline_inventory.json','docs/codex/gesc_gaussian/v2/validation/m1_labels_contract.md','/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a')
print(json.dumps({'frozen_runs':len(r['runs']),'labels_path':'/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a/labels.json'}),flush=True)
PY
```

```bash
timeout 300s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_calibration_v1.log 2>&1 <<'PY'
import json
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import calibrate_v2_detector
r=calibrate_v2_detector('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a/labels.json','/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_calibration_v1')
print(json.dumps({'status':r['status'],'grid_count':len(r['grid_results']),'selected':r['selected']}),flush=True)
PY
```

```bash
timeout 120s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_bag_replay.py ros2_ws/src/ros_esc/test/test_bag_analysis.py' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_replay_tests.log 2>&1
```

The label-owner patch was captured during the completed label-freeze job. The calibration-owner patch was captured by the final report-publication command, which verified that its analyzer/core hashes match those recorded during calibration. These exact retention commands are included in the command artifact. Existing output directories are exclusive; do not rerun these commands against retained paths.

Label/calibration commands exited 0; calibration scientific status is failed. The earlier label publication command exited 1 and remains retained. Loaded owner source patches and all input/output hashes are retained; the detector hash stayed unchanged through the grid.

## Next evidence boundary

Preserve this fixed failure. A separately recorded diagnostic/development amendment may address window-period aliasing and construct an independently qualified basin-region oracle. It must use fresh versioned outputs, retain the failed grid/labels, and state how its new criteria were chosen. No threshold, geometry label or existing outcome has been changed by this report. No Gazebo or hardware was launched.
