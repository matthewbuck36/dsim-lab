# M2 full upstream DDS regression — 2026-09-09 UTC

Final focused fixture result: **2 passed in 8.00 s**, exit0, under timeout120s on
isolated ROS_DOMAIN_ID176 (v8). Review identified that silently dropping a
conflicting upstream sample leaves earlier point confidence alive. The v6 test
and log are preserved; v7 verifies the explicit downstream invalidation
contract, then fresh instantaneous recovery. V8 repeats the unchanged fixture
after the final callback-entry receipt capture correction. The results below validate
the source-clock correction with
synthetic inputs through the actual existing owners. It does not qualify the
retained natural trajectories, reopen the unavailable192-anchor reference,
select detector parameters, establish a spatial gradient, or release Gazebo/M3/M4.

## Owners and input contract

`test_v2_upstream_transport.py` instantiates the actual `EncoderNode`,
`SensorPosition`, `CostFunction`, `SimulationDisturbanceNode`, `ModifiedCost2D`
and `CustomFilter` in a bounded single-threaded ROS executor. The harness sends
JointState, Odometry, Timekeeper, Clock, AlgorithmState and a fixed GaussianFill.
It never fabricates encoder, sensor transform, raw/augmented cost, provenance,
objective or direction messages, calls a production callback directly, starts
a launch graph, or publishes a motion command.

Only the cost and noise functions are replaced. With the actual selected sensor
geometry, the analytic raw cost is `-cos(sensor_world_phase)-G(sensor_xy)`;
the real composer adds the known Gaussian `G`, giving an exactly checkable
`-cos(sensor_world_phase)` augmented objective. The selected full-rotation GESC
filter and actual transform, delay and composition owners run normally.

The static descriptor and typed provenance/objective/direction/observation
wires use schema2, with `cost_key_basis=model_input_time`. Timekeeper origin
is10s. JointState headers carry 30Hz absolute acquisition stamps and alternate
two frame labels; their receipt order remains unchanged. Odometry moves and
turns the base, with exact source headers. The real sensor owner receives the
matching odometry before each encoder-triggered calculation; this fixture
does not claim that arbitrary production cached odometry is simultaneous.

The source owners see100ms /clock ticks. Three distinct acquisitions lead each
held clock by up to100ms. For the first batch only, composer/filter clock
subscriptions are remapped to a second harness Clock topic: delayed metadata
arrives before those consumers receive clock coverage. This deterministic
transport ordering models lagging DDS clock delivery, not separate physical
time domains. Both clock streams then advance together. A single initial
acquisition batch is omitted to complete the deliberate lag case; the maximum
source gap remains below the existing500ms bound.

## Assertions and observed counts

- 453 accepted acquisitions span15.166666667s and produce453 raw samples,
  objectives and valid filter outputs. Each original encoder/transform key is
  preserved exactly through evaluation, raw/source-cost and objective metadata.
- 151 actual cost-publication stamps each occur three times. Acquisition keys
  and sequences remain distinct; integer publication time remains separate.
- The existing100ms sensor delay preserves serialized raw and provenance
  messages exactly. Metadata cannot bypass consumer clock coverage.
- Every observed source/pose/encoder bracket is exact, with zero synchronization
  error. Source/publication/bracket stamps are covered before admission/output.
  Earliest original receipt can precede acquisition; latest receipt also includes
  the objective created after composer catch-up. Neither is rewritten as admission.
- 186 source observations qualify after at least three measured revolutions,
  with required actual sector counts and a0.5 blend. Qualification persists into
  VERIFY under the same objective identity. Gaussian values, observed sensor
  geometry and finite current-body outputs match the analytic fixture.
- Identical retransmissions create no new accepted source sample. V7 forwards
  the first finite same-stamp contradiction and a1ms source-order regression
  through the actual sensor owner. They produce two invalid provenance
  notifications, with no additional cost evaluation or raw/source-cost sample.
  The notification of the previously evaluated key retains its actual cost
  publication time; the never-evaluated regression carries zero under invalid
  flags. The real delay preserves both notifications, and composer/filter
  tombstone both keys. Filter confidence clears and no valid output is produced.
  Original and contradictory JointState retransmissions cannot rehabilitate
  either key. Frame labels do not establish authority.
- One fresh source after invalidation resumes finite instantaneous GESC with
  zero blend and no restored three-cycle confidence. V7 therefore has454 valid
  evaluated samples overall:453 in the qualification stream plus one recovery.
- A detached future transform expires after its original500ms steady receipt
  lifetime while ROS /clock remains held. A repeated JointState does not refresh
  that lifetime. Subsequent clock coverage cannot evaluate the expired packet.
- A stopped source emits no further output after expiry even after explicitly
  acknowledging fresh selected odometry and fresh state at the actual filter.
- A separate real upstream default-mode case preserves the legacy publication
  clock stamp, string headers and array layout for two distinct acquisitions
  under one held clock; it publishes no V2 provenance.

Three inherited `invalid value encountered in sqrt` warnings occur while the
legacy quaternion helper computes unused candidate components. They were not
suppressed. The emitted transforms, evaluated matrices and outputs pass the
finite/geometry assertions. This test does not repair or broadly qualify that
unchanged quaternion routine.

## Exact command and retained versions

Run from `/home/mattb/dsim-lab` after sourcing the rebuilt isolated interfaces:

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_upstream_transport_v8.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export ROS_DOMAIN_ID=176
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q -s ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py
BASH
```

Each earlier command is identical except for its retained log suffix. No log
was overwritten. The main fixture also has an80s wall deadline and2s delivery
bounds; the legacy fixture has a15s wall deadline. Executor shutdown is bounded
at2s. Context preflight was
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
and passed, exit0, before the new test was written.

All logs below are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`:

The passing v6 test itself is retained in that directory as
`test_v2_upstream_transport_v6.py`, with the same source hash recorded below.

| Log | Result | Interpretation/correction |
|---|---|---|
| `m2_upstream_transport_v1.log` |1 failed,1 passed;0.91s;exit1 |Fixture setup used nonexistent GaussianFill validity/array fields. Replaced with the real scalar covariance/active fields before any V2 acquisition.|
| `m2_upstream_transport_v2.log` |1 failed,1 passed;6.95s;exit1 |All453 outputs arrived; final diagnostic callback was not yet acknowledged. Added its independent DDS delivery acknowledgement.|
| `m2_upstream_transport_v3.log` |1 failed,1 passed;7.38s;exit1 |Fixture incorrectly required the latest receipt to precede acquisition although the objective is composed after catch-up. Corrected to the preserved earliest receipt.|
| `m2_upstream_transport_v4.log` |2 passed;7.83s;exit0 |Complete transport, confidence, rejection, expiry and legacy checks.|
| `m2_upstream_transport_v5.log` |2 passed;7.66s;exit0 |Added explicit exact key equality end to end and serialized raw-delay equality.|
| `m2_upstream_transport_v6.log` |2 passed;7.54s;exit0 |Also acknowledges fresh selected pose before the stale-source assertion; later conflict-invalidation review gap remains outside this version's assertions.|
| `m2_upstream_transport_v7.log` |2 passed;8.58s;exit0 |New explicit source invalidations reach actual downstream owners, reset confidence and prevent replay; one fresh source resumes instantaneous fallback. Final callback-entry receipt patch still pending.|
| `m2_upstream_transport_v8.log` |2 passed;8.00s;exit0 |Final unchanged fixture after callback-entry receipt capture correction.|

The retained failures are fixture defects/incorrect test assumptions, not
successful runs or demonstrated production losses. The old omitted-upstream
fixture passes and unavailable reference outcome retain their original scope.

## Final v8 source identity

SHA256 values read after the final focused run, with source owners frozen:

| File (relative to repository unless a log basename) | SHA256 |
|---|---|
| `ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py` |`3ad743450f78043c550f0e4cec1dd871598038be8942a02efa0305b7266799c2`|
| `ros2_ws/src/ros_esc/ros_esc/encoder_node/encoder_node_script.py` |`26daa65446c79a99c6cc09b752a476e64ae110231ac302a203913d56f009b230`|
| `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/sensor_pose_node_script.py` |`027c2633274ec1f58b1b70045b0e7ddef4444b35fab9226bde63fd0f86e44f7e`|
| `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py` |`2bccf998b56967e91ea090d3aad56e55273abe5243f047cfdf867581130be29e`|
| `ros2_ws/src/ros_esc/ros_esc/filter_node/v2_runtime.py` |`1d4e0955dd261ceebb8f97523324b35b987c7dd546d6ca792f7193e581241335`|
| `ros2_ws/src/ros_esc/ros_esc/filter_node/rolling_gesc.py` |`447f6f739fbbc5f2ba168c82717cf77191d05ca8daa99b522e657a3e886e6648`|
| `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_objective.py` |`ff27435e9358458e2387d9c2b8e820fabfd5a84b3f58a0f514658bfd1534cd83`|
| `ros2_ws/src/ros_esc/ros_esc/v2_stream.py` |`7e4caf66723d6dd8159478995799c076ec3fb45da91060141cacef70bbb842d2`|
| `ros2_ws/src/ros_esc_interfaces/msg/SynchronizedObservation.msg` |`e82b6b939496ebe2097b40164f1d1cc0caf409d731630cd655380660dabdae8b`|
| `m2_upstream_transport_v8.log` |`682df6b6aa875eddddbf2d49519eb67431bcff49f1e1456c4f63b66116cb7eab`|

V7 used the same test source as v8. Its retained log SHA256 is
`ceefa9d9852913335c3d33ef3bb89af9bfc5734a1f024bd04a89d37fba68a55f`.

## Retained v6 source identity

SHA256 values read after the v6 focused run, before the explicit invalidation
correction:

| File (relative to repository unless a log basename) | SHA256 |
|---|---|
| `ros2_ws/src/ros_esc/test/test_v2_upstream_transport.py` |`7d510287e5206b121f4fd9f642a740fce2e479537070407dfcad59137a69749e`|
| `ros2_ws/src/ros_esc/ros_esc/encoder_node/encoder_node_script.py` |`113a76ae528a94504b9ef9e6a02608b9bd1a6bd65e58a70ae0360840aa1d288c`|
| `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/sensor_pose_node_script.py` |`f2beaf4dfb9eb01a9d189dfe9f36c8e59705998b5b42a3314b67528793e9f726`|
| `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py` |`5cd0ea5a5600045e45ec652175a159c92539c47aa30fc3a9fb4ca584d79b4f78`|
| `ros2_ws/src/ros_esc/ros_esc/filter_node/v2_runtime.py` |`d9cdbe22f806f498ebf6e9c8c349ff96286da78166c72f91488dc276759a301d`|
| `ros2_ws/src/ros_esc/ros_esc/filter_node/rolling_gesc.py` |`7545bd6a9ef2f1f66e21929796fd00d743093e1bad666eeb102b927f6d81320c`|
| `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_objective.py` |`992e25081e67dbc349584557c2413d64ef4b4cc7ea3e02b983aa060d326d3f0a`|
| `ros2_ws/src/ros_esc/ros_esc/v2_stream.py` |`7e4caf66723d6dd8159478995799c076ec3fb45da91060141cacef70bbb842d2`|
| `ros2_ws/src/ros_esc_interfaces/msg/SynchronizedObservation.msg` |`e82b6b939496ebe2097b40164f1d1cc0caf409d731630cd655380660dabdae8b`|
| `m2_upstream_transport_v6.log` |`e3f3d0587fec0201f4ef23f17c87990edf5b0035ea2f188dcca3d68624004bb7`|

Earlier fixture-source hashes, in version order v1–v5:

```text
v1 14454e50e6505d48ea6e81128895704eb6e0806b1977e9c93ceb37cfacabd629
v2 af89422af7a8aee044f8b8c5cbf79b58a35f0adf7cfb4e3ed4f30a5ac4365117
v3 a00e7a3684e5ff3619cc7621ad7e7dfc645e2a7ab10898e8699728cfa40494b9
v4 a70126557086c3073dbae569f8c99f15931efb5140ad2665a23f11151008457b
v5 6402c5b66a73ea4f46529d5d1e72a4f43679600d5add8bf3c6c805d82839088a
```

Only the new test and this validation note were edited by this subtask. Parent
owns the correction's aggregate regressions, checkpoint and milestone status.
