# M4 numerical reference scalar boundary correction

Status: ADOPTED, 2026-09-10, simulation only. This bounded addition to
[D3](m4_post_v9_analysis_plan.md) and the
[development amendment](method_development_20260910.md) addresses a failure
found by the new retained-development direction job. Historical V9 and the
failed development direction job remain unchanged.

The actual observed-phase numerical reference returns nested NumPy scalar
values. The existing atomic JSON writer rejects a NumPy boolean when publishing
the first target. Separately, M4 summary counters use `is True` and therefore
can exclude true NumPy flags before serialization. Changing only the final writer
would leave those denominators incorrect.

Extend `m4_pilot.evaluate_direction_targets` at the numerical-reference return
boundary: use the existing `gesc_gaussian_bag_analysis._q1_plain` conversion
before retaining/publishing each complete M4 row and before summary counting. Preserve numerical
values, reference/target selection, qualification conditions, tolerances, solver,
atomic writer, normal CLI routing and all later receipt checks. No numerical
solver or historical evidence edit is authorized by this correction.

Before source changes, retain a failing generated-fixture test using the actual
observed-phase numerical reference and a simple analytic angular objective.
Verify native boolean flags, informative/qualified summary denominators, complete
24-target JSON publication, and semantic equality to the numerical result. The
baseline is bounded to60 seconds. Then run the complete existing metrics and CLI
modules under120 seconds. The earlier D3 192-case pass remains a separate source
boundary; do not repeat the unrelated125-case campaign. All output/log/JUnit and
scoped pre/post source receipts belong under external
`builds/m4_post_v9_analysis_v1/`, with failed versions retained.

The independent direction job is held until this source change and focused
checks are terminal. It will bind the corrected current source using a fresh
pre-dispatch manifest; no old source contract is claimed to pass on changed
source. This correction establishes analysis operation, not either research goal.

The first focused correction normalized only the reference object. The actual
numerical fixture retained two failures because the cycle object also contains
NumPy booleans. Preserve that failed source/test version. The bounded correction
therefore normalizes the complete result row immediately before appending it,
calling `on_result`, and summarizing. This also leaves numerical input values and
the solver call path unchanged. Run the same two modules as a fresh focused
version under the original120-second cap; no budget or acceptance change.
