# V3 physical deployment — authorized 2026-09-29

This is the accepted physical-plan implementation authority. It incorporates
the user's corrections: use `/home/pi/ros2_ws`, preserve V1 in `mbuck_backups`,
retain original legacy ESC behavior, omit SSH-loss/session heartbeat logic, and
make the physical V3 Bash command build, source and launch in that order.
The simulation refactor's no-build runner rule remains simulation-specific.

## Selected behavior

- Shared V3 algorithm, gains 0.5/5, physical caps 0.05 m/s and 0.30 rad/s,
  affine 2.0. The user authorized these lower caps after the first floor-run
  review; initial deployment and Gazebo used 0.10/0.50.
- Original fixed 5 Hz UNO firmware, nominal arm 20 RPM, calibration 54 degrees
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
