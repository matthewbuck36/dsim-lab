# Prospective M1 centroid-grid diagnosis

Date: 2026-09-09 UTC. Status: **independent analytic diagnosis and proposed
future grid**, not an executed calibration result, selected configuration, or
amendment to the approved contract. This document was prepared without reading
detector outputs or calibration outcomes. The frozen V1 grid must still be
executed and its outcome retained before any separately versioned amendment.

The input definitions inspected are the approved V2 plan and the predetermined
synthetic population in
`ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`,
function `_v2_synthetic_traces` (line 3176 at preparation). They define circles
of radius 0.15 m and periods 3, 4.5 and 6 s, phases 0 and 0.7 rad, source steps
0.05 and 0.10 s; corresponding fore/aft motion; translating circles and straight
motion at 0.02 and 0.05 m/s; loops of radius 1 and 1.5 m; and a positive circle
with changing source rate. No labels, metric, radius grid or source code are
changed here. Source identification is not established by positional settling.

## Exact continuous-time circle calculation

Represent planar position as a complex number. For a fixed-center circle,

`p(t) = b + r exp(i (omega t + phi))`, where `omega = 2 pi / P`.

Here `b` is the fixed center in metres, `r` the radius in metres, `P` the period
in seconds, and `phi` the initial phase in radians. For consecutive windows
`[k W, (k+1) W]`, set `a = omega W / 2 = pi W / P`. Direct integration gives

`c_k = b + r (sin(a)/a) exp(i (omega (k+1/2) W + phi))`.

Each adjacent centroid distance therefore has the same magnitude:

`|c_k - c_(k-1)| = 2 r sin(a)^2 / a`.

The metric sums five nonnegative distances over six centroids, so

`S_circle = 10 r sin(pi W/P)^2 / (pi W/P)` metres.

This value is independent of starting phase and window number. Changing the
start of the six-window block does not make this ideal fixed circle detectable
later if the score remains above threshold. A window averages an arc; its mean
need not equal the circle's center. Exact cancellation occurs when `W/P` is an
integer. The five distances cannot cancel one another because each is a norm.
Consequently, using means alone does not guarantee a small circle score for
every relationship between the window duration and oscillation period.

For `r = 0.15 m`, the exact values below are rounded to twelve decimal places.
Zero entries are mathematically zero, rather than floating-point sine residue.

| W (s) | P=3 s: S (m) | P=4.5 s: S (m) | P=6 s: S (m) | Largest S (m) |
| --- | ---: | ---: | ---: | ---: |
| 3 | 0 | 0.537147932935 | 0.954929658551 | 0.954929658551 |
| 6 | 0 | 0.268573966468 | 0 | 0.268573966468 |
| 9 | 0 | 0 | 0.318309886184 | 0.318309886184 |

Thus every permitted W has a declared positive circle whose ideal score exceeds
the frozen maximum epsilon of 0.24 m. The same conclusion survives the source
sampling bound below. This predicts an obstruction in the frozen 36-grid; it
does not replace the required recorded calibration outcome. Increasing the
confinement radius cannot fix a failed score condition.

Fore/aft sine motion is a coordinate projection of the same circle. Projection
cannot increase any centroid distance, so its score is bounded above by the
corresponding circle score for any phase. Stationary motion has score zero.

## Drift separation, including translating circles

For straight translation `p(t) = b + u t`, the time-weighted centroid of each
window is its midpoint position. With speed `v = |u|`,

`S_translation = 5 v W`.

Because eligibility requires `S < epsilon`, the score alone rejects straight
drift at or above `v_resolution = epsilon / (5 W)`. This is an effective
constant-drift resolution, not a guarantee for arbitrary slowly changing
trajectories. Confinement can additionally reject motion; it cannot weaken this
score rejection. Piecewise linear integration represents straight translation
exactly at any valid sampling schedule.

For a translating circle, each centroid difference is `u W + d_k`, where
`d_k` is the circle's centroid difference. Apply the triangle inequality to the
sum of all five vectors and telescope the circular terms:

`S >= |5 u W + (c_5_circle - c_0_circle)|`

`S >= 5 v W - 2 r |sin(a) sin(5 a)| / a`.

This lower bound is independent of initial circle phase and translation
direction. It applies to every `v >= 0.02 m/s` using 0.02 on its right side.
Unlike applying the triangle inequality separately to each difference, it
retains cancellation of the circular terms across the full block. It is a
conservative lower bound, not a claimed attainable minimum.

| W (s) | Straight v=0.02: S (m) | Smallest translating-circle lower bound over the three periods (m) |
| --- | ---: | ---: |
| 3 | 0.300000000000 | 0.109014068290 |
| 6 | 0.600000000000 | 0.546285206706 |
| 9 | 0.900000000000 | 0.836338022763 |

At W=3, no score threshold can both accept the largest declared positive-circle
score (about 0.955 m) and reject straight 0.02 m/s translation (0.300 m).
Confinement also cannot resolve that particular pair with the unchanged radius
grid: straight translation over 18 s has radius `3 v W = 0.18 m`, below even
R=0.25 m. At W=6 and W=9 the circle and drift bounds leave useful margins.

## Sampling and confinement bounds

The runtime metric integrates the piecewise linear trajectory through source
samples, not the unknown continuous circle. For a twice differentiable circle,
`max |p''(t)| = M = r (2 pi/P)^2`. With every source gap at most `h`, linear
interpolation has pointwise error at most `E = M h^2 / 8`. Integrating this
bound gives centroid error at most E per window, including interpolated
boundaries and irregular source rates. Therefore

`|S_sampled - S_continuous| <= 10 E`.

Translation adds no interpolation error, so the same bound applies to
translating circles. At the frozen synthetic maximum gap h=0.10 s, the score
error bounds are 0.008224670334 m for P=3, 0.003655409037 m for P=4.5, and
0.002056167584 m for P=6. Combining each period's own error bound with its own
score or drift bound gives:

| W (s) | Upper bound: all declared small-circle scores (m) | Lower bound: all declared translating-circle scores for v>=0.02 (m) |
| --- | ---: | ---: |
| 3 | 0.956985826135 | 0.106957900706 |
| 6 | 0.272229375505 | 0.542629797669 |
| 9 | 0.320366053767 | 0.834281855180 |

The troublesome positive circles also have sampled-score lower bounds of
0.952873490968, 0.264918557430, and 0.316253718600 m for W=3, 6, and 9
respectively. All exceed 0.24 m. These bounds cover the changing-rate positive
circle because its largest source gap remains 0.10 s. They do not claim the
same margins at the runtime maximum permitted gap of 0.50 s or for noisy
retained odometry; those inputs require the frozen replay.

For these periods, each six-window duration `6 W` contains an integer number
of revolutions, so its ideal overall center is b. A conservative sampled
confinement upper bound is `r + 2 E <= 0.151644934067 m` for the positive
circle family. All unchanged radii {0.25, 0.50, 0.75} exceed this. For the
declared large loops, actual source samples lie on the circle and the sampled
overall center differs from b by at most E. Their maximum represented radius
is therefore at least `r - E`; its smallest bound over the declared family is
0.994516886444 m, above the largest allowed R=0.75 m. Thus raising epsilon
within the proposed grid below does not analytically remove the large-loop
rejection in these synthetic cases.

## Bounded prospective amendment

After the frozen-grid outcome is retained, a possible fresh 36-combination
grid keeps W={3,6,9} s and R={0.25,0.50,0.75} m and replaces only epsilon with
**{0.24,0.30,0.36,0.48} m**. This document does not authorize that replacement
by itself. Keep the same labels, inputs, score definition, strict inequality,
radius condition and selection rule in a separately versioned execution.

The analytic intervals above place epsilon=0.30, 0.36 and 0.48 strictly between
the W=6 positive upper bound and negative lower bound. At W=9, epsilon=0.36
and 0.48 lie between them. These are margins for the declared synthetic
families, not predicted retained-run acceptance or a selected configuration.
The retained 0.24 point anchors comparison with the frozen grid. W=3 remains
present so the approved W set is preserved, although the declared ideal pair
already prevents full qualification at that W.

| W (s) | epsilon=0.24: v_resolution (m/s) | 0.30 | 0.36 | 0.48 |
| --- | ---: | ---: | ---: | ---: |
| 3 | 0.016000000000 | 0.020000000000 | 0.024000000000 | 0.032000000000 |
| 6 | 0.008000000000 | 0.010000000000 | 0.012000000000 | 0.016000000000 |
| 9 | 0.005333333333 | 0.006666666667 | 0.008000000000 | 0.010666666667 |

The six-window observation floor remains 18, 36 or 54 s respectively. Faster
confirmation relative to a labeled basin entry remains an empirical target;
neither the observation floor nor this analytic separation establishes the
required latency improvement, source validity, correct fills or goal decisions.

## Independent arithmetic verification

One bounded `timeout 30s python3 -` invocation used only Python's `math` module,
the formulas above, and independent composite trapezoidal sums. It imported no
detector, replay helper, synthetic generator or calibration output. Exit code
0; all 36 quadrature identities passed across the three W values, three
periods, two phases and two uniform steps. Maximum absolute sampled-versus-
continuous score difference was 0.000872948308 m. This is verification of the
calculation, not a 36-configuration calibration run.

The arithmetic check is reproducible from the following command:

```bash
timeout 30s python3 - <<'PY'
import math
r = 0.15
checks = 0
maximum_error = 0.0
for w in (3.0, 6.0, 9.0):
    for p in (3.0, 4.5, 6.0):
        omega = 2 * math.pi / p
        a = math.pi * w / p
        exact = 10 * r * math.sin(a) ** 2 / a
        drift_lower = 5 * 0.02 * w - 2 * r * abs(math.sin(a) * math.sin(5*a)) / a
        error_bound = 10 * r * omega**2 * 0.10**2 / 8
        print(w, p, exact, drift_lower, error_bound)
        for phase in (0.0, 0.7):
            for dt in (0.05, 0.10):
                n = round(w / dt)
                centers = []
                for k in range(6):
                    points = [complex(r*math.cos(omega*(k*w+i*dt)+phase),
                                      r*math.sin(omega*(k*w+i*dt)+phase))
                              for i in range(n+1)]
                    integral = dt * (0.5*points[0] + sum(points[1:-1]) + 0.5*points[-1])
                    centers.append(integral / w)
                sampled = sum(abs(centers[k]-centers[k-1]) for k in range(1, 6))
                z = omega * dt / 2
                assert abs(sampled - (z/math.tan(z))*exact) < 1e-12
                assert abs(sampled-exact) <= 10*r*omega**2*dt**2/8 + 1e-12
                maximum_error = max(maximum_error, abs(sampled-exact))
                checks += 1
print('identities passed:', checks, 'maximum score error:', maximum_error)
PY
```

The identity used for the uniform-sampling check is that composite trapezoidal
integration multiplies the sinusoidal centroid by `z cot(z)`, where
`z = omega h / 2`, when window boundaries coincide with the sample lattice.
The error-bound argument above is the applicable safeguard when they do not.
