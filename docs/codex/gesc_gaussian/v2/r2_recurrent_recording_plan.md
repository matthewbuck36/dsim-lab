# R2 recurrent recording and evaluation integration

ADOPTED 2026-09-10 under the recurrent runtime plan. Extend existing recording,
validation and scenario-evaluation owners. Preserve historical wire layouts,
centroid formula checks and optional-topic behavior. Initial release is selected
rolling simulation only; stationary recurrent requests need their own compatible
adapter before a four-arm comparison and are rejected for now.

The existing manifest adds the optional simulation-only typed recurrent topic.
When recurrent_geometry_v3 is selected, require that exact topic/type, selected
algorithm pose, singleton publisher, complete diagnostic coverage and explicit
mode/source-gap/source-freshness metadata. Validate retained metadata against
resolved launch values; a descriptor from another mode cannot silently become
current. All fixed branch constants are owned by recurrent_contract.py, with
full diagnostic checks reused by the recorder and existing lifecycle join.

Reuse the existing diagnostic simulated-publication coverage function for the
new stream, with a descriptive keyword preserving its legacy default. Invalid
history status covers the interval but never counts as convergence. Compare
publication coverage against recorded /clock at readiness bounds, not wall
speed. Recurrent confirmation selection in the scenario evaluator must use
explicit matching diagnostic support through existing typed lifecycle evidence;
legacy six-centroid diagnostics remain separate.

Preserve scoped pre-edit files externally at development/20260910/
recurrent_recording_v1/. Focused tests cover correct and missing/wrong typed
routes, unselected defaults, incompatible stationary/physical selection,
retained-metadata mismatch, source/freshness bounds and simulation-clock
coverage including interior gaps. Run the relevant existing recording-selection
regressions once after the new interfaces are built. No Gazebo or bag read in
these source checks. Record exact finite command/log/JUnit and source pins.
