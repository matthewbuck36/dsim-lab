# M1a: independent enclosure labels and a fresh centroid threshold grid

Status: **FROZEN M1a v1 after root review, 2026-09-09 UTC.** The machine-readable
contract is `validation/m1a_contract_v1.json`. Execute only after its focused
implementation checks pass and the pre-experiment checkpoint is recorded.
This is a bounded simulation-only
M1 numerical/evidence correction under the approved V2 development process.
The root agent must review and lock the complete contract before execution.
It does not change the research objective or advance M2–M4.

## Preserved failure and reason for this version

The original 36-configuration calibration completed with zero qualifying
configurations. Preserve its scientific FAIL, rather than modifying its grid,
labels or reported outcome. Its retained summary is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_calibration_v1/calibration.json`,
SHA256 `9b10b120dc7cd59b07e08536e246d79919f1f36fce73898056b42ab48c7c898b`.
Its selected configuration is null. The original frozen label manifest is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a/labels.json`,
SHA256 `70890350ef896c042a947bb50d3c1ff882bb555efb1e5e6c23afb3a6555884ad`.
Preserve those directories, the earlier failed `m1_labels_v1` publication,
their logs, and all original contracts. M1a must use new exclusive-create paths.

Two independently identified numerical issues motivate this version:

1. [The analytic score diagnosis](validation/m1_centroid_grid_diagnosis.md)
   derives why the old maximum epsilon=0.24 m cannot accept every declared
   positive small-circle trace at any allowed W. Its sampling-error bounds
   establish threshold ranges that can separate the declared circle family
   from translation at >=0.02 m/s without changing those labels.
2. A bounded evaluator-only geometry diagnosis found angular integration and
   point-minimum interpretation issues. A narrow angular response can be
   under-resolved by 72/144 samples, and a connected annular low-cost region
   need not have one uniquely identifiable point minimum. Replace the point
   optimizer/ring test with a resolved, enclosed low-cost-region test. This
   must be justified by numerical error and enclosure evidence, independently
   of detector outputs; it must not merely reduce the old 0.025 cost margin.

The geometry diagnosis remains at
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_geometry_diagnostic_v1/`.
Its evidence is diagnostic, not a new basin qualification or detector result.

## Fixed inputs and independence

Keep the original `validation/baseline_inventory.json`, SHA256
`eae9b60fc2f6f3e638f7ee9e56fd52174176fb4495de78bb145640eddb93e90d`.
The same eight development inputs are seeds
`19801, 19811, 19851, 19901, 19911, 19931, 20001, 20031`.
The thirteen retrospective holdout inputs remain excluded:
`19812, 19813, 19814, 19815, 19816, 19817, 19818, 19819, 19820,
19912, 19913, 19914, 19915`. Do not move runs between partitions.

Reuse the original **79 synthetic traces byte-for-byte**, including coordinates,
timestamps, identities and labels, from
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1a/synthetic_inputs.json`.
Its SHA256 must remain
`4eb9cf3799616e1664e16e8b60f633c2051bf6fda697a83fad67fa3e1bdd136c`.
Reference this immutable file or copy it without reserialization and verify its
hash. Do not regenerate a changed population or drop a failed positive.

Reuse the qualified development input traces only after verifying their frozen
hashes and the underlying bag/configuration hashes. The label pass uses pose,
source/sensor inputs and evaluator geometry. It does not read detector output,
fill outcomes, or supervisor states to choose enclosure geometry or spatial
labels. Apply recorded SEARCH/readiness masks only after spatial labels freeze.
Preserve the original timekeeper reconciliation, source/pose gap <=0.50 s,
source/encoder/transform alignment <=0.05 s, frame validity and existing
recorded-freshness limitations. Unqualified inputs remain unknown.

Reuse the existing aggregate-field evaluator and geometry binding with their
recorded configuration, cost sign and units. Source coordinates seed a finite
geometric search; they do not establish a basin center, label, source validity
or runtime input. Do not import detector outputs into the geometry pass.

## Finite numerical enclosure protocol

Use the following finite construction for each distinct recorded geometry and
source. At most six source enclosures are evaluated across the three currently
frozen geometry/configuration groups. A changed or larger population requires
a separate prospective contract, not automatic expansion.

1. **Exploration grid.** Center a 33-by-33 Cartesian vertex grid on the source
   coordinate, spanning +/-0.75 m in each axis, with spacing h=0.046875 m. The
   entire square must lie inside the recorded scenario bounds; otherwise the
   source is unknown. Do not clip, move or shrink the square to obtain a result.
   Add the midpoint of each of its 128 outer grid edges to the boundary witness
   set. The source only locates this exploration square.
2. **Stationary cycle mean.** At every used location, integrate the unchanged
   evaluator raw cost over sensor world angle 0..2*pi and divide by 2*pi.
   Use `scipy.integrate.quad` with `epsabs=2*pi*1e-7`, `epsrel=1e-7`, and
   `limit=128`. Breakpoints include multiples of 30 degrees and the bearings
   from the evaluated location to every recorded source, plus their antipodes.
   Deduplicate and wrap the interior breakpoints; omit the undefined bearing
   when a source coincides with the evaluated point. Perform an independent
   second integration with the 30-degree partition shifted by 15 degrees,
   retaining the same source-bearing/antipode breakpoints. No angular minimum
   or envelope replaces the mean.
3. **Numerical uncertainty.** Let J be the average of those two mean estimates.
   Let e be the maximum of their two reported mean errors and their absolute
   disagreement. Any integration warning, failure, nonfinite value, or
   e>1e-6 raw-cost unit makes the source unqualified/unknown. Preserve both
   values, both error estimates, breakpoints, warnings and evaluation counts.
   These are numerical error estimates and cross-checks, not rigorous error
   bounds over all angles.
4. **Provisional barrier and level.** On the initial grid and boundary witness
   points, set `m_hi=min(J+e)`, `B_lo=min_boundary(J-e)` and
   `E=max(1e-8, all e)`. Require `Delta=B_lo-m_hi > 10 E`. The fixed provisional
   low-cost level is `T=m_hi+Delta/2`. A vertex is low when `J+e<T`, high when
   `J-e>T`, and otherwise ambiguous. This relates the barrier margin to
   independently measured numerical resolution; no replacement fixed cost
   depth is tuned to a trajectory or detector output.
5. **Cell-center checks and one recomputation.** Evaluate the center of every
   cell whose four original vertices are provisionally low, using both angular
   integrations above. There are at most 1024 such centers. Recompute m_hi and
   E once using all completed locations, retain B_lo from all outer witnesses,
   require `Delta>10 E` again, and set the final T by the same midpoint rule.
   This added set can only decrease m_hi and T, so no previously untested
   four-low-corner cell can become newly eligible. Do not run an iterative
   threshold or spatial refinement search.
6. **Connected-region qualification.** Final low grid vertices must form one
   eight-neighbor connected component, with no boundary contact. Equivalently,
   a lexicographically first minimum may identify it, but any competing
   disconnected low component makes this source unknown; do not choose the
   favorable component. Accept a cell only when its four vertices AND its
   checked center satisfy `J+e<T`. The accepted cells must form exactly one
   component connected through full shared edges, containing at least four
   cells and touching no outer boundary. Diagonal contacts do not connect
   cells. Disconnected, boundary-touching, empty or unresolved cases remain
   unknown. Mixed cells are not positive regions. Retain the exact cell mask
   and its outer and hole boundaries.

The final positive region is the **interior of the union of those accepted
closed cells**. Do not fill annular holes. Its reported center is the
area-weighted centroid of the cells; its reported radius is the maximum
distance of their vertices from that derived center. Neither value is the
source seed or a point-optimizer result. This radius describes the independent
label region and does not replace the detector's separately calibrated R.

The geometry is an operational finite-grid enclosure supported by the sampled
low-region and higher outer-boundary witnesses. The five-point cell stencil
does not certify every unsampled point inside a cell, and midpoint boundary
checks do not prove a continuous barrier between witnesses. Report h, cell
diagonal `sqrt(2)*h` (about 0.0663 m), all uncertainty indicators and this
limitation. The cell diagonal is spatial resolution, not a proved error bound
on the location of the true continuous well boundary. Do not call this a
formal attraction basin or a continuous-domain certificate.

For positive membership, treat any position or represented segment touching an
outer or hole boundary within 1e-9 m as unknown. Split each piecewise linear
pose segment at grid-line crossings and check the resulting open-subsegment
midpoints and endpoints against the region. Shared edges inside the accepted
union remain interior; an internal shared edge or grid corner counts as interior
only when all of its incident cells are accepted. Only the actual outer/hole
boundary is excluded. Do not
resample time or evaluate cost at trajectory positions to alter the region.

For conservative negative exclusion, form a possible-well mask from all cells
incident to the selected low-vertex component, then add one cell of Chebyshev
dilation clipped to the exploration square. A negative segment chain must be
disjoint from every qualified source's possible-well union, including its
boundary. Use exact grid-crossing segmentation with the same 1e-9 m tolerance;
an endpoint-only test is insufficient. Annular holes never become positive by
filling them. Hole motion remains unknown unless its entire segment chain lies
outside these conservative possible-well unions AND independently satisfies
the unchanged directed-progress test. Record both positive and negative
exclusion masks, so this distinction can be audited.

Maximum distinct locations are 1089 grid vertices + 128 outer-edge midpoints +
1024 candidate cell centers = **2241 per source**, with two bounded angular
integrations per location. No extra spatial grid, seed, region radius, optimizer,
angular retry or favorable-component choice is permitted within this version.

## Label semantics and unchanged temporal comparison

The qualified geometric region will be an explicit **operational modeled
basin-residence region**: an enclosure containing a numerically resolved,
connected low-cost region with a higher surrounding boundary. It is not a
formal basin of attraction, uniqueness theorem, exact optimizer certificate,
or proof of source-seeking dynamics. Ambiguous or unresolved geometry remains
unknown; an absent positive label does not turn the interval negative.

Preserve the original temporal contract:

- A positive residence lasts at least 12 s of continuously qualified support;
  its onset is the first qualifying in-region sample. Invalid support or
  geometric uncertainty interrupts residence.
- The common positive comparison requires 54 s of uninterrupted eligible
  support, independently of W. Report shorter intervals as right-censored.
- Use only the earliest genuine residence opportunity in each observed SEARCH
  epoch. If it is censored or interrupted, censor that epoch; a later opportunity
  cannot replace it. Preserve one detector latch per epoch and do not reset at
  label boundaries.
- Negative directed progress still requires six seconds outside every
  qualified enclosure, >=0.12 m net travel, and net/path-length ratio >=0.80.
  Use an exact six-second source-time interval: interpolate its initial
  position on the recorded piecewise linear segment at `end_time - 6 s`.
  This measurement-only clipping neither resamples nor changes the frozen
  trace or region. It avoids counting an irregular 6–6.5 s interval with
  0.12 m travel as the intended >=0.02 m/s progress. This pre-execution
  clarification applies only to M1a; original v1 evidence remains unchanged.
  Include piecewise trajectory segments in exclusion, not just their endpoints.
  If any relevant source enclosure is unresolved, outside-all-regions travel
  remains unknown. Union overlapping qualified negative intervals as before.
- Report every event as positive, negative or unknown; include all censored
  and unavailable denominators. Unknown events are not true positives.

Freeze the enclosure masks and all spatial interval labels before applying
runtime eligibility masks or importing the detector for calibration.

## Fresh 36-configuration grid and unchanged acceptance

| Parameter | Frozen M1a candidates after root lock |
| --- | --- |
| W (s) | 3, 6, 9 |
| epsilon (m) | 0.24, 0.30, 0.36, 0.48 |
| Maximum radius R (m) | 0.25, 0.50, 0.75 |

Keep the six non-overlapping time-weighted windows, five Euclidean centroid
differences, strict `S < epsilon`, confinement condition, gap/epoch semantics
and one-confirmation latch unchanged. No runtime default is selected or changed
by this amendment. Extend the existing analyzer/label owner with a versioned
contract; do not add a parallel labeling or calibration pipeline.

The prospective derivation gives W=6 sampled small-circle score <=0.272229375505
m and translating-circle score >=0.542629797669 m for the declared synthetic
family. At W=9 these bounds are <=0.320366053767 and >=0.834281855180 m.
They justify a finite new grid, not a claim that any configuration qualifies on
retained data. Report straight-drift resolution `epsilon/(5 W)` and the
18/36/54 s observation floors with any eventual selection.

Acceptance remains **all declared uncensored positive detections and zero
detections on declared negative intervals**, with synthetic and retained
counts reported separately. Do not waive either population or treat an empty
retained positive denominator as successful qualification. Among qualifying
configurations minimize median positive detection delay, then smaller R,
smaller epsilon, and shorter W, exactly as before. Preserve the historical
analyzer's `convergence_time` goal-event meaning.

If zero configurations qualify, retain a fresh scientific FAIL with no
selection. If geometry or input qualification cannot establish the required
population, report the unresolved evidence condition and do not claim detector
qualification. Neither outcome allows thresholds, regions, labels or
denominators to change within this version.

## Execution boundaries and durable outputs

Root must review and lock this plan, its machine-readable versioned contract
and acceptance ledger before executing fresh labels.
Implementation may then extend only existing owners, with focused numerical
and evidence-contract regressions and the existing bounded detector regressions.

The primary resource caps are **`timeout 600s` for geometry plus input/label
freeze**, and **`timeout 300s` for the complete fresh 36-grid calibration**.
They are resource limits, not promises that all geometry will qualify or finish
within them. Run the focused numerical/label tests under `timeout 180s`, and
context/checkpoint commands under `timeout 30s`. A timeout or evaluation cap
stops the current attempt and retains it as incomplete; no automatic retry,
budget extension, relaxed tolerance or population reduction is permitted.

Before the first geometry evaluation, save the locked contract and input/owner
hashes in the new attempt directory. Save each completed point's dual-integral
receipt and each completed source geometry incrementally through exclusive
atomic publication. Incomplete temporary files never count as complete
receipts. A separately recorded technical recovery may reuse verified completed
receipts only if their location, model/configuration, owner and full numerical
contract hashes match; it must not recompute them to seek a preferable result.
Recovery requires its own bounded command and retained attempt record. It
cannot change a scientific failure, geometry rule, grid or label definition.

Focused tests must distinguish a connected annular well from a flat field,
monotone/open region, competing disconnected wells and diagonal-only cell
contacts; reject boundary clipping, quadrature warnings/nonfinite values,
excessive dual-integration disagreement and an unresolved barrier; retain
annular holes and mixed cells as specified; and exercise segment crossings,
boundary touches, an internal shared edge, and negative-mask dilation. Test the
immutable synthetic hash and 8/13 split, pre-detector label publication,
exclusive artifact creation and timeout/partial-receipt handling. Use bounded
analytic fixtures for these checks; do not use old detector events as labels.

Proposed exclusive-create artifact namespaces below
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/` are `m1a_labels_v1/` and
`m1a_calibration_v1/`, with distinct logs. A preexisting path aborts publication.
The label manifest records this contract hash, owner/model/configuration hashes,
input/trace/synthetic hashes, all numerical receipts, explicit region geometry,
unknown reasons, temporal labels and the unchanged partition. Publish and hash
it before importing or invoking the detector calibration helper.

The calibration manifest records that frozen label hash, its explicit new grid,
the detector source hash, common masks, every per-case outcome, all denominators,
selection/tie calculations and proof limitations. Publish each completed grid
receipt incrementally. Timeout/interruption leaves a retained incomplete
attempt; it must not publish success from a partial grid.

This amendment authorizes no Gazebo run, hardware action, holdout calibration,
M2 implementation, source-cost model change, or runtime threshold selection.
Root records exact commands/results, reviews the complete diff, checkpoints M1a,
and decides whether its declared evidence criteria permit the next milestone.
