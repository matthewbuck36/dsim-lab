# M3 Arm C history clock admission — 2026-09-09

Status: bounded correction implemented; focused and existing actual DDS epoch
regressions pass. This record does not qualify M1 neighborhoods, M2 directional
performance, natural trajectories, or release M4/Gazebo.

## Defect and correction

The PDE owner and detector receive `/clock` independently. A valid PDE history
publication can therefore lead the detector's held local clock. Immediate
rejection discarded valid Arm C support even though its source owner had already
admitted the input. The selected rolling graph now queues authenticated histories
until the detector clock covers publication, without changing the inherited PDE
arithmetic, crossing threshold, or dwell decision.

`convergence_detector_node/v2_binding.py` validates the selected stream, immutable
epoch, payload hash, finite legacy values and source support before enqueueing.
It preserves detached data and the detector's first ROS/steady receipts. The
queue holds at most1024 wrappers; original receiver receipts and sender support
remain bounded by0.5s. Repeated packets do not refresh either receipt. Context
heartbeat delivery may follow the wrapper within the same immutable epoch;
admission waits for the referenced context sequence and local clock coverage.

Authenticated revocations immediately remove old numerical authority and fence
older sequences; their ordered queue processing still waits for clock coverage.
Conflicting sequences remain poisoned. A persistent sequence frontier prevents
unseen older histories from reviving after revocation, expiry or bounded cache
eviction. Admission of a revocation preserves later queued recovery evidence.
An epoch change clears old pending support. Final confirmation also rechecks the
original detector receipts, including steady time while `/clock` is held.

The source/input support must start at or after the bound epoch. An original
receipt may precede a nonzero Timekeeper origin when the valid future context
and source arrived before clock coverage; its valid range is
`0 <= receipt <= publication`, with the same0.5s freshness bound. No receipt is
replaced by a fabricated admission time. The focused fixture explicitly covers
sender and receiver receipts at9.9s with a10s origin/source/publication.

The earlier centroid admission/frame/reset fixes in this shared helper remain.
Standalone/default paths remain selected through their existing owners. The
parent separately owns the matching recorder receipt-bound correction.

## Exact commands and outcomes

All commands ran from `/home/mattb/dsim-lab`; the existing ROS and isolated V2
overlay were sourced and the inherited `PYTHONPATH` was preserved. No Gazebo,
hardware, command publisher, new field experiment, or commit was run.

Initial bounded test version, retained before the receipt-before-origin fixture:

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_history_admission_v1.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/ros_esc/test${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_history_admission.py ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py
BASH
```

Exit0: **47 passed in0.41s**, no warnings. This earlier test set is retained;
the following version validates the final source and added original-origin case.

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_history_admission_v2.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/ros_esc/test${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_history_admission.py ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py
BASH
```

Exit0: **68 passed in0.43s**, no warnings. Coverage includes delayed publication,
detached payloads, original receipt expiry, duplicates/conflicts, delayed and
out-of-order revocations, newer recovery, missing context heartbeat, epoch exit,
invalid envelope/hash/future bounds, finite queue capacity, stale sender support,
final-publication freshness, and existing epoch/origin/centroid regressions.

```bash
timeout 90s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_epoch_transport_v7.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export ROS_DOMAIN_ID=184
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/ros_esc/test${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_transport.py
BASH
```

Exit0: **3 passed in1.14s**, no warnings. The existing actual PDE/detector DDS
fixture covers Arm C and Arm D over two authoritative epochs, plus Arm D headers
leading the held clock by33,333,333ns. Its synthetic thresholds accelerate the
fixture. The new Arm C split-clock publication/revocation cases are deterministic
callback fixtures using actual wrapper construction; the DDS test does not
independently demonstrate those specific split-clock orderings.

`git diff --check -- ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/v2_binding.py`
also returned0 with no output. No additional generalized review or matrix rerun
was performed after these bounded checks.

## Validated source and artifact hashes

SHA-256 at closeout, before parent checkpoint:

| File | SHA-256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/v2_binding.py` | `04fd300c983ef295b67b4d9cd2024e9ee47f0e136f32216d9f0bae7bac9f0baa` |
| `ros2_ws/src/ros_esc/test/test_v2_history_admission.py` | `fdfdb63b583daa4e910e5fcd7ee85e9fad2c500c18c495b9d3c9e14f6875303c` |
| `m3_history_admission_v1.log` | `e9b604b2b388411d4f35d2c1463a415805e9cafa55635910e986df87ca84ee18` |
| `m3_history_admission_v2.log` | `b33b219240cf9a70b4a3e8c8174e4de6f841de873f1c955f31709a30619ec4c0` |
| `m3_epoch_transport_v7.log` | `7d209e7a67d4d4056b2535bffba5ccf0984c48a48b54ea9fa1588672ad3be0f3` |

All listed logs reside under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.
The parent's812-test integrated v2 result predates this final Arm C correction;
the68 focused and3 DDS checks above are the direct evidence for this source hash.
