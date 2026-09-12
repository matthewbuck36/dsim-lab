# M4 v5 diagnostic export correction

Adopted 2026-09-10 UTC under the active full V2 goal and the user's authority
for recommended bounded corrections. This is a separate diagnostic version;
the first attempt in `m4_v5_moving_fill_diagnostic_plan.md` remains failed.

The one permitted original extraction opened the finalized C bag read-only,
then failed while exporting the first event: an invalid source timestamp is
NaN and strict JSON rejects it. It terminated exit 1 in 2.670308 seconds
(helper 2.236346 seconds). The partial `events_v1.json`, helper, command, log
and failed receipts are retained under external
`builds/m4_v5_moving_fill_v1/diagnostic/`. No event detail was recovered.
Post-failure hashing verifies all 11 original C run artifacts unchanged;
the pre-read audit verified all 618 source pins. No old outcome is changed.

This Level B export defect permits one separate corrected extraction under
`builds/m4_v5_moving_fill_v1/diagnostic_export_v2/`, using the same existing
`read_run_bag`, same eight allowed aliases including automatic readiness,
same 60-second extraction / 70-second outer ceiling and one-attempt limit.
This is not a retry of any experiment or a renewed scientific-analysis budget.
Preserve nonfinite floats as explicit tagged JSON values (`NaN`, `Infinity`,
`-Infinity`) together with their original validity fields. Do not silently
replace invalid numbers with valid zero or null. Verify this serialization
on a finite local fixture before reading; write output exclusively and verify
the original input/source hashes before and after, including on failure.

Retain complete events/state transitions and bounded typed transaction
descriptors only. No position labels, direction references, numerical model,
science reevaluation, ROS graph, Gazebo, bag repair or old-result edits.
Source and controls remain held until exact recorded diagnosis and the
subsequent implementation amendment. Preserve all earlier failed versions.
