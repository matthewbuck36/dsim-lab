# V2 M0 retained baseline inventory

Created 2026-09-09T04:10:20.253750+00:00; baseline Git 3369cfc83a64ff5d8354827fd5310caaf0c8e945.

Frozen inventory: 21 retained simulation runs, 5.160 GB, 18 historical passes and three failures. This adds no replay, V2 performance or new runtime result. All full database hashes, exact absolute paths and provenance are in [baseline_inventory.json](baseline_inventory.json).

## Frozen retrospective split

Within accepted primary/secondary repeat suites, sort (seed, run_id): first repeat is development; remaining repeats are retrospective holdout. All visible probes and three fixed failures are development diagnostics. Historical outcomes were already exposed; no V2 output was computed to choose the split. This is not unseen-population or statistical validation.

Development seeds: [19801, 19811, 19851, 19901, 19911, 19931, 20001, 20031].
Retrospective holdout seeds: [19812, 19813, 19814, 19815, 19816, 19817, 19818, 19819, 19820, 19912, 19913, 19914, 19915].

| Seed | Layout | Partition | Historical outcome | GB | Retained bag |
| --- | --- | --- | --- | ---: | --- |
| 19801 | primary | development_diagnostic | passed | 0.249 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_probe/2026-07-31/20260731T173056885644Z_simulation_phase08_v8_10_primary_visible_probe-v8_10_primary_probe_r1p5_a45_h25_19801-robus_d984451c/bag>) |
| 19811 | primary | development_replay | passed | 0.339 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T174647872704Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__0c6fce1d/bag>) |
| 19812 | primary | retrospective_holdout | passed | 0.253 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T175444823850Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__86d37cc2/bag>) |
| 19813 | primary | retrospective_holdout | passed | 0.295 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T180040525470Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__2e64532a/bag>) |
| 19814 | primary | retrospective_holdout | passed | 0.248 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T180737134521Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__40586d56/bag>) |
| 19815 | primary | retrospective_holdout | passed | 0.293 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T181322600424Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__6d852a0b/bag>) |
| 19816 | primary | retrospective_holdout | passed | 0.204 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T182011204534Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__cd6e0228/bag>) |
| 19817 | primary | retrospective_holdout | passed | 0.200 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T182456908057Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__64ce2ee7/bag>) |
| 19818 | primary | retrospective_holdout | passed | 0.245 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T182937296869Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__81504b96/bag>) |
| 19819 | primary | retrospective_holdout | passed | 0.303 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T183521295563Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__76348284/bag>) |
| 19820 | primary | retrospective_holdout | passed | 0.251 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_primary_repeats/2026-07-31/20260731T184228184557Z_simulation_phase08_v8_10_primary_repeats-v8_10_primary_repeat_r1p5_a45_h25-robust_gaussian__43e93b13/bag>) |
| 19851 | secondary | development_diagnostic | failed | 0.307 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_10_secondary_probe/2026-07-31/20260731T191433826976Z_simulation_phase08_v8_10_secondary_visible_probe-v8_10_secondary_probe_r1p5_a67p5_h25_19851_5cffc8a7/bag>) |
| 19901 | secondary | development_diagnostic | passed | 0.200 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_probe/2026-07-31/20260731T210056770365Z_simulation_phase08_v8_11_secondary_visible_probe-v8_11_secondary_probe_r1p5_a67p5_h25_19901_c0544b8e/bag>) |
| 19911 | secondary | development_replay | passed | 0.200 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/2026-07-31/20260731T211245658756Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_b9e46a70/bag>) |
| 19912 | secondary | retrospective_holdout | passed | 0.278 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/2026-07-31/20260731T211723714744Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_15c56eee/bag>) |
| 19913 | secondary | retrospective_holdout | passed | 0.199 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/2026-07-31/20260731T212352071223Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_96457b4e/bag>) |
| 19914 | secondary | retrospective_holdout | passed | 0.201 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/2026-07-31/20260731T212828990981Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d39b9a91/bag>) |
| 19915 | secondary | retrospective_holdout | passed | 0.195 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_secondary_repeats/2026-07-31/20260731T213307752047Z_simulation_phase08_v8_11_secondary_repeats-v8_11_secondary_repeats_r1p5_a67p5_h25-robust_ga_d014dc3c/bag>) |
| 19931 | varied_1to3 | development_diagnostic | failed | 0.313 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_broad_matrix/2026-07-31/20260731T215508693457Z_simulation_phase08_v8_11_broad_matrix-v8_11_matrix_r1p25_a45_ratio1to3_19931-robust_gaussia_056336a1/bag>) |
| 20001 | varied_1to3 | development_diagnostic | passed | 0.188 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_12_interior_anchor_probe/2026-07-31/20260731T231351648763Z_simulation_phase08_v8_12_interior_anchor_visible_probe-v8_12_interior_anchor_r1p25_a45_rati_439a8eac/bag>) |
| 20031 | varied_1to3 | development_diagnostic | failed | 0.199 | [bag](</home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_12_broad_matrix/2026-07-31/20260731T233137972843Z_simulation_phase08_v8_12_broad_matrix-v8_12_matrix_r1p25_a45_ratio1to3_20031-robust_gaussia_6efe976a/bag>) |

Exact paths come from hashed runner summaries; no suffix was reconstructed. JSON records full db3 hashes, resolved parameters/topics/scenarios, metadata/results/analysis hashes, retained Git commits, current versus historical parameter-file digests, all topic counts and bag receipt ranges, and selected decoded source/ROS timestamps, frame, position, phase and transform availability. Endpoint decoding is availability evidence, not full-stream qualification.

## Historical outcome provenance

- [phase08_8_10_primary_probe](../../validation/phase_08_8_m4_11_primary_probe.md)
- [phase08_8_10_primary_repeats](../../validation/phase_08_8_m4_11_primary_repeats.md)
- [phase08_8_10_secondary_probe](../../validation/phase_08_8_m4_11_secondary_probe.md)
- [phase08_8_11_secondary_probe](../../validation/phase_08_8_m8_3_v8_11_secondary_visible_probe.md)
- [phase08_8_11_secondary_repeats](../../validation/phase_08_8_m8_3_v8_11_secondary_repeats.md)
- [phase08_8_11_broad_matrix](../../validation/phase_08_8_m8_4_v8_11_broad_matrix.md)
- [phase08_8_12_interior_anchor_probe](../../validation/phase_08_8_m8_8_v8_12_visible_probe.md)
- [phase08_8_12_broad_matrix](../../validation/phase_08_8_m8_9_v8_12_broad_matrix.md)

Seed 19851 remains failed under the old lamp-association gate. Seed 19931 remains failed for unavailable outside-radius approach history. Seed 20031 remains formal 13/14 failure from direct-exit alignment despite complete scientific behavior; seeds 20032-20034 remain withheld. Old flags, fills and GOAL_HOLD are outputs to compare, never independent truth labels.

## Independent trap/progress and direction labels

M0 creates no independent interval labels. M1 must extend the existing bag reader/analyzer and aggregate_field_truth owner before performance claims:

1. Bind each replay to recorded Git/model, resolved source parameters, actual sensor geometry and source/ROS time mapping. Qualify finite values, source gaps and frame continuity across the full streams.
2. Derive evaluator-only aggregate-field basin regions and freeze sustained-entry/progress rules separately from the detector calibration grid; never consult old/new convergence outputs, fill centers or terminal states when setting truth labels. Preserve ambiguous/invalid intervals as unknown.
3. Revalidate field geometry prospectively: primary v8.10 has no retained aggregate topology result; v8.11/v8.12 local basins report optimizer_success=false at a fixed iteration bound. Those historical gates stay untouched, but approximate centers alone cannot certify new convergence onset labels.
4. Use actual observed pose and complete sensor cycles to label basin residence/progress. For direction, use a stationary-cycle GESC reference at fixed sampled positions with matching geometry/angular response/filter dynamics/objective. Weak references have no meaningful angular error.
5. Replay measures responses on logged trajectories; earlier intervention and moving verification need fresh simulation for behavioral evidence.

Existing owners: plotting_scripts/bag_reader.py, plotting_scripts/gesc_gaussian_bag_analysis.py, scenario_runner/aggregate_field_truth.py. No new analysis pipeline or Gazebo run is needed for label construction.

## Environment and next qualification

ROS Humble, rclpy, rosbag2_py, generated interfaces, NumPy/SciPy and Gazebo binaries are available after sourcing Humble and the ordinary workspace install. X display :0 responded to bounded xdpyinfo. Exact module origins, package prefixes, source/install digests and disk bytes are in JSON.

| Owner | Source equals normal install |
| --- | --- |
| detector | NO |
| runner | NO |
| schema | NO |
| analyzer | yes |

The ordinary detector/runner/schema install is stale. Fresh isolated build and explicit import/install qualification are necessary before M1 ROS tests/runtime; the root agent is undertaking that separately. Available dependencies permit this next work. This inventory performs no build or ROS/Gazebo launch.

Free disk at capture: 260.4 GiB. Runtime process inspection completed successfully; 0 matching Gazebo/runner/recorder processes were observed. The process-name/executable-token filter and exact output are in JSON.

## M0 checks and limits

- Full bag SHA-256: all 21 databases. SQLite checks: True; topic and total count agreement: True; required input topics present: True.
- Command: timeout 120s around sourced-Humble/workspace inline Python. SQLite URI mode=ro&immutable=1; PRAGMA quick_check; grouped COUNT/MIN/MAX; selected first/last payload decoding; streaming SHA-256. No reusable script or alternate pipeline added.
- No old analyzer invocation, retained-output mutation, failed experiment retry, hardware action or independent-label claim.
