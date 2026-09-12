# M4v10 workflow source boundary

SOURCE_VALIDATED, 2026-09-10 under the
[adopted comparison plan](../m4_v10_arrival_comparison_plan.md), including its
prospective 40 s freeze/report reserve amendment. No preparation, acquisition,
bag read, numerical job, commit or push was performed for this source boundary.

The existing `m4_workflow.py` now binds V10's distinct method/release selector,
primary topology and matched gain, 240 s labels and shared 40 s freeze/report,
1400 s total science/15800 s suite budgets. Historical versions keep their existing
contract outputs and timeout-release behavior. Existing Q5 installed console
entry-point resolution remains authoritative; a separate read-only binding
checks the selected stationary recurrent interface overlay and generated new
request/diagnostic/guidance layouts. V10 source collection includes the adopted
plans, runtime script/source chain, installed wrappers/metadata, and generated
Python/native interface files.

The new release policy requires four complete selected analysis products,
completed labels/two references/summary jobs, exact required check names,
all 24 C/D targets through the existing direction-product checker, immutable
nested receipts and late source/input checks. It compares summary fields with
their retained per-run analysis and actual acquisition outcomes. At least B or D
must establish local recovery through arrival; D must provide observed continuous
acquisition with complete authority and command pairing. Complete baseline
failures, censored latency and unexposed targets remain valid results.

Finalization retains all sixteen slots even when development release fails.
V10 reports arrival separately from controller GOAL_REACHED, completed scientific
blocks separately from behavioral outcomes, and fresh confirmation on previously
exposed conditions. Original failed ledgers and historical reporting remain.
`m4_science_job.py` is unchanged.

Before-sources are retained externally at
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_workflow_source_v1/`.
The context validator passed and both changed/new Python files passed AST parsing.
At the initial implementation boundary, tests were pending while the other
owners completed shared source. The coordinated validation below closes that
pending source boundary.

Prepared focused tests in `ros2_ws/src/ros_esc/test/test_m4_v10_workflow.py` use the
real preparation/schema/release/finalizer owners with synthetic finite job
receipts. They cover versioned preparation, runtime/policy binding, failed and
censored baselines, unexposed references, timeouts, changed nested products,
invented completion checks, arrival claims inconsistent with actual outcomes,
late input changes, already-started confirmation and sixteen-slot failed-release
reporting. No test creates a ROS graph, bag or field model.

The root ran the coordinated bundle through the verified
`stationary_recurrent_pairing_v1/runtime_environment_v2.sh`, with
`env -u PYTHONPATH`, a 230 s pytest cap plus 5 s termination allowance and 260 s
inclusive wrapper cap. Before/after collection used
`collect_sources('m4-pilot-v10')` and actual installed entry-point equality.
The retained receipts contain the exact commands, selectors, logs and JUnit
paths. All paths in the following table are relative to
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/`.

| Receipt | Retained outcome | Elapsed wall time |
| --- | --- | --- |
| `focused_v1/source_validation.json` | 607 passed, 1 fixture failure; source and installed bindings stable | 131.639977 s |
| `focused_v2/source_validation.json` | 32 passed in the corrected version-test module; source and installed bindings stable | 9.894771 s |
| `source_validation_combined.json` | 608 unique passing cases; production and installed bindings unchanged between jobs | 141.534748 s combined |
| `retained_motion_v1/receipt.json` | PASS on cached original D02 exports; original artifact hashes verified, 764 pins stable | 4.244722 s |
| `cli_v1/receipt.json` | All 5 actual help commands passed; 756 pins and 21 installed entry points stable | 5.850403 s |

The first failure, `test_retained_v9_scenario_bytes_remain_exact`, is preserved
in `focused_v1/pytest.log` and its original receipt. The fixture had supplied
sorted-JSON topology mappings where the original V9 byte comparison required
the insertion order of its retained YAML input. Only
`test_m4_v10_versions.py` changed for the repair; production did not change.
`detector_v9_fixture_correction_v1.json` records the diagnosis. The combined
result takes the union of case identities, so the 32 passing rerun cases are not
added to 607 as new cases. Its SHA256 is
`3de8cde1884801d566102b9d1c33da1159417b36afdf3a9027a03ea11cf23109`.
The bundle includes the new V10 workflow tests, existing V9 workflow/budget
coverage and the base workflow regressions.

The cached motion check exercised the actual V10 motion owner on the original
D02 typed exports and odometry CSV. It found two continuous acquisition
segments, complete command pairing and authority, and zero mandatory stopped
acquisitions, while retaining the observed zero publications. It consumed the
prior valid native lifecycle result without revalidating that lifecycle or
decoding a bag. The five CLI commands were installed `run_scenario --help` and
`record_run --help`, plus native `m4_workflow.py prepare --help`, `run_m4.py
--help` and `evaluate_m4.py --help`; no node or acquisition was dispatched.

The independent retained-data compatibility review also checked these exact
existing products without decoding bags:

- B02 `stationary_integrated_02/attempt_result.json` records the arrival sample
  at bag stamp 1789073827215258002 and distance 0.4992701632296781 m. Its live
  evaluator time 172.634 s joins exactly one native
  `analysis_v1/analyzer/tables/odometry.csv` row with ROS stamp 172634000000,
  identical position and `in_readiness_interval=True`. These representations
  match the new arrival owner; native controller-goal timing may remain
  not applicable.
- `c_analysis_profile_v1/labels.json` has the expected dictionary
  `pose_faults={}` and native boolean `readiness_eligible` flags: 10537 of 10608
  poses are eligible, with integer monotone eligible stamps and successive
  gaps at most 0.5 s. Those retained representations match the scientific
  completeness and path-length checks.
- Both `visible_integrated_02/direction_reference_v1/result.json` and the
  corresponding `visible_integrated_03` product contain the exact ordered 24
  reference targets with consistent identities and native boolean qualification,
  eligibility and usability flags. D02 has 6 observed/18 unexposed targets;
  D03 has 5 observed/19 unexposed. These shapes match
  `direction_product_complete`, including valid unexposed outcomes.

These checks validate the source contract and compatibility with retained
development products. They do not turn those earlier runs into V10 evidence.
V10 frozen preparation, four-arm acquisition, usable development science and
the actual release decision remain separate prospective boundaries. No source
or test changed during this final documentation update.
