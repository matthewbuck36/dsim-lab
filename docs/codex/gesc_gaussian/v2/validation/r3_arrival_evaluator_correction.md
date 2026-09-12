# R3 arrival evaluator correction: source validation

SOURCE_VALIDATION_PASS, 2026-09-10, under
[the prospective plan](../r3_arrival_evaluator_correction_plan.md). No bag read
or simulation was dispatched. Attempt02 and all previous outcomes remain intact.
Parent owns the next separately versioned scenario, checkpoint and dispatch.

The recurrent-only private event adapter now uses the confirmed `history_end`
support coordinate minus the immutable observed Timekeeper origin. Its audit
retains `diagnostic_source_stamp_ns`, `diagnostic_history_end_ns`,
`diagnostic_publication_stamp_ns`, `evaluator_source_stamp_ns` and the explicit
`evaluator_coordinate=confirmed_history_end`. Existing centroid timestamp
semantics and output shape remain unchanged. Public messages, exact typed
identity/geometry/run/epoch joins, causal freshness and origin guards remain.

`success.criterion: post_recovery_arrival_v1` explicitly selects the development
arrival contract. Schema validation restricts it to schema14+, the named
simulation development suite and partition, and robust counted two-source case.
It binds existing local direct/assisted recovery paths ending in SEARCH and the
0.5 m evaluator-only global boundary. Recording, cleanup, full local recovery,
fill cardinality, applicable command ownership and forbidden-event/state guards
remain. Live and offline owners use the same ranked-goal prerequisite selector.
An actual ranked-goal observation remains separately reportable; its absence
cannot veto selected post-recovery arrival. Omission preserves old requirements.

The exact scenario mutation is exercised by
`test_r3_arrival_evaluator.py:selected_document`: remove `controller_goal` and
`expected_terminal_state` from case and full-lifecycle scope predicates, omit
the declared terminal state, end the existing required recovery paths in SEARCH,
and require local CONVERGENCE_CONFIRMED/FILL_CREATED/ESCAPE_STARTED events only.
Keep `ground_truth_goal`, local recovery, ownership and all other existing gates.
Scenario expansion and metadata preserve the selector; launch arguments and
algorithm configuration are identical to the corresponding old criterion.

## Tests and receipts

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/arrival_evaluator_correction_v1/`.
Exact shell commands are saved in `commands.json`; each test command used
`env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1`, sourced the existing
`centered_runtime_v2/environment.sh`, then `timeout 90s python3 -m pytest -q`.

- `focused_v1.log`:20 PASS/1 fixture FAIL,12.99 s. The launch-comparison test
  omitted the already required shared `run_id`; production checks passed.
  Preserve this failure. Both comparison calls were corrected to supply the
  same explicit run ID, matching the actual runtime owner contract.
- `focused_v2.log`:286 PASS/1 SKIP,41.26 s. Files: new
  `test_r3_arrival_evaluator.py`, existing `test_m4_monitor_progression.py`,
  `test_m4_centroid_event_evaluation.py`, and `test_scenario_runner.py`.
  The21 new cases cover schema/metadata roundtrip, incompatible/unknown/default
  selectors, missing fill/ownership predicates, radius/path/goal contradictions,
  actual generated recurrent support/input timestamps with nonzero origin,
  private staged-fill join, immutable public payloads, existing live callbacks
  and actual offline owner with a finite generated-wire reader fixture.
  Arrival before recovery or with conflicting/missing current evidence fails;
  omitted selection still requires the ranked event. The sole skip is inherited
  `test_recorded_short_headless_end_to_end`, which requires the explicit
  `RUN_GESC_PHASE06_GAZEBO_E2E=1` opt-in and is outside this source-only task.
- `validate_phase_context.sh v2 plan` and `v2 implement`:PASS.
  `git diff --check`:PASS. All12 scoped source/input/environment pins are
  unchanged through the final test command; no source/test job remains active.

`result.json` SHA256:
`80328ee882e63839452726c9086ecbb9f99337ef270a8f3d8770b0a5704602d2`.
`source_pins_v2.json` SHA256:
`3b7ecb2dc8ce96d7d299bead18af7c09ac3fe594a27d47e181f4b7a549738eec`.
Final runner SHA256:
`8a2beca35990eb271c94928fa95bc5f7cfb95f6f4b0d8771ec9691bce961ce42`.
Final schema SHA256:
`ee3024ba9601957d1e67217d60f794d858e9cff1c89917f7c89944dd70b8f6eb`.

The parent was notified of source/CPU release before D3's new single-C profile
pinning. No source edit is permitted under that subsequent profile hold. This
boundary verifies the prospective evaluator and its existing-owner plumbing;
fresh graceful-stop behavior remains for the parent's new visible attempt03.
