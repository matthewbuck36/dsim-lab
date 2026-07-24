# Robust Gaussian Algorithm Specification

## 1. Definitions

Let:

- \(x_k \in \mathbb{R}^2\): robot position sample.
- \(J_k\): raw minimization cost sample.
- \(s_k \in [0,1]\): calibrated source score.
- \(\mu\): estimated center of an undesired basin.
- \(\Sigma\): estimated basin covariance.
- \(F_i(x)\): the \(i\)-th active positive Gaussian fill.
- \(J_{\mathrm{aug}}\): cost presented to GESC.

For minimization:

\[
F_i(x)
=
A_i
\exp\left(
-\frac{1}{2}
(x-\mu_i)^T
\Sigma_i^{-1}
(x-\mu_i)
\right)
\]

and:

\[
J_{\mathrm{aug}}(x,t)
=
w_s(t)J_{\mathrm{raw}}(x)
+
w_g(t)\sum_i F_i(x)
+
w_a(t)J_{\mathrm{affine}}(x)
\]

The sign of `J_raw` is not changed by this feature. The repository audit must verify that stronger desired light produces the expected GESC direction.

---

## 2. Sample window

When convergence is detected, freeze a local-estimation window containing synchronized:

```text
timestamp
x
y
yaw
raw sensor
raw cost
source score
controller mode
```

Initial simulation defaults:

```yaml
estimation_window_sec: 8.0
minimum_valid_samples: 40
maximum_sample_age_sec: 12.0
```

The implementation must use time duration rather than assuming a fixed publish frequency.

Reject samples that have:

- invalid or stale pose,
- invalid sensor,
- nonfinite values,
- timestamp regression,
- distance jumps inconsistent with configured robot limits.

Apply median-absolute-deviation rejection to cost and position increments.

---

## 3. Center estimation

### Initialization

Use the valid sample with minimum raw minimization cost:

\[
\mu^{(0)} = x_{\arg\min_k J_k}
\]

### Iterative kernel and cost weighting

For iteration \(r\):

\[
\tilde w_k^{(r)}
=
\exp\left(
-\frac{\|x_k-\mu^{(r)}\|^2}{2h_x^2}
\right)
\exp\left(
-\frac{J_k-J_{\min}}{\tau_J}
\right)
\]

Normalize stably:

\[
w_k^{(r)}
=
\frac{\tilde w_k^{(r)}}{\sum_\ell \tilde w_\ell^{(r)}}
\]

Then:

\[
\mu^{(r+1)}
=
\sum_k w_k^{(r)}x_k
\]

Stop after 5 iterations or when:

\[
\|\mu^{(r+1)}-\mu^{(r)}\| < 0.005\ \mathrm{m}
\]

Initial normalized defaults:

```yaml
mean_shift_iterations: 5
center_tolerance_m: 0.005
position_kernel_bandwidth_m: 0.25
cost_temperature_normalized: 0.05
```

Use log-sum-exp style normalization to prevent underflow.

---

## 4. Covariance estimate

Using final weights:

\[
\Sigma_{\mathrm{sample}}
=
\sum_k
w_k
(x_k-\mu)
(x_k-\mu)^T
\]

Then:

1. Symmetrize.
2. Eigen-decompose.
3. Clip eigenvalues to:

```yaml
covariance_eigenvalue_min_m2: 0.0025
covariance_eigenvalue_max_m2: 0.25
```

The lower value corresponds to \(0.05^2\ \mathrm{m}^2\); the upper value corresponds to \(0.5^2\ \mathrm{m}^2\).

---

## 5. Local quadratic model

Fit the regularized model around \(\mu\):

\[
\hat J(\delta)
=
c + g^T\delta + \frac{1}{2}\delta^T H\delta
\]

where:

\[
\delta = x-\mu
\]

Use weighted least squares with ridge regularization.

Then:

- symmetrize \(H\),
- clip negative fitted eigenvalues to zero for basin-size estimation,
- record fit residual and condition number,
- reject the fit if ill-conditioned or underdetermined.

If the fit is rejected, use the depth-only fallback below.

---

## 6. Basin depth

Estimate the center cost as a weighted low percentile and the shoulder cost from valid samples outside the inner covariance ellipse.

Recommended:

```yaml
center_cost_percentile: 10.0
shoulder_cost_percentile: 80.0
inner_mahalanobis_radius: 1.0
```

Then:

\[
\Delta J = \max(J_{\mathrm{shoulder}}-J_{\mathrm{center}}, \Delta J_{\min})
\]

Initial normalized default:

```yaml
minimum_basin_depth: 0.02
```

---

## 7. Initial fill width

Let the eigenvalues of \(\Sigma_{\mathrm{sample}}\) be \(\lambda_1,\lambda_2\).

Use:

\[
\Sigma_{\mathrm{fill}}
=
\kappa_\Sigma \Sigma_{\mathrm{sample}}
+
\sigma_{\mathrm{floor}}^2 I
\]

Initial defaults:

```yaml
covariance_scale: 2.5
sigma_floor_m: 0.15
sigma_ceiling_m: 1.25
```

Clip the resulting standard deviations to the floor and ceiling.

This deliberately makes the fill broader than the estimated trajectory cluster.

---

## 8. Initial amplitude

Depth requirement:

\[
A_{\mathrm{depth}}
=
\alpha_d \Delta J
\]

Curvature requirement, when the quadratic fit is valid:

\[
A_{\mathrm{curvature}}
=
\alpha_h
\lambda_{\max}(H)
\lambda_{\max}(\Sigma_{\mathrm{fill}})
\]

Then:

\[
A
=
\operatorname{clip}
\left(
\max(A_{\min},A_{\mathrm{depth}},A_{\mathrm{curvature}}),
A_{\min},
A_{\max}
\right)
\]

Initial normalized defaults:

```yaml
amplitude_depth_scale: 1.5
amplitude_curvature_scale: 1.2
amplitude_min: 0.10
amplitude_max: 3.00
```

The width and amplitude are therefore coupled. A wider fill is not allowed to become arbitrarily flat.

---

## 9. Residual-minimum validation

Before publishing the fill, evaluate:

\[
\hat J_{\mathrm{aug}}(x)
=
\hat J(x) + F(x)
\]

on a local grid covering \(\pm 3\sigma\) in both principal directions.

Initial defaults:

```yaml
validation_grid_points_per_axis: 41
validation_support_sigma: 3.0
maximum_design_escalations: 5
amplitude_escalation_factor: 1.5
width_escalation_factor: 1.25
```

Detect 8-neighbor interior grid minima inside the exit support.

Escalation order:

1. Increase amplitude by 1.5, up to the cap.
2. If residual minima remain and width is below its cap:
   - multiply each standard deviation by 1.25,
   - multiply amplitude by \(1.25^2\) to approximately preserve curvature strength.
3. Repeat up to five times.

If the fitted model still contains an interior minimum:

- publish `fill_design_failed`,
- do not pretend the design succeeded,
- enter the supervisor's controlled fallback/failsafe path.

---

## 10. Soft association and fill merging

For a new candidate center \(x\) and existing cluster centers \(x_j^*\):

\[
p_j(x)
=
\frac{
\exp(-\|x-x_j^*\|^2/(2h_m^2))
}{
\sum_i \exp(-\|x-x_i^*\|^2/(2h_m^2))
}
\]

A candidate may merge only when both are true:

1. Hard overlap gate:

\[
\|x-x_j^*\|
\le
r_{\mathrm{merge}}
=
k_m
\max(\sigma_{\max,j},\sigma_{\max,\mathrm{new}})
\]

2. Soft association:

\[
\max_j p_j \ge p_{\min}
\]

Initial defaults:

```yaml
merge_bandwidth_m: 0.50
merge_radius_scale: 2.0
minimum_merge_probability: 0.60
```

When merging:

- update the cluster's weighted center and covariance,
- include the new sample window in sufficient statistics,
- redesign one fill for the merged cluster,
- deactivate the superseded fill version,
- publish a merge event.

Do not simply sum narrow overlapping fills.

Well-separated fill clusters remain separate and their contributions may be summed.

---

## 11. Fill support and escape radius

Define:

\[
\sigma_{\max}
=
\sqrt{\lambda_{\max}(\Sigma_{\mathrm{fill}})}
\]

Recommended:

\[
r_{\mathrm{support}} = 3\sigma_{\max}
\]

\[
r_{\mathrm{exit}} = 2.5\sigma_{\max}
\]

The active center and `r_exit` are frozen during one escape attempt.

---

## 12. Confidence

Publish a fill-confidence value derived from:

- valid sample count,
- sample angular/spatial coverage,
- quadratic-fit condition,
- fit residual,
- parameter-cap usage,
- residual-minimum validation result.

Do not use a low-confidence fill without marking it in the log.

---

## 13. Required unit tests

1. Kernel weights sum to one.
2. Kernel calculation remains finite for large distances.
3. Lower-cost nearby samples receive higher weight.
4. Center estimate is stable under outliers.
5. Covariance is symmetric positive semidefinite.
6. Width clipping is correct.
7. Amplitude scales with width and curvature.
8. A synthetic quadratic minimum is removed.
9. Residual minima trigger escalation.
10. Nearby candidates merge.
11. Distant candidates do not merge.
12. Superseded fills are not double-counted.
13. Fill gradient points outward away from the center for a minimization problem.
