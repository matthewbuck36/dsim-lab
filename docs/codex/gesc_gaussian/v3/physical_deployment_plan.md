# V3 physical deployment — authorized 2026-09-29

This is the accepted physical-plan implementation authority. It incorporates
the user's corrections: use `/home/pi/ros2_ws`, preserve V1 in `mbuck_backups`,
retain original legacy ESC behavior, omit SSH-loss/session heartbeat logic, and
make the physical V3 Bash command build, source and launch in that order.
The simulation refactor's no-build runner rule remains simulation-specific.

## Selected behavior

- Shared V3 algorithm, trial gains0.10/1.0 (second gain comparison authorized2026-10-09), physical trial caps0.10 m/s and0.50 rad/s,
  affine 2.0. Higher caps restored by the user on 2026-10-09 after two successful
  lower-cap (0.05/0.30) trials; initial deployment and Gazebo used 0.10/0.50.
- Original fixed 5 Hz UNO firmware, nominal arm 20 RPM, calibration 353 degrees
  applied once; no firmware/rate command change.
- Direct assistance disabled by default. Optional one pulse per escape after
  less than 5 cm outward progress over 15 seconds, limited to 20 cm measured
  path, then ordinary GESC. Keep the separate stable-exit window unchanged.
- Continuous moving SEARCH/VERIFY/DESIGN/ESCAPE; no arbitrary approach,
  verification, escape or operator-run deadline. Operator stops with Ctrl+C;
  an approximately 20–30 cm global-source orbit is acceptable.
- Bad/duplicate samples do not renew freshness. Expired essential data stops
  temporarily and resumes automatically. Retain committed escape geometry and
  affine guidance through ordinary data gaps/reconnects in the same frame/time
  domain, while discarding stale direction, progress and pending-fit evidence.
- No research supervisor, recorder-readiness protocol, Vicon control input,
  mandatory plotting or duplicate CSV recording. Optional ordinary rosbag.
- Narrow local actuator/process protection and normal Ctrl+C cleanup remain;
  there is no SSH monitoring or network/session-loss stop condition.

## Implementation and evidence milestones

1. Inspect live Pi without devices, verify V46 source, preserve complete current
   source/build/install and dependency/firmware provenance under `mbuck_backups`.
   Verify a redundant host archive and restoration instructions before replacing
   the workspace. Preserve all previous failed records/backups.
2. Implement/test shared recovery and bounded optional assistance. Add a V3-only
   config resolver/entrypoint without modifying legacy numerical APIs/parsers.
3. Implement the physical acquisition/rotation adapter outside dsim-lab: bounded
   serial work, honest host receipt times and unknown ADC uncertainty, genuine
   encoder-edge freshness, shared ObservationBuilder and OpenCR odometry.
   Implement/test local process/actuator stop ownership independently of data
   quality, research progress, recording and SSH.
4. Merge additions into the verified original physical packages, retaining
   legacy source/config/launch dependencies and the original interface superset.
   Retire the V1-only symlink-building wrapper from the selected command path.
   Add an explicit V3 physical build/source/launch command. Fresh ordinary build
   in the existing workspace, then native software, installed-path, source
   parity, legacy compatibility and incremental-build checks.
5. Synchronize the offline physical mirror with preservation of its prior state;
   write deployment manifest, rollback instructions, run command and current
   qualification boundaries. Review shared Git diff and focused regressions.

Physical motion requires the operator's readiness to observe it. Raised-wheel
Ctrl+C/process-stop checks precede a floor trial; actual OpenCR stop behavior
cannot be certified from source or synthetic tests. Full physical escape/global
approach is operator acceptance after deployment, not a software-test claim.
Promote V3 to the generic Gaussian default and remove unused V1-only source only
after that physical acceptance; preserve legacy dependency closure and backups.

## Checkpoint

Use this plan, `physical_deployment_status.md`, diff checks and external receipts
instead of unsupported legacy phase tooling. Bound all automated commands.
Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_deployment_20260929T210229Z`.

## Authorized Vicon restoration — 2026-09-29 local / 2026-09-30 UTC

The user requested independent Vicon tracking by default, with V3 still running
when the server is off. Reuse the retained physical `odometry_node` client on
`/gesc_gaussian/evaluation/vicon_odom`; preserve its legacy source, wire format
and baseline methods. Add that topic to the physical V3 bag. Treat this process
as optional: no startup/data/exit gate, no input to controller/acquisition, no
change to OpenCR `/odom`, gains, firmware or stopping ownership. Keep ordinary
build/source/launch and optional `--no-vicon`.

Validate command selection, optional failure/isolation and cleanup with bounded
software tests; deploy backed-up files only after confirming idle. A stationary
Vicon-only reception/recording check is within scope; no base/arm launch. Preserve
existing floor recordings. The inherited one-shot server/client handshake and
server-per-client lifetime must be reported rather than silently redesigned.
Evidence: `/home/mattb/Experiments/GESC-Gaussian/v3/vicon_restore_20260930T032350Z`.

## Authorized physical speed reduction — 2026-09-29 local / 2026-09-30 UTC

After reviewing floor run `20260929T203345_844703Z-3962`, the user authorized
changing physical V3 caps to 0.05 m/s and 0.30 rad/s. Preserve gains0.5/5,
affine2.0, assistance off, fixed5Hz, nominal20RPM and54-degree calibration.
Leave Gazebo tuning and all legacy methods unchanged. Back up the selected
physical JSON and any affected display/test files, update the startup message
to show resolved caps, build ordinarily and verify installed selection using
`--check-only` plus focused software checks. Refresh the offline mirror and
current guidance. No physical motion is part of this configuration change.

## Authorized worker initialization correction — 2026-09-30

The user authorized fixing and deploying the reproduced cold-worker deadline
loop. Load selected numerical dependencies inside the worker before its ready
message. Keep control nonblocking during initialization, existing coherence
and fill job deadlines, source-age checks, parent-death cleanup and physical
tuning unchanged. Add a delayed-import regression, then verify the original
recorded job and fresh 5 Hz replay with the actual Pi worker. Back up and
ordinary-build the bounded change, verify installed/source/mirror parity and
record limitations. No ROS/device/actuator launch or floor trial is authorized
by this software correction.

## Authorized steering correction — 2026-09-30 local / 2026-10-01 UTC

The user authorized the one-light review's recommended corrections on the Pi.
Retain an immutable accepted rolling direction only while a replacement's
coherence computation is pending and the accepted direction remains within
its original source/receipt freshness bounds and current context. Do not
transfer old confidence to a new snapshot. Expiry/rejection/reset must discard
the held result; fresh instantaneous fallback remains recoverable. Preserve
current-yaw reprojection, worker budgets and continuous moving transitions.

Separately test priming the core's initial washout state with the first valid
cost. Do not introduce startup sleeps, rotation waits or a primed zero on an
in-motion objective change. Preserve the original standalone GESC numerical
helper/legacy methods and all physical/simulation tuning.

Regression-check pending/delayed/expired/rejected work and context resets;
replay the closed one-light inputs with correction variants separately and
together. Confirm idle before backup/deployment, build ordinarily in the
original Pi workspace and verify imported installed code plus offline parity.
Use device-free Pi replay and focused native tests; no physical motion, ROS
hardware launch or firmware changes are included. Source/software success
does not establish physical convergence or Gaussian escape.


## Continuation preferences and proposals — 2026-10-01

The user selected physical-led refinement as the immediate priority; further
Gazebo experiments are not a prerequisite. Keep implementation simple, preserve
continuous motion and ordinary data recovery, and judge physical functionality
through controlled operator trials. Completion time is secondary, although an
escape taking roughly ten minutes is undesirable. This preference does not
select a new run-ending deadline or waive essential freshness/process stopping.

Follow [physical fresh-chat handoff](physical_fresh_chat_handoff.md) for the
latest floor evidence and setup constraints. Proposed next comparisons include
steady one-light conditions, Vicon/known lamp geometry, angular gain5→7.5 with
other tuning fixed, and longer existing detector observation windows. These
specific tuning/window changes remain **unapproved and unimplemented**. Do not
silently deploy them from this discussion, increase only the radius ceiling,
or treat the lack of a second light as the cause of no candidate. Recover the
current state and agree the concrete next experiment in the continuing chat.

## Authorized physical gain comparison — 2026-10-09

The user authorized the proposed common0.1 gain scaling for the next floor
trial: physical k_vx0.5→0.05 and k_wz5→0.5. Preserve caps0.05/0.30,75%/25%
steering blend, detector settings, affine2, assistance off, clocks, firmware,
arm speed/calibration and legacy behavior. Gazebo gains remain0.5/5.
Back up the selected Pi source/installed configuration, change the physical
source JSON, ordinary-build through the existing runner's `--check-only` path,
and verify effective installed selection and focused existing checks without
hardware startup. Retain exact source differences and backup/validation receipts.
The operator will launch the next floor trial after deployment.

The user explicitly deferred offline-mirror refresh until they announce that
testing is finished for the day. Leave that mirror untouched during testing;
keep Pi backups and redundant laptop receipts, and record the temporary mismatch.

## Authorized encoder reference correction — 2026-10-09

With the arm physically straight ahead, the operator measured 298–300 degrees
using `calibrate_encoder_zero_angle.py`. Live inspection confirms its reader
already subtracts 54 degrees, as does installed V3. The implied raw forward
angle is 352–354 degrees. The user authorized replacing the offset with the
midpoint, 353 degrees, applied once. Update the shared physical encoder reader,
V3 acquisition, startup/receipt labels and matching tests; preserve backups on
Pi and laptop. This also corrects the encoder reference used by legacy physical
readers, without changing their algorithms. Keep gains, caps, arm speed,
firmware and shared simulation algorithms unchanged. Ordinary check-only build,
focused software tests and source/install verification precede the operator's
stationary forward-angle recheck. Floor behavior remains unqualified. Offline
mirror refresh remains deferred until the user ends today's testing.

## Authorized post-calibration gain comparison — 2026-10-09

Following the corrected-reference run4810 review, the user authorized gains
0.05/0.5 -> 0.10/1.0. Preserve 353-degree calibration, caps0.05/0.30, detector,
blend, firmware, arm speed, assistance and lamp setup. Back up source/installed
controller JSON and the matching integration-test expectation to Pi and laptop;
ordinary build/check-only, focused native tests and installed configuration
verification precede the operator's next run. No hardware launch or offline
mirror refresh is part of this deployment. This is an unqualified response
comparison, not a claim of orbit formation or successful escape.

## Authorized static-confinement radius correction — 2026-10-09

The user authorized the run6323 recommendation: static support radius0.04->0.06m
only. Preserve30s support,0.005m/s drift threshold, all circle/oscillation model
and persistence criteria, moving verification and fill/escape logic. Keep gains
0.10/1.0, caps0.05/0.30 and encoder353. Maintain shared algorithm parity by the
same one-line numerical change in this checkout and the Pi; no Gazebo retuning
or simulation qualification is implied. Add focused radius/drift/support tests,
run numerical/core regressions, replay the four retained physical traces, then
back up and install the matching Pi source with ordinary check-only build and
native checks. No physical motion or offline-mirror refresh is included.

## Authorized higher-cap comparison — 2026-10-09

After two consecutive successful local fill/escape trials, the user authorized
caps0.05->0.10m/s and0.30->0.50rad/s only. Preserve gains0.10/1.0, encoder353,
static radius0.06m, detector/evidence/escape behavior, clocks, firmware and arm
speed. These restore initial V3/baseline ceilings without restoring baseline
gains. Preserve the successful lower-cap configuration on Pi and laptop before
editing. Ordinary check-only build, native selected-configuration/command-limit
checks and source/install audit precede the operator's run. No hardware launch
or offline-mirror refresh. Prior successful runs remain lower-cap evidence;
the higher-cap physical behavior is a new, unqualified comparison.

## Authorized return to successful lower caps — 2026-10-09

Following successful higher-cap run3461 and its longer confinement delay, the
user authorized restoring physical0.05m/s /0.30rad/s for a third lower-cap trial.
Restore only controller JSON and the two matching test files from the preserved
pre-cap-change originals, after checking no intervening source changes. Preserve
the higher-cap state on Pi/laptop first, ordinary build/check-only, native checks,
and source/install audit. Gains0.10/1.0, encoder353, detector6cm and other settings
stay fixed. Operator owns launch; offline mirror refresh remains deferred.

## Authorized end-of-testing mirror refresh — 2026-10-09

The user ended testing and explicitly authorized the previously deferred live
Pi-to-local snapshot synchronization. Preserve the complete previous snapshot,
use the established source/data/full-backup filter with active generated trees
excluded, keep the Pi read-only, and verify independent source hashes plus a
zero-change full-scope checksum dry run. Completed evidence is linked in status;
no physical build, launch, tuning, shutdown, Git commit or push is included.
