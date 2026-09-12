# M4 prerequisite audit and prospective definitions

Status: READ-ONLY AUDIT COMPLETE; recommendations below are a draft for the
parent M4 amendment, not an executable release. Prepared 2026-09-09 from live
AGENTS, fresh-chat handoff, plan/status, M4/M4A plans and source. No model,
label/reference job, build, ROS graph, bag acquisition or hardware was run.
The user has selected Q7 two-block comparison; source validation is in progress.

## Required before the first case

The unresolved contracts are explicit in `../m4_plan.md:197-222`. Q7 resolves
the method choice only. Finish these independent pieces prospectively:

1. Independent labels and first-opportunity/censoring/latency denominator.
2. Direction targets, informative eligibility, paired methods, availability,
   jitter, relative lag and fallback-duration definitions.
3. Exact disturbed secondary topology receipts and their limited meaning.
4. New M4 augmented-objective input adapter, preserving Q1/Q2 restrictions.
5. Exact 16-slot resource, finite dispatcher/analysis budgets, integrity gates,
   and one development-to-holdout release/freeze receipt.

The original >=30% basin-entry latency target, angular targets, no mandatory
stopped acquisition and complete D-arm holdout sequence remain unchanged.
No criterion is satisfied by renaming missing evidence.

## Recommended label and latency contract

Retain the independently modeled finite-grid basin-region definition and its
annular holes/exclusions. Reuse verified geometry only when its exact selected
model/source/geometry/numerical-owner bindings match. A fresh geometry requires
its own prospective receipt and bounded job; it cannot reuse an old result hash
after changing inputs. The relevant owner is
`ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`:
`label_v2_basin_intervals` at line3147 and immutable segment helper at line3133;
the enclosure implementation is adjacent `v2_enclosure.py`. These are
operational finite-grid model regions, not a proof of attraction dynamics.

Keep positive residence >=12 source seconds and the existing negative
definition: a continuous six-second segment outside all qualified exclusions,
net displacement >=0.12m and net/path >=0.80, source gaps <=0.5s. Unknown geometry,
holes, incomplete timing and boundary ambiguity remain unknown. Freeze geometry
and position-only labels before reading detector outputs. SEARCH/readiness and
input validity are a separate eligibility mask, as in Q1; do not use candidate,
verification, fill or goal success to create a positive label.

Recommended primary population: first labeled local-basin opportunity after
ready/SEARCH admission in each run, with first opportunity retained even when
short, censored or unconfirmed. Report later episodes separately. Reset/clock
ambiguity, recording end, leaving the region and an objective-changing
intervention bound an observation; never stitch separated opportunities. Entry
latency is source-time first confirmation minus independently labeled entry.
Entry preceding eligible SEARCH has a separately reported left-censor flag.

Important feasibility boundary: requiring continued SEARCH after an earlier
confirmation would censor the successful faster detector because its own action
ends SEARCH. Freeze spatial residence independently of state, then admit the
confirmation only if all required pre-confirmation input/state guards hold.
If confirmation occurs before the independent12s sustained-residence criterion
can be established and an intervention ends that observation, mark the original
basin-entry endpoint censored/ambiguous. Do not use post-fill residence to
retroactively certify the unmodified objective or substitute confinement.

Recommended conservative primary comparison: six predeclared holdout pairs,
B versus A and D versus C for each of the three conditions, with development
reported separately. Publish every pair's first opportunity, confirmation or
censor bound. Compare equally weighted medians over the six enabled and six
control values only if all12 first endpoints are independently eligible and
observed. Otherwise report the complete-case descriptive statistic with its
explicit subset denominator, and original30% target EVIDENCE_UNAVAILABLE;
do not claim acceptance from a selected confirmed subset. Report per-condition
pairs and separate B/A and D/C summaries even when pooling is available.

This is deliberately conservative for a small pilot. If a more informative
censored-data estimand is wanted, define and validate it before looking at new
outcomes. A positional-confinement statistic may be added as a clearly separate
diagnostic; replacing basin-entry acceptance with it changes the original claim.

## Recommended direction and exposure contract

Freeze24 symbolic targets per C/D run at readiness source origin plus
15+30*k seconds, k=0..23:192 slots across eight C/D runs,48 development and144
holdout. This covers the declared recording horizon without copying Q1/Q2's
125s/48-slot study. Slots beyond actual exposure or after a graceful terminal
stop remain explicitly missing/terminated, with no replacement. Select the
first input in [target,target+0.05s], independently of confidence/error/nominee.

Reuse `v2_direction_reference.select_causal_anchor` (line255),
`observed_phase_cycle` and `observed_phase_reference` (line555), with the exact
existing source/context/gap/readiness/complete-cycle/sector/informative numerical
guards. Its reference is the fixed-position periodic response under the recorded
phase waveform and frozen objective; it is neither a spatial gradient nor a
prediction of delayed moving dynamics. Keep the existing25000 distinct-angle
cap and numerical tolerances; no recalculation with looser settings.

Compare actual C/D selected output and its aligned instantaneous output on the
same target/trajectory/reference. This matches existing analyzer line6208-6213.
A/B trajectory outcomes remain matched experimental controls, but their
stationary filter does not create this moving typed observation stream
(`filter_node/filter_node_script.py:126`). Do not change their filter solely to
fill direction columns. A separately declared inherited-filter replay can use
`v2_direction_reference.replay_custom_filter` (line676), explicitly labeled
matched-input replay with its shared initialization limitations.

Eligibility denominator: all scheduled targets with complete input-only,
readiness/state and informative-reference qualification. Weak/invalid output,
failed rolling confidence or fallback stays in that denominator as unavailable
averaging. Angular percentiles use finite nonzero outputs and report their own
count; paired improvements use only targets where both methods yield an angle,
with missing pairs enumerated. Report scheduled, exposed, input-qualified,
reference-qualified, informative, usable-output and usable-averaging counts.
Report C/D separately per condition and pooled with equal slot weighting.

For whole-run fallback duration, integrate the actual selected policy state over
consecutive same-context source intervals <=0.5s while moving-search use is
eligible. Separate unknown gaps, natural command reversals, safety/final stops
and mandatory stopped acquisition. This duration is separate from the sampled
informative-target availability percentage.

Recommended secondary diagnostics: on a fixed0.1s source grid within complete
same-objective/reset contexts, report one-second circular-heading dispersion
as operational jitter, acknowledging that intentional turns contribute. For
relative filter lag, compare recorded rolling and aligned instantaneous headings
over predeclared nonoverlapping30s windows with at least90% grid support,
instantaneous circular excursion >=10degrees and candidate lags0..6s in0.1s
steps. Minimize mean squared wrapped angle on the common30s support trimmed6s
at both ends; ties select smallest lag. Report insufficient excitation/ambiguous
windows. This is relative smoothing lag, not ground-truth response delay.
Also report publication/source transport delay separately; it cannot substitute
for directional lag. No target outcome is selected using these diagnostics.

## Objective adapter and disturbed topology owners

`gesc_gaussian_bag_analysis._prepare_policy_direction_inputs` (line5009) shares
typed identity/source/clock extraction, but line5089 rejects nonempty fills or
affine terms. Preserve this behavior in old Q1/Q2 entrypoints. Add a distinct
M4 route binding recorded objective digest/revision/weights, full Gaussian
registry and affine law at each exact composition stamp; malformed/missing
snapshots remain unavailable or integrity failures, never fabricated zero terms.

`modified_cost_node/v2_objective.py:28-56` serializes fill center/covariance/
amplitude and affine b0/t0/decay/expiry controls. Match the exact active vector
at composition time using existing composer semantics
(`modified_cost_script.py:922-968`). The numerical
`v2_direction_reference.augmented_objective` (line63) already accepts Gaussian
terms and effective decayed affine vectors. Verify reconstructed channel costs
and hashes against the actual receipt. Preserve post-fill targets and bias/
selected-sensor semantics; no raw-only reference substitution.

`scenario_runner/scenario_schema.py:3555` delegates exact `verified_trap`
validation to `aggregate_field_truth.validate_two_source_topology_qualification`
(line1386), which recomputes `derive_two_source_topology_qualification` (line1135).
Generate separately bound secondary nominal/noise/delay receipts using the
unchanged owner and exact disturbances. Its `_noise_margin` (line1636) uses
3*Gaussian standard deviation,0.045 cost units here. That is a three-sigma
static score margin, not a deterministic Gaussian bound. Delay fields enter
the disturbance hash but not dynamic topology calculations. Keep the limited
static-model claim and evaluate actual delayed input/reference completeness
from recordings. Do not describe these receipts as delayed-motion qualification.

## Recommended finite execution and release contract

Freeze exact16 slots, arm matching, source/installed resources, runtime JSON,
IDL and chosen Q7 parameters. Use an exclusive new external root and unique
run IDs. A one-case existing `run_scenario` CLI is the plain child of M4A;
existing recorder/analyzer/scenario owners retain their behavior. Verify exact
child summary/run directory, inner recorder session, final zero, typed
integrity and cleanup. An exit1 with complete safe behavioral failure remains
an outcome; missing/inconsistent integrity aborts later dispatch.

Suggested per-case envelope: case_end=min(start+900,suite_end), reserve30s for
the wrapper's separately bounded cleanup/receipt checks, and pass case_end-30s
to M4A, which already reserves60s for cancellation. The recorder720s remains a
maximum. If a complete shorter exposure ends at a valid terminal condition,
retain it; if deadline interrupts before complete finalization, abort. Never
import Q1's125 simulated seconds or promise720 source seconds.

`run_scenario.cleanup_evidence` (line554) calls `ros_graph_nodes` (line506),
which currently returns an empty set on inspection errors and can enter native
ROS teardown. Calling it without an outer finite process does not prove the
cleanup reserve. A selected strict/bounded use must expose inspection failure;
preserve old helper defaults. `session_processes` already has a5s subprocess
timeout. Use actual inner and outer session receipts; an empty outer SID alone
does not establish nested recorder cleanup.

Before the suite starts, a recommended one-time preparation cap is600s for any
new required topology/enclosure receipt computation; partial/failed work stays
retained, with no retry under the same version. Do not execute this draft job.
For the pilot itself, conservatively retain the single15300s inclusive ceiling:
16*900s case maxima plus at most900s total scientific/release work. A prospective
allocation is four30s label jobs (one block each), eight75s reference jobs (one
C/D run each), four30s block summaries, and60s total freeze/report receipt work.
Every job gets min(its cap, remaining absolute suite time); no renewed deadline.
These are resource caps, not feasibility evidence. Bag extraction already inside
each run remains inside that case. If focused source tests or actual work show
this finite analysis allocation is inadequate, preserve timeout evidence and
report unavailable metrics; do not launch extra runs or silently extend the suite.

Recommended one-time development release: all four exact acquisitions have
complete safe recording/cleanup and unchanged source/configuration; attempted
development analysis has a complete outcome ledger including unavailable/failed
metrics; no unresolved Level A issue or source correction requiring retest.
Freeze reviewed bytes/results and all twelve unstarted slots once. Scientific
targets can honestly fail or be unavailable in development without erasing the
outcome or automatically disqualifying a frozen pilot. If further source work is
needed, stop at that boundary; four extra development slots are not authorized.
Reserve remaining declared case and scientific work before starting any slot.

## Authority and feasibility limits

No additional user choice is inherently required for these bounded prospective
implementation definitions under the approved objective. The parent must adopt
one coherent contract and validate its implementation before dispatch. A Level A
choice is required only if proceeding would replace the original basin-entry
claim with confinement, waive error/availability gates, change the population,
objective/sign/ownership, or exceed physical authorization. An empty or censored
primary denominator is permitted evidence unavailability, not authority to make
such a replacement. This audit establishes owners and unresolved contracts;
it does not certify that the finite pilot will produce usable scientific targets.
