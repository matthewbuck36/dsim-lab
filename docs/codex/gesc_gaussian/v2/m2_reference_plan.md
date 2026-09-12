# M2 stationary GESC reference protocol — frozen 2026-09-09 UTC

This is the prospective M2 development reference version `m2-reference-v1`.
It is frozen before new model/reference calculations. It extends `m2_plan.md`
and changes no M1 labels, detector setting, holdout population or pilot gate.
The existing bag analyzer owns execution; a subordinate numerical helper is
allowed. No separate analysis pipeline, physical action or Gazebo release.

## Meaning and exact selected dynamics

At fixed base position p and frozen objective composition, J(p,theta) is the
existing evaluator's angular cost, including its sensor position/orientation.
The selected sensor joint has zero XY displacement, identity mount rotation,
joint height .355 m, and sensor displacement (.18,0,.015) m. Reverify the full
binding against recorded configuration; reject other geometry. Under this
binding theta is observed world sensor phase and also world demodulation phase.
For runtime/reconstructed input, effective body phase is theta minus the
interpolated base yaw. Do not infer phase from the nominal rotation command.

The selected filter has d=.18 m, washout alpha=1/s, zdot=alpha*(J-z), and
q_body=-(2/d)*(J-z)*[cos(phi),sin(phi)]. Its output precedes its forward Euler
state update. Define the exact angular coefficients

`mu = integral(J dtheta)/(2*pi)`,
`a = integral(J*cos(theta) dtheta)/pi`,
`b = integral(J*sin(theta) dtheta)/pi`.

For signed constant world angular rate Omega, write
`Hc = i*Omega/(alpha+i*Omega) = u+i*v`. The primary reference is

`q_ref_world = -[u*a+v*b, u*b-v*a]/d`.

Rotate by minus the current base yaw only when comparing body vectors. This is
the steady-state continuous washout/full-cycle demodulation mean. Higher angular
harmonics have zero continuous mean contribution by orthogonality. Nonlinear
light angular response remains in J; this is an averaged GESC improvement
signal, not a proven spatial gradient, attraction basin or trajectory truth.
Finite washout startup, translating p, variable rate, evolving objectives and
nonuniform sampling make the reference a local stationary counterfactual.

Report the observed signed rate from the latest complete monotonic world-phase
revolution: Omega=sign*2*pi/duration. Nominal 20 rpm (2*pi/3 rad/s; 3 s) is a
separate value. Constant-rate approximation requires time-weighted coefficient
of variation of interval rates <=.10, with finite positive time increments and
no opposite-signed phase increments beyond 1e-12 rad. Report rate variation and
base translation rather than claiming stationary execution.

The required numerical sensitivity is
`Hd = (exp(i*Omega*h)-1)/(exp(i*Omega*h)-1+alpha*h)` for output-before-Euler.
Use median observed h only when every interval differs from it by <=1% and
0<alpha*h<2. Otherwise mark Hd unavailable. Hd describes the first-harmonic
uniform-sample response; high angular harmonics can alias under actual sampling.
Cadence uses actual source interarrival intervals; an interpolated cycle boundary
is not an additional observation. Each of twelve absolute 30-degree sectors needs
two actual observations inside the full cycle for input-coverage qualification.
Neither Hc nor Hd claims exact irregular-callback parity. Replay uses the actual
selected custom-filter implementation and preserves explicit timing choices.

## Frozen numerical integration and informative reference

Integrate mu, a and b independently with scipy.integrate.quad on [0,2*pi]. Each
integral is evaluated with two independent breakpoint sets: every 30 degrees,
then the same lattice shifted by 15 degrees. Both sets additionally contain all
source bearings and antipodes at p. Use epsabs=normalization*1e-7, where
normalization is 2*pi for mu and pi for a/b; epsrel=1e-7; limit=128. All finite
results are mandatory; any warning or integrator failure makes the anchor
unavailable. Cache exact floating angle calls within an anchor, with a maximum
25,000 distinct objective evaluations. There is no fallback coarse angle grid.

For each coefficient use the mean of the two estimates. Its error estimate is
the maximum of both normalized reported errors and their absolute disagreement.
Every coefficient error must be <=1e-6. These are independent numerical checks
and estimates, not certified integration bounds. Retain both complete receipts.

Let E_q=abs(Hc)*hypot(error_a,error_b)/d. Reference direction is informative only
when norm(q_ref)>max(1e-6,20*E_q), in filter-output units. This gives an estimated
angular uncertainty <=asin(1/20), approximately 2.87 degrees, from integration
alone. Never normalize weak vectors. The method's own confidence or magnitude
does not select the reference population.

Analytic fixtures cover DC, first sine/cosine and higher harmonics, signed-rate
reversal, yaw covariance, Hc/Hd cadence convergence and unstable-step rejection.
At nominal rate Hc=.8143503760075071+.38882366325101514i. For J=cos(theta), the
reference is (-4.524168755597262,+2.1601314625056396). Tests also exercise narrow
analytic angular peaks, integration warnings, budget exhaustion, numerical weak
references, rotating Gaussian/affine corrections and exclusive receipt writes.

## Matching the objective

At each anchor freeze causal source/weights/fill/affine-law identity. Evaluate
raw angular cost through the existing model owner. Add active Gaussian terms
at each rotating sensor position using the selected covariance/amplitude law;
add affine terms at that sensor position with the actual vector evaluated at
the anchor's composition time. Their scalar weights must match the stream.
SEARCH can contain prior fills or return assistance; state name alone does not
establish a raw objective. Require causal complete fill/affine provenance.
Scalar CostBreakdown values alone cannot reconstruct an angular objective.

Missing reconstruction or identity is an unavailable augmented reference,
never permission to substitute raw cost. A separately named raw-only reference
can compare a matching raw demodulation stream, not augmented/repulsion output.
The primary bounded job evaluates augmented references only. Any diagnostic
raw-only study needs its own predeclared population/version.

## Fixed population, timing and receipts

Use the same eight development seeds 19801,19811,19851,19901,19911,19931,20001,
20031 and inventory SHA256
`eae9b60fc2f6f3e638f7ee9e56fd52174176fb4495de78bb145640eddb93e90d`.
The thirteen retrospective holdouts stay excluded. Reverify each bag, resolved
input/configuration, historical sensor binding and evaluator owner hashes.

Preselect 24 source-time targets per bag at readiness-origin+10*k seconds,
k=1..24. Readiness-origin is the source time of the first raw input received at
or after the first true recording-ready record, mapped by the single valid
recorded simulation Timekeeper origin. Readiness is a receipt-based proxy in
old bags and is recorded as such. Choose the first causally qualified sample at
or after each target within 50 ms; missing, late or end-of-bag targets remain
unavailable without replacement. Freeze all 192 target identities before any
method output or field evaluation. Same anchors/objective for both methods.
The selection comparison uses model-input stamp (the explicitly named model-input
proxy for old bags), so later publication cannot admit an observation that
precedes its target. The raw-publication readiness origin remains as defined.

Resolve selected configuration from recorded target_argv plus the recorded
commit's launch XML defaults, not current launch defaults. Verify the selected
filter/model against frozen parameter-file provenance and Git blobs; verify
selected transform JSON and URDF blobs and the live robot_description captured
in resolved_parameters.yaml. Pass that verified binding explicitly to the
evaluator. These checks parse files/geometry only and perform no field evaluation.

Pose/encoder must bracket the represented model-input time within 50 ms without
extrapolation. Use the observed world phase, not an invented nominal phase.
For old recordings, the source publisher's exact evaluated-transform identity
was not captured: any reconstructed matches are labeled proxies. Do not rename
publication time as acquisition time or promote bag arrival order to proven
DDS callback order. Actual captured M2 metadata is the source-time authority.

The fixed anchor denominator is 192. Separately report causally qualified,
objective-reconstructable, full-cycle/rate-qualified, numerically qualified,
informative and matched-method counts, including every unavailability reason.
Compare angular errors at identical informative anchors; also report availability,
lag/jitter where supported and the timing/provenance limitations. No empty
denominator passes a target. Retained replay cannot qualify new transport or
predict trajectories under different commands. Analytic/synthetic matched-input
tests and bounded prospective typed transport capture are separate evidence.

Report all-state matched errors descriptively. The direction-mode target
denominator is input-coverage-qualified, independently informative anchors with
fresh recorded SEARCH/VERIFY/DESIGN state. Include startup after the first full
input revolution, weak method vectors, inconsistent cycles and all fallbacks.
Three-cycle agreement is method success, never an eligibility filter. Missing
method direction cannot silently disappear from availability or count as an
angular-error pass. Escape/other-state counts remain explicit. Frozen selected
filter file SHA256 is
`f1cfd23a9c60e08780a4477f23cacc80a9e0c75b127448291e321756de7a2dce`.

Bound the reference job by one `timeout 300s` invocation and 192 anchors, write
atomic exclusive started/target/per-anchor/final receipts in a fresh versioned
artifact directory, and preserve partial output on timeout. No automatic retry,
replacement anchor, holdout access, 72-angle approximation, spatial grid or
field tuning. Tests have `timeout 180s`. Source/test review and a checkpoint precede
the actual reference job; this document does not itself execute it.
