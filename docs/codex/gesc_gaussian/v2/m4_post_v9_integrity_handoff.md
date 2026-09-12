# Post-V9 D1 integrity diagnostic handoff

D1 is DIAGNOSTIC_ONLY_COMPLETE, 2026-09-10 UTC. Full V2 remains IN_PROGRESS.
Read [plan](m4_post_v9_integrity_plan.md) and
[exact validation](validation/m4_post_v9_integrity.md).

One45s fixture job passed28 tests in2.864638930 s outer. One90s read-only
extraction completed11.807023401 s outer, retaining63856 records across8 selected
streams from the original closed noiseCslot11 bag. All645 source pins and12
original files/inventory match entry/exit; both children are terminal/reaped.
No ROS initialization, model/science/full-validator rerun or source edit occurred.

All21 failures are a missing startup prefix: objective ordinals0–20, source
sequences1–21, keys.303–.9830000000000001 s lack raw/provenance; key.643 also lacks
augmented cost. Raw/provenance first key1.0170000000000001 has sequence22.
There are92 pre-readiness objectives (21 misses),10497 in-readiness (0 misses),
14 afterward (0 misses). No duplicates or identity/insertion errors. This
does not reconstruct DDS delivery cause or reclassify V9; no records are dropped.
All original V9 results and its archivefc818ab0...ad759 remain immutable.

External D1 root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_integrity_v1/diagnostic_v1/`.
Hold071fb32fab4d7bf8d888a400b0d82d72c2ebc813b0e3dc452fa33eb0b91cae5c;
summary383b9a4009f9ea6fb867496674be3acacca5c4b7864d625bb6e70261f834b5f7;
childreceipt52796cbc6dab6df28af14c3d68b6c715086c08f9e77890b602d6f6cf21098f31.
Full gzip payloads are bound in summary/receipt; use them for later authorized
diagnosis rather than reading the original bag again. Exact commands, budgets,
JUnit, logs, wrapper/outer receipts and hashes are retained alongside them.

Next save the exact startup-admission correction and its finite integration
proof before editing. Existing motion readiness depends on valid objective/filter
heartbeats: a naive composer motion-ready gate would deadlock. A recorder-only
prelaunch subscription bootstrap is a candidate under review; advertising
endpoints alone does not guarantee immediate publisher delivery. Preserve strict
full-bag joins, legacy/default behavior and all startup/case/suite deadlines.
No new acquisition or source repair is released by the diagnostic result alone.

The independently confirmed discovery-baseline and live-stage progression
defects still need correction, and labels analysis needs adequate throughput
under the saved budgets. Their saved source directions are in the plan/validation;
do not substitute them for measured detector/direction performance. Both original
goals remain open. The user already authorizes recommended bounded corrections.

Branch feature/gesc-gaussian-robustness-v2, HEAD3369cfc83a64ff5d8354827fd5310caaf0c8e945;
all task work saved uncommitted. No V1/Pi/physical action or commit/push.
D1 checkpoint PASS0.227897537 s under30. Material archive PASS3.724403036 s
under60:423 repository files/35 artifact references,1691320-byte verified tar.
External manifest: checkpoints/m4_post_v9_integrity_d1_v1/manifest.json,
SHA256 db9c3e1262eb176418fdabc573ce8e401b0da3613c9e4f3206e538c6446538e7.
Exact archive execution receipt: builds/m4_post_v9_integrity_v1/
d1_archive_execution_v1.json. This receipt postdates the immutable archive.
The archive binds all D1 helpers/results, selected payload,12 original files and
V9 closure/source/prepared references. No source bytes or old evidence changed.

Independent startup reviews agree that the proposed recorder-only registration
barrier improves ordering but cannot prove a future publisher matched rosbag.
The original console already advertised subscriptions before first objectives.
Installed Humble exposes aggregate matched counts and graph endpoint identities
separately; count>0 can be satisfied by another consumer. Do not adopt this as a
proven solution or accept a favorable fixture with waits absent from production.
Next resolve the smallest selected admission/retention mechanism through existing
owners, with an adversarial delayed-recorder first-sequence test and unchanged
full-bag validator. No startup correction is yet adopted or implemented.
