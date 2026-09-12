# V6 B recorded-motion diagnostic plot

Adopted prospectively 2026-09-10 UTC under the active simulation-only V2 goal.
This is one descriptive visualization of the already extracted, closed M4v5 B
trajectory and recorded centroid diagnostics. It supports diagnosis of B's
missed confirmations while the separate C/D reconstruction is prepared. It
does not release a new algorithm setting, simulation or scientific evaluation.

Use only B's complete `pose_v1.jsonl.gz` and
`centroid_convergence_diagnostics_v1.jsonl.gz`, bound by the completed extraction
receipt under `builds/m4_v6_development_diagnostic_v1/B/`. Verify that receipt
against `diagnostic_hold_v1.json`, whose SHA256 is
`42e32d584ed83aeab934ac5d2739cf2451af2ca0707b4e2909a14f93f6b2be24`.
Keep all623 v5 source pins unchanged before and after. Never reopen a bag or
alter any retained input, output, selection, failed classification or threshold.

Plot all recorded pose-source XY positions with source time indicated, XY
against source time, and the recorded score/radius against diagnostic
publication time. Mark the existing0.18m and0.50m thresholds. Preserve full
counts; invalid/nonfinite values produce explicit plot gaps and reported
counts, not invented zeros. Do not select favorable intervals or resample the
trajectory. Use equal spatial axes. Retain original units and timestamp bases.

No circle/period fitting, field or basin membership computation, new numerical
detector replay, latency or direction endpoints, parameter sweep, acceptance
decision, or causal inference. Visual appearance alone cannot qualify trapping
or justify a new threshold. Independent labeling or algorithm changes still
need their own saved evidence contract.

External output directory: `builds/m4_v6_b_motion_plot_v1/`. Save the exact
helper, exclusive attempt marker, command/log/receipt, input/source hashes,
PNG and PDF. One finite30s inclusive command (SIGINT at28s, kill grace2s), no
retry or overwrite. Use standard plotting tools without ROS initialization.
Inspect the rendered PNG and record findings with their descriptive limit.
