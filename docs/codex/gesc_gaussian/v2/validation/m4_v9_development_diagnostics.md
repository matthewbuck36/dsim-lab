# V9 development observations for work after comparison closure

Status: READ_ONLY_DIAGNOSIS, 2026-09-10 UTC. This is not an adopted implementation
amendment or permission to change V9 source, controls, targets or results.
The original dispatcher77764 is terminal1; V9 is CLOSED_INCOMPLETE.
No tests, models, bag reads, runtime queries or edits to source were used here.
The observations below combine retained small receipts with static source review.

## Terminal slot11: discovery baseline and independent recording failure

Slots1–10 outer baselines contain the exact daemon
`/_ros2cli_daemon_201_43f547f7f0ec4c73834cdd093a15b9c9`; slot11's outer baseline
is empty, its inner baseline includes that same daemon, and its outer final
graph contains only that daemon. Inner cleanup passes; outer cleanup fails on
the graph difference. Both kernel proofs pass and no owned/session survivors
are reported. Independent read-only inspection finds none of486 retained V9
PID/start identities alive or reused; dispatcher/owner PIDs are absent.

`run_m4.py:254–255` calls `ensure_ros_daemon()` then probes immediately. Existing
`run_scenario.py:1101` checks startup CLI exit only, discarding output and daemon
identity; its native graph probe at545 waits0.25 s. Installed Humble daemon
startup establishes process/pipe readiness, not visibility to another DDS probe.
A transient discovery miss is plausible, but no exact daemon creation PID/time
or discovery trace was retained. Do not claim an established transport cause.

Prospective correction belongs in pre-dispatch baseline admission: establish
and record the exact shared daemon identity, require bounded visibility before
dispatch, and fail admission on absence/change. Preserve strict rejection of
new unregistered nodes and all process checks; no wildcard daemon exemption or
broad process kill. Existing dispatcher fixtures can cover delayed/permanent
absence, identity change and a real new node under the original deadlines.

This cannot resolve the other integrity failure: slot11 completeness59/60 has21
`atomic cost lacks selected raw/augmented/provenance join` details. Three
`transform_original_receipt_expired` warnings after shutdown do not establish a
causal relationship. A separately planned, bounded retained-data diagnosis must
identify which tuple/clock/topic join is absent and distinguish missing recorded
evidence from incorrect selection. Preserve the strict contract and original
failed recording; no replay or source fix is admitted by this note alone.

## Live stage progression can regress after an incomplete later join

The finalized D receipt records Stage B start142.411/latest364.465 s, but its
stop is a Stage A timeout364.533−.529=364.004 s. The live timestamp audit has
five matched confirmations and reports a missing typed companion. Final recorded
evaluation matches all six confirmations and one completed recovery. Exact D
hashes and timing limits are retained in [V9 validation](m4_v9_budget_comparison.md).

Root and independent source review support this control-flow mechanism:

1. Existing `run_scenario.py::refresh_stage_a` (line1753) revalidates every
   accumulated confirmation on each callback. A binding error overwrites both
   `observed['stage_a']` and `observed['fill_cardinality']` with False, even after
   a valid recovery and Stage B entry were observed.
2. `_centroid_convergence_evaluation_events` (line2977) reports a missing typed
   companion. On error it returns the original unnormalized events; the existing
   recovery evaluator cannot use their invalid legacy source coordinates.
3. The next odometry callback (line1861) takes the Stage A branch again and uses
   the original start time. Beyond360 s this sets the sticky Stage A timeout.
   The polling loop (line2049) breaks before another callback can complete a join.
4. Final `_bag_outcomes` sees all six recorded pairs and passes the same final
   matching contract. Classification checks final extraction/completeness/cleanup;
   it does not turn the live monitor error into an infrastructure failure.

This explains the retained COMPLETE/integrity PASS result alongside incomplete
post-recovery observation. It is not evidence of successful goal behavior. The
producer publishes diagnostic before event (detector line1112 then1124), but they
arrive on separate subscriptions. The receipts cannot distinguish a queued or
delayed companion from one missed by the live subscriber; no callback-delivery
trace was recorded. Do not claim an exact transport cause from this evidence.

The existing late-arrival regression (`test_m4_centroid_event_evaluation.py:153`)
delivers both companions before its first odometry callback. It does not cover
a new incomplete join after recovery and after the original Stage A deadline.

After V9 closes, investigate a bounded correction within this existing monitor:
preserve completed stage progression; distinguish pending companions from
contradictory evidence; withhold dependent acceptance while pending, with the
original Stage B and wall deadlines continuing. Keep exact identity checks and
the500 ms publication-order bound. Contradictions and unresolved final evidence
must still fail. Prospective callback-schedule tests need both arrival orders,
interleaved odometry after360 s, eventual completion, permanently missing and
conflicting companions, unchanged legacy behavior and unchanged Stage B deadline.
No correction or new experiment is adopted by these notes, and V9's retained
timeout must never be rewritten into a full300 s post-recovery observation.

The later nominal holdout B (slot6) independently retains the same pattern:
Stage B209.616–389.952 s, then Stage A timeout390.054−.108=389.946 s with the same
missing-companion message. Final recorded-data evaluation binds all four
confirmations and one assisted recovery. Recording52/52 and cleanup pass. This
second occurrence supports the progression diagnosis and again limits exposure;
it does not resolve the unknown live callback-delivery cause or authorize a fix
inside the frozen comparison. Exact slot6 receipts are in current validation.

## Labels analysis timeout

Block0 labels reached the original work deadline and were cleanly terminated.
The log ends with cancellation in `bag_reader.read_run_bag`; partial A/B/C outputs
remain. The block ledger marks all four scientific results unavailable and skips
dependent references/summary. This identifies the interrupted operation, not its
dominant cost. A read-only source review of existing decode/processing ownership
is in progress; no timing probe, rerun, budget increase or outcome revision has
been performed. Any retained-data follow-up needs a separate durable scope and
isolated evidence version after the frozen comparison closes.

The independent review is now complete. `evaluate_m4.py::labels_stage` (line278)
reads each run exactly once with union aliases and shares BagData across analysis.
`bag_reader.py` filters topics before decoding selected messages once. D was
interrupted during that first read. Bag-open gaps17.79/19.82/63.21 s encompass
all prior-run decoding, processing and writes; they do not isolate a dominant
operation or justify calling this a duplicate-decode bug.

Confirmed avoidable work in the current source:

- At evaluate_m4.py310–311, `atomic_exclusive_json` returns the exact written
  SHA-256, but labels_stage discards it and `receipt` opens and hashes that file
  again. C's normalized output is89,986,365 bytes. The existing atomic writer
  already hashes its encoded payload after exclusive publication.
- At analyzer5241–5253, each M4 observation constructs an initial objective
  snapshot including `message_payload(objective)`, then replaces it using
  `_m4_objective_snapshot`. C retains10,605 unique observations. Avoiding the
  discarded conversion can preserve the chosen snapshot and legacy branch.
- Whole-stream policy validation indexes and hashes companions; the adapter
  repeats indexing at5178 and repeats pair validation. Sharing validated state
  requires preserving all error, conflict, duplicate and ordering semantics.
- Normalization deep-copies all observations, hashes canonical serialization,
  then serializes the full output. These are full-data passes; the ownership
  contract must be checked before removing copies or changing representation.

Root source inspection confirms the first two paths. The smallest candidate
correction reuses the writer's digest and avoids the discarded M4 snapshot;
prospective tests must compare exact output bytes/hashes, legacy results and
conversion counts. Broader validation/copy reuse requires additional evidence.
No profiling occurred, and these savings are not proven sufficient to meet the
unchanged block budget. This diagnosis does not authorize rerunning V9 analysis,
extending its caps, or converting its partial files into completed results.

Nominal block1 repeats the timeout with a different interrupted operation:
canonical JSON serialization during C processing. Partial slot5/6 labels+metrics
and slot7 labels exist; slot7 metrics and every slot8 analysis output are absent.
The complete block ledger marks all four scientific rows unavailable. This adds
evidence about the interrupted processing stage, not a measured cost profile.
Large intermediate serialization is a candidate for future review alongside
the repeated conversion/hash/copy work. No format, input, metric or cap changes
are made during V9, and no partial normalization is treated as complete.

## Nominal C direct-exit alignment and missing rejected geometry

Slot7C reaches the direct escape alignment guard only after the earlier frozen
direction/geometry/state-weight/radial-progress/zero-supervisor-command/ordinary-
GESC-composition/final-saturation/returned-SEARCH checks pass. The helper has374
supervisor-command samples and547 control samples. Thus the recorded failure
is geometric acceptance, not an earlier command transport/ownership mismatch.

Existing runner line5050 computes the dot product of the unit fill-center-to-exit
vector with the frozen selected direction and requires >=.80. It selects the
odometry sample nearest the first returned-SEARCH boundary within its existing
freshness bound. The interior_farthest fallback changes anchor admission only:
slot7 displacement1.343568 m is above .50 m and inside1.377112 m radius. It does
not waive alignment. Runtime `escape_recenter.py:456` instead completes after
radial clearance, nonnegative radial progress and the exit hold. A curved exit
can satisfy runtime completion but fail the stricter recorded alignment guard.
The retained V1 [v8.12 report](../../validation/phase_08_8_m8_9_v8_12_broad_matrix.md)
already documents that general possibility; it does not prove slot7's trajectory.

The failed numeric alignment cannot be reconstructed from the permitted small
receipts: failure returns before the success-only geometry audit at runner5061.
The selected exit pose/stamp and numeric alignment are omitted. Final pose near
632 s cannot substitute for the escape boundary near332 s. No bag was decoded
or trajectory/reference calculation introduced to fill this gap.

A prospective evidence-only correction could retain these already-computed
fields on rejection and test the unchanged verdict at the existing boundary.
The V5 moving transport fixture ends immediately after escape admission; it
does not qualify exit geometry. No algorithm or .80 gate change is justified
by these notes, and no change is admitted during frozen V9 acquisition.

## Future compact intermediate representation: static boundary only

A separate read-only consumer review identifies compact JSON as a candidate for
large future M4 intermediate files. Decoded contents/types/array order and the
existing `m4_pilot.canonical_sha256` can remain identical while changing only
indentation/separators. Preserve sorting, float encoding, finite-value rejection,
Unicode behavior and trailing newline. External file SHA-256 necessarily changes;
reference/summary consumers parse JSON and verify recorded receipts rather than
indentation, so every new file needs its own exact receipt in a fresh evidence
version. Existing V9 files and their unavailable results remain untouched.

Owner choice matters. `q1_study.py` checks the original numerical-owner pins and
an explicit unchanged `_v2_enclosure_geometry_task` boundary for the analyzer.
Changing the whole-file-pinned `v2_enclosure.py` writer would affect inherited
geometry reuse. A narrower candidate is the existing analyzer `_v2_write_json`
(line2903), which already uses exclusive atomic publication and interruption
cleanup. A default-off compact option selected only for future large M4
intermediates could preserve default writer bytes and the geometry task. Root
confirmed the existing atomic writer, canonical-hash implementation and geometry
reuse checks; no writer, source pin, field derivation or evidence format changed.

Prospective validation must prove exact legacy-byte parity, compact decoded/type
and canonical-hash equality, actual receipt-consuming reference/summary behavior,
rejection of stale/altered receipts, exclusive publication and interruption
cleanup. This may reduce output allocation/serialization/writes/hash/parse work;
it does not remove bag decoding, repeated conversion, canonical hashing, copies
or numerical work. There is no measured speedup or proof of budget feasibility.
The review is an implementation candidate, not an adopted amendment or authority
to retry either failed V9 analysis block.
