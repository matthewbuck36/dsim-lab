# Q6 analytic decision: mean aggregation versus required history

Status: ANALYTIC_COMPARISON_COMPLETE; methodological choice pending. No new
runtime metric or empirical parameter setting selected. Q5 source remains held.

## Result

Both predeclared settings pass the same ideal circle/harmonic fore-aft,
translation and confinement challenge. The tested unchanged five-shift setting
requires108s of history; the proposed two-block mean comparison requires36s.
This is a comparison of required history, not measured detection latency or a
claim that108s is the shortest possible setting of the existing detector.

| Declared setting | Existing five shifts | Proposed two-block difference |
| --- | --- | --- |
| Six base windows | 18s each | 6s each |
| Compared mean duration | 18s | 18s (three6s windows) |
| Required history | 108s | 36s |
| Threshold | 0.90m | 0.18m |
| Fixed-motion score upper bound | 0.770591m | 0.154119m |
| Translating-motion score lower bound | 1.029409m | 0.205881m |
| Fixed-motion confinement upper bound | 0.378596m | 0.428111m |
| Radius limit | 0.50m | 0.50m |

Bounds are conservatively rounded from the saved continuous-interval enclosure.
The radius/amplitude is<=0.35m, constant period3–24s, translation>=0.02m/s,
source intervals<=0.10s, and no pose noise. Circle projections include sinusoidal
fore/aft motion. Arbitrary periodic motion is not covered by amplitude and period
alone. Large circles/harmonic oscillations of amplitude>=1m violate the radius
guard: their sampled half-diameter is at least0.994521m. Neither setting is
qualified for real trajectories, varying orbital speed, noise or slower drift.

## Derivation and independent review

For p(t)=p0+vt+r(cos(omega*t+phi),sin(omega*t+phi)), let L=18s and x=omega*L/2.
Two adjacent L-second time-weighted position means differ, for the oscillatory
part, by d=2r*sin(x)^2/abs(x). The existing five-shift circle score is5d.
The proposed score is the norm of the newest three6s centroid means minus the
oldest three6s centroid means, exactly d for a circle. Every quantity is in
metres. Equal-duration time-weighted windows make this aggregation exact.

The continuous harmonic maximum over x in[3pi/4,6pi] is about0.214660688386,
attained at tan(x)=2x near4.6042167772, corresponding to period12.2819299136s.
Independent derivation covers all phases and translation directions. Root used
an upper enclosure0.214685615507, obtained by fixed interval evaluation plus
|f'|<=1/x_min+1/x_min^2 times half interval width and conservative float padding.
This is a bound for one continuous period interval, not a tuning grid.

Piecewise-linear interpolation changes a time mean by at most
 delta = r*(2pi/3)^2*(0.10)^2/8 = 0.001919089745m.
The score margins are10delta and2delta respectively. Translation is interpolated
exactly; the reverse triangle inequality gives lower bounds90*speed minus the
first score upper bound, or18*speed minus the second. For history H, confinement
is bounded by r*(1+24/(pi*H))+2delta. These equations produce the table above.
Both settings have the same pure-translation threshold resolution0.01m/s;
worst allowed oscillation requires a higher sufficient rejection speed. The
proposal reduces the number of long-mean comparisons, hence history persistence.
It can behave differently for nonstationary motion and needs actual validation.

## Reproducibility and decision boundary

One bounded job completed exit0 in0.084s under90s. Exact command/script/log/result:
/home/mattb/Experiments/GESC-Gaussian/v2/decisions/q6_method_comparison_v1/.
result.json SHA256
fbb87b4fca3f0224f174036d508aac6bebbbb68f53a72a72a34c1567f9d6e8c6;
compare.py SHA256
bf1693c9aae9c3398e8ab54a9fe67821842eb1982b1c0999f3395f68938a4a3c.
One independent derivation agrees, with slightly tighter stationary-root bounds.
No old bag/model/grid/confirmation was read, no parameter adapted after this
job, and no runtime source changed. This finite comparison is complete.

The approved plan explicitly fixes five adjacent centroid distances. Replacing
that with one difference between two longer means is a methodological change;
ask the user to choose before implementing it. The two-block proposal is the
preferred candidate for testing faster detection, with existing confinement,
raw verification, units, legacy modes and closed evidence preserved. Choosing
the existing method remains valid, but this tested long-window setting has a
visible latency cost. Do not call either choice achieved research performance.

After that decision, document one bounded implementation/configuration amendment
and use the already approved four visible M4 development runs plus twelve frozen
holdouts. Direction targets and support/fallback denominators must be evaluated
independently of detector nomination. M3 evidence comparability and12s timeout
remain meaningful gates; no automatic tolerance widening follows from this math.

The asynchronous user question is pending: test the proposed two-block mean
comparison (recommended), or keep the agreed five-shift method. The question
explicitly distinguishes ideal checks from measured performance. No answer,
authorization or empirical selection is inferred from elapsed time. Independent
M4 preparation is saved in ../m4_plan.md as PROSPECTIVE DRAFT ONLY, not a release.
It records exact16slots, inclusive deadlines, behavior/integrity separation and
the required extension for actual post-fill objective reference inputs. Label,
reference population/budget and development-release definitions remain pending.
Root verified all Q5 ROS source hashes still match its immutable closeout.
