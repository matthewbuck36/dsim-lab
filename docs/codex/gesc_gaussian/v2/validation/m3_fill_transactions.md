# M3 Gaussian preparation and atomic activation validation

Status: focused implementation evidence passes; milestone-wide integration and
scientific qualification remain separate. No Gazebo, physical actions, field
probes, calibration, or commits were performed by this task.

## Implemented owner behavior

The existing Gaussian node opts into one `MovingFillRuntime`. Its single worker
receives detached support and frozen estimator/designer/registry configuration,
uses the existing estimator and bounded designer, and returns an immutable
proposal without allocating IDs, publishing, or accessing live node buffers.
The serialized owner polls completion and handles PREPARE/ACTIVATE/CANCEL.

Snapshot hashes retain shared boundary observations. Only the union of the
three half-open actual-sample index ranges enters raw fitting. Boundary brackets
are validated and used to check interpolated boundary confinement; their raw
costs do not enter fitting. A fixture changes outside-interval bracket costs to
`-1e200` without changing any fit input. Frozen support bounds preserve the
existing speed/MAD filters without substituting the legacy request-ending eight
second window. Fresh V2 redesign support is retained and merged with compatible
cluster samples; the legacy retained-only redesign option remains confined to
its existing legacy path. Conflicting samples and capacity excess are rejected,
not overwritten or decimated.

The owner independently binds the first actual selected Timekeeper origin.
Invalid or changed origins prevent further admission. Own selected poses retain
original ROS/steady receipt times, accept at most0.5s source lead in a64-item
buffer, and keep the latest mature pose available while newer poses await clock
coverage. Final activation requires fresh source and original receipt, matching
fresh epoch/state, the original immutable expiry, exact generation/target/hash,
and a pose inside the frozen neighborhood. Equal-stamp AlgorithmState updates
retain that stamp's first receipt even for legitimate transitions under a held
clock; source regressions invalidate and terminal changes cancel immediately.

PREPARE permits fresh preceding VERIFY/REPULSE as well as the matching DESIGN
purpose, allowing cross-topic delivery order. ACTIVATE requires current DESIGN
and its exact previous state. The original design deadline is never extended.
Registry staging builds geometry, retained support and containers before the
serialized generation/ID change. The owner validates again after staging and
hashing, commits without a yield, caches ACTIVATED, then publishes combined
result and canonical/compatibility/event mirrors. Post-commit publication
failure cannot turn the accepted commit into rejection. A canceled late worker
cannot commit. Commands retain identity/hash/outcome tombstones, at most4096 per
run; terminal preparations release their large snapshot/proposal buffers.

The existing modified-cost node consumes combined activation atomically in V2.
It validates new and superseded geometry, exact prior/resulting active-law
digests and sequential generation before replacing Gaussian/affine maps. It
ignores canonical Gaussian mirrors as activation authority. ALREADY_ACTIVATED
has its own whole-envelope hash; commit identity excludes response enum,
command sequence, outer publication stamp and that envelope hash, while keeping
all immutable commit fields. Repeated commits do not reapply map changes.
Lifecycle endpoint overrides must resolve to the frozen canonical endpoints;
hidden custom topics fail startup. Selected sensor/pose streams remain bound
through the existing stream descriptor.

Legacy selector/default, topics, fit policy, sign and units remain. The optional
`freeze_sample_window(..., snapshot_bounds=...)` affects only V2 callers.
Compatibility `source_timestamp` is the candidate confirmation's seconds from
the bound Timekeeper origin; typed preparation/commit/source bounds remain
absolute integer nanoseconds.

## Exact commands and retained results

All commands ran from `/home/mattb/dsim-lab`. Logs live in
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.
The common shell setup for every pytest invocation was:

```bash
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}"
```

The preflight was:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

It passed before source changes. Syntax compilation was used during editing;
it is not substituted for the tests below.

| Retained log | Outer bound | Exact pytest file arguments under `ros2_ws/src/ros_esc/test/` | Result |
|---|---:|---|---|
| `m3_fill_transactions_v1.log` | `timeout 180s bash` | `test_v2_fill_transactions.py test_robust_gaussian_algorithm.py` |57 PASS,3.28s |
| `m3_fill_transport_v1.log` | `timeout 120s bash` | `test_v2_fill_transport.py test_v2_fill_transactions.py test_v2_direction_transport.py test_v2_upstream_transport.py` |39 PASS,2 SKIP,6.73s; upstream's explicit domain176 guard skipped because outer domain was unset |
| `m3_fill_transport_v2.log` | `timeout 120s bash` | same four files, `export ROS_DOMAIN_ID=176` |42 PASS,3 inherited warnings,13.96s |
| `m3_fill_transport_v3.log` | `timeout 120s bash` | same four plus `test_robust_gaussian_algorithm.py`, domain176 |1 FAIL,74 PASS,3 inherited warnings,15.21s; retained exception-path defect below |
| `m3_fill_transport_v4.log` | `timeout 120s bash` | same five files, domain176 |76 PASS,3 inherited warnings,15.02s |
| `m3_fill_regressions_v1.log` | `timeout 180s bash` | `test_legacy_behavior.py test_v2_runtime.py test_v2_clock_admission.py` |109 PASS,2.63s |

Every row used `python3 -m pytest -q` and redirected stdout/stderr to its exact
log. The final transport invocation was:

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_transport_v4.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export ROS_DOMAIN_ID=176
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_fill_transport.py ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py ros2_ws/src/ros_esc/test/test_v2_direction_transport.py ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py
BASH
```

The retained v3 failure showed that rejecting reuse of an accepted preparation
ID was swallowed by a publication-error handler that tested the old pending
record's accepted status. It now tests whether the current callback actually
committed. The rejected new command emits REJECTED while the original accepted
record remains retryable as ALREADY_ACTIVATED. Another review fixture verifies
that a CANCEL for an old terminal preparation cannot cancel a newer preparation.

The three warnings are inherited unused quaternion-intermediate square-root
warnings in the upstream fixture. Checked transforms and outputs remain finite;
no new warnings arose in fill preparation or registry/composition tests.

## Evidence boundaries

Pure controlled-worker fixtures test cancellation before/during/after completion,
deadline/source/receipt/pose/epoch/state failures, last-check staging races,
command conflicts/capacity, immutable IDs, exact revision/generation binding,
atomic supersession, canonical-mirror suppression and duplicate/retry handling.
A separate analytic support fixture executes the existing estimator/designer.

`test_v2_fill_transport.py` uses the actual Gaussian node, its actual worker,
real typed DDS messages, and actual modified-cost owner on isolated domain177.
It verifies inactive preparation, activation/digest/mirror delivery, and a late
CANCEL preserving the accepted fill. CandidateSnapshot is synthetic frozen
input; this fixture does not run the supervisor's evidence classifier or a
robot controller and does not prove natural-trajectory qualification.

The inherited direction/domain122 and upstream/domain176 transport tests now
supply an explicitly synthetic combined activation fixture via
`v2_fill_fixture.py`. This changes only their fill setup authority; it does not
claim those tests exercise the actual fill owner. Old M2 source/evidence and
logs remain retained. The actual upstream graph still exercises encoder,
sensor pose, cost, delayed source, composer and filter with held-clock source
admission, qualified rolling output and fault recovery.

M1 has no selected calibrated neighborhood, M2 historical research reference
remains unavailable, and M4/Gazebo is not released by these synthetic checks.
Root owns the remaining M3 integration, milestone status, checkpoint and handoff.

## Source and retained result hashes

SHA256 at this validation boundary; shared files include earlier M2 changes.

```text
8d23c6627dd4e005c6180323e08ba3701fcbe5512a61275043255dab175b0b36  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py
ee39be947009d3a39966a12534cac8c597133ee78706e8cfd182f17337ae1803  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py
1d94e7b2ee3282236d6556febcf8c2f215ff4a73831e8f0d87a97d513a070f32  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_preparation.py
149f06c71e15d6f0183667d61dcd3cf77597085af8c51a4259932d612f4293f6  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/v2_fill_runtime.py
82c26b57f012288183cef96b2f77f5fa795f0d9b9f7620115020f0f38d549674  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py
7e9d0a9fe9897e959395ae3f717bac8aaef29d318e1e86cdb41fc22231e745c0  ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py
0cf1d63372c0e5908c6f67688dc49a4a510b05c82c5cacf720b6695dbe97aafa  ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_fill_activation.py
b078e60d45771360d91091a310a9b992aa64eb4ae3715d48a5701f2f54a478b2  ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py
131d0b03e69535a893ae71a5b3f54be2fde087d7cbc8a3593ab8c1a30a8400ae  ros2_ws/src/ros_esc/test/test_v2_fill_transport.py
f22e797facdd1d634eb82e7832af4b0636a667cb4df01870b9751b3cbae6beb4  ros2_ws/src/ros_esc/test/v2_fill_fixture.py
6a1e972611d4242b4062662cce1e99a59bf06e840c258c2c2be2d3c1d7da942b  ros2_ws/src/ros_esc/test/test_v2_direction_transport.py
9ba967e063b081100899e56edf8ac6d3adc70e882b845f295e969564df6e17ac  ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py
18ec7d9c214929ba8b370c3d05833fbe6119815d4225391363ef8a781d744104  /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_transport_v3.log
3744e01cba20a06cbb7c2c4f7dd0ae99a134cf71766f357593b8398e601dfd51  /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_transport_v4.log
4ea832d58dae3f6ffdc4b9980b1f9a87d44066c485a3d54a6cadd037458117fc  /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_regressions_v1.log
```

Final scoped whitespace review passed:

```bash
git diff --check -- ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node ros2_ws/src/ros_esc/ros_esc/modified_cost_node ros2_ws/src/ros_esc/test/test_v2_direction_transport.py ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py
```

## Final bounded contract correction, v5

Root's review authorized two further checks before pipeline execution. Frozen
snapshot MAD, uncertainty and information disagreement must be nonnegative;
the existing floor/amplitude guards require strictly positive information.
Expected DDS `RuntimeError` during result publication is logged while the
already cached outcome stays retryable. A mirror publication runtime failure
also retains the committed registry and lets the owner process later commands.
Neither failure rolls back or allocates another ID. Fixtures cover both actual
result-publication failure/retry and canonical-mirror runtime failure.

```bash
timeout 180s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_contract_v5.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py ros2_ws/src/ros_esc/test/test_v2_fill_transport.py
BASH
```

Result:51 PASS in4.24s; no warnings. This focused rerun includes the actual
Gaussian/composer DDS test and supersedes the v4 hashes below only for the two
changed source/test files; other v4 source hashes remain unchanged.

```text
4e7cfe51b4da327d2ba140148f5d018626e461e2dee0273e176496c82c3f7d1d  ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/v2_fill_runtime.py
2e57d54b3b5584556078e7a17924d700df769c667dacf5c6dac3ffcc33698c62  ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py
9826517a438514e7c8c5eb6210bed8be3b99cbc86be5d4a7a41ee2c91fd41f55  /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_fill_contract_v5.log
```
