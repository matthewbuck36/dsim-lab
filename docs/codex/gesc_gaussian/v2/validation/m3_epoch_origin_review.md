# M3 guarded epoch-origin correction

The read-only common-owner review found that `EpochBinding.set_timekeeper`
checked finiteness, then called `round(start_time * 1e9)` outside an exception
guard. A finite `1e308` start time raised `OverflowError` before setting
`origin_fault` or invalidating the current context. A finite value beyond ROS
Time's upper bound could similarly fail while constructing the contract ID.

The shared epoch owner now uses existing `relative_stamp_ns(0, start_time)` and
constructs the contract ID inside a guard. Wrong simulation mode, missing or
malformed fields, negative values (including sub-nanosecond negatives),
nonfinite values, overflow and out-of-range ROS times invalidate authorization.
Its first valid origin/contract stays unchanged. Once invalid or changed origin
has faulted an owner, later valid packets cannot restore authorization or
replace that origin. Valid origin rounding and identical retries are unchanged.

Scope: only `ros_esc/v2_epoch.py` and new `test_v2_epoch_origin.py`. Root owns
centroid admission/frame corrections, PDE revocation ordering, and broader
common/DDS regressions. No Gazebo, field probe, hardware, or commit was run.

The focused test command ran from `/home/mattb/dsim-lab`:

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_epoch_origin_v1.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/ros_esc/test${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py
BASH
```

Result:20 PASS in0.24s, exit0, no warnings. Fixtures cover initially authorized
context revocation, immutable first origin, invalid first-origin non-recovery,
wrong/missing fields, real Timekeeper overflow, upper ROS range, valid fractional
rounding, idempotent valid repeats, and changed finite origin. Malformed Python
callback inputs use a small namespace where generated ROS setters would reject
them before transport.

The pre-fix reproduction was an in-memory callback probe under `timeout 30s
bash`, sourcing the same ROS/isolated overlay and PYTHONPATH. It constructed the
existing `test_v2_epoch_binding.Host`, `EpochBinding(host,resets.append)`, then
called `set_timekeeper(Timekeeper(mode='sim time',start_time=1e308))`. Its captured
output was `OverflowError cannot convert float infinity to integer origin_fault=
False resets=[]`. No experiment data was read or recomputed by that probe.

`git diff --check -- ros2_ws/src/ros_esc/ros_esc/v2_epoch.py` passed.

SHA256 at this correction boundary:

```text
974b8b00b33b55f7a9fe6b5709881ec62806042d0cc96dc03065ef721b34ebd7  ros2_ws/src/ros_esc/ros_esc/v2_epoch.py
442bb40315da2a22cda55a376be7bea1243b1ff5bb25a711df13f4d86de4920d  ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py
83975f7abb679f50002c0d6c3164b85e3e6d8ad1d91f6bae28e7042b39673295  /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_epoch_origin_v1.log
```
