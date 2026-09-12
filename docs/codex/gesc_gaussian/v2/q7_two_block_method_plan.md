# Q7 two-block centroid method amendment

Status: ADOPTED FOR SIMULATION IMPLEMENTATION, 2026-09-09. The user explicitly
selected the Q6 proposed two-block mean comparison in the restart request.
This amends the detector method for the next development/pilot version; it
does not reopen or relabel M1/Q1/Q2/Q6 evidence. Parent plan: `plan.md`.

## Exact method and compatibility

Add the explicit selector `centroid_two_block_v2` beside unchanged
`pde_mean_v1` (default) and `centroid_windows_v2` (five adjacent shifts).
For six consecutive equal-duration time-weighted centroids c0,...,c5, oldest
first, compute

`score_m = norm((c3+c4+c5)/3 - (c0+c1+c2)/3)`.

The prospective selected setting is W=6 seconds, epsilon=0.18 metres,
maximum radius=0.50 metres: two adjacent 18-second position means and
36 seconds of complete represented history. Require score strictly below
epsilon and represented trajectory radius at most the radius limit around
the mean of all six centroids. This measures positional settling, not basin
membership. Q6's ideal bounds and 0.10-second sampling limitation remain as
recorded; inherited maximum source gap 0.5 seconds is not qualified by that
analytic bound. No claim of empirical latency improvement follows.

Reuse `centroid_windows.py` integration/interpolation, source clock/reset,
confinement, bounded history and once-per-SEARCH latch. Add an explicit mode
to its configuration, defaulting to the historical five-shift behavior.
Reuse `centroid_contract.py` for shared mode-aware score arithmetic and
validation. Diagnostic `metric_mode` binds the formula. Keep all six window
centroids and the five adjacent `displacement_m` values unchanged as supporting
geometry; only `score_m` uses the selected formula. Reuse the existing IDL
layout and document both meanings; never reinterpret absent/old mode values,
historical bags, or legacy `r_mean_m2`.

Extend actual node selection and publication, typed confirmation/snapshot
admission, Q5 stationary Supervisor/Gaussian request selection, moving
Supervisor consumers, recorder metadata/validation, offline lifecycle analysis,
scenario schema and resolved launch pose routing. Bind recorded and live
evidence to the exact selected metric, not merely any admitted centroid mode.
Keep existing CLI/global parameter defaults unchanged; selected pilot B/D
must supply W=6, epsilon=0.18, radius=0.50 explicitly. Preserve Q1/Q2 scenarios,
existing PDE/five-shift selectors, numerical costs, clocks, topics, ownership,
moving information/comparability guards and 12-second abandonment.

## Bounded source milestone and validation

Before source edits retain a hash/archive of current dirty source and Q5/Q6/
M4A receipts externally. Implement one coherent source milestone using existing
owners; no new node, recorder, numerical evaluator or analysis pipeline.

Validate with independently computed two-block arithmetic, unequal sample
spacing/interpolated boundaries, fixed circles/fore-aft motion, drift/large
loops, strict threshold/radius, invalid mode and reset/latch cases. Exercise
both centroid scores through typed runtime/recording checks, reject switched
metric identity and wrong score arithmetic, and run relevant legacy, Q3/Q5,
moving lifecycle and launch regressions. Use actual DDS transport for the new
detector and stationary/moving consumers with supplied simulation-clock inputs.
Bound each test process at 300 seconds or less; external logs retain failures
and exact commands. Rebuild only if installed resources need it; unchanged
IDL layout needs no new generated schema. Inspect actual installed bindings.

Record results in `validation/q7_two_block_method.md`, update status and the
acceptance ledger, run the existing V2 checkpoint tool, and retain a material
source archive before advancing. No commit or push is newly authorized.

## Next empirical boundary

The next acquisitions remain the approved four visible development runs and
twelve frozen holdouts from `m4_plan.md`, with its exact arms/seeds/conditions,
720-second recording, 900-second inclusive case and 15,300-second suite caps.
Do not begin another qualification-only chain. Finish the saved independent
entry/settling and censoring definitions, direction target/denominator contract,
actual augmented-objective adapter, disturbance evaluator receipts, bounded
analysis and one-time freeze/release prerequisites before dispatch. Source
tests alone do not release a case or establish any research acceptance target.

Scope is this simulation checkout only. Preserve physical workspaces, V1 at
its final commit, every retained failed run, sealed confirmation and earlier
closed scientific results. The full V2 objective remains IN_PROGRESS.
