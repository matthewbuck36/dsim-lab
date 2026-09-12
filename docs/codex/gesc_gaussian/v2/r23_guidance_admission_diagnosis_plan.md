# R23: retained guidance/admission ordering diagnosis

ADOPTED on2026-09-11 after [V14 closed incomplete](m4_v14_handoff.md). This is
the current diagnostic milestone. No algorithm, validation gate or old outcome
changes are authorized by this diagnostic plan.

Question: did C11 emit approach guidance that concealed an already admitted
collection, or does the validator reject a legitimate earlier publication sharing
the admission's ROS clock tick? Current summaries establish the failed predicate
but omit the rejected message. Neither hypothesis is assumed true.

One read of the retained C11 bag through existing `read_run_bag`, restricted to
`v2_verification_guidance`, `algorithm_events`, `algorithm_state` and the owner's
automatic readiness stream. Use the existing R21 environment. Bound the entire
capture at45s SIGINT plus5s kill. Save exact typed projections, publication
sequences, message hashes, bag receipt times and ROS stamps in an exclusive
`development/20260911/r23_guidance_admission_v1/` directory. Preserve every selected
record; cap selected records at100000. No full bag scan through another reader,
bag rewriting, raw hash rescan, numerical model, labels, references or simulation.
Record native bag file stats before/after and inherited receipt identities;
stat stability is not a newly computed raw hash. Hash the small direct inputs and
existing reader/serialization/validator/runtime owner sources before/after.

Using these saved projections, report every valid approach message failing the
original exact predicate, with candidate/epoch, publication sequence and timestamp,
admitted_at field, actual admission event, and neighboring guidance revisions.
Preserve the full selected input even if no violation or an unexpected mismatch
appears. Separately check whether collection_started ever regresses within one
candidate and whether an exact same-stamp AlgorithmState companion exists.
Bag receipt order alone is not causal sender order. Any proposed equality-boundary
correction needs the owner's publication sequence and runtime transition semantics,
not a blanket <= timestamp change.

Independent source audit and cached captured-result review precede a repair plan.
If source and data show a runtime contradiction, address the runtime. If they
establish an evaluator ordering defect, scope a prospective correction to its
existing owner with adversarial tests; original C11/V14 failures remain immutable.
No new full matrix, retries, replacements, parameter tuning, physical/Pi/snapshot,
V1, commit or push. Record exact findings, limits and next acceptance criterion
in live status/handoff. The original research objective and missing comparison
conditions remain open.
