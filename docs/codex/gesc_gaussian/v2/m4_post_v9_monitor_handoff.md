# Post-V9 D2 monitor source handoff

D2 is SOURCE_VALIDATION_PASS, 2026-09-10 UTC, simulation only. Full V2 remains
IN_PROGRESS. Read the [plan](m4_post_v9_monitor_plan.md) and
[exact validation](validation/m4_post_v9_monitor.md).

The existing selected M4 monitor now retains first valid recovery evidence for
its temporal progression, while continuing full-history current validation.
Later missing/conflicting companions cannot regress the phase or pause/reset the
original Stage B deadline. New approach/closer/proximity acceptance requires
valid current evidence. Terminal live errors, or false current cardinality/stage
with a retained completion, fail classification even if final bag facts pass.
Existing extraction/completeness/cleanup failures keep priority. Nonselected
legacy behavior/result shape, the exact matcher and500ms ordering remain intact.

Only two functions in run_scenario.py changed. Runner SHA256
92aa2b07c5d66e00fd6af54b7c6fed850265411836f33e4b706119fddbc4789c;
focused test9194e8e3af51462872cbe515b38c3314bfcdf9f1c1c0b2c754a032e307a8d77f.
Both root review and independent review PASS. No source change follows the tests.

Root validation:57 focused PASS under180s and224 relevant PASS under240s,
281 unique current-source cases across4 modules. One existing Gazebo E2E was
explicitly deselected; no failures/errors/skips. Both jobs terminal/reaped.
All647 current source/plan pins and21 installed entry-point bindings remain
stable across jobs;644 of645 prior pins are unchanged. The281 count excludes
earlier baselines. Baselinev1 retains a blanket serialized-byte assertion problem;
corrected baselinev2 retained6 PASS/21 behavioral FAIL on unchanged old source.
Full canonical payload and event timestamp immutability checks replace the
unsupported comparison between separate serialization allocations.

External build: `/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_monitor_v1/`.
Aggregate source_validation_v1.json SHA256
0feb3a36cd69bd36ba0ce7b797b4d758f50ded6f24c967c06b6eda4d343bda78.
Exact commands, JUnit, logs, before/after sources, correction hold/patch and all
failed/passing versions remain retained. D1 and V9 archives remain unchanged.

Material checkpoint PASS0.220877727 s under30. The sole archive PASS0 completed
1.143492353 s under60, retaining428 repository files/35 artifact references and
1708498-byte verified tar. Manifest
`checkpoints/m4_post_v9_monitor_source_v1/manifest.json` SHA256
d5df2e6049b15ea99515426dfd17448f31260412ea161b5e55c7310c4f2ff814.
Exact checkpoint/archive execution receipts remain in the D2 build; this terminal
receipt postdates the immutable archive. No source changed afterward.

Next adopt the next concrete repair scope. Startup endpoint visibility/counts were proven insufficient as matching
proof; a bounded selected transient-local retention route is documented in
[startup design findings](validation/m4_post_v9_startup_design.md), with no source
or integration release yet. Daemon baseline visibility and labels throughput
remain independent blockers. The two local throughput corrections identified in
[V9 diagnoses](validation/m4_v9_development_diagnostics.md) still need source and
finite performance validation. No fresh16-run comparison is released.

Branch feature/gesc-gaussian-robustness-v2, HEAD3369cfc83a64ff5d8354827fd5310caaf0c8e945.
All task work is saved uncommitted. No commit/push/V1/Pi/physical action.
No research target or old run is promoted by this source pass.
