# Q6 finite method decision before M4

Status: ADOPTED READ-ONLY ANALYTIC DECISION SCOPE. Q5 source is closed and held.
This is one finite mathematical comparison, not another Gazebo acquisition
series or authorization to replace the agreed detector formula. Read plan.md,
status.md, q5_stationary_centroid_adapter_handoff.md and the closed Q2v2 handoff.

## Decision and scope

The user goal is faster positional-settling detection including oscillation,
plus better moving GESC. All20 valid complete Q2 discovery detector histories
failed the agreed five-adjacent-shift score; Q3 addresses a distinct receipt
issue. The ideal response note identifies window/orbit sensitivity. Longer
windows may suppress this sensitivity but delay first eligibility. Before
blindly selecting a longer setting, make that timing tradeoff concrete.

Evaluate exactly two prospectively specified ideal settings once:

1. Existing five-shift score, W18s, epsilon0.90m, radius0.50m. Six windows require
   108s. This parameter setting is proposed, not calibrated or selected.
2. Proposal only: Euclidean difference between the means of the first three and
   last three of six existing W6s windows, epsilon0.18m, radius0.50m. Six windows
   require36s. Equal-duration time-weighted centroids can form these two means.
   This changes the agreed score and requires an explicit methodological choice
   before any runtime implementation. Do not silently substitute it for S.

Prospective ideal class: fixed-center circles or their fore/aft projections,
constant periods3–24s, radius/amplitude<=0.35m; translated counterparts with
speed>=0.02m/s; circles/oscillations of amplitude>=1m as large-loop negatives.
These are declared mathematical challenge bounds, not measured coverage of
actual Q2 trajectories or a newly relabeled old experiment. No stochastic pose
error is assumed. Source intervals<=0.10s for the sampled error bound; the
runtime0.5s gap rejection remains unchanged and is not claimed qualified here.

Use closed-form continuous-time centroids, all-phase/continuous-period envelope
maxima and a conservative piecewise-linear interpolation margin from the vector
second-derivative bound times h^2/8. Retain radius support and translated-motion
triangle-inequality lower bounds. One independent derivation and one finite
<=90s computation with saved script/JSON/text suffice. No grid, adaptive search
for better parameters, recorded-data/model job or empirical run is allowed.
If a specified setting fails, record its failure and do not replace it here.

## Consequences and next work

This math can compare ideal response and minimum history length; it cannot
prove30% improvement, direction accuracy, real-field validity or M3 support.
Keep the existing moving raw-information/comparability guards and12s abandonment;
measure rejected moving verification separately from detector settling. Do not
widen M3 tolerances just to get successful fills. Direction evaluation must have
predeclared targets and denominators independent of detector nomination.

After the method decision, use the already approved four visible development
runs and twelve frozen holdouts as the next empirical sequence, not another
qualification-only acquisition chain. Preserve exact16arms/seeds/conditions,
720s recording/900s outer caps and4h15 suite ceiling, integrity stop conditions,
unchanged research targets and all negative results. M4 command/configuration
preparation can be read-only while the methodological choice is pending.

Record math, command, outcome and scope in validation/q6_method_decision.md.
No source-level alternative is authorized by this note. If the user chooses a
new score, document its exact finite amendment before editing the existing
centroid/diagnostic owners; preserve selectable legacy behavior and old evidence.
