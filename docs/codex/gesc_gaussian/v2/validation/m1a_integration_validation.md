# M1a analyzer integration validation

The existing reader/analyzer pipeline now supports the frozen M1a enclosure
contract while preserving the original M1 grid and disk-label branch. This
record describes implementation validation; no M1a field qualification or
calibration has been executed by the validation agent.

The label pass checks the frozen plan, contract, inventory, eight development
trace references, 79 synthetic traces and unchanged thirteen-run holdout.
Existing qualified input traces are referenced without regeneration. The
owner receipt includes analyzer, reader, enclosure helper, aggregate evaluator
and the actual cost-function objects module; Python/NumPy/SciPy versions are
recorded before geometry work. Three independent geometry groups use at most
three processes, disjoint incremental receipts and deterministic output order
under the unchanged global command timeout. Source, group and point populations
remain bounded by the contract.

Positive residence uses the helper's cell-union interior and complete represented
segments. Negative travel uses the conservative exclusion mask and the exact
six-second measurement interval, clipping only the first represented segment by
source-time interpolation. Frozen input coordinates and spatial masks remain
unchanged. Calibration verifies complete frozen labels and their numerical
receipts before detector import, uses the explicit contract grid, and preserves
all-positive/zero-negative/nonempty-retained-denominator acceptance.

Validation from repository root:

```bash
timeout 180s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_bag_replay.py ros2_ws/src/ros_esc/test/test_bag_analysis.py' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_replay_tests_final.log 2>&1
git diff --check
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

Result: **44 passed in 1.71 seconds**; diff and context checks passed. The
fixtures cover immutable population/hash drift, strict contract declarations,
publication before detector import, no output-bag read during relabeling,
exclusive atomic publication and partial-attempt handling, segment crossing of
holes, boundary/shared-edge behavior, exclusion dilation consumption, exact
six-second slow-drift rejection and the three-process dispatch cap. The helper's
separate numerical tests are owned and reported by its implementation agent.

## Proposed execution commands, not yet executed

Run each command from `/home/mattb/dsim-lab` only after root review/checkpoint.
Exclusive output directories and noclobber logs preserve earlier attempts. The
second command follows complete reviewed label publication; an incomplete or
timed-out label attempt does not authorize calibration.

```bash
set -o noclobber
timeout --signal=TERM --kill-after=5s 600s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1.log 2>&1 <<'PY'
import json
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import freeze_v2_replay_labels
r = freeze_v2_replay_labels(
    'docs/codex/gesc_gaussian/v2/validation/baseline_inventory.json',
    'docs/codex/gesc_gaussian/v2/validation/m1a_contract_v1.json',
    '/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1')
print(json.dumps({'frozen_runs': len(r['runs']),
                  'spatial_labels': sum(len(run['labels']) for run in r['runs']),
                  'labels_path': '/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/labels.json'}), flush=True)
PY
```

```bash
set -o noclobber
timeout --signal=TERM --kill-after=5s 300s bash -c 'source /opt/ros/humble/setup.bash; source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash; python3 -' > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_calibration_v1.log 2>&1 <<'PY'
import json
from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import calibrate_v2_detector
r = calibrate_v2_detector(
    '/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/labels.json',
    '/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_calibration_v1')
print(json.dumps({'status': r['status'], 'grid_count': len(r['grid_results']),
                  'selected': r['selected']}), flush=True)
PY
```

The five-second kill grace is process cleanup after the fixed execution timeout;
it grants no additional numerical work or automatic retry. Preserve incomplete
attempts, completed point receipts and logs. A failed fixed grid remains failed.
