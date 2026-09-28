# Accepted ESC/V3 refactor — 2026-09-28

This is the implementation authority for the user's approved refactor and
subsequent two corrections. It supersedes the earlier proposed V3 topology
and milestone order in `plan.md`. Gazebo research testing follows the software
refactor; no physical deployment is included.

## Fixed scope

- Original ESC methods and V3 remain active; Gaussian V1/V2, obsolete recipes,
  distributed runtime variants and their policy tests remain on frozen refs.
- Preserve the Pi's working V46 installation. Keep physical
  `turtlebot3_vehicle_nodes` outside dsim-lab. The snapshot is a mirror, not a
  second algorithm development fork. Shared `ros_esc` has no required Gazebo
  or plotting dependency.
- Keep original Matplotlib live plotting automatic for interactive Gazebo,
  off for physical/headless runs. Plotting is independent from CSV writing,
  rosbag and motion authorization.
- Ordinary runs continue until Ctrl+C. A best-source detection is an event,
  not automatic goal hold. Verification/design require translating motion.
- Optional rosbag starts by default; failure warns and never gates control.

## Required implementation

1. Preserve pre-refactor working tree, refs and generated installations.
   Remove generated artifacts from tracking and use one fresh symlink build.
2. Resolve one algorithm profile plus environment profile once. Keep original
   method Bash names as short explicit aliases. Run commands never build or
   rewrite JSON. Built-ins use installed resources/module references; retain
   custom original filepath configuration compatibility.
3. Select one V3 core through the existing controller entrypoint. Pure helpers
   own objective, measured-angle GESC/rolling coherence, recurrent detector,
   moving verification, Gaussian design/registry and escape. Preserve selected
   mathematics initially. No standalone supervisor/composer/detector/fill ROS
   choreography, duplicate sample joins or ACK protocol in the active V3 graph.
4. One private numerical worker process: one in-flight immutable job, no
   accumulating FIFO, no ROS/actuator/registry authority. Coherence result
   expires after 0.5 s; fill preparation after 5 s. Main owner alone commits
   matching candidate/epoch/generation results; original observation age is
   preserved. Retain finite numerical budgets and 4000-sample fit cap.
5. Keep original five messages, add SensorObservation, retain AlgorithmEvent
   and GaussianFill as output-only telemetry. Observation distinguishes source
   versus receipt time, host versus device sequence, observed pose/phase and
   unknown uncertainty. Augmented cost/state/registry are local core data.
6. Control availability is ACTIVE/WAITING_INPUT plus terminal STOPPED/FAULTED.
   Start on the first usable direction and fresh pose, not full-cycle evidence.
   Reject bad samples without renewing freshness. Expired essential inputs
   command zero and automatically recover. Candidate/fit/coverage failure
   cancels only affected research work. Recording/Vicon/plot failures do not
   stop control. Ctrl+C never automatically resumes. Unresolved actuation,
   ownership or frame/time integrity failures inhibit motion. Initial input
   expiry 0.5 s and command cadence 20 Hz are comparison defaults, not physical
   qualification.
7. Preserve original controller_output(time,state,input_values) numerical API,
   cost sign/units and original methods. First physical-target V3 profile uses
   approximately 5 Hz, nominal 20 RPM, offset54 and caps0.05/0.30. Re-evaluating
   old history under a new objective is not part of the refactor.
8. Standard rosbag with compact topic list; analysis accepts an ordinary bag
   path and treats absent metadata/metrics as unavailable. Remove compulsory
   recorder readiness, live report/hash validation and duplicate CSV recording.
9. Archive historic workflows outside active install; retain a short usage,
   architecture, environment, test guide and historical evidence index.

## Milestones and acceptance

- R1 preservation/build hygiene: exact archive/hash/mode verification, frozen
  refs, no generated files tracked; clean new build roots.
- R2 active runtime implementation: profiles/original methods, extracted V3
  mathematics, one command owner, observation/worker, optional bag/plot/analysis.
  Independent components may be implemented in parallel within this milestone.
- R3 qualification: original profile/numerical parity; first usable direction
  starts without recorder/full rotations; sample expiry/duplicate/recovery;
  nonfatal recording/candidate failure; stale job rejection; expensive worker
  isolation; Ctrl+C final zero; eight interfaces; installed resource/build
  selection; ordinary bag reading; live plotting render; environment adapter
  contract tests with no physical hardware and no truth leakage.
- R4 cleanup/handoff: remove inactive owners and obsolete test/workflow code,
  finish docs, repeat relevant clean build/integration checks, audit every
  requirement against evidence. Gazebo behavioral qualification comes next.

Use explicit finite timeouts for tests/builds/ROS checks. Retain commands,
results and failures in `refactor_status.md` and external evidence. The old
phase tools have no V3 support; this plan/status plus Git diff/check and exact
receipts are the authorized bounded V3 checkpoint equivalent. Do not create
another phase-orchestration framework or relabel V2 checkpoints as V3.
