# R3 attempt03 — automatic arrival stop established

2026-09-10. Acquisition is terminal: COMPLETE recording and inner/outer scoped
cleanup PASS. All 212 prepared source pins are stable. Root finished in
206.482343909 s, within 420 s (tool session82616, exit0). The new arrival-only
live monitor correctly recognized local recovery and stopped at a recorded
post-recovery global pose without requiring GOAL_HOLD or a ranked-goal event.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/`.
Run: `runs/2026-09-10/v2_method_development_D_20260910_03/`.
Plan: [attempt03](../r3_visible_development_03_plan.md). Exact wrapper dispatch
matches attempt02's saved command with both attempt-directory references changed
to `visible_integrated_03`; the new script/argv/prepared receipt are retained.

Observed path is SEARCH, VERIFY_EXTREMUM, DESIGN_OR_MERGE_FILL, ESCAPE_REPULSE,
SEARCH. There was no ESCAPE_ASSIST in this realization. The recurrent support
and fill now join at78.0 s, despite the distinct latest input pose timestamp.
One valid local fill is associated with its candidate, 0.048212 m from the
declared local source; fill-to-candidate displacement is0.061846 m. Stage A and
fill cardinality pass in live and retained evaluation.

Live and retained arrival evidence identify exactly the same pose at155.971 s:
(3.7412288197111785,3.0636442732174594), distance0.49859569167329104 m from
(3.5,3.5). The existing0.5 m boundary is unchanged. The monitor explicitly records
`controller_ranked_goal_required=false`, `graceful_global_proximity_stop=true`,
and no expired stage deadline. This establishes a second exposed nominal
development arrival and actual operation of the revised stop condition.

The frozen overall03 verdict remains FAILED on one inherited predicate:
`escape_command_ownership`. Its direct-repulse branch includes a geometric
requirement and reports `direct measured fill-to-exit alignment is below 0.80`.
All other declared predicates pass, including ground-truth arrival, local
recovery, state/event path, unique fill, recording and cleanup. Do not conceal
that result or treat its geometric flag as proof that command authority was
wrong. Read-only diagnosis is separating actual control ownership from the
inherited path-alignment requirement under the user's arrival criterion.
No gate has been waived and no fourth run is scheduled to recover a green result.

The existing-owner analysis completed in57.958 s under120 s, with exactly two
native scans (10.305 and9.567 s). Lifecycle is VALID with zero errors;54 output
artifacts and28 source/input pins verify, with no acquisition-source change.
Actual candidate acceptance78.1 s, collection admission84.6 s, snapshot93.5 s,
commit93.9 s, objective/direction acknowledgement94.0 s and renewed SEARCH115.4 s
are retained in `analysis_v1/`. Qualified direction inputs number4595, including
4497 within readiness, with zero integrity errors. Duplicate publications and
six unsynchronized skipped records retain their explicit denominators.

The separate fixed-target reference job completed in5.765 s under45 s, with26
artifacts and12 source/input pins verified. Of24 scheduled targets,5 were exposed,
4 were state-eligible and19 unexposed. All4 eligible estimates were usable and
improved over their paired instantaneous estimate; median error5.324428 degrees,
p9021.031274 degrees and median paired improvement46.140960 degrees. This is a
second exposed nominal realization, not a new independent field condition.

The geometric flag was reconstructed from closed exports: at the returned
SEARCH boundary, exit position(2.4638994068,1.1662629138) is1.4673606189 m from
the fill center, beyond its1.3683294852 m exit radius. Its alignment with the
frozen approach direction is0.5913724394 (53.7455 degrees), genuinely below the
old0.80 requirement. All preceding actual authority, command, radial-progress,
stable-exit and restored-SEARCH checks pass. This last geometric guard is a
directional-performance requirement inherited from V1; it is not a freshness,
command-limit, geofence or controller-ownership requirement. Its separation from
ownership under the explicit arrival criterion is now source-validated for both
direct and assisted branches; see [the prospective correction and tests](r3_arrival_alignment_separation.md). Preserve all old verdicts and report the
measured alignment honestly; no further simulation is required to erase this flag.
