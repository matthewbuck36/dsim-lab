# R3 arrival criterion: separate exit geometry from command authority

PROSPECTIVE, 2026-09-10, before implementation. Adopted by the parent under the
user's explicit [arrival criterion](global_arrival_acceptance_20260910.md).
Preserve attempt03's frozen failed verdict and all historical contracts/results.

Closed attempt03 exports reproduce the last direct-escape rejection exactly:
exit distance1.467360618904201 m exceeds its1.3683294852468366 m radius, but
alignment to the latched approach direction is0.5913724394154973, below0.80.
This directional-performance criterion originated in the V1 measured escape
proof. Actual ordinary-GESC ownership, saturation, mature radial progress,
stable exit, returned SEARCH authority and later global arrival all passed.
The measured lifecycle is VALID. The user requires arrival, not a particular
exit bearing. Neither command safety nor a geofence depends on this dot product.

Change only existing `run_scenario.py` evaluator branches. For explicit
`success.criterion=post_recovery_arrival_v1`, retain measured alignment and
threshold0.80 with `exit_alignment_passed` and `exit_alignment_required=false`.
Its numeric failure is a reported geometric diagnostic, not command-ownership
failure. Direct and assisted branches must continue every existing authority,
source freshness, unit direction/revision, command arithmetic/limit, nonzero
drive, measured exit/radial-progress and returned-SEARCH/handoff check. In
particular, assisted post-return checks follow alignment in source and must
still execute. Do not early-return success at the alignment comparison.
For omitted/other selectors, retain the exact0.80 failure, output shape and
check order. No source/control law, message, physical or launch change.

Use existing owner fixtures under one90 s focused command, with the current
schema2 environment and source pins. Exercise the actual03 center/direction/
exit geometry in the existing direct owner, default rejection, selected
acceptance with explicit failed alignment diagnostic, and both branches'
authority/geometry/freshness/saturation/post-return failures. Include assisted
failures occurring after the now-nongating alignment comparison. Keep evidence
inputs immutable. Retain logs, exact command and result under exclusive
`development/20260910/arrival_alignment_separation_v1/`, validation under
`validation/r3_arrival_alignment_separation.md`. No new Gazebo, bag scan or
historical result write. Parent owns status/checkpoint/final archive.
