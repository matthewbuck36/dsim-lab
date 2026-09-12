# Stationary recurrent integrated development02

PROSPECTIVE, 2026-09-10, after the retained
[01 entry-point failure](validation/r4_stationary_integrated_01.md).
Use the same hypothesis, unchanged geometry/seed26091003/numerical settings,
success criterion, measurements, source gates and420s acquisition/120s analysis
budgets from [the01 plan](r4_stationary_integrated_01_plan.md). This is a changed
environment version, not an unchanged retry or a new calibration observation.

New case/run `v2_method_development_B_20260910_02`, exclusive external
`development/20260910/stationary_integrated_02/`. Preserve01 source, scripts,
environment, failures and missing-acquisition status. Retain the already built
new interfaces. Create a separate runtime environment sourcing the working
centered schema2/Q5 overlays and new interfaces without prepending the source
package root that shadows complete installed entry-point metadata. Do not edit
the repository's pre-existing egg-info or rebuild unrelated packages.

Before freeze, verify distribution entry points, canonical source resolution,
new generated request resolution, and actual installed `ros2 run ros_esc
run_scenario --help` and `record_run --help` under30s each. These commands must
exit successfully and start no ROS/Gazebo/motion. Then resolve the unchanged
single case with the existing schema/launch/recording owners, freeze exact
source/environment/scenario/helper inputs and use the existing visible wrapper
with domain201, strict owned cleanup and original finite budgets. No extra
algorithm tests or parameter tuning is needed for this environment-only fix.

Use a separately pinned copy of the prepared thin B analysis invocation, bound
to02's exact run/receipt and runtime environment. Execute once only after
terminal cleanup and COMPLETE recording; keep its two native scans and full
late hashes. All behavioral/measurement decisions remain those of01's plan.
No full comparison or confirmation release follows automatically.
