# Q2 structural snapshot-copy correction

Status: SOURCE VALIDATION PASS;106 owner/97 independent checks, fixed timing,
actual DDS and1167 held integration checks pass. Material closure is recorded
with the parent Q2 milestone. This was a bounded Level B source correction.
Read `q2_policy_runtime_plan.md`, `q2_snapshot_serialization_plan.md`, live
status and `validation/q2_snapshot_serialization.md` first. The preceding CDR
timing version is closed FAILED_TIMING_GATE and remains immutable.

## Evidence and scope

Saved timing gives selected363-observation median221.798ms old/150.344ms CDR,
speedup1.475264x below2x. Four clone stages cost approximately126.856ms versus
22.776ms hashing. Hash-only work cannot satisfy the existing gate. Generated
CDR conversion also constructs empty nested messages before replacing fields.

Replace only the implementation of `v2_lifecycle.clone_ros_message` with an
exact-schema generated-message structural copy. Keep one-pass canonical hashing
and all supervisor/Gaussian call sites, detachment/publication boundaries,
freshness500ms, verification12s and design5s unchanged. No new node, IDL,
configuration, cache of mutable evidence, source gain, field or policy change.
This is source validation; no scientific acquisition or M4 release.

## Copy contract

Allow only exact installed CandidateSnapshot/FillCommand roots and nested
SynchronizedObservation/Time. Verify supported declared field/slot schemas and
cache immutable copy instructions; fail on unknown fields/types/schema drift.
Allocate each exact generated class via its ordinary object allocation without
running default-field constructors, then fill every declared slot. Share only
immutable scalar leaves. Copy every nested message/list and slice typed arrays;
repeated input aliases must detach per occurrence, matching the CDR boundary.

Explicitly validate primitive type/range and typed-array representation before
storing private slots. Preserve uint64 integers, IEEE float64 bits including
optional NaN/infinity/signed zero, ordinary Unicode and generated message types.
Reject NUL and non-UTF8-encodable strings before downstream native conversion.
Do not reinterpret raw Time fields: representable negative/non-normalized times
remain copied; established semantic Time/hash validation retains its own role.
No generic arbitrary-object cloning or setters/serialization monkeypatching.

## Fixed validation

Run existing independent38 field/hash/CDR/detachment checks and106 owner/lifecycle
regressions against the new source; add focused schema, malformed field/array,
unsupported nested type, unpaired surrogate and repeated-alias isolation cases.
Tests and source get separate editing owners. Preserve any failures explicitly.

After review and focused checks, freeze a new exclusive
`serialization_preflight_v2` timing harness by deriving v1 with only version,
path and source pins changed. Keep old immutable D3 comparator, same10x363/3x4000
population, ordering, zero warmups, parity checks, 58s internal/60s outer cap,
selected maximum<200ms and median speedup>=2x. One execution only; retain failed
v1 result and do not compare selective repetitions. Report4000 separately.

Only after this timing passes, release one freshly source-pinned existing DDS
diagnostic with the same lifecycle+two-case pipeline and direct actual context,
readiness/receipt and entire supervisor-callback timing. Keep original fixture
assertions and source allowances. Then run prepared40-file integration with
300s inner/310s outer cap. The unexecuted CDR-pinned diagnostic v3 is preserved;
use a distinct directory for the structural source revision. Failure requires
saved-result diagnosis, never freshness relaxation or favorable reruns.

Update validation/status, source/install receipts and material checkpoint at the
independently reviewable boundary. Source correctness/performance remains
separate from detector and direction qualification.
