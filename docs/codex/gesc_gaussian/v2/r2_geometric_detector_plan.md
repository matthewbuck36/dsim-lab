# R2 geometric detector development prototype

ADOPTED 2026-09-10 UTC under the method/development amendment, following the
R1 material checkpoint. This is an offline circle/static model prototype;
no production source, old outcome, field truth, bag, hardware or holdout changes.

## Hypothesis, equations and fixed decision

Partial geometric circle support may recognize B's slow loops sooner than
period-sensitive block means, if competing center translation is excluded.
No constant angular speed or1.5-cycle requirement is imposed. Unknown/ambiguous
support remains withheld. Oscillation recognition is explicitly unsupported in
this prototype; the failed two-block rule is not used as an acceptance fallback.

At each causal evaluation, use all samples from supports18,24,30,36s, at6s
endpoint increments. For each support and candidate velocity v, let
`z_i=p_i-v*(t_i-t_mid)` and fit
`||z_i-c||^2=r^2` through time-weighted algebraic least squares:
`z_x^2+z_y^2=2*c_x*z_x+2*c_y*z_y+k`, `r=sqrt(k+||c||^2)`.
Reuse the exact R1 weighted least-squares function from its saved helper by
loading only that function's AST; never execute the R1 helper's top level.
Calculate actual radial RMS, unwrapped angular span about c, full trajectory
radius about the time-weighted measured mean, rank and conditioning.

The zero-drift candidate requires rank3, finite radius in [.03,.50]m,
radialRMS<=.02m, unwrapped angular span>=2*pi/3 and actual trajectory radius<=.50m.
Reject rank-deficient/nonfinite solves; retain conditioning for diagnosis.
The radius and actual support checks limit large-loop/arc interpretations.

Compare fixed translating alternatives at speeds .01,.02,.04m/s and headings
0,pi/4,...,7*pi/4. Also calculate speed.005m/s as diagnostic allowed-drift rows.
Each alternate fit uses the same radius, radialRMS and angular-span screens on
its transformed trajectory; actual-radius bound remains on the measured path.
If any appreciable-drift alternate passes and has radialRMS
`<=min(.02, zero_drift_RMS+.002)`, withhold the zero-drift detection as ambiguous.
The .005 rows cannot veto. A discrete grid is not proof of rejecting all drift;
independent off-grid controls below test this limitation explicitly.

Separate near-static branch: over the last12s, require full source support,
time-weighted measured-mean radius<=.03m and norm of weighted least-squares
linear position slope<=.005m/s. This tolerates tiny movement; it does not
establish a source, fill or goal. No period/shape fit enters this branch.

Any passing static or circle support yields one candidate per trace, while all
later decisions remain retained for diagnosis. Source gaps>.50s, regressions,
conflicting duplicates, invalid positions/frames and unsupported boundaries
cannot contribute support. Boundary interpolation requires actual brackets;
never extrapolate. Candidate time is the endpoint, with no look-ahead.

## Inputs and fixed73-control population

Read the completed R1 `readiness_poses.jsonl`, `result.json`, `control_contract.json`,
`control_samples.jsonl`, and saved R1 helper from
`development/20260910/detector_b_v1/`. Original five B exports remain untouched;
no repeated decode. B uses readiness-clock origin3.8s and source timestamps;
initial insufficient-boundary support is withheld. Every endpoint through the
recorded readiness end is retained. There is no independent B latency label.

Preserve all28 R1 controls and their exact120s/dt.1s samples. Add the following45
traces, all120s/dt.1s, with no output-driven selection. All new circles have
radius.25m unless explicitly large. Coordinate noise is independent Gaussian,
using NumPy default_rng(20260910) once in the declared sequence below; noiseless
cases do not consume random samples.

1. Twelve fixed circles: P in {54,60,66,72}s, phase in {0,pi/2,pi}.
2. Six noisy fixed circles: P60s, sigma in {.002,.01}m, same three phases.
3. Twelve off-grid translating circles: speed in {.015,.025}m/s, heading in
   {pi/8,3*pi/8}, P in {60,66,72}s, phasepi/2, sigma.002m.
4. Four translating circles: speed in {.02,.04}m/s, those two off-grid headings,
   P60s, phasepi/2, noise0.
5. Three radius1m circles: P in {60,66,72}s, phase.73, sigma.01m.
6. Three straight drifts: speed in {.005,.015,.025}m/s, headingpi/8, sigma.002m.
   The .005 case is tolerated/gray diagnostic, not a declared-negative result.
7. Two noisy static traces: sigma in {.002,.01}m.
8. Three oscillations: amplitude.25m, P in {60,66,72}s, phase.73, sigma.002m.

All circles with fixed center and all static traces are declared positives.
All moving-center/straight-progress traces above.005m/s and large loops are
declared negatives; off-grid.015m/s is intentionally stricter than R1's.02.
All original and new oscillations remain unsupported/withheld for method-scope
reporting: record any prototype trigger but do not call them validated positives
or assume they are negatives. The .005 straight trace is likewise separate.

## Finite job, complete outputs and next decision

Exclusive directory: external V2 root
`development/20260910/geometric_detector_v1/`. Save plan/helper/command before
the single job. One118s SIGINT timeout with2s kill-after; internal110s work
limit. No unchanged numerical retry. Preserve failed/partial outputs.
Only pin this plan/helper, the reused R1 helper and five named R1 artifacts;
other agents may edit unrelated owners. Use no runtime numerical owner import
besides the isolated R1 weighted-lstsq function. This external prototype is
method exploration, not a duplicate production analyzer or runtime selector.

Retain each trace contract and all added samples, every static/zero-drift
evaluation and all32 alternatives when zero-drift geometry passes, including
rejection reasons, coefficients, residuals, radius/angle/conditioning and
candidate times. Alternate evaluation may be skipped with an explicit reason
when zero-drift geometry already fails. Retain every B endpoint and every
synthetic trace, even zero-data/never-trigger cases. Report candidate rate,
first time, branch, ambiguity counts, positive misses, negative triggers,
unsupported oscillation triggers and gray behavior. Verify exclusive artifact
hashes and selected-input/source equality and save exact timing/outcome.

No nomination if any declared negative triggers or intended circle/static
positives are missed. A failed prototype can motivate an explicitly changed
version after retaining this result. Passing these controls is only measured
development feasibility; integrated behavior, independent validation and
general motion identifiability remain separate requirements.
