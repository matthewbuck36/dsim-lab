# Phase 09 Live-Pi Source Transfer Receipt (M8A and M8B)

Verified: `2026-08-01T23:21:44Z`

Result: `PASS — SOURCE TRANSFER AND HOST-SIDE STATIC QUALIFICATION ONLY`

The sections through “Deferred gates” are the immutable M8A receipt. The M8B
additive receipt at the end supersedes its 339-file/51-path current-state
figures while preserving the historical transfer evidence.

This receipt does not claim an on-Pi build, ROS graph startup, serial access,
stationary commissioning, calibration, emergency-stop rehearsal, or physical
motion. None of those actions ran.

## Authorization and target

The user explicitly mounted the physical TurtleBot3 Pi with SSHFS and
authorized applying the reviewed Phase 09 snapshot changes to its real source
tree. The resolved endpoints were:

```text
source snapshot:
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
mounted Pi source:
  /home/mattb/tb3-pi/ros2_ws/src
mount source:
  pi@192.168.1.36:/home/pi
mount type/options:
  fuse.sshfs, rw
```

The Pi home advertised ROS 2 Humble, `TURTLEBOT3_MODEL=burger`, and
`ROS_DOMAIN_ID=36` in `.bashrc`. The SSHFS filesystem reported approximately
`1.5 GiB` free before transfer. Remote process state is not observable through
the mounted home alone; no local matching ROS/Gazebo/hardware process was
running, and no remote command or process was started.

## Pre-transfer conflict and compatibility gate

The mounted source contained the same three expected packages. It matched all
`306/306` sealed M0 regular-file hashes and all `389/389` baseline
type/mode/size entries. The exact transfer set was:

```text
manifest paths: 51
existing replacement targets: 18/18 M0-identical
declared new targets: 33/33 absent
overlaps or source errors: 0
```

An independent read-only audit reached the same result. It also reconstructed
the historical selection set and found `26/26` Bash wrappers, `8/8` launches,
and `6/6` baseline `turtlebot3_vehicle_nodes/config_files` assets hash- and
mode-identical. The full `306/306` baseline proof additionally covers every
legacy `ros_esc` controller/filter/rotation configuration.

Four pre-existing `__pycache__` directories containing six `.pyc` files were
the only source-tree additions relative to M0. They did not overlap the
manifest and were excluded and left untouched.

## Recoverable live-Pi backup

Before source transfer, a scoped backup was created outside `ros2_ws/src`:

```text
/home/mattb/tb3-pi/phase09_backups/20260801T230325Z
```

It contains byte-preserving copies of all 18 pre-existing transfer targets,
the explicit 33-path absent/new list, the full 51-path transfer manifest, the
sealed M0 source and inventory receipts, and a compressed archive of the
existing targets.

```text
existing-target hashes: 18/18 PASS
archive extraction proof: 18/18 PASS
backup manifest entries: 25/25 PASS
backup_manifest.sha256:
  17859e95c590c78abc8fb015229d825ae7f10d167d1ac86afb20d24e283f2561
existing_targets.tar.gz:
  d3ccc408259b172162927c2da47db2ff5fc7ab0484b99d32511c1533a8b38366
```

Rollback must restore those 18 files and remove only individually validated
paths listed in `new_paths_before.txt`. It must not recursively delete a
directory or use `rsync --delete`.

## Reviewed transfer

The first plan-shaped `rsync -a` dry run exposed harmless but unnecessary
owner/group and existing-directory timestamp updates. No write occurred. The
actual reviewed command retained archive semantics for files while suppressing
those unrelated directory/ownership mutations:

```bash
rsync -a --omit-dir-times --no-owner --no-group --itemize-changes \
  --files-from=/home/mattb/dsim-lab/docs/codex/gesc_gaussian/validation/phase_09_transfer_manifest.txt \
  --relative \
  --exclude=build/ --exclude=install/ --exclude=log/ \
  --exclude=__pycache__/ --exclude=.pytest_cache/ --exclude=.git/ \
  --exclude='*.pyc' \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ \
  /home/mattb/tb3-pi/ros2_ws/src/
```

The dry run and actual first transfer each resolved to `18` modified files,
`33` new files, three required new directories, zero deletions, and zero other
changes.

## Bounded operator-wrapper correction

The live-transfer audit found that the selected wrapper sourced an existing
workspace but did not run the build that the user expected from a manual Bash
entry point. This was corrected first in the offline snapshot, then copied to
the Pi through the same transfer manifest:

- `turtlebot3_vehicle_nodes/README.md` now documents build plus source;
- `gesc_gaussian_two_source_voltage.bash` now changes to the reviewed
  workspace, runs `colcon build --packages-select ros_esc_interfaces ros_esc
  turtlebot3_vehicle_nodes`, verifies `install/setup.bash`, then sources it;
- the wrapper carries an `MBuck 2026-08-01` explanation comment; and
- `test_phase09_physical_launch.py` enforces the exact three-package set and
  build-before-source order.

This changes only Phase 09-owned behavior/documentation and its regression
guard. All historical wrappers, launches, and configurations remain untouched.
The correction dry run and actual copy each contained exactly those three
manifest paths; the final dry run reported zero changes.

## Final parity and static qualification

The snapshot and mounted Pi now both satisfy the resealed final evidence:

```text
regular-file hashes: 339/339 PASS on snapshot and Pi
inventory type/mode/size entries: 425/425 PASS on snapshot and Pi
snapshot-to-Pi manifest dry run after transfer: 0 changes
legacy selection hashes after transfer: 40/40 PASS
all Bash entry points: 27/27 bash -n PASS
symlinks: 0
pre-existing generated cache state after checks: unchanged at 4 dirs/6 files
```

Host-side checks read the mounted source while writing all Python/test caches
under `/tmp`, never under the Pi source tree:

```text
Python compileall: PASS
structured parsing: 11 XML, 7 YAML, 68 JSON PASS
full final Phase 09 mounted-source collection:
  93 passed in 28.34 s
  /tmp/phase09_pi_final_full_retry.4Cft1g
direct parity/launch subset:
  44 passed
  /tmp/phase09_pi_final_static.wjVVZA
```

The test environment sourced the host's ROS 2 Humble installation and local
`dsim-lab` generated interfaces only. It did not source or execute the Pi
workspace, instantiate the physical graph, open a device, or run the wrapper's
new build command.

Final resealed artifact digests:

```text
phase_09_transfer_manifest.txt:
  5f60d69adc5d0feb87cb2fa2dd7c16cdc3bab846d3ec84fee181cb1dce9661f5
phase_09_snapshot_after.sha256:
  1d86d9ebceffbef49df06a53470f972f1897fc7488fd0fa315abd2a47004cd36
phase_09_snapshot_inventory_after.tsv:
  8eacf7b7f36cd67979688cf168ae5fd3c4e8274ebdffa149e76b12c737c647ee
phase_09_snapshot.patch:
  8985b4b2f5a33383a9abe4b6dc48a48a999c4da9dec5dfc24b88e9b324708939
```

The updated 51-path patch applies forward to a clean M0 archive and reproduces
all `339` final hashes. Its reverse reproduces all `306` M0 hashes. The four
known inherited whitespace warnings remain byte-preservation evidence.

## Deferred gates

- On-Pi three-package build: `NOT RUN` by the user's SSHFS-only instruction.
- Pi-installed `ros2 launch ... --show-args`: `NOT RUN` until that build.
- Selected-wrapper inert installed-overlay preflight: `NOT RUN` until build.
- Live topic/owner/readiness/final-zero checks: `NOT RUN`.
- Serial, photoresistor, IMU, odometry, rotating frame, OpenCR, and motors:
  `NOT ACCESSED`.
- Calibration, emergency-stop rehearsal, and physical motion: `NOT RUN` and
  not authorized.

The SSHFS mount was deliberately left mounted for the user; this receipt does
not unmount it.

## M8B evaluation/Vicon/rotation source transfer

Verified: `2026-08-02T03:19:15Z`

Result: `PASS — M8B SNAPSHOT-TO-PI SOURCE PARITY; ON-PI BUILD AND HARDWARE
DEFERRED`

The user had left the same physical Pi mounted read-write through SSHFS and
authorized the reviewed M8B source/configuration continuation. Before any
write, the mounted source matched the complete sealed M8A state:

```text
M8A regular-file hashes: 339/339 PASS
M8A type/mode/size inventory: 425/425 PASS
unexpected or missing non-generated paths: 0
pre-existing generated state: 4 __pycache__ directories / 6 pyc files
```

No command was executed on the Pi. All comparisons, backup operations, and
copies were host filesystem operations through the mounted SSHFS tree.

### Scoped M8B backup

The final 57-path transfer manifest was independently derived twice and had
the same SHA-256. Its checksum dry run against the M8A Pi resolved to exactly
15 changed existing files, six absent M8B-only files, one required new
directory, and zero deletions. Before transfer, all 15 existing files were
copied with relative paths and modes into:

```text
/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b
```

The backup contains the complete transfer manifest, existing/new
classification, reviewed itemization, full M8A before receipts, exact
pre-transfer hashes/inventory, expected after hashes, byte-preserving copies,
and a compressed archive.

```text
existing paths: 15
new_paths_before.txt: 6
backup files: 26
copied existing-target hashes: 15/15 PASS
same-permissions archive extraction: 15/15 hashes and modes PASS
existing_targets.tar.gz:
  a88dab7d51832f634558af9f886767a82c19c60ae7ff9a4b1c38764444a6fdbc
backup_manifest.sha256:
  c2fc028ba28bfb4244e706256a7b84c08654a112398987be808ae331bd7cb459
```

Rollback restores only those 15 files and individually removes only the six
validated relative files in `new_paths_before.txt`. It never recursively
deletes a directory and never uses `rsync --delete`.

### Reviewed M8B transfer

The actual command added checksum comparison and disabled file-timestamp
updates because timestamp drift is not part of the source recovery contract:

```bash
rsync -a --checksum --no-times --itemize-changes \
  --omit-dir-times --no-owner --no-group \
  --files-from=phase_09_transfer_manifest.txt --relative \
  --exclude=build/ --exclude=install/ --exclude=log/ \
  --exclude=__pycache__/ --exclude=.pytest_cache/ --exclude=.git/ \
  --exclude='*.pyc' \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ \
  /home/mattb/tb3-pi/ros2_ws/src/
```

The actual 21-file itemization matched the reviewed dry run byte-for-byte:
15 existing replacements, six new files, no deletion. A second dry run of the
57-path manifest was empty. A complete snapshot-to-Pi source dry run, excluding
only generated/cache/Git paths, was also empty.

### Final M8B parity and preservation

```text
snapshot files: 345
Pi reviewed file hashes: 345/345 PASS
snapshot inventory entries: 432
Pi type/mode/size inventory: 432/432 PASS
unexpected or missing non-generated Pi paths: 0
symlinks: 0
final manifest dry run: 0 changes
final complete source dry run: 0 changes
pre-existing Pi caches: unchanged at 4 directories / 6 pyc files
mounted-source Bash syntax: 27/27 PASS
```

The snapshot's formal legacy selection is `40/40` M0-identical and its
expanded configuration set is `68/68` M0-identical. Complete Pi parity makes
those results applicable to the mounted source after transfer. The final
snapshot artifacts are:

```text
57-path transfer manifest:
  f015285fa8b618f985d7257ac1471fe02c61e4ba17bc4701457ba36411931ff6
345-row after-file manifest:
  97af95a46bc8161f83a6776d609eb2480c0af0584b09ac62d5d60b9f2f638053
432-row inventory:
  602c2c9fa1f31fa7bd29692a07127e65b72c8570b1dcb6273226367db38643d2
57-path patch:
  6fd166368449f33cff85d5e1422a414199171b27d8420e9ea1364cb2f5090885
```

Forward and reverse patch/hash/inventory proofs pass. The final host build and
test results are recorded in `phase_09_static_qualification.md`.

### M8B deferred gates

- On-Pi three-package build and installed-overlay checks: `NOT RUN`.
- Selected installed wrapper `--check-only`: `NOT RUN` on the Pi.
- Stationary preflight and approval: `NOT RUN`.
- Live Vicon subject/segment discovery, server, and Pi client: `NOT RUN`.
- ROS topic/owner/readiness/final-zero rehearsal: `NOT RUN`.
- Serial, Arduino, encoder, GPIO, rotating frame, OpenCR, and motors:
  `NOT ACCESSED`.
- Calibration, lamps, emergency-stop rehearsal, and physical motion:
  `NOT RUN` and not authorized by this receipt.

The SSHFS mount remains mounted for the user. This receipt is source parity,
not `PHYSICAL READY`.
