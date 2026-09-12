# Prospective M4v6 matched gain comparison

Status: ADOPTED FOR SIMULATION IMPLEMENTATION, 2026-09-10 UTC, after
centroid heartbeat source closure and material archive. The active user goal
explicitly authorizes recommended algorithm corrections. This selects one
fresh matched configuration and its existing-owner source routes; preparation
and acquisition still require the gates below. M4v1-v5 and completed V6
diagnostics retain their exact outcomes and evidence.

Prerequisite: [heartbeat handoff](m4_v6_centroid_heartbeat_handoff.md).
Its final corrected source passed215 checks with625 stable pins. Material
checkpoint/archive PASS: `checkpoints/m4_v6_centroid_heartbeat_source_v1/manifest.json`
SHA256 `0ad0ce175057d6ec5e732246f021295757e12285849c2b76f92fb528897c69a3`
(379 files,65 external references,1484811-byte verified archive).
The external draft remains unchanged at SHA256
`92531597520aaf8653d753e9e4c3492693a81e5020d659be4f9adea55779f798`.

## Concrete change and evidence limits

Select one new simulation controller JSON for all sixteen fresh M4v6 slots:
`k_vx=0.5`, `k_wz=5.0`, `set_max_vx=0.1 m/s`, `set_max_wz=0.5 rad/s`.
Change only the translation gain from the retained JSON. Keep its object/module,
wheel radius 0.033 m, wheel distance 0.158 m and wheel speed 70 RPM unchanged.
Select `centroid_invalid_status_heartbeat_enabled=True` for all B/D slots;
leave that override absent for A/C. Keep centroid W=6 s, epsilon=0.18 m,
maximum radius=0.5 m, two-block formula, dwell and M3 0.75/0.15 m, sector,
information and twelve-second guards unchanged. No VERIFY centering assist,
new control policy, candidate/field-truth control input or shared-ceiling change.

The unchanged controller forms vx=k_vx*qx and wz=k_wz*qy before saturation.
Halving k_vx reduces translation for the same unsaturated direction input; when
both old/new translation commands saturate at 0.1 m/s it has no effect. This is
a prospective configuration hypothesis, not an inferred B orbit parameter or a
claim that B/D will confirm, that C/D will produce a qualified fill, or that
these changes establish either original research objective. The completed B
plot did not estimate period or basin residence. The conditional C/D diagnostic
identified spatial representativeness and separate information failures;
changing motion does not guarantee either disappears.

Retaining the shared ceiling protects existing escape capacity: controller
final saturation also applies to the supervisor-owned assist. Selected escape
has one 35 s deadline across REPULSE/ASSIST and a 1 s exit hold; lowering the
shared ceiling to 0.05 would leave at most 1.70 m ideal pre-hold travel, while
allowed exit radii can reach 2.7*1.25=3.375 m. Gain-only preserves the assist's
0.1 m/s ceiling, although slower ordinary REPULSE/search can still consume more
time. Keep the 3 s/0.05 m progress condition, disabled RECENTER, all fixed
Stage A/post-Stage-A limits and every integrity/behavior gate unchanged.

## Verified current route and smallest implementation

Repository paths below are relative to `/home/mattb/dsim-lab`.

* The actual V5 JSON is
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json`.
  SHA256: `3f255699385cc16d830fd79f560d91f1206321606b763be2971bdbc9bf6912a1`.
  The frozen V5 contract, all sixteen resolved slots, four actual launch argv
  and four metadata parameter-file lists bind this route. The four small
  metadata/resolved-parameter files match their closure audit. Controller gains
  are JSON values; the ROS parameter snapshot independently shows use_sim_time
  true and does not expose those gains as ROS parameters.
* `scenario_runner/run_scenario.py:97` declares GESC_CONTROLLER;
  `build_launch_command` inserts it at line228 then applies ordinary overrides
  at line297. `build_metadata` independently inserts the constant at line431.
  `gazebo.launch.xml:1134` passes the selected controller_config_filepath to the
  existing controller executable. The launch's bare HBESC default is not the
  selected M4 configuration.
* Prefer enabling the existing `controller_config_filepath` override through
  `scenario_runner/scenario_schema.py:LAUNCH_OVERRIDES` (currently absent), with
  a nonempty string/path check. Reuse one small general path resolver in the
  existing runner for both launch construction and metadata parameter_files;
  absent override returns the exact old GESC_CONTROLLER value. Expand tilde and
  canonicalize the selected path consistently; reject malformed/non-file paths
  before dispatch. Preserve argument-list launch construction and all unrelated
  metadata fields. This does not require a launch argument, new CLI, node,
  controller class, schema-version change or suite-specific controller switch.
* Add a new JSON beside the original, suggested basename
  `gesc_controller_full_rotation_voltage_m4_v6_gain_half.json`. Preserve the old
  file byte-for-byte. If the new file is exactly the old bytes with its single
  `"k_vx": 1.0` token replaced by `"k_vx": 0.5`, its prospective SHA256 is
  `e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606`.
  These are the exact adopted bytes; create them only in the new JSON.
* In existing m4_scenario.py, select the canonical absolute new JSON path in
  the V6 frozen_profile launch_overrides, shared across all arms and blocks.
  Use a new profile_id, e.g. m4_gain_half_control_v6. The existing frozen-profile
  overlap prohibition prevents a case from overriding this common selection.
  Add the B/D heartbeat choice at the existing per-arm override location.
  Keep V1-V5 generated profile IDs, overrides and outputs exactly unchanged.

A private runner selector keyed to suite_id would also be small, but would hide
the changed configuration outside the normal scenario override. Prefer the
existing override and common resolution route, with exact V6 binding below.

## Exact V6 identity and frozen bindings

Extend the existing explicit identity allowlists only to `m4-pilot-v6`, root
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v6`, suite_id
`m4_pilot_v6`, case prefix `m4_v6_`, and run IDs
`m4-pilot-v6-slotNN-ARM-SEED`. Keep method_version `m4-pilot-v1` (the unchanged
analysis method), process ownership `subreaper_group_v3` and its declared
initial-root-group graceful strategy and full kernel proof unchanged. There
is no process-owner implementation change. Reject cross-version roots, slots,
receipts, summaries, analysis rows and releases through existing owners.

Preserve V5's all-arm interior_anchor_fallback=True/minimum_displacement=0.50 m,
primary verified_trap topology receipt and three independent secondary topology
receipts. Add V6 to those explicit selections without changing V1-V5 output.
Keep the unchanged numerical/topology/label/reference owners and geometry chains.

Existing freeze fields already retain source_files, scenario path/hash, each
run's resolved_scenario (including frozen_profile/algorithm overrides),
launch_argv, runner_argv, expected_cost_configuration, topology_receipts and
geometry_contexts. For V6 add one explicit controller_configuration receipt
(path, sha256, profile_id) and require all the following at preparation and
verify_frozen/dispatch validation:

1. The configuration path is the one prospective V6 JSON; bytes match the
   approved hash and differ from the retained original only at gains.k_vx.
   The original JSON remains pinned and unchanged. Do not accept merely a new
   arbitrary hash without checking the selected values and original owner.
2. All sixteen resolved frozen profiles and launch argv select that same file;
   each selected parameter_files list resolves to it. Metadata must not retain
   the old constant while launch uses the new override.
3. Every B/D override is exactly heartbeat=True; every A/C override is absent
   or False. B/D recording descriptors must carry the selected heartbeat binding
   through the already validated recorder helper; no legacy descriptor rewrite.
4. collect_sources contains both JSON files and all changed owner/test files,
   plus the adopted comparison amendment and centroid heartbeat plan. The
   source collector's existing repository traversal includes a new JSON under
   ros2_ws/src; add the adopted document names to its explicit plan list.
5. Frozen audit and holdout release bind the changed profile, controller receipt,
   current final source-validation receipt, installed entrypoints/wrapper,
   scenario, all run argv, original cost/geometry controls and unchanged budgets.
   Do not describe the V6 profile as wholly inherited: list exactly the common
   translation-gain change and B/D reporting selection.

Use the current existing m4_scenario, m4_workflow, run_m4, m4_pilot and
 evaluate_m4 owners for version admission and proof. Only update a consumer if
its explicit version guard requires it; do not duplicate the pipeline. Retain
method identity, all192 target rows and all original denominator rules.

## Source acceptance and one prospective execution

Before source edits, retain old sources, V1-V5 generated scenario/metadata/argv
fixtures and helper templates externally. Meaningful focused fixtures should
show absent override exact parity; explicit malformed path rejection; identical
selected launch/metadata path; exact new JSON single-value delta; all16 V6
profile/heartbeat/identity bindings; rejection of missing, wrong-byte and
cross-arm paths; continued strict old coverage failure and enabled-heartbeat
coverage behavior; and unchanged controller saturation/assist authority.
Preserve historical unsupported-version tests by changing only the future
negative token if necessary after retaining the original. The bounded source commands below precede preparation; use existing regressions
and actual entrypoint/source binding checks, not a new test framework.

After independent source review and recorded source closure, prepare once under
the existing 600 s preparation cap, producing four fresh receipts for the same declared topology conditions through
the existing numerical owner, then perform the bounded frozen audit and archive.
Use a newly reserved simulation ROS domain selected before preparation; do not
reuse an active test domain. Root must bind the exact new environment and
current stable source receipt in the release. No acquisition may start before those prerequisites pass.

Run exactly the fixed sixteen slots: development primary nominal A/B/C/D seed
26090801; holdout secondary nominal seed26090802, noise seed26090803, and delay
seed26090804, each A/B/C/D. Preserve noise0.015, delays0.10 s, maps, source
strengths, starts, all remaining gains and ceilings, and all budgets: 720 s
recording, 900 s/case, 45 s shutdown grace, 30 s cleanup reserve, 15300 s suite;
900 s aggregate science with block labels120 s, C/D references45 s/slot,
summary10 s/block, freeze/report20 s. Preserve maximum_observations40000,
24 targets at15+30k s for each C/D slot, 192 total, and the original six holdout
pairs/30 percent goal and same-trajectory direction goals. Development science
must be attempted and recorded after four safe complete runs; freeze twelve
unstarted holdouts before their release. Scientific failure/unavailability is
retained separately from integrity failure. No replacements, tuning after
freeze, deadline extensions, reinterpretation of a failed version or guarantees
of success. The next milestone is the fresh comparison and honest complete
report under those prerequisites.


## Implementation ownership and finite source gates

Work on this milestone only after preserving the closed heartbeat source.
Before edits, save exact affected owner/test copies under a fresh external
`builds/m4_v6_matched_gain_v1/` directory; retain every prior version unchanged.

- Controller selection owner: new JSON, scenario schema allowlist/validation,
  one common runner resolver used by launch and metadata, and focused selection
  tests. Normalize after ordinary override merging so a raw relative/tilde path
  cannot overwrite the canonical launch path. Preserve absent-override bytes.
- Version/contract owner: m4_scenario, exact V6 all16 profile/configuration/
  heartbeat bindings and narrow version tests. Extend existing runner version
  admission with its owner. Add no other version consumer unless its actual
  guard requires a change. Use the existing configuration contract helper for
  both preparation and frozen verification rather than duplicating constants.
- Root workflow owner: m4_workflow source-plan pins, V6 topology preparation
  route and exact controller-configuration receipt in preparation/verification.
  Existing dispatch, analysis, release and all numerical methods stay unchanged
  except explicit version admission where required.

Finish edits and independently review before running a source-hash-pinned
bundle. One focused selected-controller/V6 contract bundle has a180-second
inclusive cap; one relevant legacy M4 scenario/workflow/selection regression
bundle has a240-second cap. Root's final integrated source gate has a520-second
inclusive cap and must verify current installed entrypoint bindings and the
complete current collect_sources hash map. Save exact argv/test selection before
each execution; reuse the existing wrapper/pytest owners. These are maxima,
not required durations or permission for duplicate passing runs. Retain failures
and tested versions; any changed-source correction uses a new exclusive receipt.
Focused or broad tests are not field derivation/preparation/acquisition.

After source closure/checkpoint/archive, allow one600-second preparation, one
30-second read-only frozen audit, then material preparation archive and exact
development dispatch release. No retries or slot substitutions. The same
single dispatcher owns all16 reserved slots; its existing development science,
freeze and one-time holdout release are unchanged. A complete behavioral failure
remains an outcome; integrity failure closes this version without replacement.

Both original research goals remain open. This amendment adopts an engineering
hypothesis and a controlled comparison, not a promised performance improvement.
