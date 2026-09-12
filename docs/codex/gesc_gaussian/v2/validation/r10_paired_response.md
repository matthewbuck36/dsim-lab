# R10 paired response validation

COMPLETE2026-09-11UTC. [Adopted plan](../r10_paired_response_plan.md).
34/34 focused adapter checks passed;empirical and synthetic complete.
Independent empirical/synthetic reviews and joint decision passed.
No simulation or new comparison is released. Original V9/R4/V11 results remain
unchanged; the historical30% first-positive-mask latency target stays unavailable.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/`.
The adapter/empirical and synthetic helpers are being prepared through existing
owners. Root owns preparation and sequential execution after independent review.

Read-only preparation confirmed3610 recorded V9 B PDE history messages and
captured stationary PDE/detector settings. The earlier combined final-core replay
contains V9 D, not B; earlier B prototype outputs cannot substitute for a new
final-core B replay. Four recurrent core/dependency files still match the prior
combined/R4 identities. Synthetic cache admission will additionally verify all96
case identities, samples, schedule and actual source-input endpoints.

Independent plan review found no methodological blocker and requested concrete
common origin, pre-admission treatment and timing-resolution rule; these are now
saved prospectively in the plan. Root execution-wrapper review corrected a cleanup
race and added a post-child prepared-manifest digest check before any execution.
The reviewer verified both corrections statically. No study was run for that review.

Pre-edit context validator and `git diff --check` passed. Exact final preparation,
commands, source/input receipts, elapsed times, outputs and scientific decision
will be appended only after those actions occur.

## Frozen review and focused checks

Independent static review PASS:13 checks,22 stable reviewed inputs. ReviewSHA256
`d594a00ea9c9993e539d8a22354288872cc96b23a2019769d88428ca3272bbd9`.
All final source/helper/plan/review files are held during execution.

Preparation command for each named job:
`timeout --signal=INT --kill-after=2s 28s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/prepare.py JOB`.
Checks preparation0.004859448s,24 pins and1 original parameter-source hash;
preparedSHA `be517a6118d5f4144f019bf18e8ed213cc7406db5ca4e5b9d1d8983f67a5e04f`.

Exact checks execution:
`timeout --signal=INT --kill-after=5s 55s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/run_job.py checks`.
Exit0,terminal/reaped PID89034,0.719458763s outer;34/34PASS,no errors,
0.060759482s internal checks.24 source/input pins and prepared manifest stable.
ResultSHA `05b0827b95bf20e92a710590ac28f076d3838092d1c279ca6066990a860b7cfc`.

## Empirical job started

Preparation0.715532631s,37 pins and13 original input hashes verified;
preparedSHA `c6ac15b5c386fa02a300822e7c8ebc09cefb95627f4831fc04616e706b892164`.
Exact execution:
`timeout --signal=INT --kill-after=5s 115s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/run_job.py empirical`.
Session90317 terminal/reaped0;PID89103.8.350992259s outer,6.270465771s helper,
one filtered read2.578843764s.37 input/source pins and prepared manifest stable.
All selected counts match metadata:3610 PDE,7325 states,10617 poses,3614 clocks,
3612 timekeeper,3749 readiness.10531 unique admitted poses,0 exclusions,
74 retained transport resets;source regressions0 for both methods.

Recurrent first source response102.008s,model endpoint102.0s,circle branch,
support72–102s,persistence beginning60s. Exactly one confirmation. PDE has no
confirmation through its last observed source360.8s;the new response precedes
that censor endpoint by258.792s. Declared sampling tolerance0.234s comprises
0.100s PDE+0.034s admitted pose+0.100s clock maximum positive spacings.
SEARCH exits360.9s;recurrent last evaluated source360.884s. Common origin0,
no pre-admission PDE response. This is selected exposed-trajectory response,
not latent trapping-onset latency or the old30% target.
ResultSHA `6ea3755792eb0ed2e0bae5c9e9dede8b41af57c2bb435116a65f3725927eb915`.
Independent cached result review PASS:14 checks,13 stable receipt/output files,
reviewSHA `bdcd8d259be6ea03466543b2b58e0713301e4f7cd6fefdeae3a9193b7693ae20`.
All74 transport resets lie outside the admitted2.864–360.884s input interval.
The original PDE owner emitted candidate events313.4s/355.0s;its final
pre-shutdown dwell was5.7/6.0s. These remain candidates,not confirmations.
No bag or detector rerun occurred in review.

## Synthetic job started

Preparation0.050827917s,34 pins and16 historical input hashes verified;
preparedSHA `b8608b0389c6fafef7cf8c1ee0a2f11fcb5378a7e63315249fc5af3eb4cb0f91`.
Exact execution:
`timeout --signal=INT --kill-after=5s 175s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/run_job.py synthetic`.
Session14723 terminal/reaped0;PID89214.100.629277890s outer,
99.873091982s numerical result,99.927198718s completed helper receipt.
34 source/input pins and prepared manifest stable. All96 original histories and
114560 original source samples completed;no recurrent detector rerun.
ResultSHA `0014afc7c62986f82879cbc3736c021ebfea2cb91cd98b22a0d40d6d8a8fa6f5`;
receiptSHA `34e10f13eb24cca4db6a12ac5a1f800db157d4542cc8635a98ecbc5020faff06`.

| Positive class | PDE observed / total | New observed / total | PDE capped median / mean,s | New capped median / mean,s |
| --- | --- | --- | --- | --- |
| All |19/36|36/36|73.3635 /92.89675|42.024 /45.179833|
| Circle |10/16|16/16|70.65 /88.251188|42.0 /42.0075|
| Oscillation |8/16|16/16|96.2635 /94.065063|48.0235 /51.389688|
| Static |1/4|4/4|120.0 /106.80575|30.0475 /33.02975|

Missed responses contribute the fixed120s cap;all36 positives remain in the
summary. Seventeen PDE positives are right-censored;new detector positives are
all observed. The new36-positive capped median is descriptively42.7181% lower.
That percentage describes this finite synthetic response study and is not the
historical30% independent basin-entry estimand.

PDE confirms4/48 declared negatives:cases072/076 (large loops) and082/083
(recurrent source spikes). The new detector confirms0/48 negatives and at most
once per history. All three new-detector reliability predicates pass.
Twelve gray/withheld cases remain excluded;PDE responds on2,new on5,without
changing their labels. Raw repeated PDE confirmations remain in the case output.

Root independently recomputed case counts and full-positive medians from cached
`cases.jsonl`;they match. Independent synthetic review PASS:14 checks,0.117126s,
all reviewed hashes stable;reviewSHA
`deefcf3eeb56b0a326ccd85cc4dfdbacfb57b9b9bda95c1c74752e3d86472174`.
There are no repeated PDE confirmations within a case;all actual lists remain
retained. Review used cached cases/receipts,not a numerical or bag rerun.

Synthetic delivery uses the original100ms or71/113/127/97ms source intervals,
ideal delivered clock=source stamp,with actual PDE initialization/CFL clamping
and gates. These finite results do not reconstruct Gazebo callback timing or
establish performance at other input rates.

## Joint decision and boundary

Exact decision command:
`timeout --signal=INT --kill-after=2s 28s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/decide.py`.
Exit0;all eight prospectively declared checks passed. DecisionSHA
`e9e6cff5869aa3ba8c7d11b470ed00b5b0b34d54fcac34d44676a029e0ef601c`.
The decision binds completed results,reviews and execution receipts. It supports
designing a prospective integrated arrival/direction comparison;no matrix has
been released. Old first-positive-mask latency and30%target remain unavailable.
Both jobs are terminal;no runtime is active. [Handoff](../r10_paired_response_handoff.md).

Material archive complete after context/diff/checkpointPASS:592 individually
verified source/docs members,48 focused evidence refs,source/evidence stable,
0.874870774s. No raw bag or large synthetic timeline reread/hash.
Exact command: `timeout --signal=INT --kill-after=5s 50s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r10_paired_response_v1/save_closed_checkpoint.py`.
Manifest `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r10_paired_response_v1/manifest.json`
SHA256 `df23819df6c4f013f8790e414ce045e2b8d7a1b03959ee40f97ec550a349625d`.
This receipt postdates the archive;scientific sources and results stay unchanged.
