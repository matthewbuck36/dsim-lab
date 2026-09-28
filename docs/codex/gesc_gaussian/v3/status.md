# V3 planning status — 2026-09-25

> Superseded for active work by the user-approved [refactor plan](refactor_plan.md)
> and [implementation status](refactor_status.md), begun 2026-09-28.

**P0 source audit and planning draft complete; P1 implementation not started.**
Read the [plan](plan.md) and [ranked fault inventory](fault_inventory.md).
The user requires continuous base motion during Gaussian verification/design.
No planned stationary collection is an acceptable V3 fallback. Actual
translation must be measured, not inferred from nonzero commands or spinning.

## Scope and Git state

- Branch: `planning/gesc-gaussian-v3-physical-constraints`, based on `e726774`.
- Protected references: V1 `1af67c6`, accepted V2/Test D `d1779b6`, selected
  5 Hz experiment `e726774`. This planning work makes no new commit.
- Only new V3 plan/inventory/status documents and their navigation link were
  added. No V3 runtime changes, tests, builds, Gazebo/ROS launches, Pi contact,
  firmware changes or physical motion occurred.
- The earlier user-requested Phase 09 → V1 comment substitutions in
  `clock_configuration.py` and `controller_node_script.py` remain uncommitted.
  Historical phase references in generated report prose remain unchanged.
- Physical V1 is preserved at the recorded V46 restoration. Its installed
  state was not re-inspected live during this offline planning task.

## Recovered evidence and boundaries

The audit used current simulation source and selected scenarios; the V46
handoff, original firmware/driver and successful operator run; the autonomous
ledger/pause and retained V29/V35 timing/resource evidence; and V42–V45
mobile diagnostics and archived physical source. Links are in the plan and
inventory. Archived code is evidence of that version, not evidence that it is
currently installed.

The preserved physical configuration is original fixed approximately 5 Hz
Arduino firmware, nominal 20 RPM and explicitly authorized 54-degree offset.
Run `970bc1b3` passed recording completeness, ran about 45 seconds after
readiness, moved about 1.2 m net and stopped on Ctrl+C. It measured 4.98 Hz
and about 17.2 RPM; no fill occurred, so it did not qualify Gaussian escape or
global-source convergence. See the [V46 review](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/operator_run_970bc1b3/REVIEW.md).

The native V2 pigpio lease was not retained in restored V1. This does not
change the successful run's result; it limits what can be inferred about
unobserved process-freeze or OS failure behavior. No hardware modification is
proposed in this planning milestone.

## Findings driving the next milestone

1. FAILSAFE combines unlike causes, including deliberate operator stop.
   Current terminal supervisor faults do not automatically recover.
2. Filter resets may recover locally but become terminal through stale-output
   watchdogs or physical recorder semantic-stop policy. Moving V2 already
   handles some candidate/fit failures without terminal stopping.
3. Sparse/nonuniform observations and moving geometry must be modeled, with
   acquisition uncertainty distinct from publication/receipt/service latency.
4. Historical physical live and offline predicates drifted: selected 5 Hz
   density relaxation and freshness differed from strict offline checks.
   These post-run inconsistencies did not cause live readiness failures.
5. CPU/recorder load, wrapper version selection, and mixed installed source
   were distinct failure mechanisms. No single explanation covers all runs.
6. The supervisor owns algorithm behavior as well as diagnostics. Simplify
   those responsibilities in existing owners; deleting it as a logging node
   would change the algorithm and remove motion checks.

## Validation record

- Read root `AGENTS.md`, environment guidance, existing workflow/current V2
  plan/status/handoff and retained evidence before planning edits.
- `timeout 20s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan`
  passed during recovery. It validates the inherited V2 context only.
- Existing `validate_phase_context.sh`, `init_phase_status.sh` and
  `checkpoint_phase.sh` support phases 0–10 and V2, not a V3 milestone.
  No V2 status/checkpoint was reused to claim V3 completion. Add explicit V3
  workflow support, or document a bounded equivalent, before implementation.
- Planning checks: Markdown local-link/line-target existence, `git diff
  --check`, and AST equivalence of the two prior comment edits. These do not
  qualify any algorithm or physical behavior.
- Final bounded Python check passed for all four edited/new documentation
  files: 149 local link occurrences, 62 unique targets, referenced lines
  within file bounds and no trailing whitespace. Both comment-edited Python
  files have the same parsed AST as HEAD; `git diff --check` passed.
- Source audits were reviewed independently for algorithm faults,
  physical/recording faults and architecture/continuous-motion requirements.

## Next incomplete acceptance criterion

P1 must demonstrate that the selected simulated sensor/timing stream has the
intended physical observation limits. In particular, the control path must
not receive hidden true acquisition times, phase or pose unavailable on the
robot. Establish deterministic healthy and adverse fixtures and validate the
input model before interpreting any new navigation result.

Freshness/uncertainty limits, permitted recovery, minimum motion quality and
runtime headroom remain design choices to settle from models and pilots.
No large matrix, further physical repair or deployment is queued here.
