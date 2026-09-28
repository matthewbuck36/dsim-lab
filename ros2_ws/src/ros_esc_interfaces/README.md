# ESC interfaces

Eight message types support the original ESC methods and V3:

| Messages | Role |
| --- | --- |
| `Timekeeper`, `StampedFloat64`, `StampedFloat64MultiArray`, `StampedString`, `StampedTransformMultiArray` | Original method compatibility |
| `SensorObservation` | One adapter-owned raw cost, observed phase/pose, source and receipt times, source identity, validity and timing uncertainty |
| `AlgorithmEvent`, `GaussianFill` | Output-only V3 telemetry |

`SensorObservation` distinguishes host sequence from an optional device sequence
and declares its timestamp basis. Unknown acquisition uncertainty is `NaN`, not
zero. The core receives observed data rather than simulated source positions.
Algorithm state and objective revisions remain local; there is no active
state-heartbeat or fill-acknowledgment protocol. The base command remains the
standard `geometry_msgs/Twist` on `/cmd_vel`.

See [usage](../../../docs/esc_usage.md),
[architecture](../../../docs/esc_architecture.md), and
[history](../../../docs/esc_history.md). Message availability is not runtime or
physical qualification. Previous interfaces and detailed documentation remain
in the frozen history and pre-refactor archive.
