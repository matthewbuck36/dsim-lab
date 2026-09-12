# R7 short visible C development03

Status: **ADOPTED**, prospectively2026-09-10 after C02 closure and installed-route
review. First run the two existing startup modules under45s work/60s total.
Preparation and acquisition remain conditional on that successful receipt and
unchanged full R7 source validation. No startup test or new runtime has run at
adoption. C02 archive566 members verified; manifest
`883cf0eb66a0ae176b520b499565946160d5be685fdb02cb2bade15c6e5bba83`.

C02 failed before recording readiness in 33.076955 s: the upstream controller
spawner timed out waiting for load, then its retry failed on an already-loaded
controller. C02 remains failed with no R7 empirical exposure. This draft selects
the already implemented, source-pinned idempotent recovery route; it introduces
no production change or new algorithm setting.

## Exact change and prerequisites

Copy [C02](r7_visible_c02_plan.md) into new run/case identity
`v2_method_development_C_20260910_03` and exclusive external
`development/20260910/visible_integrated_C_03/`. Change identity, paths,
descriptions and plan binding, and add exactly one case launch override:
`controller_spawner_load_recovery_enabled: true`. Preserve all scientific
settings, exposed seed 26091011, geometry, start, disturbances, costs, PDE,
rolling GESC, moving cycle coherence, centered tracking, half-gain controller,
R5/R6/R7 behavior, fill/escape settings and acceptance predicates from C02.

The retained preparation owner must verify both receipts before freezing:

- `development/20260910/r7_runtime_validation_v1/focused_v1/source_validation.json`:
  the unchanged full R7 source validation (332 unique checks).
- `development/20260910/visible_integrated_C_03/startup_validation_v1/source_validation.json`:
  future bounded validation of the two existing startup test modules, prepared
  separately by root; no success is assumed in this draft.

Both must report successful return, unchanged source and installed bindings.
Preparation checks every validated source hash and the actual installed entry
bindings, includes both receipts and their complete source maps in its freeze,
and confirms the resolved recovery selector is true. The installed-route audit
must confirm the selected existing spawner is reachable; an override alone is
not empirical startup evidence. Any failed prerequisite stops C03.

## Unchanged finite execution and evidence

Retain C02's existing preparation, run, native analysis and direction reference
helpers. Only preparation gains the additional receipt check. Reference is an
unchanged copy; native analysis retains one captured BagData read plus its
validator's second read and existing motion/arrival metrics. No new decoder.

After adoption, allow one visible simulation attempt: domain201, localhost1,
DISPLAY:0, clean PYTHONPATH, existing
`stationary_recurrent_pairing_v1/runtime_environment_v2.sh`; no build. Preserve
90 s inclusive preparation; 45 s preflight, 300 s run, 340 s wall, 30 s shutdown;
180/120 simulation-second stages; 420 s outer cap with independent 30 s cleanup
reserve and external SIGINT at 415 s plus 5 s kill grace. Strict daemon baseline,
readiness, final zero and both cleanup owners remain authoritative. No retry.

After complete recording and cleanup, allow the same native analysis once
(110 s work/120 s inclusive), then the same 24-target saved-input reference
(38 s work/45 s inclusive). Behavioral failure may still have complete analysis.
Retain all command zeros, motion coverage, cancellations, errors and target
eligibility/unexposed denominators. Truth remains evaluator-only.

The C02 hypothesis and decision rule remain unchanged: timely approach and
admission, valid continuous VERIFY and initial DESIGN, typed committed fill and
both ACKs, owned escape, restored SEARCH and actual global arrival within 0.5 m,
with complete native evidence and no forbidden safety event. GOAL_HOLD and exit
bearing alignment remain optional under the adopted arrival criterion. Poor
direction results and incomplete evidence remain visible. This exposed case
does not release V11, a full comparison, physical work, commits or pushes.
