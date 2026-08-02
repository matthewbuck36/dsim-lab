# Phase 09 Shared-Lab Legacy Compatibility Evidence

Verified: `2026-08-01T05:00:08Z`

Result: `PASS — STATIC/OFFLINE ONLY; NO HARDWARE`

## Compatibility amendment

The user requires the shared laboratory TurtleBot3 to retain every
pre-existing ESC method and its Bash entry point. The initial M3 draft had
extended `light_gesc_gaussian_fill_experiment.launch.xml` in place. That draft
was not accepted as the final compatibility boundary.

The selected Phase 09 graph now lives only in:

```text
turtlebot3_vehicle_nodes/launch/
  gesc_gaussian_two_source.launch.xml
```

The new
`gesc_gaussian_two_source_voltage.bash` wrapper and the physical
`record_run` target contract reference that file. The pre-existing
`gesc_gaussian_fill_full_rotation_voltage.bash` still references the old
launch. No other pre-existing wrapper references the Phase 09 launch.

## Baseline preservation

The verified M0 archive was the restore source:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260801T021552Z/ros2_ws_src.tar.gz
archive SHA-256:
  8109c5c47789ce1d2bb2cf69ba82f6901b054193989c488fefcfb9cf507404b8
```

The old GESC+Gaussian launch was restored from that archive with
`tar --same-permissions` and matches the M0 digest:

```text
542f26cc86f3ee06a8d6a6c8ee8a397fbadf2d8fc64aa39fcdf15eef8326bfaf
```

An exact `sha256sum -c` pass covered all baseline legacy assets involved in
operator selection:

| Asset class | Baseline files | Result |
|---|---:|---|
| Bash entry points | 26 | all hashes match M0 |
| launch files | 8 | all hashes match M0 |
| controller/filter/rotation configuration files | 6 | all hashes match M0 |
| total | 40 | `PASS` |

The new Phase 09 wrapper is the 27th Bash file and is intentionally not part of
the M0 hash set. All 27 Bash files pass `bash -n`.

## Wrapper and launch audit

`test_phase09_physical_launch.py` now provides a self-contained shared-lab
guard. It freezes all 26 pre-existing wrapper hashes plus the old launch hash,
checks shell syntax, requires exactly one launch target per wrapper, resolves
that launch in the package, parses its XML, checks supplied launch argument
names, and proves that the old and selected wrappers target different files.

One inherited acoustic spelling mismatch was found: all six acoustic wrappers
pass `input_encoder_data_to_filter=True`, while their unchanged launch declares
`input_encoder_data_into_filter=True`. This predates Phase 09. It is currently
behavior-neutral because every wrapper requests `True` and the effective
declared default is already `True`; ROS 2 `--show-args` also accepted the
existing invocation. The wrappers and launch were left byte-identical rather
than silently rewriting shared-lab entry points. The regression guard permits
only this exact historical case.

After the isolated build, `ros2 launch ... --show-args` resolved every unique
launch named by a Bash entry point:

```text
acoustic_esc_experiment.launch.xml
light_esc_experiment.launch.xml
light_gesc_gaussian_fill_experiment.launch.xml
light_hbesc_gaussian_fill_experiment.launch.xml
gesc_gaussian_two_source.launch.xml
rotating_frame.launch.xml
```

The retained output is:

```text
/tmp/phase09_compat_build.zdGQKP/show_args.log
```

The new Phase 09 launch contains no Vicon relay, legacy CSV collector,
`odometry_node`, broad `pkill`, evaluator geometry, or second `/cmd_vel`
owner. The restored old launch retains its historical behavior only for its
historical wrapper.

## Package/API regression evidence

The backup and current `setup.py` files were parsed as Python AST. All 12
pre-existing `ros_esc` console entry points remain present in the current 15;
all 7 pre-existing `turtlebot3_vehicle_nodes` entry points remain present in
the current 7.

The photoresistor owner retains its historical three positional arguments:
timekeeper topic, output topic, and `Voltage|Resistance`. A direct parser test
now proves both old modes retain `/dev/ttyUSB0`, `9600`, `0.50 s`, legacy-only
publication, no calibration, and no source score as their defaults. Phase 09
flags are additive.

Isolated build root:

```text
/tmp/phase09_compat_build.zdGQKP
```

Results:

```text
colcon build, ros_esc_interfaces + ros_esc + turtlebot3_vehicle_nodes:
  3 packages passed in 12.6 s
focused installed-overlay tests after the CLI regression was added:
  69 passed in 0.87 s
```

The focused collection covers shared parity, physical recorder safety,
photoresistor compatibility/semantics, and launch/wrapper compatibility.
Shared-runtime source files were not changed by this amendment, so the earlier
M2 `300 passed` shared-owner result and `34 passed` repository legacy result
remain applicable.

An attempted rerun of repository `test_legacy_behavior.py` against the
physical overlay failed during collection because that simulation test imports
the deliberately excluded `Multi_Light_Source_Cost`. This is the already
documented physical-overlay limitation, not a failed legacy behavior assertion;
the attempt did not start nodes or hardware and was not relabeled as a pass.

## Nonclaims

No legacy Bash wrapper, launch graph, ROS node, serial device, sensor, motor,
servo, lamp, SSH/SSHFS path, or live Pi was executed. The selected new-only
wrapper was invoked only as an inert preflight with deliberately motion-blocking
templates; it exited `2` before `record_run`, launch, device access, or temporary
runtime input retention. Shell syntax, XML construction, package discovery,
and `--show-args` do not prove live hardware readiness.

## M7.1 final revalidation

The final operator-entry/recording amendment changed only Phase 09-owned paths.
The fresh qualification reconfirmed:

| Guard | Result |
|---|---:|
| pre-existing Bash wrapper hashes | `26/26` M0-identical |
| pre-existing launch hashes | `8/8` M0-identical |
| pre-existing controller/filter/rotation configuration hashes | `6/6` M0-identical |
| all current Bash files | `27/27` pass `bash -n` |
| unique installed wrapper launch descriptions | `6/6` pass `--show-args` |
| repository legacy behavior | `34 passed` |

The selected wrapper and launch are installed only under
`gesc_gaussian_two_source_voltage.bash` and
`gesc_gaussian_two_source.launch.xml`; both superseded Phase 09-only names are
absent. Static graph and wrapper audits still find one `/cmd_vel` owner, one
managed `record_run`, no legacy CSV collector on the selected path, and no
rerouting of a historical wrapper. The selected wrapper's new live diagnostic
subscriptions are passive and opt-in; its bounded terminal tee and additional
hashed evidence capture do not change a legacy caller's recorder defaults.

## M8A live-Pi preservation result

Before transfer, the physical Pi matched all 306 sealed M0 source-file hashes,
not only the transfer overlap. The historical operator-selection subset was
also checked explicitly: all 26 Bash wrappers, all eight baseline launches,
and all six baseline files under
`turtlebot3_vehicle_nodes/config_files` matched their M0 bytes and modes.
That six-file count consists of the complete baseline contents of that package
directory; the broader 306-file check separately covers every actual
`ros_esc` adaptive/gradient controller, filter, and rotation configuration.

After the 51-path transfer and the selected-wrapper build/source correction,
the same 40-path selection check remains `40/40 PASS`, all 27 current Bash
files pass `bash -n`, and the mounted-source parity/launch suite reports `44
passed`. Only the new Phase 09 wrapper, its test, and the physical package
README changed for the correction. No historical wrapper, launch, or
configuration was copied or edited.

## M8B Vicon/rotation/recording preservation result

The final M8B audit reconstructed the legacy boundary directly from the M0
archive rather than assuming the M8A result still applied:

| Preserved boundary | Result |
|---|---:|
| all pre-existing Bash wrappers | `26/26` hash-identical |
| all pre-existing launches | `8/8` hash-identical |
| baseline vehicle configuration assets | `6/6` hash/mode/size-identical |
| expanded paths beneath configuration directories in all three packages | `68/68` hash/mode/size-identical |
| repository legacy behavior | `34 passed` |
| every current Bash entry point | `27/27` passes `bash -n` |
| unique installed wrapper launches | `6/6` passes `--show-args` |

The historical generic odometry/Vicon relay, seven-float Vicon server/client,
rotate-frame node, encoder, data collector, controller/filter configurations,
and their historical launch/wrapper selections remain M0-identical. M8B adds
only selected-path owners: an identity-bearing evaluation-only Vicon pair, a
recorder-gated rotation owner, a passive stationary timekeeper, and their
focused tests. The dedicated M8B launch cannot publish Vicon as `/odom`; all
controller, supervisor, modified-cost, history, fill, and escape pose
arguments remain exactly `/odom`.

The shared controller, cost/modified-cost, filter, supervisor, PDE/history,
Gaussian-fill, encoder, and core algorithm sources still match the selected
cumulative Phase 08 boundary. Physical robustness is provided by the additive
selected launch, wrapper, adapter options, and existing sole recorder. Legacy
callers retain their old defaults and do not opt into the Phase 09 readiness,
rotation-authorization, Vicon-evidence, stationary, or expanded recording
contracts.

The final snapshot has `345` reviewed files and the mounted Pi matches all
`345/345` hashes and `432/432` type/mode/size inventory entries. This makes the
snapshot preservation proof transitive to the transferred source. The Pi's
four pre-existing cache directories and six `.pyc` files were excluded and
left unchanged. No on-Pi build, installed legacy experiment, ROS graph, serial
device, GPIO, servo, or motor was executed by this compatibility gate.
