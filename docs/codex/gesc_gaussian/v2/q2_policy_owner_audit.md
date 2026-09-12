# Q2 selectable moving-cycle policy owner audit

Read-only source audit, 2026-09-09. No source/test changes, simulations, bag
reads, new weight/coherence/reference calculations, or confirmation access.
The root reports D3 COMPLETE and a development nomination of mean weight0.75;
this audit does not independently recalculate that outcome. The existing556
frozen owners remain unchanged until the parent closes the current milestone
and saves the next amendment.

## Smallest coherent public selection

Add a separate `v2_direction_policy` launch/scenario setting with default
`three_cycle_v1` (a new explicit name for the existing policy) and opt-in
`moving_cycle_coherence_v1`. Keep `continuous_search_mode=rolling_gesc_v2`,
algorithm profile `robust_gaussian_v1`, selected full-rotation filter JSON,
source schema2/model_input_time, and all detector choices independent.
The new policy is simulation-only. Map its fixed parameters internally to
mean weight0.75, coherence lower-bound threshold0.25, absolute mean/output
floor1e-6, three completed covered cycles and existing12×2 coverage. Do not
add a weight or threshold tuning surface. Unknown/nonrolling/physical policy
combinations must fail before runtime startup. Omitted policy preserves the
old0.5/30degree/3sigma behavior and all stationary modes.

Relevant current owners (all paths below are relative to
`/home/mattb/dsim-lab/`):

- `ros2_ws/src/ros_esc/ros_esc/filter_node/rolling_gesc.py:589`:
  `RollingGescConfig` currently defaults blend_weight0.5; numeric bounds and
  twelve-sector/three-cycle configuration validation live here.
- `ros2_ws/src/ros_esc/ros_esc/filter_node/v2_runtime.py:45`: adapter startup
  validates robust/simulation/stream identity and exact selected filter JSON,
  then creates `RollingGesc()` with defaults at line64. Inject the selected
  policy's validated config here. SourceSynchronizer and filter matrices need
  no numerical change.
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py:423`: add the
  explicit CLI selector alongside the existing rolling-mode arguments.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml:232,1048`:
  default the new argument and pass it only to the existing filter executable.
  Preserve actual Humble substitution-token quoting, time settings and graph.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py:109,564`:
  whitelist/validate the selector in the existing override owner, after frozen
  profile merge. `run_scenario.py:291,332` already derives argv and metadata
  from those overrides; record an explicit validated policy identity in the
  selected V2 metadata. Old metadata lacking it means the old policy.

The source stream descriptor in `ros_esc/v2_stream.py:21,34,108` currently has
exact schema1/2 key sets. Policy is not a source acquisition property. Avoid
forcing a schema3 change through encoder/sensor/composer/relay solely to carry
this filter choice. A separately validated filter-policy identity/config hash
in metadata and the policy diagnostic can bind it while source identity stays
unchanged. Parent should freeze the exact names/hash payload in Q2.

## Pure rolling arithmetic and output semantics

`rolling_gesc.py:855` (`_snapshot`) owns rolling mean/current coverage and the
old three-cycle confidence. Preserve its existing branch and old diagnostics.
The new branch retains three *covered* completed-cycle summaries as warmup,
but does not require their means to satisfy the inter-cycle angle or3sigma
conditions. Retain those statistics as explicitly named old-policy controls;
do not relabel them as current-cycle coherence.

The new denominator integrates the norm of the same represented q(t) used by
`_summarize`, including exact clipped boundary interpolation. The current
`_crossing` at line816 and `_summarize` at line831 already supply the source
support and duration-normalized trapezoidal numerator. Preserve their signed
phase, sample counts, full original gap checks, maximum30s cycle, and bounded
20000-point history. Cache completed segment norm integrals/errors as samples
arrive; recompute only the clipped boundary segment and aggregate retained
support. Do not transplant the external evaluator's whole-history scan and
repeated quadrature into every live output timer. A stable analytic primitive
or bounded cached quadrature needs independent comparison to the now-frozen
external evaluator on synthetic signals. Freeze error/roundoff accounting and
coherence lower-bound admission before runtime validation. No latency allowance
or source freshness relaxation follows from this implementation.

`invalidate` at line697 clears all cycle/phase history; clear the norm cache
there too. Preserve stream/objective revision resets, gaps, reversals, capacity,
clock rollback, original source/receipt ages and current-pose freshness.
`evaluate` at line920 currently blends and rotates into the latest admitted
body frame. New policy needs a distinct weak-mixture fallback: use the fresh
meaningful instantaneous vector if the selected mixture is nonfinite or
norm<=1e-6; if neither is meaningful, return invalid output with a reason.
The legacy branch retains its existing behavior.

Parent-approved prospective edge clarification: a fresh **finite zero**
instantaneous vector may still participate in an informative qualified mean
mixture. Only fallback requires an instantaneous norm>1e-6. Preserve the
existing property tested at `test/test_rolling_gesc.py:433`
(`test_zero_instantaneous_value_does_not_suppress_mean`). D3's finite anchor
harness conservatively required a meaningful instant for any gated output;
all24 D3 anchors were meaningful, so this runtime clarification does not change
or rerun D3. It must be explicit in Q2 and tested across zero crossings.

## Preserve recorded-wire compatibility

`ros2_ws/src/ros_esc_interfaces/msg/GescDirectionDiagnostics.msg` has no policy
identity/coherence fields. `plotting_scripts/bag_reader.py:191–197` obtains the
currently installed message class and deserializes retained CDR with it.
Appending fields to this existing IDL risks making retained bags unreadable.
Preserve its binary layout and the layouts of its nested observation/objective
messages.

Recommended additive evidence: one new typed policy companion published by the
same existing filter node, keyed by run/stream identity, diagnostic sequence,
reset sequence, observation/source identity and source/publication stamps.
It should carry the explicit policy/config hash, nominal selected weight,
coherence numerator/denominator/error/bounds/threshold, current-cycle coverage,
three-cycle warmup validity, selected mean qualification and fallback reason.
Declare exact joins to the existing direction diagnostic; missing, conflicting
or wrong-policy companions invalidate selected-policy evidence. This adds no
node or control owner. Add the new IDL through the existing interfaces CMake
list and document its semantics; build only the isolated overlay.

Parent must freeze one interpretation of the existing `qualified` flag for new
runs. A coherent choice is selected-policy qualification, with `cycles_valid`
remaining the old three-cycle-control result and the companion explicitly
identifying the selected gate. Old runs keep their exact former interpretation.
Never globally weaken `qualified -> cycles_valid` or broaden allowed weights
without recorded policy dispatch. `v2_runtime.py:516–550` is the existing
single publication owner for these fields and the companion.

## Recorder, validator and analyzer integration

- `experiment_recording/record_run.py:593,637` validates explicit V2 metadata
  and promotes selected evidence topics. Add policy validation and companion
  promotion only for moving-policy runs. The current topic manifest's
  direction entry is at `topic_manifest.yaml:69`; a companion entry must stay
  optional/minimum0 for old runs. Bind actual selected argv and singleton
  publisher/type; do not globally add a legacy startup requirement.
- `experiment_recording/validate_run.py:474–535` currently requires stable
  cycles/30degrees/3sigma whenever qualified and accepts blend weights only0
  or0.5. Split those *policy-specific* assertions by validated metadata plus
  the exact companion. Preserve common source/provenance/bracket/receipt/frame
  and output recomposition checks. New policy allows actual weight0 or0.75,
  validates coverage/warmup/coherence/error bounds and weak-mixture fallback;
  reject false coherence claims and missing/conflicting companion joins.
- `plotting_scripts/gesc_gaussian_bag_analysis.py:4825` currently defines
  applied averaging as `blend_weight == .5`; `prepare_q1_direction_inputs` at
 4851 preserves first diagnostic outputs. New-policy analysis must explicitly
  resolve the policy and join its companion before counting0.75 averaging.
  Leave old `_q1_method`, D1/D2 selectors, frozen references and default48
  contracts unchanged. Extend the existing analysis owner through a named
  new-policy route/helper; no alternative bag/model/replay pipeline.
- `bag_reader.py:144` already supports alias filtering. Use it for the new
  optional companion. Old bags without that topic remain readable and subject
  to old policy rules; new selected runs missing it fail completeness.

## Controller and M3 compatibility

`controller_node/controller_node_script.py:139,214,323` consumes the existing
stamped numeric filter output, not a direction confidence message. New weight
changes command magnitude as well as direction; preserve controller gain,
speed ceilings, saturation, source-time admission, watchdog, state arbitration
and final zero. No controller source change is inherently required.

`supervisor_node/v2_supervisor.py:303–340` consumes the immutable synchronized
raw observation and first filter-state metadata; it does not gate candidate
raw cycles on direction qualification. Preserve that contract and registry
acknowledgments, including moving VERIFY/DESIGN and objective resets. Do not
make the new direction policy an extra source-truth/M3 candidate gate. The
companion must not alter nested observation hashes or first-publication identity.

## Bounded implementation divisions and validation

1. **Pure core owner:** selector/config, cached segment norm/coherence, selected
   qualification and new fallback, existing rolling unit tests plus synthetic
   oracle comparisons. Test constant/changing collinear vectors, opposite-zero
   crossing, curved segment, signed rotation/dwell/clipping, coordinate/time
   scaling, warmup, source/reset/frame/objective faults, numerical/error/capacity
   bounds, tiny/zero signals, DC/reset transients and coherent interference.
   These are implementation properties, not noise/source qualification.
2. **Adapter/interface/config owner:** CLI and launch routing, additive typed
   companion/config identity, actual output-frame recomposition and policy
   metadata. Keep acquisition and physical paths unchanged. Actual Humble
   frontend tests must cover empty legacy/default and opt-in selector.
3. **Evidence owner:** scenario validation, recorder conditional topic/binding,
   policy-specific validator and existing analyzer normalization. Test old
   absent-policy records with strict0.5/three-cycle gates; selected0.75 records
   with correct companion; wrong/missing policy, source, sequence, units,
   denominator/error/coverage claims; actual old-wire serialized decoding.
4. **Independent transport/checks:** extend existing finite real-node fixture
   `test/test_v2_direction_transport.py:46` or a dedicated companion test using
   real CustomFilter+ModifiedCost and synthetic source/provenance support.
   Verify both policies, current source/current-pose stamps, qualified0.75 after
   three covered cycles despite changing inter-cycle means, opposite-vector
   fallback, zero-instant continuity, objective reset/warmup, VERIFY/DESIGN
   movement, stale source/state/pose no valid output, coarse-clock future
   admission and expiry recovery. Preserve prior0.5 assertions in old-policy
   fixture. Use explicit120s maximum, isolated domain, no Gazebo for this step.
   Controller transport should prove unchanged limits/arbitration/final zero
   with the new numeric output; reuse M3/clock-admission fixtures.

After component/DDS tests, this remains unqualified runtime implementation.
Fresh prospectively reserved simulation development/confirmation and the
separate detector/neighborhood gates require the next declared evidence plan.
Do not open old confirmation or release the16-run four-arm pilot from D3.
