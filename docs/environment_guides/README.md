# Root environment guides

The [parameter comparison](../environment_parameters.md) is the source-backed
simulation/physical reference. The simulation root README and AGENTS live at
the repository root. These versioned files retain the external-root guidance
in the V1 branch:

| Versioned document | Local destination |
| --- | --- |
| [physical_snapshot_README.md](physical_snapshot_README.md) | `/home/mattb/physical_TB3_files_snapshot/README.md` |
| [physical_snapshot_AGENTS.md](physical_snapshot_AGENTS.md) | `/home/mattb/physical_TB3_files_snapshot/AGENTS.md` |
| [tb3_pi_README.md](tb3_pi_README.md) | `/home/mattb/tb3-pi/README.md`, unmounted local directory only |
| [tb3_pi_AGENTS.md](tb3_pi_AGENTS.md) | `/home/mattb/tb3-pi/AGENTS.md`, unmounted local directory only |

Edit these versioned copies together with the root files. Recheck the mount
state immediately before any local `tb3-pi` guide write: it must be unmounted;
do not write through SSHFS or mount/unmount it as a side effect. While mounted,
read these tracked copies explicitly because the local mount-point files are
hidden. This task installed no files on the real Pi.

The snapshot and mount-point roots are not Git checkouts on this laptop.
Codex sessions should start at the documented root or explicitly load the
relevant AGENTS/README; automatic discovery from arbitrary nested non-Git
directories is not assumed. No global Codex setting was changed.
