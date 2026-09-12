# Discovery direction diagnostic preflight — 2026-09-09 UTC

Source implementation and focused verification PASS; the diagnostic numerical
job has not run at this boundary. This is an explicit24-target development
route, with no qualification/nomination/confirmation/M4 authority. The original
48-target Q1 route still requires both partitions and passing nomination.

Only the existing bag analyzer changed among549 original source receipts:
old SHA256 `072c239e6ba6041f2a0b753ec1e422fa9fbc400759f895413e276de32ac6a1c6`,
new `738d9a02e0f35d9a0dfacfe7a617a5a459c489d84c2657b7dd032d21e24e9e45`.
Three new receipts bind the diagnostic plan, workflow and dedicated tests,
giving552 current sources and2869 unchanged geometry receipts. Every original
source path remains bound; only the analyzer transition is permitted. Runtime,
numerical model/filter/reference, launch/configuration and IDL remain unchanged.

Independent source review compares the new numerical target loop to the closed
archive: AST-identical except for the added pre-model receipt recheck. Summary
calculations are byte-identical; extracted original contract checks are
AST-identical. The pre-model recheck propagates integrity errors immediately,
outside the numerical-unavailability handler. Exact24 discovery trace/target
metadata is checked before following trace paths, and all three new source
receipts are mandatory. Review SHA256:
`d2f87396697f5e260d7a8beac41f91207a12a8d99d89ddb7c8ae5430c4d001bd`.

## Tests and exact commands

Original numerical/reference regressions:78 PASS16.68s, no skips. Exact command
and source-owner evidence are in `q1_discovery_direction_owner.md`.
Independent diagnostic tests: initial37 PASS18.31s, then40 PASS21.60s after
adding checkpoint-artifact and in-job receipt-mutation cases. No failed
attempts occurred. Test file SHA256:
`5501ba37cc6f53d0d65c0e682571dbe31de539fdcce6e8298cdc9881eed6b334`.
Its exact final command was:

```bash
env -u PYTHONPATH bash -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash && export PYTHONPATH=/home/mattb/dsim-lab/extremum-seeking/src:$PYTHONPATH && export ROS_DOMAIN_ID=192 && timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_discovery_direction_diagnostic.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_discovery_direction_diagnostic_v2.log 2>&1'
```

Final combined verification:223 PASS40.74s, no warnings/skips, exit0:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=192 timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_discovery_direction_diagnostic.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py ros2_ws/src/ros_esc/test/test_v2_direction_reference.py ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_study.py ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_discovery_direction_integrated_v1.log 2>&1
```

The tests cover original48/default and nomination gates; exact24/no confirmation
reads; analytic, weak-output, fallback and uninformative numerical parity;
altered source/lineage/input/timing/population rejection before model/output;
timeout/exclusive partial receipts; and receipt changes before the second model
or after the final anchor preventing a false final result. No empirical bag was
evaluated by tests.

| Log under `builds/initial/` | SHA256 |
| --- | --- |
|`q1_discovery_direction_owner_v1.log`|`820f38545eed9ca6712059cdf82453ef079a2ca2b8d194cac1b5f0be369a2c1c`|
|`q1_discovery_direction_diagnostic_v2.log`|`601ec393ab51a83ea89b26cfe7f99ea6d7f0cdaaa24079b042fc529d975bbd6a`|
|`q1_discovery_direction_integrated_v1.log`|`ef0e00fd25f4a564ad1617ac5b2147bd5c6a84dcda46b01519d2cdac6d0f7b8b`|

## Frozen actual preflight

From the same sourced overlay, the freeze command exited0 under90s:

```bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py freeze > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_discovery_direction_freeze_v1.log 2>&1
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 30s python3 /tmp/dsim_q1_discovery_direction_inputs.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_discovery_direction_input_preflight_v1.log 2>&1
```

The second command calls the strict diagnostic verifier and the unchanged
`_q1_verify_run` on both actual discovery run rows using the explicitly verified
effective contract. Both normal recorded-input bindings PASS. It performs no
field calculation. The script is retained beside its preflight output; original
source snapshot was extracted from the verified closed archive without changing
historical files. Actual installed metadata resolves all21 console targets;
the isolated symlink overlay uses the current analyzer. No packaging/IDL/asset
changed, so no redundant colcon build was run.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_discovery_direction_diagnostic_v1/`.

| Relative receipt | SHA256 |
| --- | --- |
|`preflight/contract.json`|`2957ddfedf24b6c41df87f781df9e02958a5514291edac76b5d4b2179923fcd7`|
|`preflight/installed_preflight.json`|`b49abb3ae6018d4cc192eb58ca2f3c85b3c7f34f2ffb1af4fac96b2fbbfc1a38`|
|`preflight/input_binding_preflight.json`|`e677355a8693d73f93b6b313563ac6505acbdd39beac3a678f99d70f587876e1`|

Context validation and diff checks pass. The source/evidence checkpoint and
separate exact environment/validation dispatch receipt are the final release
boundary. Only one externally bounded300s numerical invocation is permitted.
Preserve every missing/weak/unavailable target and partial output on failure;
the result cannot qualify Q1 or M4. Confirmation stays sealed.
