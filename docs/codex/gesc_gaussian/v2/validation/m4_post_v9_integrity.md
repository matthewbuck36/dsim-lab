# Post-V9 integrity diagnosis and repair validation

Status: D1 DIAGNOSTIC_ONLY_COMPLETE, 2026-09-10 UTC. Source repair remains open.
Read the [adopted plan](../m4_post_v9_integrity_plan.md). Full V2 remains active;
V9 and all prior failed evidence remain immutable. This work is simulation-only.

The previous goal turn completed V9's authoritative failure report, all16/192
denominators, independent closure audit and material archive. It was progress.
This turn reverified AGENTS/current plans/status/Git/context, archived final
acquisition and645 unchanged source pins. No old dispatcher is live or restarted.
The next incomplete acceptance criterion is classification of slot11's21 exact
join failures before choosing a recording correction.

Source inspection confirms full-bag membership validation, with no readiness
clipping or nearest-time matching. Legacy raw/provenance/source streams each have
10582 records, augmented10602 and atomic objectives10603; overlap and missing-key
locations remain unknown until D1. Strict identity and provenance insertion order
are preserved in the descriptive helper, including retained later errors that
do not erase already-inserted keys. Twenty-one errors need not be21 distinct keys.

External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_integrity_v1/diagnostic_v1/`.
Root prepared one exclusive diagnostic_hold_v1.json, SHA256
071fb32fab4d7bf8d888a400b0d82d72c2ebc813b0e3dc452fa33eb0b91cae5c.
It binds645 source files, all12 original run files matching the V9 archive,
the plan and three helpers. Eight selected streams total63856 records; every
stream is below40000 and the total is below160000. No count is truncated.

| Held source | SHA256 |
| --- | --- |
| extract_v1.py | 8b4b32fe5aed64ffc0e3bf02330d54cd0800e098b6b91a92abe15a3ae97e8d97 |
| test_extract_v1.py | aa5a14f1e5e020ab1cfc0a301889581ef9162c47635063542535e7724f9770c8 |
| run_job_v1.py | 89cc47e85ed0bdedcc2f5d0f715611effe0e122764d126051593a6af39f6e521 |
| m4_post_v9_integrity_plan.md | 9849641e466a7b8de948e5bcedc0ffee2f78500cd27155f36939c20734b8c2bf |

Helper author/root static reviews and AST parsing found no remaining helper or
fixture issue; independent final review precedes release. The fixture contains
28 prospective cases, with actual counts/status reported only after execution.
Wrapper review caught unprotected hold/cleanup failures, an expired-deadline
launch path, possible JUnit overwrite and unchecked environment setup; these
were corrected before any execution. The wrapper verifies original file
inventories as well as hashes on entry/exit and preserves exclusive failures.

Exact prospective commands from repository root, once each after its gate:

```bash
timeout --signal=SIGINT --kill-after=2s 43s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_integrity_v1/diagnostic_v1/run_job_v1.py fixture
timeout --signal=SIGINT --kill-after=2s 88s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_integrity_v1/diagnostic_v1/run_job_v1.py extract
```

The first command fits45s inclusive; the second90s. Work/child-exit limits are
35/40s and75/85s respectively. Wrapper commands retain complete clean Humble→Q2→Q5
environment and absolute deadlines. Exact child commands, logs, JUnit/diagnostic
outputs and every exit receipt remain external. Fixture PASS on the same hold
is mandatory before the single original-bag read. Original source/bag hashes
must remain identical; no ROS initialization, model job, recording validator
rerun or scientific reclassification belongs to D1.

D1 fixture PASS28/28, no failed/error/skipped rows. Sole outer command returned0
in2.864638930 s/45; wrapper2.819551592 s. ChildPID125208 reaped. All645 sources,
12 original files/inventory, helpers/plan/closure/hold unchanged before/exit.
Exact outer receipt: builds/m4_post_v9_integrity_v1/d1_fixture_outer_v1.json;
child/JUnit/log underdiagnostic_v1. LogSHA256
8e749c0523d39462545493144169c7af2469abfe11fa16e24c59349589af8862.
Independent helper/fixture and revised wrapper/schema reviews PASS before run.
The same-held single90s extraction is now released; no other read/job is released.

## D1 result: missing startup prefix, not a readiness cutoff

The sole extraction PASS:11.807023401 s outer/11.763709971 s wrapper under90;
childPID125264 reaped. It decoded exactly63856 selected records with one reader
invocation. All645 source pins,12 original files and inventory, helper/plan/hold
and closure hashes match before/exit. Full selected compressed payloads remain
external; no original bag/metadata/validation result changed.

All21 failure occurrences reproduce as21 distinct keys: the first21 objective
records (ordinals0–20), source sequences1–21, source keys0.303–0.9830000000000001 s.
Every one lacks the exact raw and provenance member. Key0.643/sequence11 also
lacks augmented cost, whose recorded neighboring keys are0.609 and0.677. There
are20 raw-plus-provenance misses and one three-member miss. Neighbors are never
accepted as matches. Raw/provenance first appear atkey1.0170000000000001 s,
provenance sequence22. No duplicate, identity-envelope rejection, pre-insertion
rejection or later provenance-validation error occurred in this diagnostic.

| Objective timing relative to readiness | Occurrences | Missing exact join |
| --- | --- | --- |
| Before readiness | 92 | 21 |
| Inside readiness | 10497 | 0 |
| After readiness | 14 | 0 |

Timekeeper origin is0. Readiness bag bounds are1789053396622006838 to
1789053755585722954 ns. Unmatched objectives arrive3.137868132–2.461610023 s
before readiness; the last precedes the first recorded raw sample by0.116131412 s.
Raw/provenance first recorded samples arrive approximately2.34549 s before
readiness. These are bag-observation differences, not reconstructed DDS callback
receipt times. All objective occurrences after ordinal20 have exact members.

This establishes a missing recorded startup prefix. It does not prove why the
independent recorder missed those publications or qualify the original run.
The full-bag validator correctly retains its failure; do not discard pre-ready
records or treat the10497 joined in-ready objectives as a revalidation pass.
The shutdown transform warnings cannot explain this startup prefix.

The existing recorder starts bag then target immediately and checks its graph
barrier afterward. Local composer joins prove receipt by that owner, not capture
by a separate recorder. Original console startup messages advertise raw and
provenance subscriptions before the first recorded objective, so an advertised
endpoint alone is not proof of first-sample delivery. Exact transport causality
remains unavailable. A source repair must establish capture readiness before
valid dependent claims rather than weaken the validator.

Do not gate the composer on the existing motion-ready Bool without resolving
the dependency: operational readiness itself expects valid V2 objective/source
and filter heartbeats. That naive change would deadlock. A recorder-only staged
startup using existing typed subscription registrations/include-unpublished-topics
is being reviewed as a narrower option; it needs an actual immediate-publisher
recording fixture. New publishers can still require DDS matching after creation,
so graph registration is not a universal delivery guarantee. Any stronger
selected producer admission must also exclude queued pre-admission source triples.
No such correction is yet implemented or released by D1.

Independent diagnostic result review PASS, including all28 unique JUnit rows,
the unchanged hash maps and exact missing-member categories. It used generated
summary/receipt files, with no second original-bag read.

| Diagnostic artifact | SHA256 |
| --- | --- |
| summary.json | 383b9a4009f9ea6fb867496674be3acacca5c4b7864d625bb6e70261f834b5f7 |
| receipt.json | 52796cbc6dab6df28af14c3d68b6c715086c08f9e77890b602d6f6cf21098f31 |
| extract_execution_v1.json | f990ba0a2cc1d6c730c70a5e60a6014348ddee22db0dd05e63d64755637d04f1 |
| fixture_v1.xml | 44583799ac0ea2f26da596424cb8b2331eb79b525cdeedc2dbf53034aebc04f2 |

The summary and child receipt bind the compressed full-record file. Exact outer
execution is in builds/m4_post_v9_integrity_v1/d1_extract_outer_v1.json. This
diagnosis changes the next correction from an unspecified synchronization issue
to startup recording admission; both research goals and the fresh comparison
remain incomplete. D1 checkpoint/archive closes this diagnostic boundary before
the exact next implementation scope is adopted.

## D1 material closeout

Current recovery reverified the email and original plan: faster reliable
settling/trapping detection and reliable GESC direction during continuous search
remain the two objectives. D1 is supporting integrity work, with no empirical
acceptance promotion. Current branch/HEAD remain the saved V2 values; no staged
changes, commit/push, V1 or physical action. Context validator and diff check PASS.
The existing repository checkpoint command `timeout 30s
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`
PASS in0.227897537 s; exact receipt is builds/m4_post_v9_integrity_v1/
d1_checkpoint_execution_v1.json.

Independent review of the external archive owner PASS, helper SHA256
f669887d1edaf0216732c7acf539eb5bffc8bcbcfda62bc01f88f8ef0592e1f5.
One60s archive is released via `timeout --signal=SIGINT --kill-after=2s 58s
python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_integrity_v1/archive_d1_v1.py`.
It admits the28 clean fixture cases, one63856-record extraction,662 unchanged
held inputs, original V9 file chain and compressed payload hash
607d5e590227ac3399c0932e763bdba321740d93fb88ee5901bd3c294b9c883f.
It retains the dirty repository tar and all D1 build/original12/prior archive
references, without bag decoding or another diagnostic run. Terminal receipt
will be appended after the immutable boundary.

The startup design review found that recorder endpoint registration alone is
insufficient to prove a newly created producer has matched that reader. Original
console evidence already shows early subscriptions; an eventual fix needs a
defensible startup transport boundary and adversarial verification. A single
favorable fixture or `get_subscription_count()>0` cannot establish exact recorder
matching. No recorder-only correction has been adopted as a proven solution.

The sole archive command completed PASS0 in3.724403036 s under60. Manifest
checkpoints/m4_post_v9_integrity_d1_v1/manifest.json SHA256
db9c3e1262eb176418fdabc573ce8e401b0da3613c9e4f3206e538c6446538e7;
423 repository files/35 external artifact references and1691320-byte verified
tar. Entry/exit held hashes, source/original inventory, artifact signatures and
repository file hashes PASS. Exact external d1_archive_execution_v1.json retains
argv/elapsed/returncode/stdout/stderr and postdates the immutable archive.
D1 is materially closed; no production startup repair or fresh comparison has
been released. Both original research goals remain open.
