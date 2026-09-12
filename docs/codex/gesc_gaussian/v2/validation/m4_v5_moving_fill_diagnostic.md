# M4 v5 recorded moving-fill diagnostic

Status: diagnostic complete, 2026-09-10 UTC. This establishes the recorded
reason for the first v4 C safety stop; it does not evaluate performance,
reclassify the run or establish either original research goal.

Plans: `../m4_v5_moving_fill_diagnostic_plan.md` and the separately adopted
`../m4_v5_diagnostic_export_correction.md`. Subsequent implementation is
governed by `../m4_v5_moving_fill_plan.md`.

External root `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Input is the immutable finalized run
`pilot/m4_pilot_v4/runs/2026-09-10/m4-pilot-v4-slot03-C-26090801/`.

The first one-shot helper failed at output serialization: invalid source
timestamps may be NaN and strict JSON rejected the first event. It exited 1
in 2.670308 seconds; preserve `builds/m4_v5_moving_fill_v1/diagnostic/`,
including partial output, exact helper/command/log and failed receipt.
Post-failure hashing verified all 11 original run files unchanged. That
attempt remains failed and did not recover an event detail.

The separate corrected export represents nonfinite numbers as explicit
tagged values, retaining validity flags. Its serialization fixture passed
before execution. Exact command is in
`builds/m4_v5_moving_fill_v1/diagnostic_export_v2/command_v2.json`:
`timeout --signal=SIGINT --kill-after=10s 60s env -u PYTHONPATH bash --noprofile --norc -c ...`
sources the existing Humble, Q2 and Q5 overlays, then executes `extract_v2.py`.
The parent uses a 71-second subprocess timeout as last-resort observation
allowance; the extraction command itself has a 70-second cap including exit.
It completed exit 0 in 4.424504 seconds; existing `read_run_bag` took 1.119386.
No ROS graph, simulator, numerical model, position labels or direction
references were started. Only the plan's selected aliases were decoded.

Receipt `diagnostic_export_v2/receipt_v1.json`, relative to the build root,
SHA256 `d1ac26282e4282dcfebab19e889e6c72c68f6d5c2605bcb0a36da745f4b4e8ef`,
verifies all 11 original run-file hashes and 618 source hashes before/after.
The unmodified bag SHA256 is
`24840f73f826b6e2e8972dbe14afe8611d3a72d2045daf8d3bf7d6b15b330020`.
Full retained events, seven distinct state transitions and typed transaction
descriptors are in that same exclusive output directory.

| Recorded event | Simulated time (seconds) | Meaning |
| --- | --- | --- |
| Gaussian fill activation | 152.0 | Active fill 1, generation 1; source support time 151.41500000000002 |
| Objective and direction acknowledgement | 152.1 | Both matching-digest consumer receipts recorded in closed lifecycle audit |
| DESIGN to ESCAPE transition, then first FAILSAFE | 152.2 | No retained pose outside frozen exit radius; no ESCAPE_STARTED or escape interval |
| Postcommit CANCEL reply | 152.3 | ALREADY_ACTIVATED, preserving committed fill |
| Later controller watchdog events | 166.6 and 166.7 | Missing/stale original filter receipt, then filter input; not the first stop |

Exact first stop detail:
`open-field escape approach continuity has no pose outside the frozen exit radius`.
Committed fill exit radius is 1.3667708293638696 m. The diagnostic does not
establish an alternative policy's outcome on this trajectory or explain the
later watchdog chain. The next source work tests strict typed event authority
and prospectively selects the existing bounded interior policy, with matched
arms and retained safety guards. No v5 preparation/acquisition is released.

Repository recovery: V2 branch at `3369cfc`, all task changes saved uncommitted;
context validation passes. V1, physical/Pi and all prior experiments are held.
