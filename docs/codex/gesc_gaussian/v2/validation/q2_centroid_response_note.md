# Ideal response of the approved centroid score

This algebra explains a limitation of the current metric. It does not fit Q2
trajectories, evaluate a new setting, or change a qualification result. The
formula was derived and independently reviewed against the approved definition.

For an ideal constant-speed circle

`p(t) = c + r (cos(omega*t), sin(omega*t))`,

let `W>0` be one window duration and `x=omega*W/2`. Its time-weighted centroid
over window `i`, starting at `t0+i*W`, is

`c_i = c + r*sin(x)/x * (cos(theta_i), sin(theta_i))`,

where `theta_i=omega*(t0+(i+1/2)*W)`. Adjacent centroid angles differ by `2*x`.
Their distance is `2*r*sin(x)^2/abs(x)`, so the sum of five distances is

`S_circle = 10*r*sin(x)^2/abs(x)`.

The limiting value at `x=0` is zero. Here `c` is the fixed circle center, `r`
is radius in metres, `omega` is signed angular rate in radians/second, `W` is
seconds, and `S_circle` is metres. With period `P=2*pi/abs(omega)`, every positive
integer ratio `W/P` makes the ideal circle score zero. Other ratios can yield a
substantial score even though the center never drifts. Window means do not
automatically remove a complete orbit when each window covers only part of it.

For ideal pure translation `p(t)=p0+v*t`, adjacent centroids differ by `v*W`, hence

`S_translation = 5*W*norm(v)`.

The strict gate `S<epsilon` accepts this motion only when
`norm(v)<epsilon/(5*W)`; equality is rejected. `v` is metres/second and `epsilon`
is metres. Thus changing window length or score threshold changes both settling
responsiveness and drift resolution. The independent radius guard remains
necessary, including for large loops whose period happens to match the window.

These formulas assume complete continuous-time, constant-speed circular or
linear trajectories. They do not cover variable-speed/noncircular motion,
translation mixed with oscillation, finite source sampling or reset histories.
They establish neither empirical sensitivity nor a newly selected parameter.
Recorded diagnostics, followed by one prospective finite development decision,
are required before changing the current source/configuration.
