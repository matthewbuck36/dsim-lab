# Global arrival acceptance amendment — 2026-09-10

ADOPTED from the user's in-run clarification: reaching the global minimum is
the desired outcome; reaching the controller's GOAL_HOLD state is not required.
This supersedes prospective GOAL_HOLD/second-candidate requirements in the V2
plan, method amendment and integrated development/comparison acceptance where
they conflict. Preserve the existing runtime safety stops and selectable final
holding behavior. No algorithm change is needed solely to obtain GOAL_HOLD.

For the current declared two-source simulation, use the already selected
evaluator-only global-source proximity radius of 0.5 m. A recorded pose inside
that radius establishes arrival at the experiment's spatial resolution; do not
claim exact equality with the mathematical minimizer or a controller-recognized
goal. Report first arrival, minimum and final distance when available, alongside
recording completeness, lifecycle validity and cleanup. Source coordinates stay
out of the search, detector, verification and fill algorithms.

For integrated Gaussian-escape evidence, continue to require a valid local
candidate, moving verification, committed fill, completed escape and resumed
search preceding global arrival. These establish what produced the arrival.
Arrival does not replace component false-detection or direction-quality checks.
Future stop/evaluation settings may end at recorded post-recovery arrival and
must be saved before the next experiment. Do not require a second convergence,
terminal ranking event or GOAL_HOLD as prerequisites to arrival success.

Attempt02 had already ended when this clarification was received. Preserve its
original frozen scenario, COMPLETE recording and failed historical full-lifecycle
classification. Evaluate the retained observations separately under this explicit
user-revised arrival criterion; this is exposed development evidence and not an
untouched confirmation. Its final recorded position is (3.7386775389353977,
3.416172282538263), 0.2529704603448851 m from the declared global source (3.5,3.5).
The existing analyzer reports VALID lifecycle with no errors and one actual
candidate, snapshot, preparation and unique committed fill. Scoped cleanup passed.

The original evaluator's local-source association also failed because it compared
the recurrent diagnostic's latest input pose stamp (78.008 s) to the fill's
confirmed support endpoint (78.0 s). Diagnose and correct that private evaluator
coordinate prospectively; retain both original timestamps and old verdicts.
This issue does not erase the actual typed fill/escape path or measured arrival.

The final selected evaluator distinguishes exit bearing from command authority:
[alignment separation](r3_arrival_alignment_separation_plan.md) preserves every
ownership, freshness, command-limit, measured-exit and handoff check while
reporting bearing alignment as a geometric diagnostic. This follows the user's
arrival objective; original frozen classifications stay unchanged.
