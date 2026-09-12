# R23 correction: same-tick guidance transition evidence

ADOPTED after the single capture and independent31-check review passed. Capture
review SHA256068c325842cf2c6081ad8f561b313753b13155ac773960f67541bc4692d82fa1.
This follows [the diagnostic plan](r23_guidance_admission_diagnosis_plan.md).

Change only the existing v2_lifecycle_validation.py guidance audit and its
test_v2_lifecycle_recording.py tests. Preserve exact before bytes and hashes under
the existing external R23 root before editing. Runtime, clocks, topics, controller,
configuration, algorithms and old results remain unchanged.

An approach publication strictly before admission keeps its existing route.
Publication after admission still fails. Equality can be deferred only with
admitted_at=0 and all original identity, immutable candidate, exact state,
pose/freshness, command and verification deadline checks passed. Resolve this
pending row only using the FIRST fully validated COLLECT publication for that
candidate/epoch/admission across all publication times. That first witness must
itself be at the exact admission timestamp, be VERIFY, and have a higher sender
publication_sequence. Existing immutable association binds acceptance and center.
No unvalidated witness, cross-topic receipt ordering, later replacement witness,
timestamp regression or blanket <= comparison may grant acceptance. Unresolved
pending rows retain the original error and are omitted from accepted metrics.

One focused test job,60s SIGINT plus5s kill, covers existing lifecycle-recording
tests, trapping recording selection and lifecycle contracts. Add actual serialized
wire fixture cases for the supported transition, absent/invalid/wrong-tick witness,
false approach after an earlier collection, backdated approach after a later-tick
collection, nonzero admission, timestamp substitution and identical replay.
Retain all current negative tests. Preserve a failed validation before any new
bounded correction; do not weaken assertions to pass.

Independent source review and exact focused results precede qualification of this
source correction. Captured sequence3234/3235 provide empirical motivation and
matching pose/state/deadline evidence; they do not change C11 completeness or
promote its nonarrival. No raw-bag revalidation, numerical reference, simulation,
new matrix, old report rewrite, physical/Pi/snapshot/V1/commit/push is released.
After the correction, the still-unmeasured noise/delay conditions and original
latency target remain required open research work.
