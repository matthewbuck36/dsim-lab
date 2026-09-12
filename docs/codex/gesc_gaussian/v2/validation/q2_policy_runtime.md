# Q2 moving-cycle policy source validation

Status: SOURCE VALIDATION PASS under `../q2_policy_runtime_plan.md`. Runtime,
evidence routing, performance and held integrated checks are complete. Earlier
failed versions remain retained. Material closeout is recorded in the live status
and `../q2_policy_runtime_handoff.md`. No fresh scientific qualification,
old confirmation access or M4 release follows from these source checks.

The additive policy message and three selected packages built successfully
into `/home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/`.
The earlier installed overlay is preserved. From `ros2_ws`, after sourcing
ROS Humble and `builds/initial/install/local_setup.bash`, the command was:

```bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/log build --symlink-install --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/build_v1.log 2>&1
```

Build: three packages finished in 25.7 seconds, exit0. New tests source Humble
and the Q2 overlay, appending only `extremum-seeking/src` to PYTHONPATH.
Never prepend the ros_esc source package directory and select its stale tracked
egg-info. The existing message binaries and source acquisition schema remain
unchanged; only the policy companion is additive.

## Completed source checks

Core: **107 tests pass in 6.49 seconds**, including the old rolling tests and
new cached-coherence tests. The current SourceSynchronizer methods, crossing,
summarization and extracted legacy snapshot body match the D3 archive at AST
level. The immutable external norm oracle is used only on synthetic signals.
Core source hashes, exact commands, test log and parity receipt are documented
in external `core_validation.md` (SHA256
`c73dfbf5f51f068112eb293d06eb0f810b96470e5150e86556de2108246d002b`).
Core test log SHA256:
`8626d3deddf873ad2bc01124568f643c1f38dda21f5755daec65da964d087455`.

Adapter/CLI/actual Humble frontend: **79 tests pass in 11.45 seconds**, under
90s, using `test_q2_policy_adapter.py`, `test_v2_runtime.py` and
`test_q1_launch_frontend.py`. Both launch branches resolve old and new policies.
The new policy's state adapter rejects a weak instantaneous fallback outside
averaging states, while preserving a finite-zero instantaneous contribution
when an eligible meaningful mean can be used. Default policy behavior remains.
Log `adapter_v1.log`, SHA256
`4558c87ea93797ac6378dffe28bb884e240347fcb21c342bee09633cb265c40f`.

Independent contract checks: **30 pass in 0.92 seconds**, including fixed
policy metadata/environment, immutable old message layouts, old0.5/zero
behavior, selected0.75 body rotation, changing old cycle means and reset/stale
conditions. This preliminary log is under external
`builds/initial/q2_policy_contract_v1.log`.

## Single synthetic performance check

One predeclared 1000-update job passed under60s, without retry. Inputs use
34ms source steps, analytic harmonic world vectors, varying base yaw and
world phase `.137+2*pi*t/3+.02*sin(t)`. The two core source hashes are checked
before and after the job. The fixed maximum-update requirement is34ms.

Update p50/p99/maximum: **0.564767/0.87764121/0.950311 ms**. There are735
post-warmup qualified updates. Maximum new norm calls378 (cap2048), maximum
represented-window calls2625 (cap20000), maximum cached segments89.
This establishes synthetic execution headroom on this host, not a statistical
real-time guarantee or whole-node DDS latency.

External receipts under `builds/q2_policy_runtime_v1/`:

- `performance_1000.py`: `1e601dcc3d3652b197d061cc26773da8945333d2abdf6dd6c1f2abb9f5309bd2`.
- `performance_1000.log`: `4b550a1e6939c744be7350c5e4549700f90f9b07a2f49728a91a4278c4b3a7a1`.
- `performance_1000.json`: `c86ed741ae35124a190cad95bbc937d4eece2a2bedd3b2609b99a446362781c1`.

The exact invocation and raw timing/count samples are retained with the core
validation note.

## Transport and recording integration

Real filter/controller DDS: **2 pass in9.19s**, log
`builds/initial/q2_policy_transport_v4.log`, SHA256
`a64d36233c38aca1c82b80569972a2ed64cdd3d4f456057224f38c24e105e9ab`.
Both policies receive450 synthetic samples at approximately30Hz with100ms
held clock ticks. Checks cover exact companion joins, old0.5/new0.75 application,
new averaging despite changing old cycle means, moving VERIFY/DESIGN,
unchanged speed ceilings, objective reset, stale input and final zero.
Test-only failed versions1–3 remain retained: wrong enum name, an initial
binding-reset baseline assumption, and a prior output still in the DDS queue
when stale-output counting began. Runtime source did not change between them.

Recording/evidence: **156 pass in5.96s**, log
`builds/q2_policy_runtime_v1/recording_v2.log`, SHA256
`03e60618239e3346d22179808500bbe994ca6c529863ae001867e1d27911a5b8`.
Files: `test_q2_policy_recording.py`, `test_q1_direction_inputs.py`,
`test_v2_recording_contract.py`, `test_v2_source_contract.py`,
`test_v2_clock_admission.py`. Tests cover explicit policy metadata, conditional
companion requirements, exact first-publication joins, numerical bounds,
mandatory eligible blending, output algebra and preserved old strict gates.

The retained first recording run had106pass/1fail. A valid schema2 source
fixture had receipt9.99s, experiment origin10s, source10.25s and admission10.28s.
SourceSynchronizer accepts this queued input, but the old validator required
receipt>=origin. The narrow correction allows nonnegative pre-origin receipt
for model-input-time provenance while retaining source>=origin, admission
ordering and every source/pose/cost freshness bound. This is evidence-contract
parity, not a runtime freshness change. Failed log SHA256
`250b9a935452fb59d2cdf89b9d5e33f52ed3d31b6c12192ce906a9fc567d3747`.

Commands above source Humble then the isolated Q2 overlay, append only
`extremum-seeking/src` to PYTHONPATH, and use pytest with timeout120s.
Transport uses domains193/194 inside its fixture; recording uses domain187.
All test files are under `ros2_ws/src/ros_esc/test/`; retained paths above are
relative to `/home/mattb/Experiments/GESC-Gaussian/v2/`.

## First integrated run: retained failure

The37-file integrated run finished **956pass,3fail,10errors,3skips in133.94s**.
Exact argv is retained in `builds/q2_policy_runtime_v1/integrated_command.json`;
the exclusive wrapper `run_integrated_v2.py` invokes pytest with timeout180s
inside an outer190s cap, Q2 overlay and domain192. Full output is
`integrated_v1.log`. A preceding preparation script omitted an import and
produced an empty helper; invoking that empty file ran no pytest. It is
explicitly recorded in `integrated_preparation_v1.txt`, not counted as a pass.

One failure and ten setup errors are the old Q1 installed-entry-point tests
correctly rejecting the new Q2 prefix: their expected build is `builds/initial`.
The source helper is being generalized with an explicit expected-build argument;
the original default remains strict. Dedicated old/new environment tests must
validate both bindings. No active prefix may select its own expected identity.

Both moving-pipeline transport cases failed freshness checks during candidate
preparation. The fixture and five relevant lifecycle owners match their D3
archive hashes. A single bounded instrumented diagnosis is underway; neither
runtime freshness limits nor behavioral assertions have been relaxed.

Three skips require domains173 and176. The source-provenance case subsequently
passed in its required domain173: **1pass in0.63s**, timeout90s, retained
`source_transport_v1.log`. The two upstream cases require separate completion.
These failures/skips must be resolved with concrete evidence before source
closeout; they do not authorize a new scientific acquisition.

## Review corrections and resolved focused checks

The final recording review found three additional consistency gaps, corrected
without changing runtime. Incoming policy metadata inside `v2_identity` is
rejected; only the declared sibling descriptor can select policy interpretation.
The recorded `blend_allowed` flag must match the recorded valid SEARCH/VERIFY/
DESIGN state. A full current mean must end at its observation source time with
matching positive duration, one signed phase revolution and sample/sector counts;
covered means additionally satisfy30s/.5s/12x2 bounds. Full but uncovered windows
remain distinguishable. Integrity failures quarantine the run, preventing a
contradictory flag from silently removing an output from the analysis denominator.

Focused recording progression after these three code changes:
`recording_v3.log`162PASS6.77s, `recording_v4.log`167PASS7.12s, and final
`recording_v5.log`**173PASS7.17s**. Final log SHA256:
`8e88d9fe0a1a6ede61c695f447c782f565282e7cde08d8ef8d1c04b20e08295a`.
These are new adversarial consistency cases plus the same focused regressions.

The environment helper now accepts explicit `expected_build` in both binding
and release verification, retaining `builds/initial` as its default. New Q2
tests: **19PASS2.40s**, timeout90s, `environment_v1.log`, SHA256
`9568ba29de99c084d6a9a52e6290c870cd6334ec4d276e9acdc1a969af4a819d`.
Old Q1 environment tests: **23PASS2.65s**, timeout90s, domain191,
`old_environment_v2.log`, SHA256
`4f1854eac0ecf10b3fcc877518f4867fa9b37f44fbff7982b299812e6c391096`.
For that compatibility check only, source Humble, the initial overlay, then
`q2_policy_runtime_v1/install/ros_esc_interfaces/share/ros_esc_interfaces/package.bash`:
the old ros_esc metadata/wrappers remain selected while the current source can
import the additive interface. An initial command used a nonexistent package
setup path and exited before pytest/log creation; it is not a test outcome.

Separate-domain source tests resolved all three integrated skips:
`source_transport_v1.log`1PASS0.63s (domain173, timeout90s), SHA256
`1ab9905d8b0f34f6d791ff7da4efa2de0f7f3e282a078758cc0496cc0230c0f0`;
`upstream_transport_v1.log`2PASS8.15s (domain176, timeout120s), SHA256
`16d0c84a1d9316f1949784fc6aed6e704c342db58efd4945cb440d17deb53248`.
Three inherited analytic-fixture sqrt warnings are reported in the latter log.

The moving-pipeline timing diagnosis found the shared executor and source
producer were serially blocked by snapshot/command processing. Its one
instrumented run passed but measured original pose age489.048ms, leaving only
11ms inside the unchanged500ms limit. This diagnostic is not a substitute for
the integrated failures, whose exact failing ages were not recorded.
An executor-only correction still failed both cases. The corrected fixture
uses an independent finite40Hz source producer with the exact363-sample prefix
and continuing genuine source/clock/pose/readiness updates during preparation.
It preserves immutable evidence, real workers, registry/activation and pending-
worker departure assertions, original freshness limits and50s/120s caps.
Its first run had one pass and one final DDS observer race after actual escape;
the final correction waits for the exact published ESCAPE state and fill ID.

Final pipeline check: **2PASS21.84s**, `pipeline_scheduling_v3.log`, SHA256
`330b6079186188a6818c594aa212033f512f52b212347be72f5ccdd0c047dc10`.
Exact commands, all failures, diagnostic and four unchanged runtime hashes are
bound in `pipeline_timing_diagnostic_v1/scheduling_correction_receipt.json`,
SHA256 `05e97ea3548d4002d32c0dd14697f112bcf7b4e2af3398cccf1bca9b36f06111`.

The corrected35-file integrated run completed with every source owner held:
`run_integrated_v3.py`, `integrated_command_v2.json`, `integrated_v2.log`.
It selects Q2 environment tests and leaves the three required-domain cases
and original-build environment checks to the successful separate invocations
above. Bounds remained180s pytest/190s outer. Result: **981PASS/1FAIL in148.35s**,
one inherited analytic sqrt warning, no skips/errors. The sole remaining
failure is the moving-pipeline activation case: both registries had not reached
generation1 within its120-new-source-sample allowance. The pending-worker
departure case passed. This assertion did not log the state/worker/result
context, so its cause is not yet established. A bounded instrumented diagnosis
is pending; no runtime freshness, source gains or lifecycle deadline changed.
This failed integrated result remains retained and source closeout stays open.

The independent installed-binding receipt verifies21 exact Q2 console targets,
wrapper/metadata/module hashes and old/new generated interface bindings without
ROS initialization: `installed_binding_v1.json`, SHA256
`1d03c85df51c3fce5923d3f8d9d562566801807a8dd5ca2a41f99b1a2b878ec9`.
The D3-source comparison records14 changed owners and542 unchanged earlier
owners plus10 additive policy source/test receipts: `source_scope_v1.json`,
SHA256 `7d2eef25d077855e2fa6349beac4ce9b7f86066b58ec9502e14a7480fb6412af`.
Controller, lifecycle, acquisition identity and numerical reference owners are
unchanged. These receipts predate any further fixture correction; refresh them
explicitly if a covered source changes.

## Reproduced cancellation and source correction boundary

The single instrumented reproduction with the preceding lifecycle-contract
file returned20PASS/1FAIL in24.86s. It records Gaussian/composer generations0/0
and CANCELLED `epoch context changed`, before the167.499797ms worker completed.
The failing case's supervisor snapshot took395.645891ms and begin-preparation
193.983441ms, about589.6ms inside the same serialized timer callback. The
previously reported238.95ms preparation maximum belongs to the other case.
Readiness subscription and context publication share that callback group;
publishing context after this work can therefore observe the original readiness
receipt beyond its unchanged500ms limit. The exact invalid context bit was not
captured, so this final readiness explanation is a source-supported inference.
The cancellation itself and worker timing are directly recorded.

Receipt `pipeline_timing_diagnostic_v2/receipt.json`, SHA256
`20d0e6c924312bbfb8f37f4f3af253ba027eccdcb2132b172d656cde9144535f`,
binds original failure, exact120s diagnostic invocation, timing, log and unchanged
source hashes. No activation occurred; a separately noticed composer future-clock
admission race was not exercised and cannot explain this result.

`../q2_snapshot_serialization_plan.md` now authorizes a bounded correction to
the existing lifecycle/supervisor/Gaussian owners: one-pass identical canonical
hashing and detached generated-message cloning through CDR. Hash, publication
exclusion, malformed-Time rejection, nested storage separation and representable
string semantics must remain tested. No freshness or deadline changes.

Before source edits, the existing context/diff/checkpoint tools passed and an
immutable incomplete material archive was saved at
`checkpoints/q2_policy_runtime_before_serialization_v1/manifest.json`, SHA256
`9687649841f5e6d81d05803da9a621703396cd109c8cda70411c18e60646af68`:
247 files,1024768-byte verified archive,396 retained artifact hashes.
The later plan clarifications about embedded-NUL rejection and old malformed
observation-publication stamps postdate that archive; source had not changed.
This is a recoverable failure/correction boundary, not source milestone closure.

## Final integrated source validation

After the separately recorded structural-copy correction, the held40-file
suite passed **1167 tests in162.63s**, no failures/errors/skips and one inherited
analytic sqrt warning. `builds/q2_policy_runtime_v1/integrated_v3.log`, SHA256
`e3ddb2b8d41d1a90366ccfb9e31a636bf12c387da7983c4dd2eeee6b6abe1923`.
All426 source/test/script pins match before and after. Receipt
`integrated_receipt_v3.json`, SHA256
`0f6b70c83588e7d262b48decbb87978b35814b5255d64291c1667179f3aaaf56`,
binds exact argv/release, source pins and log. Invocation sources Humble then Q2
overlay, appends extremum-seeking/src, sets ROS_DOMAIN_ID192 and runs
`timeout 310s python3 .../builds/q2_policy_runtime_v1/run_integrated_v4.py`;
that exclusive wrapper retains the exact40-file `timeout 300s python3 -m pytest
-q` argv and writes `integrated_v3.log`. Dedicated-domain3 and original-overlay23
checks remain separately passed as recorded above; no skip is treated as pass.

The original1000-update direction-core performance job remains unchanged and
closed PASS. Snapshot copy v1 failed2x and stays failed; fresh structural v2
passes4.582815x, selected maximum46.180069ms. Actual lifecycle+pipeline DDS
passes21 tests with entire supervisor callback<=79.667692ms; exact context
publication/receipt joins stay valid. Canonical hashes, mutable detachment,
freshness and deadlines are preserved. Complete commands and artifact hashes
are in `q2_snapshot_serialization.md`.

Refreshed installed binding verifies21 console targets and6 generated message
bindings plus the three copy owners: `installed_binding_v2.json`, SHA256
`9d446ac6ab68f810a6db0157b206039f058d418fc34703f212cb1d0be4158868`.
Source scope `source_scope_v2.json`, SHA256
`d2c33c9be762308b641b96ac95bd69f0d62c320819c517b5f90384e73de89fd8`,
records17 changed D3 owners,539 unchanged and12 additive files. These source
checks qualify implementation only. Fresh detector/neighborhood and actual
direction science, Arm B adapter, the retained composer clock-ordering question,
and the unchanged M4 pilot remain separate outstanding work.
