# R21 D02 validation and execution

The adopted plan is [D02](../r21_visible_d02_plan.md). Full goal remains open.
External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/visible_integrated_D_02/`.

Only analyzer production source changed among588 D01 pins. Old SHA256
`14d944ca5a2aa5ee405a003fd170927ef50764d91c1a217676809e33b3c11ad2`
is retained in source_correction/analyzer.before.py; new SHA256
`8b644d3b516c471f03c6697599cf8261ea3d6168fa14457b8084c05e776acb2c`.
The old default interval body remains exact AST parity. Explicit selected
simulation publication durations retain3/rate gap limits and both clock domains.
Generic analysis completeness remains unchanged.

Source session36428 terminal/reaped1,8.540867512outer/7.67pytest seconds:62passed,
1failed in63cases. The new legacy-parity fixture expectedunit s while unchanged
legacy is s by state. Original failure/testbytes retained; source unchanged.
Corrected single-case session76219 terminal/reaped0,1.676026208outer/.83pytest
seconds. The63-case selection is covered by62priorpasses plus1correctedcase.
Original command/pins:source_prepared.json and source_validation_v1.json;
correction:source_fixture_prepared.json and source_validation.json.
Current testSHAa0b7facb56ea6cf45eced208a035854bb51d4ce33c29982115c1cdfdcbf0ab2e.

Cached state session5336 terminal/reaped0,1.768348089outer/1.302828372helper
seconds;8checksPASS,604stable execution pins. No bag/nativeanalysis/motion/model
or reference call.2991selected records,2990source intervals, support2.5–151.9s,
149.4seconds, no boundary extrapolation. Original two bag-gap failures retained;
independent0.2s publication-gap control remainsinvalid. Prepared SHA256
`0c56c94f09ca0aab99f0e11926568987b758311d179f0bee99530f1b4011a120`;
commands/results in cached_state_prepared.json,cached_state_execution.json and
cached_state_component/. Independent cached review19checksPASS; receiptSHA256
`e8d215b64a1afd92f93a1cbdc45dfee45450ca2762560ce02354c84e69d66a13`.

Preparation session27638 terminal/reaped0,3.997549117outer/3.389780403helper
seconds. PASS607sourcepins/21entrypoints; expected noisy configSHA256
`578d11609f5d207c6981dc84ed22009de68d7f6980f908cd2742fc9d00e2ae9f`.
Prepared SHA256
`e3c3d67ab3821cd854a8fced7446a5978ef48909c8ec8251a69876146dcb3160`.
All source/input checks pass. Actual recorder argv excludes fixed simduration
and preserves600s wallbound,45s preflight,650+30runner and720root budgets.
Pre-dispatch procfs snapshot finds no selected runtime and no inspection errors.
No simulation has yet been dispatched at this source/preparation boundary.

D02 pre-visible material archive PASS:660 verified source members in1.474091725s;
manifest SHA256
`e4a6f4382fd447ed4387bf7d125f8b4f61718e486f4512e72f89b3c227043cac`
at `checkpoints/r21_d02_previsible_v1/`. Context/diff/checkpoint checks PASS.
This receipt postdates the immutable archive. The sole visible acquisition
session93267 is now RUNNING under the720-second inclusive root cap; exact
argv/start/prepared hash are retained in D02/execution_started.json. All607
prepared source/helper paths must remain unchanged until terminal analysis.
No other simulation or matrix is released.

## D02 terminal complete acquisition and active analysis

Session93267 terminal/reaped0,255.288028865outer/254.767491861helper seconds.
All607 sourcepins stable; both cleanup owners PASS. Native recording COMPLETE
with no failures/run_error and finalzero observed. All11primary predicates PASS.
State path SEARCH→VERIFY→DESIGN→ESCAPE_REPULSE→ESCAPE_ASSIST→SEARCH, one
committed fill and completed recovery. Live arrival197.18sim seconds,
0.499521337533m at(3.543455871,3.002372475); recorded exact pose join is pending
the sole analysis. Optional fixed simulationduration is absent as intended.
GOAL_HOLD not required. Exact outcome retained in acquisition_projection.json.

Analysis prepared617pins, SHA256
`8f814f69bef26d8b12e862aa45e1cff415e3c9eb2dbf336a921b770d4ed66321`;
sole session6585 RUNNING under120s inclusive, outputs analysis_v1/. Two native
scans only, new explicit simulation publication-duration basis, existing native
completeness/motion/arrival gates. No new reference or simulation yet.

## D02 terminal analysis and direction

Analysis session6585 terminal/reaped0:77.091955925outer/76.228665074helper seconds.
ANALYSIS_RETAINED, native analysis complete, lifecycle valid, no errors; all five
measurement-completeness checks PASS. Exactly two native scans12.813549083s and
12.504929950s, one captured BagData,617 outer and621 internal pins stable.
The explicit simulation_publication_v1 state-duration basis is selected.

Exact recorded_pose_arrival_v1 confirms197.18s from original Timekeeper origin0,
pose(3.543455870892421,3.0023724747006995), distance0.49952133753276723m;
no interpolation or GOAL_HOLD is required. Motion is
OBSERVED_CONTINUOUS_ACQUISITION,0 mandatory stops, complete command pairing and
authority. VERIFY90.2–102.6s has365 poses and0.367563944m path; DESIGN102.6–103.4s
has23 poses and0.006418m path. These are the measured acquisition segments.

Reference session29000 terminal/reaped0:7.450380546outer/6.913838008helper seconds.
REFERENCE_RETAINED; unchanged numerical gates PASS: median23.531230621 degrees,
P9039.475368039 degrees, averaging5/5 eligible informative targets. All five
paired targets improve, median paired improvement35.278736678 degrees. Preserve
all24 scheduled targets:6 observed and18 unexposed;5 fully eligible. Numerical
reference is the observed-phase stationary GESC response, not a universal spatial
gradient. Reference source/input pins626 stable.

Exact commands and before/after pins are retained in analysis_prepared_v1.json,
analysis_execution_v1.json,direction_reference_prepared_v1.json and
 direction_reference_execution_v1.json under the D02 root. Reference preparation
SHA256`bde98cfbd6c8ff6fe713b503310591b2cbed5279bcd2cdc3c5ff8ad559ded218`.
Both commands use the R21 runtime_environment.sh, clean initial PYTHONPATH/RMW,
single BLAS threads and explicit timeout:115+5s analysis,40+5s reference.
Outputs:analysis_v1/ and direction_reference_v1/. Independent cached review is
pending; no scientific rerun or new matrix has been dispatched.

## D02 independent review and R21 closure

Independent cached review COMPLETE/PASS34checks in1.828369s, with no bag read,
model/reference/analysis rerun. It verifies all11 acquisition predicates,
62 native checks, both strict cleanups, native analysis/lifecycle, exact arrival,
continuous acquisition and all24 fixed direction targets. All source/input pins
and current nonbag artifact hashes match. Target4 is observed but its original
blend_allowed=False/instantaneous output makes it ineligible; it stays reported.

Review:cached_complete_review_v1.json, SHA256
`10178d8a0aaf696f7a3ad6217249f31afdc87e0e6fb06af122e98980b9e43253`;
execution/hash receipt:cached_complete_review_receipt_v1.json. R21 development is
COMPLETE with one complete successful noisy integrated D02 case. D01 and earlier
failures remain retained. Full goal remains open; V13 is proposed, not released.

R21 D02 material closure:context/diff/checkpoint PASS. Archive
checkpoints/r21_d02_complete_v1/ has661 verified source members,1.813813077s;
manifest SHA256`3b184f33918c1ca3a7a0be60ecfed208cdba61f14c6e58395ca8c9becf797ec5`.
Command: `timeout --signal=INT --kill-after=5s 25s python3
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/save_d02_complete_checkpoint.py`. All scientific and
checkpoint sessions are terminal/reaped. This receipt postdates the archive.
V13 is now prospectively ADOPTED for source implementation/validation under
m4_v13_integrated_comparison_plan.md; preparation/dispatch await those gates.
