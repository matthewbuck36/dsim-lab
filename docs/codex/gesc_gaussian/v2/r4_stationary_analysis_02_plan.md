# Stationary development02 analysis invocation

PROSPECTIVE before analysis, 2026-09-10. Acquisition02 is terminal and passed:
219.483315s root wall, all284 pins stable, COMPLETE recording, strict owned
cleanupPASS, local circle confirmation/one fill/assisted escape and global
arrival at172.634 simulated seconds. Live and retained arrival poses agree.
Use [the02 plan](r4_stationary_integrated_02_plan.md)'s one120s native analysis.

Independent review found that the prepared helper did not hash `console.log`
and `notes.md`, although fresh native validation consumes them. Preserve that
unexecuted helper and its acquisition hash. Create `analysis/run_analysis_v2.py`
as an exact copy adding only those two validation-input pins and this amendment
to its source pins. The existing native analyzer/readers, fixed source methods,
numeric outputs, success checks and110s work/118s SIGINT+2s kill bounds remain.
This is an invocation evidence correction; no production source or numerical
method changes and no additional decoder scan.

Run once against the actual02 run directory with exclusive `analysis_v1/`
output. Retain the exact command, both helper versions, elapsed time, two native
decoder scans, all before/after source/input hashes, actual complete/partial
status and stationary audit tables. Require fresh completeness and valid typed
joins. A complete recording may still produce an explicitly partial native
analysis; preserve its reasons. Do not translate missing GOAL_REACHED timing
into a failed global arrival. No matrix or confirmation release.
