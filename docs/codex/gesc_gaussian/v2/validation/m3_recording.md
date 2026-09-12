# M3 lifecycle recording validation

Verified 2026-09-09T08:33:42.854532+00:00. Final combined suite:
**82 passed in 24.24s**, exit0. This is implementation and serialized-wire
verification. No Gazebo, hardware, field probe, full-owner DDS experiment or
scientific qualification occurred in this subtask. M3 and the pilot remain
subject to [m3_plan.md](../m3_plan.md) and [status.md](../status.md).

## Existing owner integration

The subordinate `experiment_recording/v2_lifecycle_validation.py` supplies
`lifecycle_stream_errors(messages, identity, *, topics=None, metric_mode=None,
candidate_cost_mad_scale=3.0) -> (errors, metrics)`. Input is the existing bag
reader shape: topic mapped to `(bag_timestamp_ns, deserialized_message)` records
in each topic's recorded order. Optional `topics` maps manifest aliases to
selected paths. No separate recorder, bag reader, node or analysis pipeline.

The existing `validate_run.py` calls this helper after the unchanged strict M2
synchronized-stream check, emitting `v2_lifecycle_contract` and
`v2_lifecycle_metrics`. It resolves the selected detector mode/MAD scale from
retained launch arguments, with inherited defaults `pde_mean_v1` and3.0.
The helper tables contain epochs, confirmations, candidates, preparations,
unique commits, acknowledgement availability and GOAL associations. Direct
callers must pass an overridden MAD scale explicitly.

Lifecycle protocol schema1 is separate from nested observation schema2. The
root-owned manifest requires the epoch heartbeat and registers event streams
with minimum0. Missing event occurrences are valid; required topic registration
and types remain separate completeness checks. Invalid unbound startup contexts
and properly hashed explicit PDE invalidations are observable without authorizing
support.

## Verified contracts

- Exact run/stream/origin/frame, context sequences, authoritative epoch/start,
  fresh referenced SEARCH context and once-per-epoch confirmations. PDE wrappers
  bind hashes, actual recorded pose endpoints, finite inherited arrays and
  absolute timestamps. Confirmations join matching PDE support or centroid
  diagnostics. Later explicit PDE invalidation cannot authorize a new
  confirmation using that old support.
- Successful candidate snapshots publish independently of PREPARE, including
  no-fill GOAL cases. Hashes bind actual source/admission/receipt evidence and
  frozen candidate/metric association. Each observation joins recorded typed
  source and valid filter diagnostics. Source invalidation poisons its model
  stamp regardless of the notice's new sequence.
- The claimed first diagnostic received by the supervisor matches an exact
  recorded valid diagnostic observation/state/stamp and stays consistent across
  snapshot revisions. Separate DDS subscriptions cannot prove globally first
  receipt; the validator does not select the globally earliest bag diagnostic.
- Integer cycle bounds, three nonoverlapping half-open actual assignments,
  duplicate IDs, finite values, source gaps, caps and represented-position
  confinement. Interpolation-only outer brackets are not raw samples and may
  lie outside R when their represented boundary lies inside R.
- Exactly one actual raw minimum per revolution feeds existing
  `RotationCostWindow.summarize_minima`, which recomputes estimate, MAD,
  uncertainty and lower/upper negative-cost interval using the resolved scale.
  Bracket and augmented values cannot replace assigned actual raw minima. The
  numerical information floor is recomputed in raw units.
- PREPARE joins an exact previously published snapshot. Command sequences,
  immutable retries, original expiry, expected generation, target revision and
  prepared hashes remain bound. ACTIVATE/CANCEL may omit the unused snapshot;
  supplied snapshots must match. PREPARED cannot allocate or activate a fill.
- Every result hash is recomputed. ACTIVATED advances one generation and
  reproduces both registry digests; supersession preserves the exact old law.
  ALREADY_ACTIVATED never adds a commit count. Terminal results cannot precede
  commit in result-publisher order, including equal ROS ticks. Publishing CANCEL
  before commit does not establish that the owner received CANCEL before commit.
- Canonical mirrors must match typed authority and cannot be published before
  the committed source-version stamp. Their bag receipt may precede the typed
  result. Valid objective digests must reference the initial empty law or a
  typed generation created by composition time. Older known laws may remain
  during delivery/acknowledgement delay. Missing acknowledgements are explicit
  table values, not invented latency measurements.

## Evidence boundaries

No reconstruction of supervisor wall-clock readiness, callback receipt ordering,
full world-phase sector geometry/information profiles or latest-triplet choice
is claimed. Information amplitude/disagreement receive finite/threshold checks;
the existing moving-evidence owner/tests own their full numerical reconstruction.
The helper reuses the actual minima summarizer and adds no duplicate classifier.
The prepared-proposal digest is checked for identity and consistent echoes;
the unpublished worker payload cannot be reconstructed from its wire digest.

GOAL is associated with verified evidence in its recorded authoritative epoch.
`AlgorithmState` has no candidate ID, so a finer association is not claimed.
Strict M2 quarantine of ambiguous source evidence remains unchanged. These
limitations do not waive runtime, behavior, calibration or pilot gates.

## Retained attempts

Logs live at `/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`, basename
`m3_lifecycle_recording_<version>.log`. v1 covered the initial helper; v2 added
supersession/brackets and existing M2 regressions. v3 remains failed: all44
lifecycle failures came from the detached fixture lacking the shared supervisor's
new snapshot publication cache/collecting publisher;27 other checks passed.
v4 fixed that fixture and covered candidate/GOAL, optional payload and equal-tick
cases. v5 added actual raw summaries and sequence-independent revocation; v6
records the supervisor-receipt evidence correction; v7 adds canonical/objective
source-time authority. Intermediate evidence is retained separately.

| Version | Result | Bytes | SHA256 |
| --- | --- | ---: | --- |
| v1 | 32 passed in 10.63s | 100 | `60a6110fadc1b1ed6297761c879b04aad20bd2967364ee6cc0305cca70eb4467` |
| v2 | 67 passed in 16.07s | 100 | `64859f7f7988fddffa99b6a9c4fc4e36689c88568a16cf233bb33380e485649a` |
| v3 | 44 failed, 27 passed in 11.37s | 190790 | `c27224f2335e840de23fc896279a8367b191fa030ef11014b0f29c3d86118b25` |
| v4 | 71 passed in 19.77s | 100 | `040c481839540f90193fd38030d32a8d90439f37a5329f6a6e61a27907a642a9` |
| v5 | 78 passed in 21.26s | 180 | `f0a76445021404ade6e2963a845181d35f20307422add6d363f2e14284d401bb` |
| v6 | 80 passed in 22.66s | 180 | `b3e354bd6a44685e6b105dd9219075175a1daf8b7376c9f1745f2de8b2623a12` |
| v7 | 82 passed in 24.24s | 180 | `43b5f4dc5faad9224bc258ec073d03995675ccd715c65f5211f854c6e37f2f77` |

## Exact commands

All commands ran from `/home/mattb/dsim-lab`. These pytest commands launched no
ROS graph. Both lifecycle arms round-trip actual generated ROS messages through
serialization. The detached fixture invokes the existing supervisor snapshot
owner with a collecting publisher. The unchanged strict M2 recording tests run
alongside separate lifecycle fixtures; no full M2 runtime graph claim follows.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v1.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v2.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v3.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v4.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v5.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v6.log 2>&1
```

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_lifecycle_recording_v7.log 2>&1
```

Final static checks passed:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/experiment_recording/v2_lifecycle_validation.py ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py
git diff --check -- ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py
python3 - <<'PY'
from pathlib import Path
for name in ('ros2_ws/src/ros_esc/ros_esc/experiment_recording/v2_lifecycle_validation.py','ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py'):
    p=Path(name)
    assert all(line == line.rstrip() for line in p.read_text().splitlines()), name
print('Scoped compile and whitespace checks passed')
PY
```

A documentation-only construction command initially failed with a nested here-doc
terminator syntax error before writing this file; the corrected command used a
distinct delimiter. No source or validation result changed.

## Source boundary

These hashes identify this subtask's final tested source, not a freeze of the
concurrently implemented supervisor/fill owners or the entire M3 milestone.

| Owner | Bytes | SHA256 |
| --- | ---: | --- |
| `ros2_ws/src/ros_esc/ros_esc/experiment_recording/v2_lifecycle_validation.py` | 42308 | `6a2fddb0b444e207903b0b0dcb75f9557d0bbe73fd14dfb413651827c7858250` |
| `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py` | 68295 | `d24abbafeed34a888668f788a3e407c526b2f2ce14f5d2490dfa1ec1d9cf7876` |
| `ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py` | 27802 | `5843cc97896a63f475a42d23ee9126507c69f91c39cb23a849c4e799c6175ccd` |
