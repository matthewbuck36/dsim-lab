# Phase 09 Future Pi Transfer and Rollback Procedure

Status: `M8B SOURCE TRANSFER EXECUTED — ON-PI BUILD AND M9 HARDWARE DEFERRED`

The source/configuration transfer was completed on 2026-08-01 under explicit
user authorization. Its exact preflight, backup, scoped-copy, post-transfer
hashes, wrapper build/source correction, static tests, and remaining deferrals
are recorded in `phase_09_pi_transfer_receipt.md`. The SSHFS mount was already
read-write when the authorized comparison began; every pre-write operation was
read-only, and no source write occurred until the backup and itemized dry run
passed. The actual transfer added no deletion flag and suppressed unrelated
owner/group and existing-directory timestamp changes.

The original procedure below remains the rollback contract. Its on-Pi build,
installed-overlay checks, inert wrapper preflight, and every hardware gate have
not run. Do not infer their completion from the source-transfer pass.

This was the reviewed M8 procedure. Its source-transfer portion is now covered
by the user's explicit authorization and the receipt above. It still does not
authorize an on-Pi command, launch, serial access, calibration, actuation, or
motion. M9 hardware commissioning requires another authorization after the
remaining M8 build/static-installed checks close.

## Frozen local inputs

```text
snapshot source:
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
future mounted Pi source:
  /home/mattb/tb3-pi/ros2_ws/src
transfer manifest:
  /home/mattb/dsim-lab/docs/codex/gesc_gaussian/validation/
    phase_09_transfer_manifest.txt
snapshot after hashes:
  /home/mattb/dsim-lab/docs/codex/gesc_gaussian/validation/
    phase_09_snapshot_after.sha256
snapshot after inventory/modes:
  /home/mattb/dsim-lab/docs/codex/gesc_gaussian/validation/
    phase_09_snapshot_inventory_after.tsv
```

The current transfer manifest contains exactly 57 paths: the 51-path M8A
boundary plus six new M8B-only Vicon/rotation/test files. It deliberately
includes the
new `gesc_gaussian_two_source.launch.xml` and its new-only manual entry point,
`gesc_gaussian_two_source_voltage.bash`. It does not include the historical
`light_gesc_gaussian_fill_experiment.launch.xml` or its Bash entry point; both
remain untouched. The superseded Phase 09-only names are not transfer targets.

## Stop-before-write checks

Before any mount or comparison, confirm the approved host, Pi address/user,
SSH key, maintenance window, ROS distribution, TurtleBot model, disk space,
and responsible operator. Stop if any value is unknown.

1. Verify that no ROS, Gazebo, recorder, serial, motor, servo, or rotating-frame
   process is running.
2. Mount the Pi read-only at `/home/mattb/tb3-pi`; verify the mount flags and
   retain the exact mount command/output.
3. Compare package manifests, Python/ROS versions, the complete 51-path
   transfer set, and the 40 frozen legacy selection assets.
4. Stop on any live-Pi modification that overlaps a transfer path, on a missing
   legacy Bash/launch/config asset, or on a material package/API mismatch.
5. Do not infer that the local historical snapshot is newer or authoritative
   merely because it exists.

The read-only comparison result and every overlap decision must be added to the
live Phase 09 status before write authorization is requested.

## Scoped backup before transfer

After a clean read-only comparison and separate write authorization, create a
UTC-named backup outside `ros2_ws/src` on the mounted Pi. Resolve the path to a
specific directory; do not use an unset variable, home shortcut, glob, or
broad recursive target.

For every transfer-manifest path, record whether it exists on the Pi. Copy each
existing file with permissions and timestamps into the backup using the same
relative path. Record the absent paths separately as `new_paths_before.txt`.
Hash and inventory the backup, then re-read it before transfer. A missing or
unverifiable backup is a hard stop.

The absent-path list can be derived safely from a retained live inventory; do
not assume that every path absent from the historical M0 snapshot is also
absent from the live Pi.

## Dry run and transfer

Remount read-write only after the backup receipt is complete and the user has
confirmed the exact itemized dry run. From the snapshot source root, use an
`rsync` command shaped as follows:

```text
rsync -a --checksum --no-times --itemize-changes --dry-run
  --files-from=/home/mattb/dsim-lab/docs/codex/gesc_gaussian/validation/
    phase_09_transfer_manifest.txt
  --relative
  --exclude=build/
  --exclude=install/
  --exclude=log/
  --exclude=__pycache__/
  --exclude=.pytest_cache/
  --exclude=.git/
  --exclude='*.pyc'
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/
  /home/mattb/tb3-pi/ros2_ws/src/
```

Review every item. There must be exactly the approved manifest paths, no
deletion, and no generated/runtime content. The actual transfer repeats the
reviewed command without `--dry-run`; it never adds `--delete`.

## Post-transfer static checks

1. Generate a manifest-scoped expected checksum file by joining the 57-path
   transfer manifest with `phase_09_snapshot_after.sha256`.
2. From the mounted Pi source root, require all 57 checksums to match.
3. Require the old GESC+Gaussian launch and all 26 pre-existing Bash entry
   points to retain their reviewed live-Pi pre-transfer hashes.
4. Build only `ros_esc_interfaces`, `ros_esc`, and
   `turtlebot3_vehicle_nodes` under a finite timeout.
5. Run Pi-compatible syntax, interface, pure-helper, wrapper hash/argument, and
   launch `--show-args` checks. Do not launch a node, open serial, or move any
   mechanism.
6. Require the exact selected wrapper/launch names to be installed and both
   superseded Phase 09-only names to be absent. Require `record_run --help` to
   expose `--evidence-file`, `--stream-console`, and
   `--live-diagnostics-period-sec`.
7. Run only the inert selected-wrapper preflight with the shipped
   motion-blocking templates. It must exit `2` before device/ROS access and
   leave no temporary `phase09_gesc_gaussian.*` directory. This does not
   authorize a commissioned wrapper run.
8. Recheck the exact pre-transfer hashes for all 26 legacy wrappers, eight
   legacy launches, and six legacy configurations after the scoped build and
   preflight.
9. Record exact skips and resource limitations. A build pass is not motion
   authorization.

## Rollback

Rollback uses only the verified live-Pi backup and its recorded absent-path
list.

1. Stop all potentially related processes and remount read-write only with
   rollback authorization.
2. Restore every backed-up existing file to its exact relative path with its
   recorded mode and hash.
3. For each path in `new_paths_before.txt`, verify that it is a normalized
   relative path present in the 57-path transfer manifest, then remove only
   that exact file. Do not remove directories recursively; prune only empty,
   explicitly reviewed Phase 09-created directories.
4. Recompute the pre-transfer hashes/inventory and require equality.
5. Rebuild the three packages under a timeout without starting the graph.
6. Remount read-only, retain the rollback receipt, and stop.

Never use a whole-home copy, wildcard restore, recursive delete, blind snapshot
overwrite, or `rsync --delete`. If an exact target, backup, mode, or absent-path
classification cannot be proven, rollback stops for review.

## Current nonexecution evidence

During M0-M7.1, `/home/mattb/tb3-pi` was not a mountpoint. M8A and M8B later
used the user-mounted SSHFS tree for backed-up source/configuration transfer
and host-side filesystem/static inspection only. No command was executed on
the Pi; no on-Pi build, serial access, ROS hardware launch, Vicon client,
calibration, mechanism actuation, or physical motion was executed.

## M8B additive transfer receipt

The M8B source was frozen and host-qualified before any Pi write. The mounted
Pi first matched the sealed M8A state at `339/339` file hashes and `425/425`
inventory entries. A checksum dry run of the final 57-path manifest resolved
only `15` existing content replacements, `6` absent Phase 09-only files, one
new directory, and zero deletions. File timestamps were deliberately excluded
because they are neither source nor recovery evidence and one unchanged shared
CMake file had only host-side mtime drift.

The scoped rollback backup was verified before transfer:

```text
/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b

existing targets: 15/15 hash and mode proof PASS
new-path absence list: 6 paths
archive extraction proof: 15/15 PASS
existing_targets.tar.gz:
  a88dab7d51832f634558af9f886767a82c19c60ae7ff9a4b1c38764444a6fdbc
backup_manifest.sha256:
  c2fc028ba28bfb4244e706256a7b84c08654a112398987be808ae331bd7cb459
```

The actual itemization matched the reviewed dry run exactly. The final
manifest-scoped and complete source-tree dry runs both reported zero changes.
Mounted-source proof then matched all `345/345` reviewed file hashes and all
`432/432` type/mode/size inventory entries, with zero missing or unexpected
non-generated paths. The four pre-existing cache directories and six `.pyc`
files remained unchanged and excluded. The exact full receipt remains in
`phase_09_pi_transfer_receipt.md`.
