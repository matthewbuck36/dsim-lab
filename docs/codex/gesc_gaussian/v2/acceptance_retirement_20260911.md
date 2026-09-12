# V2 acceptance update and unresolved-issue triage — 2026-09-11

## User-accepted simulation closeout

The user explicitly states that simulation work for the new Test D algorithm
is done and will open a fresh chat to discuss real-robot source integration.
The accepted simulation scope is COMPLETE with its recorded limitations.
Retired targets and deferred issues do not automatically reopen that scope.
Physical implementation and validation remain separate future work; no transfer,
physical source edit, hardware operation or new simulation occurred here.
The [fresh-chat handoff](fresh_chat_handoff.md) records the compatibility starting
points, including physical clocks/adapters and V2's current simulation-only
admission checks. Existing runtime GOAL_HOLD remains optional for acceptance.

Documentation closeout checks passed: `timeout 30s bash
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
v2 plan`, the same command with `v2 implement`, and `git diff --check`.
Direct review of all six changed documents checked added whitespace and links;
before copies and `documentation.patch` are in
`/tmp/dsim-v2-simulation-closeout-uuqwt_1j/`.
Final receipt: [checkpoint.txt](checkpoint.txt), generated with
`timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`.
No runtime tests/build were needed for this documentation-only closeout.
Git remains V2 at `3369cfc` with uncommitted work; no commit or push performed.

## Latest user decision: accept Test D; defer investigations; retain GOAL_HOLD

The user subsequently asked to "forget the bug fixes on those tests" for now
and to keep GOAL_HOLD optional. This supersedes the diagnostic priorities below.
Defer the stale-fill, C/D command-consistency and missing-direction-anchor
investigations. A's baseline failures and C's partial-method failures are accepted
comparison outcomes. No runtime repair or new experiment is scheduled.
Keep the existing runtime GOAL_HOLD behavior; reaching it remains optional for
arrival acceptance. Its removal is no longer planned. The 30% detector-delay
target remains retired. Historical failures remain recorded, not relabelled fixed.

The user's final follow-up accepts **Test D as the working GESC + Gaussian
baseline** and considers the current improvement/demonstration work settled.
No additional repair or test is required under the current request. Keep the
earlier cancellation and command-ownership issues deferred; reconsider them if
future evidence shows a material problem or the user requests investigation.
A, B and C remain comparison arms. Their historical failures are not repair
targets or prerequisites for accepting D. Preserve their selectable behavior
and all study results. This is practical acceptance of the demonstrated D
behavior; earlier failures and scientific limitations remain documented.

Final practical-acceptance documentation validation: plan/implement context
validators and `git diff --check` passed. Five navigation/decision documents
were reviewed against pre-edit copies; all prepared runtime/source hashes remain
unchanged. Exact commands, scope and patch are retained at
`/tmp/dsim-v2-D-accepted-tc2wdmyf`. No runtime tests or build were needed;
no experiment, code change, commit or push was performed. The current
[checkpoint](checkpoint.txt) records this documentation boundary.

### Five most recent launched visible runs, checked from terminal records

Ordered oldest to newest by UTC run identity; the last row occurred on September
11 in the user's local timezone. Root prefix:
`/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/`.

| Directory under that root | Arrival, simulation seconds | Command ownership | Fill evidence |
|---|---:|---|---|
| `20260911T211235Z_D_nominal_visible_half_speed` | 150.807 | FAIL | One commit; zero moving-fill terminal failures |
| `20260911T213153Z_A_nominal_visible_half_speed` | 313.450 | PASS | One fill; no failed-fill event reported |
| `20260911T234202Z_D_nominal_visible_normal_speed_phone` | 164.150 | FAIL | One commit; zero moving-fill terminal failures |
| `20260911T235211Z_D_nominal_visible_normal_speed_repeat` | 158.053 | PASS | One commit; zero cancelled/expired/rejected results |
| `20260912T000449Z_A_nominal_visible_normal_speed` | 210.823 | PASS | One fill; no failed-fill event reported |

All five arrived and passed recording completeness and native/outer cleanup.
The latest D and A each passed all 11 scenario predicates, without a source
change. D took 52.770 fewer simulation seconds (25.0305%) in that matched normal
pacing pair. The three D runs have zero terminal failure results in the retained
V2 lifecycle metrics. A uses the legacy stationary path, so a V2 cancellation
counter is not applicable; its event/state summaries show one fill and successful
recovery with no failed-fill event. No complete raw A fill-result stream was
newly extracted for this review.

This confirms that the latest pair succeeded without the earlier ownership
failure and that D's cancelled fills did not recur in these three successful D
runs. The ownership issue did recur in two earlier rows of this five-run sample.
The evidence supports deferral by user choice; it does not establish a repair or
explain the intermittent failures. The older three-cancellation run is outside
these five latest launched demonstrations and remains preserved.

Review used `attempt_result.json`, its hash-matched `scenario_summary.yaml`,
each run's `completeness.json`, cached post-run reviews, and the A text logs and
event summaries. No bag database, simulator, scientific pipeline or runtime
source was changed. The bounded metadata extraction and pre-edit document copies
are retained at `/tmp/dsim-v2-five-runs-ox07mf4w/`; `review.json` records the five
rows and SHA-256 identities of the 15 terminal input files.
Pre-edit `timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passed. Post-edit plan/implement context validators and `git diff --check` PASS;
direct comparison of all five edited documents checked added whitespace and
current links, and all 15 terminal input hashes are unchanged. Review patch:
`/tmp/dsim-v2-five-runs-ox07mf4w/documentation.patch`.
Final checkpoint command:
`timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`;
receipt: [checkpoint](checkpoint.txt). No runtime tests/build are needed for
this decision. V2 remains at `3369cfc`, with prior work and these documentation
changes uncommitted; no commit, push or physical action was performed.

The earlier retirement amendment and triage below are retained history; their
proposed next investigations and GOAL_HOLD removal are now deferred/cancelled.

ADOPTED from the user's explicit request: "yes, retire it", referring to the
30% detector-delay target. The user accepts the noticeable improvement shown
by the completed 16-run comparison and wants to prioritize unresolved bugs.

## Decision and evidence boundary

Retire the requirement to demonstrate a >=30% reduction in median detection
delay measured from independently labelled trapping onset. It is no longer
an active V2 acceptance criterion or a prerequisite to further development.
No replacement percentage or new experiment is required. This supersedes
prospective requirements in the root plan and restart instructions.

The original study endpoint remains EVIDENCE_UNAVAILABLE: it had no valid
independent-onset pairs. Retirement is a change of future objectives, not a
claim that the endpoint passed. Preserve the closed R25 results, original
contracts, report products, and historical evaluator code unchanged.

The selected improvements are accepted as sufficient to proceed with D as the
development baseline. This does not establish universal, acoustic, or physical
robustness and does not close the unresolved runtime issues below.

Practical success remains local fill, escape, resumed search, and arrival within
the existing evaluator-only 0.5 m global-source region. GOAL_HOLD and second
candidate ranking are not arrival requirements. Runtime GOAL_HOLD still exists;
removing it is separate proposed work, not accomplished by this amendment.

## Remaining criteria and their relevance

| Criterion or result | Current evidence | Effect on the next work |
|---|---|---|
| >=30% independent-onset detector improvement | Historical evidence unavailable | RETIRED prospectively; no blocker |
| Direction median <=30 degrees, P90 <=60 degrees, averaging availability >=80% of eligible intervals | D passes available-sample summaries; D/noise lacks one scheduled anchor | Retain scientific reporting criteria; incomplete coverage limits the strict claim, not permission to diagnose or fix bugs |
| Zero mandatory stopped acquisitions | D meets this in all four study runs | Preserve this improved behavior |
| Local recovery and global-region arrival | D has four qualified study arrivals; later failed demonstration remains | Accepted selected-study improvement; investigate demonstration reliability |
| GOAL_HOLD / second terminal ranking | Already optional under the arrival amendment | No acceptance blocker; runtime simplification remains separate |
| Valid commands, fill consistency, recording and cleanup | Study D passes; later demonstration ownership discrepancy unresolved | Continue applicable correctness checks; report each outcome separately and investigate actual defects |
| Broad field, acoustic, and physical validation | Not established | Separate future scope, not a prerequisite to simulation bug fixes |

No additional research acceptance criterion must be completed before the
following diagnostics. This does not retire the numerical direction criteria
or automatically relax runtime guards, command checks, or recording checks.

## Bounded next work, in order

1. **D's three cancelled fills.** Start with retained data from
   `demonstrations/20260911T210019Z_D_nominal_visible/` under
   `/home/mattb/Experiments/GESC-Gaussian/v2/`. The compact diagnostic records
   three primary cancellations: 98.7 s (`stale or invalid state`), 165.4 s and
   238.1 s (`stale or changed epoch context`). Each is followed 0.2 s later by
   `preparation terminal` for the same candidate; these are follow-up command
   rejections, not three additional independent fill failures. Trace the
   existing fill/supervisor owners to distinguish timestamp age, receipt age,
   identity changes and callback ordering. The compact diagnostic cannot
   distinguish these causes. CPU pressure remains a hypothesis. No blanket
   freshness-limit increase or guard deletion is justified yet.
2. **Command consistency in C nominal and the later D demonstration.** Inspect
   the first mismatching diagnostic and its controller/state context using
   retained evidence. These share an offline predicate; a shared root cause is
   not established. Preserve observed arrivals independently. Fix runtime or
   measurement alignment only when the evidence identifies the defect.
3. **D/noise missing direction anchor.** Lower-priority measurement investigation:
   target 7, offset 195 s, target_ns=197229000000. Determine whether the gap comes
   from coverage, extraction or evaluation. Keep the original missing row and
   strict qualification unavailable; any justified derived correction needs a
   separately identified evidence view. A new noise matrix is not required to
   begin the first two diagnostics.

A's three nonarrivals and C's noisy nonarrival/direction failure are retained
comparison outcomes. Making those comparison arms succeed is not a prerequisite
to improving D. Investigate a shared defect if evidence points to one; do not
retune or rerun them simply to make the historical table pass.

Use the existing readers and runtime owners. Analyze only closed recordings;
never query an actively written database. No new simulation, matrix, physical
work, runtime refactor, commit or push is part of this documentation update.
Bound any subsequent evidence extraction and save its exact scope before work.

## Validation and handoff

This milestone changes acceptance documentation and records initial triage only.
The cancellation, command-consistency and missing-anchor causes remain
undiagnosed; no runtime fix is claimed.

Pre-edit command:
`timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passed. Git was V2 at `3369cfc` with the prior uncommitted implementation.
Pre-edit copies of the four navigation files and checkpoint, plus SHA-256
identities of ten protected study/report/runtime files, are retained at
`/tmp/dsim-v2-acceptance-retirement-dvae_e7i/` for this edit's review.
Post-edit validation:

- `timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan`: PASS.
- `timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`: PASS.
- `git diff --check`: PASS. Because these V2 documents are already untracked,
  the five edited documents were also compared directly to their pre-edit
  copies; the review patch is `review.patch` in the temporary directory above.
  Added-line whitespace and all amendment links pass. The first all-lines
  whitespace assertion found seven inherited trailing-space lines in status.md;
  those existing lines were preserved and the final review checked new lines.
- All ten protected study/report/runtime SHA-256 identities are unchanged.
- Source review of `v2_fill_runtime.py` confirms `preparation terminal` is a
  response to a command for an already terminal/cancelled preparation. No raw
  recording database was queried; only the existing compact JSON records read.
- Final checkpoint command:
  `timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`;
  its generated receipt is [checkpoint.txt](checkpoint.txt).

No runtime test or build was needed for this documentation-only amendment.
The source and report limitations above remain unchanged. Next incomplete
criterion is identifying which live condition rejected D's fill preparation,
using bounded retained-record analysis before any runtime correction.

Sources: [R25 closeout](r25_five_case_completion_handoff.md),
[demonstrations](visible_advisor_demos_20260911.md),
[arrival amendment](global_arrival_acceptance_20260910.md), and the closed
demonstration's `live_fill_result_diagnostic.json` / `demonstration_failure.json`.
