# Manual Testing Only Cleanup - 2026-05-18

Matt clarified that Gazebo testing should be done manually, one scenario at a
time, so he can watch Gazebo/live plots and stop each simulation himself.

Files in this folder were retired because they supported batch or matrix-style
multi-run workflows.

Retired:

```text
hb_baseline_matrix_acoustic.bash
```

Keep `hb_scenario_acoustic.bash` active. It launches exactly one selected
scenario and matches the desired manual workflow.

