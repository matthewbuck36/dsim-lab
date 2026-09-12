# R7 approach feasibility

Status: **ADOPTED**, 2026-09-10 after [R6 source validation](r6_verification_expiry_handoff.md).
R6 archive555 members verified in0.833943s; manifest SHA256
`fa2fcdc72e72920577f5f87b123c07539903db09047788f413ec4cabe2b7af29`.
This authorizes the bounded prototype and input preparation below, with no
production change or Gazebo acquisition. C01 and V10 remain failed.

## Question and candidate

The [C01 handoff](r5_visible_c01_handoff.md) reports 235 moving odometry samples,
minimum center distance 0.093241 m and no entry into the unchanged 0.08 m gate.
That is distinct from R6's ordinary-expiry fault race. Current
`centered_verification.tracking_command` applies a 0.03 m circular target at
0.3 rad/s, including its 0.009 m/s derivative divided by the 0.5 linear gain,
throughout approach and collection. This offset may impede approach for some
initial positions/headings; the retained trace alone does not establish cause.

Compare exactly two laws through the existing `Directional_Controller`:

- Baseline: current circular target and feedforward throughout.
- Prototype: use the frozen-center position error, rotated into the body frame,
  during approach; after the first valid collection admission, use the existing
  circular tracking law unchanged, including its original acceptance-clock
  phase. Do not reset phase, candidate time or admission on re-entry.

Retain gains `k_vx=0.5`, `k_wz=5`, ceilings 0.1 m/s and 0.5 rad/s, and existing
signed saturation. For ideal unsaturated point tracking with radius `r>0`,
`dr/dt = -k_vx * e_parallel^2 / r <= 0`. This motivates the comparison; zero
radial progress at perpendicular headings and finite turning prevent treating
it as an eight-second reachability proof. No stopped fallback is introduced.

## Reuse and frozen inputs

Adapt the retained external `centered_verification_v2/run.py` harness once into
an exclusive `development/20260910/r7_approach_feasibility_v1/` directory under
`/home/mattb/Experiments/GESC-Gaussian/v2/`. Preserve both earlier harnesses and
results. Reuse their 0.025 s midpoint unicycle integration, observation fixture,
actual controller and `MovingRawEvidence` collector; do not build another
simulator, controller, collector or analysis pipeline.

Freeze input rows/manifests through a read-only30s preparation cap before
dispatch; no numerical integration during preparation. Review exact joins and
helper/source hashes once. Freeze69 starts; run both laws on every start
(138 trajectories):

| Set | Fixed definition | Count |
| --- | --- | ---: |
| Original | Radius 0.25, 0.35, 0.50 m; position bearing 0, pi/2; absolute yaw 0, pi/2, pi | 18 |
| Near gate | Radius 0.09, 0.10, 0.15 m; bearing 0, pi/2; yaw equal to bearing plus `k*pi/4`, k=0..7 | 48 |
| Retained | First valid VERIFY guidance in C01, D02 and D03, joined to odometry by its exact pose_stamp | 3 |

The retained roots are `visible_integrated_C_01`, `visible_integrated_02` and
`visible_integrated_03` beneath the same development date. Use only their
existing `analysis_v1/v2_verification_guidance.jsonl`,
`v2_detector_confirmation.jsonl`, `analyzer/tables/odometry.csv` and receipts.
Pin exact row identities, center, x/y/yaw, acceptance/pose/publication times and
input hashes in a pre-dispatch manifest. First valid guidance records are
C01 line 1424 / pose 71193000000 ns, D02 line 1563 / pose 78178000000 ns, and
D03 line 1563 / pose 78179000000 ns. All first publications are 0.1 s after
acceptance: retain that elapsed offset and remaining budget. These precisely
joined anchors need not equal a summary's first selected odometry sample.
Missing or ambiguous joins block dispatch; do not substitute a favorable row.

## Finite measurement and decision

Keep admission at radius <=0.08 m and elapsed <=8 s, one immutable collection
deadline `min(admission+12 s, acceptance+20 s)`, and evidence readiness strictly
before that deadline. Check approach every integration tick and evidence at the
existing 0.1 s cadence. Count readiness only when collection has actually been
admitted; retain any earlier readiness separately. Existing eligible approach
history remains usable, without imposing a new post-admission-only rule.
Late approach/readiness during the full 20 s diagnostic trace never passes.

Use the earlier optimistic signal `-2+0.5*cos(2*pi*t/3+yaw)`, unchanged collector
guards and initially empty histories for both laws. Retained poses anchor
geometry; these are not signal replays. Record every rejection reason, first
admission and eligible readiness, deadline, center radius, path, commands,
saturation, motion maxima and longest joint commanded-zero interval. Preserve
all cases, including failure and post-deadline diagnostic samples.

Nominate the prototype only if all 63 required starts (12 original 0.25/0.35 m,
48 near-gate and three retained anchors) approach and collect on time, obey
ceilings and have no joint commanded-zero interval >=0.5 s during authorized
verification. Report the six original 0.50 m hard cases separately. Compare
every paired outcome and time, including regressions. If the baseline does not
reproduce the C01 approach failure, report that limitation; a prototype pass
does not identify the actual runtime cause or establish field direction quality.

R6 fixtures are terminal and source is held. Allow one job: 85 s work plus at most
5 s termination/receipt allowance, 90 s inclusive wall cap. Save source/config,
helper and input hashes before and after, terminal status, elapsed time and
output hashes. Timeout or changed inputs remain failed/incomplete; no unchanged
retry or tuning within the job. No bags, PDE references, ROS, Gazebo or GUI.
A pass permits a separately adopted bounded runtime correction and visible
case, not comparison release or qualification.

## Existing owners for a later implementation decision

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/centered_verification.py`:
  tracking law; `v2_supervisor.py`: immutable admission and phase selection.
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
  and `controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage_m4_v6_gain_half.json`:
  actual controller and selected configuration (the configuration directory is
  under `ros_esc/controller_node/`).
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/moving_evidence.py` and
  `ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py`: collector and existing
  observation fixture. R6 authorization and R5 activated-fill handoff remain
  separate, preserved owners; this draft changes none of them.

Preparation evidence: repository text and retained extracted records inspected;
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan`
passed. No production import, numerical job, test or runtime was executed.

Runtime feasibility budget uses retained v2 harness18 trajectories/20s each in
5.461519s. The new138 trajectories imply approximately42s at that measured
throughput, leaving headroom within85s work. This is an estimate, not a new
benchmark or permission to extend a failed cap.
