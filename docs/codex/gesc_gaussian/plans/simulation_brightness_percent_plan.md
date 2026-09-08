# Simulation brightness percentage interface

## Scope and authorization

The user requests simulated light brightness expressed as percentages, with
100% representing a nominal 1600-lumen Hue bulb. This is a separately scoped
post-V1 interface change, not a new Phase 08 experiment or a robustness claim.
Phase 08 remains closed; Phase 09 physical validation remains outstanding.

One milestone: support `brightness_percent` from scenario/config/launch input
through the existing simulated cost owner, recorder metadata, and surface
plot. Use the linear assumption `nominal_lumens = 16 * brightness_percent`.
Accept finite values from 0 through 100; 0 means off. The real bulb's app
percentage-to-output curve is not claimed to have been calibrated.

## Ownership and compatibility

- Extend `Multi_Light_Source_Cost`, the existing cost-node CLI, central Gazebo
  XML, scenario schema/runner, and surface plotter. Use one shared simulation
  brightness conversion helper, with no new node, recorder, or launch graph.
- Keep internal fitted-curve normalization (`reference_intensity_lumens`) and
  the cost sign/output units unchanged. Equivalent percentage/lumen inputs
  must produce the same cost surface and evaluation geometry.
- New user-facing examples use percentages. Legacy JSON/YAML lumen fields,
  launch flags/defaults, and old wrappers remain supported without clamping
  historical values above 1600. Percent arguments explicitly override legacy
  launch defaults for the same source. Config/scenario input with both units
  is rejected as ambiguous.
- Resolved percentage scenarios retain their requested percentage and derived
  nominal intensity for the existing evaluator; old scenario expansion and
  deterministic keys remain unchanged. Plot labels use percent for the new
  interface; legacy plots retain their original labels.
- Do not edit frozen phase plans/statuses/reports/results/scenarios, shared
  controllers/Gaussian/supervisor behavior, or the physical snapshot/Pi.

## Acceptance and validation

1. Test conversion boundaries, invalid/nonfinite inputs, off behavior, dual-unit
   rejection, and equality of percentage/lumen cost outputs.
2. Test JSON configuration, scenario normalization/expansion, launch arguments,
   metadata, cost-node configuration events, and plotter input/labels.
3. Run focused legacy, observability, scenario-schema/runner, and aggregate
   field regressions with explicit timeouts; check historical content hashes.
4. Build the affected simulation packages in an isolated host workspace and
   construct the installed XML launch with percentage arguments without
   executing Gazebo or motion. Check the installed example and CLI routes.
5. Record exact outcomes, skips, commands, and artifacts in the accompanying
   status. This interface work does not rerun any closed simulation matrix or
   regenerate historical phase checkpoints. No commit is authorized here.

## Initial preflight

The checkout is clean at `01e7645`; the documentation relocation is already
committed. The relocated Phase 08 implement-context validator passes and
selects the terminal v8.12 plan. Old launch defaults include 2500 lumens and
some wrappers use 3000, so a blanket replacement with percentages would alter
historical behavior or exceed 100%. Preserve those compatibility paths and
provide a percentage-only example for new work.
