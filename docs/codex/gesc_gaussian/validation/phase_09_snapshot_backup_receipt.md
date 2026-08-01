# Phase 09 Snapshot Backup Receipt

Verified: `2026-08-01T02:17:00Z`

## Scope

This receipt seals the no-hardware, pre-edit baseline for:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

The reserved live-Pi mount point `/home/mattb/tb3-pi` was absent from the
mount table. No SSH, SSHFS, serial, ROS, Gazebo, sensor, motor, or other
physical process was used.

## Recoverable archive

```text
archive:
  /home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260801T021552Z/ros2_ws_src.tar.gz
archive SHA-256:
  8109c5c47789ce1d2bb2cf69ba82f6901b054193989c488fefcfb9cf507404b8
archive entries: 390
```

The archive uses relative paths rooted at the snapshot source directory. A
path audit found no absolute path or parent-directory traversal entry, and
`gzip -t` passed.

## Baseline evidence

```text
inventory:
  docs/codex/gesc_gaussian/validation/
  phase_09_snapshot_inventory_before.tsv
inventory entries: 389
inventory SHA-256:
  4f7e130190441574a5663cc193be4fe1ac3b1a291e28fe98aaa3dee72ff25522

regular-file manifest:
  docs/codex/gesc_gaussian/validation/
  phase_09_snapshot_before.sha256
regular files: 306
manifest SHA-256:
  e38179695045e92cea03f023b6c7778d006c0df0a6c8f94ea1ce91c129999e17
```

The inventory records each relative path, type, mode, size, and symlink
target. The regular-file manifest records one SHA-256 per file. The baseline
has zero symlinks and zero nested `.git` directories.

## Extraction proof

The archive was extracted into a bounded `mktemp -d` directory under `/tmp`
with `tar --same-permissions`. Its complete inventory and all 306 regular-file
hashes matched the baseline byte-for-byte. A second read of the live snapshot
also matched the before manifest, proving the source stayed stable while the
backup was created and checked. The temporary extraction was then removed.

The first validation invocation used tar's default extraction permissions.
The current process umask changed one historical executable from mode `0777`
to `0775`, so that extra mode check stopped. It changed neither the archive
nor the snapshot. Revalidation with `--same-permissions` reproduced the exact
inventory and hashes and passed. Do not repeat the default-permission
extraction when testing this archive.

## Restore boundary

Restoration is not authorized during this no-hardware implementation. If a
future recovery is explicitly required, first verify the archive hash above,
extract it with `--same-permissions` into a new bounded temporary directory,
compare its inventory and hashes, and only then review a scoped restore. Never
restore into the live Pi or delete snapshot content without separate approval.
