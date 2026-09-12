# M4 v6 conditional moving raw-evidence diagnostic

Completed 2026-09-10 UTC. This independently reviewed, bounded offline diagnostic
completed its single fixture/C/D sequence. All eleven candidate windows and all
70 scheduled evaluations were retained. It identifies specific unchanged M3
guards that block under the declared delivery schedule; it does not recover
unrecorded supervisor callback timing, reclassify M4v5, or qualify either research
objective. M4v5 remains CLOSED_INCOMPLETE; final D remains right-censored.

## Frozen method and execution

Prospective authority and exact scheduling are in
`../m4_v6_raw_evidence_reconstruction_plan.md`. The only evaluated inputs were
the completed C/D exports from `m4_v6_development_diagnostic_v1`; no original
bag was read again. Complete generated messages were restored, including tagged
NaN/Infinity and nested/fixed fields, and checked by full round-trip equality.
The existing MovingSupervisor direction/provenance/readiness/pose methods and
MovingRawEvidence evaluator were reused without a production source change.
There was no ROS initialization, acquisition, model/reference/primary-metric
job, public snapshot, state-machine step, parameter sweep or retry.

The single schedule preserves per-topic recorder order, merges by bag time and
fixed alias/index ties, advances a detached ROS clock using recorded /clock and
publication catch-up, and uses recorder time spacing as detached steady time.
Those clocks and cross-topic ordering are conditional assumptions. Results are
neither exact runtime causes nor upper/lower bounds on readiness. In particular,
the absence of real snapshots leaves callback acceptance time as an interval,
not a reconstructed point. Its deadline bounds remain exactly acceptance+12 s.

All C/D windows were frozen before C's first evaluation. Ten have recorded
VERIFY-to-SEARCH returns. D7 is censored by its recorded readiness/stop endpoint;
its missing return is not fabricated. Evaluation occurred at entry, cycle/reset
changes, and the final recorded VERIFY sample, with the prospective 256-per-
candidate cap. All 70 delivered evaluations are before the earliest conditional
deadline; this timing label does not establish actual callback admission.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_raw_evidence_reconstruction_v1/`.
Exact clean Humble -> Q2 -> Q5 commands/environment are in each
`{fixture,C,D}_command_v1.json`; complete output is in the corresponding
`*_execution_v1.log`. Root ran the following single sequence:

```
timeout --signal=INT --kill-after=1s 44s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_raw_evidence_reconstruction_v1/run_job_v1.py fixture
timeout --signal=INT --kill-after=1s 129s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_raw_evidence_reconstruction_v1/run_job_v1.py C
timeout --signal=INT --kill-after=1s 129s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_raw_evidence_reconstruction_v1/run_job_v1.py D
```

| Job | Outcome | Inclusive elapsed | Prospective cap |
|---|---|---:|---:|
| Synthetic fixtures | 21 PASS, pytest 1.38 s | 2.432620512 s | 45 s |
| C | Conditional diagnostic complete; 4 candidates/28 evaluations | 81.303188809 s | 130 s |
| D | Conditional diagnostic complete; 7 candidates/42 evaluations | 64.256769546 s | 130 s |
| Total | No interrupted job, forced kill, failure or retry | 147.992578867 s | 305 s |

The 120 s C/D work allowance plus 10 s exit/hash allowance was saved before
execution following review of repeated generated-message restoration work. It
was an offline diagnostic allowance, not renewed simulation/science budget.

## C: spatial support and cost-profile failures are distinct

All 28 conditional evaluations have recording-ready true and a fresh pose
inside the fixed 0.75 m candidate radius. They do not exhibit a missing-pose,
readiness or deadline blocker under this schedule.

C1 returns `missing_qualified_neighborhood_cycles` at all seven evaluations.
By its last evaluation it has 30 completed, phase-qualified sensor revolutions;
24 stay within the 0.75 m radius, but only two have their time-integrated base
centroid within 0.15 m of the fixed confirmation center. Those two distances are
0.144845 and 0.129785 m. The five revolutions completed during its VERIFY window
have centroid distances 0.321846, 0.354524, 0.325863, 0.253705 and 0.170677 m.
Their entire trajectories fit the radius, but their centroid margins are
negative. This conditional failure is spatial representativeness, not absent
phase coverage. No profile evaluation was reached; later cost guards remain
unavailable for C1.

C2-C4 each have 31 completed/qualified revolutions by their last evaluation,
all within radius, and four eligible cycles. Each selected latest-three set
passes the 0.15 m sector-trajectory comparison comfortably. Each set remains
unchanged throughout all seven evaluations; its three cycles are all pretrigger.
New VERIFY cycles do not meet the fixed-center centroid requirement. Selected
cycle starts are about 18 s apart, so these sets represent recurring visits to
the qualifying geometry rather than three adjacent sensor revolutions.

The raw evaluator groups several predicates under `uninformative_raw_profiles`.
The retained margins resolve them as follows. All values below are from the
unchanged selected raw-cost scale; the information floor is 0.000001 throughout.

| Candidate | Amplitude A | Disagreement D | A - max(3D,floor) | Median minimum estimate | MAD | Uncertainty | Upper cost bound | Specific failing guard(s) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C2 | 0.025113516 | 0.003201147 | +0.015510074 | -1.057325459 | 0.444551936 | 1.333655809 | +0.276330350 | Conservative upper cost bound is not negative |
| C3 | 0.042408031 | 0.040596469 | -0.079381375 | -2.235209405 | 0.232722757 | 0.698168272 | -1.537041133 | Profile disagreement exceeds the information allowance |
| C4 | 0.019274141 | 0.011902953 | -0.016434718 | -1.069157863 | 0.494101191 | 1.482303572 | +0.413145709 | Both information and conservative upper cost bound |

All three baseline-negativity checks pass: baselines are -0.009513527,
-0.015204918 and -0.007800444. Sector-centroid margins are respectively
+0.123354472, +0.098755205 and +0.124627743 m. Boundary support counts are
237, 233 and 240, well below the unchanged 4000 snapshot cap. These failures
are not numerical-floor or capacity failures. Calling all three merely
"insufficient amplitude" would misstate C2, whose amplitude comparison passes.

## D: short revolutions do not represent the frozen detector center

All 42 conditional D evaluations return
`missing_qualified_neighborhood_cycles`; none has even one eligible cycle.
Recording-ready and fresh pose-inside are true at all evaluations. Every
completed cycle in the final evaluation of each candidate is phase-qualified,
with at least five actual observations per sector. Short sensor cycles last
approximately 2.44-2.98 s, far below the 30 s cycle limit.

| Candidate | Evaluations | Completed/qualified cycles at last evaluation | Cycles within 0.75 m radius | Minimum cycle-centroid distance to fixed center | Window disposition |
|---|---:|---:|---:|---:|---|
| D1 | 6 | 26 | 20 | 0.237643 m | Closed return |
| D2 | 6 | 18 | 18 | 0.239322 m | Closed return |
| D3 | 6 | 18 | 18 | 0.239491 m | Closed return |
| D4 | 6 | 18 | 18 | 0.228561 m | Closed return |
| D5 | 7 | 18 | 18 | 0.220061 m | Closed return |
| D6 | 6 | 18 | 18 | 0.236988 m | Closed return |
| D7 | 5 | 17 | 17 | 0.233779 m | Right-censored |

For D2-D7 every reconstructed cycle stays inside the outer neighborhood yet
misses the 0.15 m centroid tolerance; even the closest is 0.070061 m beyond it.
D1 includes earlier approach cycles outside radius, but its later VERIFY
cycles also fail the centroid requirement despite fitting inside radius.
D7's observed interval ends at 360.6 s after entry at 351.0 s; it is not treated
as a full verification timeout or an observed return. No D profile reached the
later information/cost guards, so this diagnostic makes no claim that D would
pass those guards if its geometry changed.

## Interpretation and next work

The combined evidence supports a representativeness mismatch for separate
method review: the selected centroid detector describes a stable center over
36 s of history, while a short sensor revolution samples the base locally as
the robot moves around that center. A stable long-horizon orbit center does not
make each short-revolution base centroid close to it. The D guard distances and
C's recurring, widely spaced qualifying cycles support this interpretation;
they do not by themselves identify exact runtime callback causes.

The strict guards correctly withhold a snapshot under the reconstructed
conditions. Increasing radius/epsilon, relocating the frozen candidate, waiting
past 12 s, choosing a favorable older cost triple, or reducing the uncertainty
or information requirement is not justified by this result. Those changes would
alter the declared evidence contract to accommodate the failed observations.

A coherent candidate correction is to make the existing moving VERIFY control
path collect spatially representative evidence near its frozen center while
continuing bounded motion. A selected centering assist through the existing
supervisor proposal/controller owner requires its own prospective method/source
amendment and control/freshness/recording tests; it is not adopted or implemented
by this diagnostic. Whether it can collect three sufficiently comparable cycles
within the unchanged 12 s interval remains an acceptance question, not a promise.

C additionally requires a bounded signal-repeatability diagnosis using exactly
the already selected cycles, with no favorable reselection: compare their
recorded raw waveforms, sector profiles and minima against measured sensor phase
and base geometry. C2's negative excursions vary enough to make its conservative
upper bound positive; C3's centered profile varies across its selected cycles;
C4 exhibits both. The present summaries do not distinguish field shape,
measurement variability or trajectory-conditioned sampling as the cause.
Publishing the existing M3 evaluation reason at cancellation through an existing
observability owner would also remove a future runtime diagnostic blind spot,
without weakening readiness or inventing retrospective causes.

## Exact closure evidence

The immutable external `diagnostic_hold_v1.json` binds all commands, logs,
results, generated window identity, helper pins and before/after/exit audits.
Its SHA256 is
`6984b2b34791326d551e39c68e3d32a0d83ad618191d2d6857cac69c7ee20f43`.

| Artifact | SHA256 |
|---|---|
| Prepared review manifest | `2e9753a7e58f0e59cfc7715f4657222a7a5343f67a56bb32985cb7d87ed34744` |
| Frozen eleven-candidate windows | `639927e680b8cff0a961c9887c7ffb27d16b10a5329af4c55f67b948bfd9f964` |
| C result | `cf8204333ca369fb993a31bafd5f510c7005dd7ca71a33317a9081d6d89bce3a` |
| C evaluation stream | `8aceefc29c8ac2afae771b155e5882170c30cc4a3398eedb61bee3fcb6bda53e` |
| D result | `0b2bc60cb5999619ff18ade0e5ec0566a09cf5538357d4d60e6b237f2bb44c46` |
| D evaluation stream | `10a0d7e2e1f9259999eff89e0b388490c948b0fe4faae21c981aaf096ceb0362` |

At this diagnostic closure, all 623 current production source pins matched the
frozen v5 validation receipt. Each job's complete before/after/exit maps matched;
the review manifest binds five helper/plan/README pins and 51 retained input
pins. Closeout rechecked source bytes and completed audit/result JSON; it did
not reopen bags or decoded extraction payloads or invoke a numerical owner.
The hold seals this boundary before any separate heartbeat/control amendment.
Root owns the live-status/handoff/ledger/checkpoint and next source release.
