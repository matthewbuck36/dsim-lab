# V6 B recorded-motion plot result

The single descriptive visualization under
[the prospective plan](../m4_v6_b_motion_plot_plan.md) completed with exit0,
4.345530599s command wall time within30s; helper work2.576242934s.
The rendered PNG was inspected. The trajectory shows repeated loops after its
initial approach. The corresponding recorded score stays above0.18m even
through much of the motion for which the recorded confinement passes0.50m.
This makes the missed-circling issue concrete; it does not independently label
basin residence, measure a period, prove latency, or justify changing a threshold.

External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_b_motion_plot_v1/`.
The exact command is in `command_v1.txt`, with output in `execution_v1.log`.
`draw_v1.py` retained all10617 pose rows and10718 centroid diagnostic rows.
Zero pose rows were invalid. The1276 unavailable score/radius rows are explicit
plot gaps, not substituted zeros. All623 source pins and the full629-entry
source/input/helper/plan hash map matched before and after. No bag, ROS node,
model evaluation, detector replay, numerical fit, parameter sweep or scientific
endpoint job was run; no input or earlier result changed.

- `recorded_motion_v1.png` SHA256
  `1b6548ddff6069f74825efaa218ab9fd60c468617d3c432e6a358d0a191cc4ae`.
- `recorded_motion_v1.pdf` SHA256
  `ac9997208874291b343ca5c07be1be22e024e3860e077c9c17b0018fd16abe06`.
- `receipt_v1.json` SHA256
  `2e53b03a62aad612049ff2c75001b658ac75d2a085cc0692a5adf7277d1cee07`.
- `draw_v1.py` SHA256
  `7e6b9271058345980bcef2639e985e27c8876b4e9a0910e85e860a2bef965c95`.

M4v5 remains CLOSED_INCOMPLETE. A future detector correction must address
observed circling with a prospective method and independent negative controls;
raising a threshold just above the observed minimum is not qualification.
