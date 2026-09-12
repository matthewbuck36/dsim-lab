# V11 measurement diagnosis execution

[Adopted plan](../m4_v11_measurement_diagnosis_plan.md). Separate diagnostics;
closed V11 outputs and all source/numerical methods remain unchanged.

Job2 command extraction is ACTIVE, sole session56873, reviewed helper SHA256
`c7d0dd728783976cb1cc350f6cd57cf3c6e817af7f6882617d75ca92d4a1a14e`,
prepared SHA256 `1760418ff9dbb465eec364f9cf791551b6134c85d1b8ade3641d3851ea0609ad`.
Exact argv/environment/cwd are in external
`development/20260910/m4_v11_command_diagnosis_v1/prepared.json`.
Outer115s SIGINT+5s kill; internal100s work leaves post-hash reserve.29prepared
pins plus prepared.json; one filtered existing reader call. Root dispatched
saved argv once using subprocess with exclusive console.log; execution.json
will record return code/elapsed time. No ROS node or simulation is started.
Job1 cached-residence helper remains in preparation and has not executed.

Job2 COMPLETE; sole session56873 terminal/reaped0. Outer3.933934s, result3.519206s,
filtered reader1.481228s. Exactly one reader call; all30source/input/prepared pins
stable, original12119/12118counts and5197mismatch indices reproduced exactly.
Result SHA256 `72022a867305ed75c529de0a0cd5d7b6bbfbf7e045616543003c77ee49711177`.
312 possible single removals (indices0..311) each yield exact bounded matching;
all candidates are zero commands before readiness. Latest candidate bag timestamp
1789088895362747296 precedes readiness1789088895370017390 by7.270094ms.
Diagnostic source stamps are monotonic. The startup row is not uniquely identified;
no headerless source time is invented. This supports startup-prefix offset as an
explanation, while the frozen C motion result remains EVIDENCE_UNAVAILABLE.
Independent cached-only review of interval boundaries is pending. Job1 helper
preparation continues; no simulation or extraction process remains active.

Independent Job2 cached review PASS,0.371s; `review.json`SHA256
`ec29803badba2935ed64f503e7c0c799c8d5ff9dc9ba433769e25c13009b72cb`.
Before readiness311diagnostics/312commands, allzero. During readiness11493/11493
exact valid matches, maxbagdelta12.478026ms; afterward314/314exactmatches,
maxdelta4.424969ms. No matchedpair crosses readinessboundaries. This identifies
startup-only scope contamination; a prospective correction can restrict both
streams identically to readiness while retaining unchanged strict pairing checks.
No source correction or new motion qualification yet.

Job1 ACTIVE sole session74919, exact saved command `bash .../m4_v11_residence_diagnosis_v1/run_once.sh`.
Prepared revision2 SHA256 `e7d2e83f1f2fdfeea45a1391f73c3c83adf2f0aacb24d3360bde3322e1605c2b`,
helperSHA256 `b520f6ffdf21c0b56a3c9b049cf2c18b1512fbd2cbfbb3280844123aaf9674dc`.
26pins plus preparedreceipt; wrapper55sSIGINT+5skill,50sinternalwork.
Root review corrected only the unreleased wrapper to fail on environment-source
error and use Python-B; initialprepared/wrapper/receipt bytes remain asinitial_*
with explicit supersedes reason. No bag/model read, newlabels or negative recomputation.

Job1 PASS; session74919 terminal/reaped0, outer2.870768s/result2.505274s,
all27 source/input/prepared pins stable. ResultSHA256
`94b4dcf11a0fe7d6648965f1f0249d2b14a3d17ebb7f56f78f64fd64560b17fa`.
Allfour original raw-input hashes and local residence prefixes reproduced exactly.
Pre-fill local residence counts A/B/C/D13/9/20/15. Every observed point break
was outside the positive mask but inside the local exclusion mask; C additionally
had2 connecting-segment breaks. No gap/invalid-source break was observed in these
prefixes. Long nonpositive spans can remain close to the local source; these are
mask membership failures, not automatically departure from its neighborhood.
The saved diagnostic scope ends at first fill, so some poses follow behavior-
changing VERIFY. Those are descriptive only and cannot independently certify
pre-detection settling. Independent review will distinguish wholly pre-VERIFY spans.
No new label, detector threshold, runtime, reference or frozen result was changed.

Independent Job1 review PASS;27 original pins and23 reviewed artifacts stable.
ReviewSHA256 `804627122d3e7302cf9829494d4377008b23141833d092f57b417af0d9e40920`.
Wholly pre-first-VERIFY examples: D58.566–83.590s,25.024s, fixed-source distance
0.146468–0.240942m; C45.467–56.177s,10.710s,0.210033–0.241242m. These are
existing descriptive intervening spans with positive boundary anchors, not new
positive labels. C's2 initial segment breaks span34ms and2.865/2.271mm despite
positive endpoints. Its60.282s span crosses VERIFY and is not independent truth.
Both jobs and reviews are COMPLETE. Source-read hold released before R9 editing.
