# Q2 dated-directory correction validation

Status: SOURCE/BUILD/BINDING PASS; material preflight freeze under
`../q2_acquisition_path_correction_plan.md`. Q2 v1 is CLOSED_INCOMPLETE at
closure672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02
and checkpoint670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44.
The fresh31-series acquisition subsequently completed4/4 accepted inputs.
Its scientific result is EVIDENCE_UNAVAILABLE for detector qualification;
see `q2_qualification_v2_result.md` for the completed diagnostic and seals.

The analyzer now admits the existing recorder's dated directory through the
existing unique exact-run lookup. It checks reserved run/partition identity,
canonical ISO-date bucket, resolved root and exact directory before input reads.
The new finite q2-primary-shadow-v2 identity uses31–34 with unchanged science,
policy, runtime and numerical owners. Original Q2 v1/default and Q1 routes stay.
V2 binds the original incomplete closure and source checkpoint. Label, setting,
job, target and trace versions must match their selected contract exactly.

## Completed checks

Logs below are under external `builds/q2_policy_runtime_v1/`.

- Legacy input/reference/D1/D2 and policy recording:210PASS54.18s, timeout120s,
  `q2_dated_layout_old_routes_v1.log`, SHA256
  `9e6b01abefcbc12c7ab8ea81043b6f537e90911164366b91afae448a31d718bc`.
  Exact selection: test_q1_direction_inputs.py, test_q1_direction_references.py,
  test_q1_discovery_direction_diagnostic.py, test_q1_observed_phase_diagnostic.py,
  test_q2_policy_recording.py. Synthetic regressions, no old science rerun.
- Both Q2 versions and inherited study routing:92PASS4.12s, timeout90s,
  `q2_corrected_study_focused_v1.log`, SHA256
  `74c48e2cf1041174fded4a1349192ab792fdf3bea8363cb14e50bd2942dfca35`.
  Exact selection: test_q2_study.py test_q1_study.py. Six scientific label
  functions remain AST-identical. Source held throughout this focused run.
- Acquisition identities/configuration/nonuse and inherited routing:99PASS,
  3deselected4.02s, timeout90s, `q2_corrected_acquisition_focused_v1.log`, SHA256
  `db20ad7311e6409e86132eb2cba905bca432e3f98b2a4b2beb9d8727f899b52e`.
  Selection: test_q2_acquisition.py test_q1_recovery_paths.py, excluding
  freeze_assembly_keeps_geometry_and_acquisition_recovery_distinct. Those three
  strict-original-build cases passed separately in1.72s using initial ros_esc
  plus Q2 interfaces: `q2_corrected_acquisition_old_environment_v1.log`, SHA256
  `d9c689ef1f80e4d52f782d21ebcd9e88c243432db233678e56116999b0e3bd22`.
  All102 selected cases covered; source held and no failures in either run.
- Independent path/version/contract checks:122PASS35.35s, timeout120s/domain187,
  `q2_path_contract_v1.log`, SHA256
  `dcc2ecf7163783733c57e80de4003317ccdb076d9a44aae0f5eb2abed3ecb665`.
  Selection: test_q2_qualification_contract.py test_q2_recorded_layout.py.
  The inherited actual recorder.run fixture created date buckets on both sides
  of UTC midnight, for both Q2 versions, which the actual lookup and analyzer
  admitted.26 invalid-path/identity cases rejected before every input hash/YAML/
  bag read. Both48/sealed24 branches and strict cross-version/closure checks
  pass. No runtime process/node or real bag/reference calculation was started.
  Final test hashes50dedaea2714d0e68a4c9f90c22445070e6fb985ddcf78fce1ddd5a9d7fad7c6
  and aac605123b278ebdbebf8935f5cec9e5df9e0a157e93f5575a7da613409d3884;
  analyzer unchanged throughout. No failures in this correction's focused runs.

Commands source Humble then the external Q2 overlay and append only
`/home/mattb/dsim-lab/extremum-seeking/src` to PYTHONPATH. Analyzer held SHA256
`018f64fc1ab5191e95d0a2c0b14daf2d6c6b9c9fa69351e625f28e051d8cca03`;
q1_study SHA256 `b95ad1752909ee9ec1ecca55ce389d3be03a69ed92b2429f6a4c48dbcaa66ced`;
evaluate_q1 SHA256 `4b74d0e43fd4f2fe6b52b2d5da94be17aebaddfa45e8cb52173f61604ea22a90`.

Independent bounded source review PASS:
`q2_corrected_source_review_v1.json`, SHA256
`4a6dbec7260113cbfa3aaed7f1d6d0e6561868d9914b7c0172709eb90360c26c`.
The actual recorder and existing lookup align with the new admission. Numerical
per-anchor loop and entire summary/acceptance tail are AST-identical; six label
functions and seven runtime/numerical/recorder/lookup owners are unchanged.
The review performed no model, bag or confirmation input reads.

## Resource build and binding

Rebuilt only ros_esc under timeout180s with --symlink-install and the existing
external Q2 build/install bases; log root qualification_build_log_v3.
PASS1.80s, `qualification_build_v3.log`, SHA256
`f557eef1b189e39e4c50120b749089bb12026bbd56e698d5beacf1670555c194`.
The Q2v2 scenario is now installed through the existing setup.py resource list.
Binding audit under45s/domain191 passed21 console targets, generated interfaces,
copy owners and exact source/installed v2 YAML bytes without ROS initialization.
`qualification_installed_binding_v2.json`, SHA256
`8035879e89afa9361f41301093a208a1f550f1f833cb7f2bd5dce605fb22a728`.

## Material freeze

Checkpoint `checkpoints/q2_path_correction_preflight_v1/manifest.json`, SHA256
`dd58bf51154efdfbfeff2240770c2c66a92abfde512882d6a3917d1685d4582d`:
263files,1092156-byte verified archive,109retained hashes. Context/diff/checkpoint
PASS. Existing freezer under60s with --acquisition-version q2-primary-shadow-v2
saved the exclusive contract at `qualification/q2_primary_shadow_v2/preflight/contract.json`,
SHA256 `f3e31a16b6008e11ae953813f0188e52a451e275a653fb865d88d50922704fa6`:
573 source receipts,2869 geometry receipts,4 cases and48 symbolic slots.
Current source/geometry/installed/environment/display checks PASS. Final frozen
case audit and explicit release receipt precede the single acquisition. No
scientific gate or M4 release follows from source tests alone.
