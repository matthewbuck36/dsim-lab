# R3 arrival alignment separation: source validation

SOURCE_VALIDATION_PASS, 2026-09-10, under the prospectively saved
[amendment](../r3_arrival_alignment_separation_plan.md). No Gazebo or bag scan.
Attempt03's original COMPLETE recording, failed frozen classification and
successful recorded global arrival remain unchanged. Parent owns closeout.

Only the existing direct/assisted escape evaluator branches changed. For exact
`post_recovery_arrival_v1`, exit bearing is retained as a performance diagnostic:
`fill_to_exit_alignment`, `exit_alignment_threshold=0.80`,
`exit_alignment_passed`, `exit_alignment_required=false`. Its failure does not
fail command ownership. Every other guard still executes, including all
assisted post-alignment handoff, authority-clearing and saturation checks.
Default and other selectors retain the old0.80 rejection and output shape.
No algorithm, controller limit, source stream, message or launch changed.

## Actual retained geometry

Closed03 event/state/odometry exports reproduce the existing nearest-boundary
selection without another bag read. SEARCH starts115.4 s; selected odometry is
115.409 s at(2.4638994067988924,1.1662629137534182), bag stamp
1789070417795153591 ns,23.389 microseconds before the recorded SEARCH message.
The frozen fill center is(0.9968323455755517,1.1369128918721536) and selected
direction(0.575124615259862,0.818065814541957). Measured exit distance
1.467360618904201 m exceeds radius1.3683294852468366 m by0.09903113365736438 m.
Alignment0.5913724394154973 means53.7455387 degrees from that direction; the
historical0.80 limit permits36.8698976 degrees. This is a real directional
performance miss. The earlier owner checks passed426 repulse states,1052
nonzero ordinary GESC control samples,426 zero supervisor commands and364
mature progress samples (minimum0.11156426836024 m versus0.05 required), plus
stable returned SEARCH and authority clearing. This diagnostic does not
reinterpret the original frozen scenario result.

## Focused validation

One90 s test command completed240 PASS/1 SKIP in39.95 s, terminal exit0.
It ran `test_r3_arrival_alignment.py`, `test_r3_arrival_evaluator.py`, and
`test_scenario_runner.py` in the existing schema2 overlay. The25 new owner
cases cover exact03 geometry, old/default rejection, unknown-selector rejection,
selected acceptance with explicit failed alignment, good alignment reporting,
immutable input fixtures, retained direct measured-exit/radial-progress/
freshness/ownership/saturation guards, and seven assisted failures after the
alignment comparison. Those later faults still reject: retained state
authority, nonzero supervisor command, missing diagnostics, contribution
arithmetic, saturation, no ordinary return and delayed ordinary return.
Actual classification still requires the ownership predicate.

The sole inherited skip is the opt-in recorded headless Gazebo end-to-end test
(`RUN_GESC_PHASE06_GAZEBO_E2E` unset). No unavailable required test. Existing
phase-context validation and `git diff --check` PASS. All seven scoped source,
test, plan and environment pins remained unchanged during the finite test job.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/arrival_alignment_separation_v1/`.
`command.json` retains the exact shell invocation and cwd, `focused.log` the
complete test output, `source_pins.json` the held identity, and `result.json`
the verdict and original03/export receipts. The command used
`env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1`, sourced
`centered_runtime_v2/environment.sh`, and ran `timeout 90s python3 -m pytest -q`.
There is no active source/test job. The original03 summary/result files were
only hashed for this receipt, never modified or reclassified.

`result.json` SHA256:
`23aa0a5cead278d030bcb66a26b3c13ec1b1cb13e77e574097eb8c5ee2543ab9`.
Final `run_scenario.py` SHA256:
`03a567d22977512d7bb49beab1cf6e906d600762d695e933c469842b3e039f6c`.
