# Phase 09 M8N stationary-odometry estimator correction

Date: 2026-08-18
Classification: Level B bounded runtime correction
Result: host and local physical snapshot qualified; corrected source transferred
to the mounted Pi; Pi build, check-only, and physical validation deferred

## Retained failed evidence

Preserve this run unchanged:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-18/
  20260818T131824869516Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_9991e716
```

It reached `CONVERGED_FILL_READY`, entered `VERIFY_EXTREMUM`, completed three
candidate rotations, and transitioned to `DESIGN_OR_MERGE_FILL`. The Gaussian
fill owner then emitted `FILL_REJECTED` reason 30:

```text
detail: insufficient valid synchronized samples
input_sample_count: 40
valid_sample_count: 22
rejected_position_increment_mad: 18
```

The supervisor entered `FAILSAFE` with `fill design rejected`; the recorder
then revoked readiness. Completeness passed `60/62`. Vicon evaluation, all
required topics, rotation sequencing, legacy CSV export, and final bag command
zeros passed. The failed run is not replaced or promoted to acceptance.

## Diagnosis

Read-only decoding of the finalized sqlite3 bag reproduced the exact 40-sample
estimation window. The stationary `/odom` increments were approximately
`25.311e-6` and `50.621e-6 m`, while the increment median and MAD were about
`1.6e-9 m`. The old unbounded modified-z denominator assigned scores above
`10,000` to encoder-scale quantization.

Passing all 40 otherwise-valid samples through the unchanged downstream
estimator and designer produced a valid fill. This isolated the correction to
the position-increment MAD scale; no sample-count, speed, synchronization,
design, or supervisor gate needed relaxation.

## Correction

The shared `EstimatorConfig` now declares
`position_increment_mad_floor_m=1e-4`. The robust Gaussian node declares the
same ROS parameter, passes it into the estimator, and includes it in its typed
configuration event.

Only the position-increment MAD denominator is floored. A value of zero
retains the prior calculation. The independent hard
`maximum_position_speed_mps` check remains ahead of MAD filtering. Raw-cost
MAD, finite and timestamp validation, synchronization, the minimum of 40,
fill validation, and fail-safe behavior are unchanged. The implementation is
shared by simulation and physical robust profiles; legacy behavior does not
construct this estimator.

## Exact replay result

The retained bag was copied temporarily to the host for read-only sqlite/CDR
decoding; the Pi run directory was not modified.

```text
corrected_valid=40 corrected_position_rejected=0
prior_valid=22 prior_position_rejected=18
fill_success=True amplitude=0.499920 exit_radius=1.366771 confidence=0.614507
```

## Validation

All commands were bounded where they could run processes.

| Gate | Result |
|---|---:|
| `test_robust_gaussian_algorithm.py` | 31 passed |
| `test_observability_contract.py` | 15 passed |
| `test_legacy_behavior.py` | 37 passed |
| `test_supervisor_integration.py` | 62 passed |
| snapshot robust regression using snapshot source | 31 passed |
| snapshot shared parity | 29 passed |
| remaining snapshot Phase 09 tests | 201 passed |
| modified Python compile + critical lint | PASS |
| `git diff --check` | PASS |
| canonical isolated three-package build | PASS, 13.8 s |
| snapshot isolated three-package build | PASS, 15.0 s |
| installed snapshot robust-node parameter probe | `0.0001` declared/effective |

Canonical build root:

```text
/tmp/phase09_m8n_build.7XaecP
```

Snapshot build root:

```text
/tmp/phase09_m8n_snapshot_build.eeMnuK
```

The first canonical build attempt selected the physical-only package name and
omitted canonical `turtlebot3_rotating_sensor`; a clean correctly scoped retry
passed. An exploratory `colcon test` invocation used canonical checkout
discovery with the snapshot build root, omitted the physical package, and
encountered the inherited `ros_esc_interfaces` CMake-lint baseline. It was
stopped and replaced by the explicit snapshot pytest suites above. These are
command-scope diagnostics, not product regressions.

## Snapshot recovery and parity

Pre-edit backup and patches:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260818T203147Z_m8n_stationary_odom_mad
```

The backup archive SHA-256 is
`a6eb685badf2dffdde04c278abd912f3b9d04ac2c66961b7999a7cf938d8f834`.
Checkout and snapshot hashes now match:

```text
basin_estimator.py
  cc0665556eefd84b4ae098fd7553cb9e32ef4b39a9159d98edcd8d6a75f43bb0
gaussian_fill_script.py
  58d3e6921a528ffc2bdfd87fcae1393c191414df099b067d432442d116a2ecfa
```

## Authorized mounted-Pi source transfer

The operator explicitly authorized implementation in the mounted physical-Pi
files. Immediately before transfer, both target hashes still matched the
expected pre-M8N source, so no overlapping Pi-side edit existed. The two files
were preserved at this Pi path:

```text
/home/pi/phase09_backups/20260818T204100Z_m8n_stationary_odom_mad
```

The backup contains unpacked copies with their original relative paths and a
`source_before.tar.gz` archive. Its hashes are:

```text
basin_estimator.py
  1ebd730772a1a1a947b8a7d95a61d6db3fcf0f7d6338dcb9ea5ef6577568a53b
gaussian_fill_script.py
  5fd0886aeca9dc70bfeb9951f9149728252b2174285bc582dfe257648ede83bc
source_before.tar.gz
  a7d81e0050085e2d3e83a292f567ef2af1642b086ec5ab57966a4a08532d5ded
```

An exact-file `rsync -rlptO --checksum --itemize-changes --dry-run` named only
`basin_estimator.py` and `gaussian_fill_script.py`. The same command without
`--dry-run` transferred those two files, with no deletion option. The
post-transfer dry run was empty. Checkout, local snapshot, and mounted Pi now
share these hashes:

```text
basin_estimator.py
  cc0665556eefd84b4ae098fd7553cb9e32ef4b39a9159d98edcd8d6a75f43bb0
gaussian_fill_script.py
  58d3e6921a528ffc2bdfd87fcae1393c191414df099b067d432442d116a2ecfa
```

Read-only host validation against the mounted source passed the shared parity
suite (`29 passed`), the robust Gaussian regression (`31 passed`), AST parsing
of both transferred files, and fatal `flake8` selections
`E9,F63,F7,F82`. An import probe resolved both modules from
`/home/mattb/tb3-pi/...` and reported the estimator default as `0.0001`.

Two exploratory broader-suite invocations are retained as command-scope
diagnostics. The canonical legacy suite cannot collect with the physical
package first on `PYTHONPATH` because that package intentionally omits the
simulation-only `Multi_Light_Source_Cost`. The observability suite then
reported `13 passed, 2 failed` because its legacy cost-owner CLI expectations
also target the canonical simulation package; the second failure followed the
first test's interrupted ROS context. Neither diagnostic implicates either
transferred Gaussian owner. The compatible mounted parity and robust suites
are the acceptance evidence.

The material transfer and mounted-source test commands were:

```bash
pi_dir=/home/mattb/tb3-pi/ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node
snapshot_dir=/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node

rsync -rlptO --checksum --itemize-changes --dry-run \
  "$snapshot_dir/basin_estimator.py" "$pi_dir/"
rsync -rlptO --checksum --itemize-changes --dry-run \
  "$snapshot_dir/gaussian_fill_script.py" "$pi_dir/"
rsync -rlptO --checksum --itemize-changes \
  "$snapshot_dir/basin_estimator.py" "$pi_dir/"
rsync -rlptO --checksum --itemize-changes \
  "$snapshot_dir/gaussian_fill_script.py" "$pi_dir/"

source /opt/ros/humble/setup.bash
source /home/mattb/dsim-lab/ros2_ws/install/setup.bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/home/mattb/tb3-pi/ros2_ws/src/ros_esc:/home/mattb/tb3-pi/ros2_ws/src/turtlebot3_vehicle_nodes:${PYTHONPATH:-}
timeout 120s python3 -m pytest -q \
  /home/mattb/tb3-pi/ros2_ws/src/ros_esc/test/test_phase09_shared_parity.py
timeout 180s python3 -m pytest -q \
  /home/mattb/dsim-lab/ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py
```

## Explicitly deferred

No Pi build, Pi-terminal command, ROS graph, Vicon process, device access,
recording, actuation, lamp operation, or motion occurred. The operator-owned
bare wrapper build and `--check-only`, followed by a fresh retained physical
trial, remain separate future gates. Source parity alone is not physical
validation. The frozen Phase 10 V1 report was not edited and does not claim
M8N results.
