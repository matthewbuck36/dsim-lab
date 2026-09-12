# R21 D01: retained diagnostic analysis of the arrival-successful incomplete run

ADOPTED prospectively after D01 acquisition terminated, before any new bag
analysis. Preserve the fixed D01 scenario, metadata, source pins, helpers and
formal incomplete recording verdict. No replacement simulation is released.

D01 observed the complete SEARCH→VERIFY→DESIGN→ESCAPE→SEARCH sequence, one
committed fill, owned recovery and global arrival. The live evaluator records
151.897s and0.499035717m. Both cleanup owners passed, source pins stayed stable,
and every primary predicate except recording completeness passed. Native source
and lifecycle validation passed. The sole failed native check is
clean_shutdown_metadata: the explicitly selected600s simulation-duration setting
requires a complete fixed recording window, conflicting with the intended early
stop on arrival. That configuration mistake is not a behavioral nonarrival.

Obtain direction and timing measurements from this retained acquisition through
the existing analyzer, validator, motion metric, corrected recorded-pose arrival
join and direction-reference owners. Create a separate diagnostic helper under
`visible_integrated_D_01/analysis_diagnostic/`; do not edit the frozen helper or
alter a recorded file to make completeness pass. The original analysis was
withheld because its complete-recording prerequisite is already known to fail.

Before execution, freeze the helper and exact command/output destinations. Require
the original complete recovery/global-arrival receipts, matching run identity,
both cleanups and source stability. The diagnostic admission exception is limited
to the recorded fixed-duration interruption and exactly one failed native check,
clean_shutdown_metadata. Re-run the existing native validator as planned and
require all other checks, including typed source/lifecycle, coverage and final
zero, to pass. If any further native failure appears, withhold qualified direction
claims and retain the explicit error. Keep the run formally incomplete in every
new receipt; individual supported measurements have their own availability.

Allow one analyzer BagData read and its native validator's second read, within
110s work/115s INT+5s kill (120s inclusive). Reuse that BagData for supplementary
exports, exact verification/fill/certificate/event decisions, observed continuous
motion and the explicit recorded_pose_arrival_v1 join. No third read, alternate
data selection, new source model or changed scientific threshold. Preserve D,
noise, development identity and all24 scheduled direction targets at15+30k seconds.

After successfully retaining qualified normalized inputs, allow one unchanged
reference-owner execution,38s work/40s INT+5s kill (45s inclusive). Retain median
andP90 error, instantaneous comparison and every eligibility/availability count.
Existing thresholds remain30degrees median,60degreesP90 and0.8 availability
among eligible informative targets; zero eligible targets cannot pass. This is a
separate diagnostic analysis, not retrospective D01 or V12 qualification.

Keep exact source/input hashes, all native verdicts, commands, elapsed times,
failures and output paths. A cached independent review follows numerical output;
no rerun is permitted solely to recover context. Future acquisition configuration
must resolve the duration/arrival conflict prospectively in a separately named
version. The full research goal remains open; no matrix or physical work is
released by this plan.
