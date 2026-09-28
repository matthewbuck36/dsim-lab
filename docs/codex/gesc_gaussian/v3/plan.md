# GESC + Gaussian V3: continuous search under physical constraints

Planning draft, 2026-09-25. Source audit and proposed experiments only; no V3 runtime is implemented or tested. Start with [status](status.md) and the [fault inventory](fault_inventory.md). The user explicitly requires continuous base motion during verification and Gaussian design. A protective stop may be necessary after loss of trustworthy control, but it is an interruption, not a successful continuous-motion acquisition.

## Objective and protected baselines

Retain V2's useful research ideas—measured-angle rolling GESC, moving trapping verification, bounded Gaussian interventions, escape and return to SEARCH—while reducing synchronization dependencies, computing cost and unnecessary terminal failures. Demonstrate them in Gazebo with constrained sensing, nonuniform rotation, delayed delivery and limited runtime capacity before considering hardware deployment.

- Preserve physical V1 restored by [V46](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/HANDOFF.md): fixed approximately 5 Hz firmware, 54-degree encoder offset, nominal 20 RPM, gains 1/5, caps 0.05 m/s and 0.30 rad/s. No Pi contact, deployment, firmware change or hardware trial in this planning task.
- Preserve frozen V1 `1af67c6`, accepted V2/Test D `d1779b6`, and selected 5 Hz experiment `e726774`. V3 starts on `planning/gesc-gaussian-v3-physical-constraints` from `e726774`; the two earlier user-requested comment renames remain uncommitted and otherwise unchanged.
- The [5 Hz V2 case](../v2/low_rate_5hz_handoff.md) demonstrated fill/escape/arrival, but original completeness failed and the quadratic was ill-conditioned. It is a comparison case, not proof V3 already works.
- No planned stationary acquisition, automatic fallback to physical V1, or cross-host offloading is selected. A simpler implementation must still meet the moving-search objective.

## What the physical evidence establishes

| Evidence | Consequence for V3 |
| --- | --- |
| [V1 run 970bc1b3](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/operator_run_970bc1b3/analysis.json): 4.978 Hz, median interval 200.885 ms, maximum 207.033 ms; encoder mean 17.176 RPM | Use this as a healthy recorded example, not a universal worst-case specification. Nominal 20 RPM is not actual angular velocity. |
| [V29 motor review](/home/mattb/Experiments/GESC-Gaussian/physical_integration/arm_qos_event_revision_20260924_v29/evidence/arm_speed_analysis_01/findings.md): mean 16.958 RPM, sector medians approximately 14.08–19.90 RPM; encoder continued through a 616 ms valid-source gap | Model rotation variation independently from missing photometric/support delivery. The cause of variation and outer-arm coupling remain unmeasured. |
| [V44 synchronization diagnosis](/home/mattb/Experiments/GESC-Gaussian/physical_integration/mobile_v2_synchronization_diagnosis_20260924_v44/FINDING.md): different support brackets reproduced geometry disagreements; cost callbacks arrived at 539/582 ms; missing left encoder brackets at 94/107 ms | Preserve the actual acquisition/support identity once; do not independently reconstruct supposedly identical geometry from different subscriber histories. Distinguish unavailable past support from waiting for future support. |
| [V35 verified CPU comparison](/home/mattb/Experiments/GESC-Gaussian/physical_integration/arm_recorder_load_comparison_20260924_v35/evidence/retained_comparison_recovery_01/verification.json): six-owner replay plus harness about 3.09 cores without bag, 3.69 with bag; bag about 0.77 core | Recording and interprocess/runtime work are part of the performance problem. Small constructor improvements did not provide material aggregate headroom. These replays omit parts of the full physical graph. |
| [Autonomous ledger](/home/mattb/Experiments/GESC-Gaussian/physical_integration/arm_automation_20260922/LEDGER.md): isolated 10/15 Hz sensor successes, full pipeline failures, and much better closed-data replay than live admission | Do not claim the Uno intrinsically cannot sample above 5 Hz or that average Hz alone measures useful control input. Preserve failed approaches; no unchanged physical retry is part of V3. |

At 5 Hz and 20 RPM there are 15 samples per nominal revolution; at the recovered approximately 17.2 RPM there are about 17.4. A blanket 24-sample-per-revolution gate cannot be the nominal V3 requirement. However, fewer samples still require evidence of angular observability and direction quality; deleting density checks is not a sufficient estimator design.

At 20 RPM, a 0.5-second unaccounted timing error corresponds to 60 degrees of arm rotation. Three measured revolutions at 17.2 RPM take approximately 10.5 seconds; at 0.05 m/s the base can travel approximately 0.52 m during that history. A stationary-field fit at the latest position is therefore not automatically a valid moving estimator.

## Hardware model: facts, approximations and unknowns

Manufacturer references were checked on 2026-09-25. [Arduino UNO R3 specifications](https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf) identify the 16 MHz ATmega328P and 2 kB SRAM. The retained flash receipt identifies an ATmega328P; the USB bridge is CH340, so do not assume the official board's USB bridge. The restored [sketch](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/restored_source/turtlebot3_vehicle_nodes/data_acquisition_subpackages/photoresistor_scripts/photoresistor.ino) uses `analogRead`, a 0–1023 conversion, 9600 baud, text output and `delay(200)`. Its approximately 5 Hz rate is an application choice, not an ADC limit. It transmits no acquisition timestamp/sequence; model the uncertainty between acquisition and host receipt explicitly.

[Parallax's servo specifications](https://www.parallax.com/product/parallax-feedback-360-high-speed-servo/) specify 50 Hz command PWM, a zero-speed deadband and approximately 910 Hz angle feedback. Those numbers are electrical interfaces, not ROS publication rates or guaranteed loaded RPM. The installed [driver](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/restored_source/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/parallax_360_servo_communication.py) maps requested RPM to PWM using a fitted feedforward relation; it does not close the speed loop. Its angle conversion truncates to integer degrees. Keep nominal command, actual shaft phase, reported angle and callback time as separate model variables.

| Layer | First model | Additional stress/unknowns |
| --- | --- | --- |
| Acquisition | Original firmware's nominal 200 ms cycle plus processing; reproduce approximately 4.98–5 Hz observed delivery. Finite ADC quantization uses an explicit synthetic voltage scale | Recorded source/receipt stamps are not measured ADC acquisition times. Noise, saturation, bias, missed/duplicated/malformed frames and device restart are separate perturbations. Photoresistor dynamics and voltage calibration are not identified; use labelled sensitivity parameters. |
| Serial/receipt | Existing 9600-baud text format; preserve acquisition and receipt separately; finite buffered batches | Framing/partial reads, bounded backlog, sample-age uncertainty. Serial serialization is approximately `10 * bytes / baud` seconds for 8N1, not the whole USB/ROS delay. |
| Arm | 20 RPM request, approximately 17.2 RPM measured mean, recorded nonuniform phase, integer angle observation | Startup lag, deadband, direction change, stuck/missing angle, phase bias/slip. Unknown inertia/load/supply effects remain sensitivity studies until measured. Preserve 54-degree calibration as the physical baseline. |
| Base/pose | V1 caps 0.05/0.30 first; independent pose cadence and receipt timing | Odometry noise/drift, wheel slip and support loss. Use 0.10/0.50 only as a separately identified later comparison. Ground truth is evaluator-only. |
| Transport | Separate acquisition, publication, receipt and callback/service times; preserve original identity through delay | Independent versus correlated delays, reordering, bounded queues and sustained outage. A proposed 0.2–0.8 s sensitivity sweep includes observed roughly 0.54–0.62 s late/gap events; it is not a measured delay distribution or maximum. |
| Computing/recording | Actual algorithm owners plus selected recorder at normal-speed Gazebo; per-process CPU and bounded queue measurements | Process-specific CPU pressure and scheduling stalls. Slowing simulated time can hide wall-time overload; report real-time factor and both clocks. Host throttling is not Pi instruction-level emulation. |

First separate a healthy operating envelope from adverse-condition tests. Do not demand uninterrupted motion during arbitrary sensor outage or a stopped control process. For such tests, passing means the declared protective response and bounded recovery; the continuous-motion outcome is separately marked interrupted.

Inject recorded symptoms at the observable layer supported by their evidence.
A valid-source gap is not proof that the ADC stopped sampling; an encoder
callback timestamp is not proof of the exact electrical edge time. Keep
alternative causes as separate sensitivity cases when the original record
cannot identify which layer introduced the delay.

## Simpler ownership and runtime policy

The complexity concern is supported by source inspection. The simulation
[acoustic GESC wrapper](/home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_full_rotation_acoustic.bash)
and RMSprop wrapper are each 25 lines; the simulation
[Gaussian wrapper](/home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash)
is 74 lines, including a large visualization block. The restored physical
Gaussian wrapper is 544 lines and the archived V45 shared wrapper is 863.
These include build, configuration, admission, launch and recording duties.
Line count is evidence of operator/configuration burden, not a CPU diagnosis.
Moving that same script behind a short wrapper would not resolve duplicated
configuration or excessive coupling.

The supervisor presently owns algorithm states, objective weights, fill
transactions and escape guidance, as well as events. The controller is the
sole command writer. Retain the necessary state logic, then reduce its
selected path and dependencies; retaining the whole supervisor just for
logging is not justified. Existing unused modes remain available as legacy
behavior instead of entering the V3 selected configuration.

1. **One authoritative measurement.** Extend the existing source adapter/objective contract to carry cost, source identity, observed phase/pose support, time basis and uncertainty once. Reuse the lesson of [V45](/home/mattb/Experiments/GESC-Gaussian/physical_integration/mobile_v2_authoritative_measurement_20260924_v45/HANDOFF.md), without assuming that archived repair solved physical scheduling. No second synchronizer or parallel raw/augmented/provenance joins for the same selected measurement. Simulation must not grant the controller perfect support that hardware cannot observe.
2. **One rolling direction owner.** Retain moving pose-aware GESC mathematics initially. Evaluate windows by angular spread, identifiability, residual/noise and freshness, using actual phase. Do not invent samples or make old measurements fresh by republishing. Compare a bounded nonuniform-angle fit only if the retained estimator demonstrably cannot meet the low-rate envelope; that is a separate mathematical change.
3. **Small algorithm state manager.** Retain SEARCH, moving verification/design, owned escape and return to SEARCH through existing supervisor/controller owners. Cancel an invalid fill transaction and continue valid SEARCH where supported. Preserve a single `/cmd_vel` writer. Logging is an observer, not the reason to retain a large supervisor process.
4. **Separate response severity.** Hardware/command-authority failure demands inhibition. Discard an isolated bad sample or cancel an unsuitable candidate window while a still-qualified control estimate supports continued motion. Stop protectively when required control evidence exceeds its bounded age/uncertainty; recovery after that stop does not restore the continuous-motion result. Failed fitting usually cancels that fill. Optional recorder/evaluator loss changes evidence status; an explicitly recording-required experiment may instead abort under its declared experiment policy. Every transition records its cause. The [inventory](fault_inventory.md) distinguishes current behavior from proposed V3 policy. No old failure is reclassified.
5. **Remove repeated work before adding processes.** Compute expensive estimates on fresh information, not every heartbeat. Cache immutable configuration and maintain bounded incremental windows. Publish state on changes plus a modest liveness cadence; put large diagnostics behind an explicit option. Evaluate composition of existing owners only after measuring the resulting callback fairness and stopping behavior. Avoid adding watchdogs to compensate for each new wrapper.
6. **Minimal operator entry point.** Shell selects a named versioned profile and delegates to the existing launch/runner; routine launch does not rebuild. Keep algorithm settings in one profile, environment/device settings in the physical/simulation adapter profile, visualization settings optional, build/check operations separate. Resolve and record configuration once. A 10–25-line entry point is a usability target, not a claim that deleting lines removes necessary responsibilities. Test actual version selection and source/install identity across entry points.

Keep monotonic process/actuator leases independent from algorithm time. A small software supervisor is not a substitute for actuator-local command expiry. V46's successful Ctrl+C test does not qualify process-freeze or Pi/pigpiod failure handling; any future hardware deployment needs those boundaries reviewed independently.

## Staged experiments and exit decisions

Work one stage at a time. This plan does not launch a batch. Reuse `run_scenario`, `record_run`, the existing disturbance owner and analysis owners; no new commissioning framework.

| Stage | Work | Exit evidence |
| --- | --- | --- |
| P0 — policy/design | Finish source fault inventory; identify the selected input/time/stop contract and smallest reusable owners | Ranked faults with direct/indirect path and recovery; explicit continuous-motion requirement; implementation scope bounded before edits |
| P1 — model credibility | Extend existing `simulation_disturbance_node` and selected sensor/rotation adapters for trace-based/nonuniform timing; add hardware-observation mode. Keep latent acquisition time, true shaft angle and ground-truth pose private to the evaluator; expose only observations and uncertainty available on hardware | Pure deterministic tests prove timestamps, masks, queues and perturbations; recorded healthy/adverse fixtures reproduce their intended properties; no control success claimed yet |
| P2 — controlled baseline | Run the retained 5 Hz V2 mathematical baseline under the healthy model, then one independently changed disturbance at a time | Exact failure attribution and controller freshness/coverage/direction metrics, with no tuning to relabel baseline failures |
| P3 — V3 implementation comparison | First remove duplicated joins and unnecessary live evidence coupling with mathematics fixed; then optimize the measured expensive owners. Change estimator/fault-recovery policy in separately labelled comparisons | Meaningful decrease in loaded CPU/queue age with unchanged essential checks; fault-injection tests prove proposed recovery. No blanket timeout inflation |
| P4 — moving behavior | Start with the existing nominal two-source case and matched seed; confirm fill, owned escape, resumed SEARCH and arrival while verification/design remain moving | Actual command/odometry continuity, no mandatory acquisition stop, no premature fill, correct cost sign, bounded intervention and cleanup; classify numerical fallback separately |
| P5 — limited confirmation | Freeze source/policy; choose fresh seeds/start phases and combined credible disturbances after pilot behavior is explained | Repeated outcomes across nominal and credible tail conditions; separately report hard-fault stop tests and outside-envelope failures; no replacement of failed cases |

For P2 use single-factor families: (a) sparse/quantized sensing; (b) nonuniform arm motion; (c) independent cost/pose/encoder delay; (d) burst loss/backlog; (e) recording/CPU pressure; (f) restart/clock discontinuity. Use retained timestamp patterns before arbitrary distributions. Test threshold boundaries deliberately. Combinations follow only when single-factor mechanisms are understood.

Use explicit finite startup, acquisition and shutdown limits for every command and one live graph at a time. Set scenario deadlines before dispatch using rotation periods and the retained 5 Hz arrival as context; a provisional 360 simulated seconds per mobile pilot is reasonable, but compute a finite wall deadline from the declared real-time-factor floor and retain timeout failures. Never increase a timeout merely to convert a failed fixed case into a pass. Keep recording-on and recording-off comparisons matched and clearly distinguish changes in observable behavior from changes in retained evidence.

## Metrics and acceptance that answer the physical question

- **Safety/control:** finite bounded commands; exactly one authority; command expiry and stop latency by owner; no stale data made fresh; collision/contact checked in simulation; report unsupported physical safety coverage explicitly.
- **Continuous motion:** no planned stop during verification/design; report maximum zero-command interval, longest zero-forward-speed interval, and actual translational speed/displacement by state. Pure spin or commands issued to a stalled base do not satisfy moving verification. Define measurement resolution and the minimum meaningful translation before confirmation. Protective stops are recorded interruptions, not quietly excluded from the result. Normal startup and deliberate final stop are separate.
- **Observation quality:** unique admitted samples, age distribution at actual consumer service, phase error, angular spread, support uncertainty, useful direction availability and recovery time. Diagnostic publication counts are not sample counts.
- **Behavior:** trapping detection, false fills, fit/fallback status, fill count, escape ownership, time/distance to global region, and return to SEARCH. Preserve separate outcome, numerical validity and evidence completeness fields.
- **Runtime:** CPU core-seconds, per-owner p95/p99 callback age, queue occupancy/drop reason, memory bounds, recorder overhead and real-time factor. Aim for substantial measured headroom; do not convert laptop core-seconds into a claimed Pi capacity guarantee. Future native-Pi validation remains required.
- **Maintainability:** one profile owner per parameter, one selected measurement path, no hidden algorithm selector, short auditable entry point, and source/install/schema compatibility checks. No requirement for a new per-attempt custom Python launcher.

Fix numerical admission/age/recovery limits from an explicit model and pilot evidence, then freeze them before confirmation. A tolerance should express physical uncertainty or required control quality; it should not exist solely to make two independently reconstructed floating-point results identical. Startup and offline validators must use the same selected V3 policy and must not inherit impossible density or zero-jitter gates.

## First implementation milestone and decisions still open

The next proposed milestone is **P1: a truthful input and timing model**, after this plan is reviewed. No runtime changes or Gazebo execution occurred during planning. Preserve the V2 reference while adding an explicit V3 scenario/policy selection through existing owners. Do not attempt all architecture changes at once.

Open choices to settle from the audit/pilots: required freshness versus permitted motion uncertainty; when a discarded sample actually invalidates the rolling direction; whether a bounded uncertainty-aware fit is needed; minimum loaded CPU headroom; and which faults may recover automatically after a protective stop. Continuous motion, preservation of physical V1, fixed5Hz as the first physical target, and separation of evidence failure from hardware hazard are the current design constraints.
