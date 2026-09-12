# M4 preparation and initial release

Preparation PASS, one attempt,2026-09-09. No new enclosure/replay or additional
qualification acquisition was performed. Source remained held throughout.
The approved pilot is now dispatched; read live acquisition receipts before
any recovery and never start another dispatcher under this version.

External experiment root:
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v1/`.

The single preparation wrapper completed45.713929s (inner44.355990s) inside its
600s inclusive cap. Exact command/log/result are retained in
`builds/m4_pilot_runtime_v1/{run_preparation_v1.py,preparation_v1.log,
preparation_v1_receipt.json}` under the external V2 root. Existing numerical
owners verified original primary/secondary geometry/recovery receipts and
derived separately bound secondary nominal/noise/delay topology receipts.
The noise receipt uses0.045 raw-cost three-sigma margin; it is not a hard
Gaussian bound. The delay receipt binds configuration, not delayed dynamics.

| Artifact | SHA256 |
|---|---|
| `preflight/contract.json` | `b6366e66a8d2bfc8c05e428a2214dbfe5b0e5578164f5b1328d8dc36a50a9e77` |
| `preflight/prepared.json` | `224d5335e932fda4a83daad5915875f4ad2638bbd5b7f3eee54c543f12d1420f` |
| `preflight/frozen_audit_v2.json` | `e0b50039a64c18aceff793368c18363444ecefaaabda320b15c1e3b41829f89c` |
| `preflight/frozen_audit_v2_details.json` | `a17355860620043a00a928254cf24e1227c54e42b746741104a97a01cd5225b0` |
| `preflight/dispatch_release.json` | `ce44b8158674a5d336abdea136600cead88e18d7fa5749054279ad2146b75f8e` |

The independent read-only audit verified all16 identities, arms, seeds and GUI
settings; identical inherited controls; exact launch/runner argv; all606 source
hashes against validation and current files;21 installed targets; exact selected
environment; geometry/point receipts; separate topology/result/disturbance
bindings; and seeded noisy JSON with every other base field unchanged. It
performed no model recomputation, bag decode, ROS initialization or acquisition.
Its first invocation remains FAIL in `preflight/frozen_audit.json`: rebuilding
argument order from alphabetically sorted JSON mappings differed from the
actual original YAML insertion order. Corrected v2 retained exact argv equality
using the actual runner's YAML order and separately verified mapping equality.
No source, frozen command, numerical result or acceptance gate was changed.

Material archives under external `checkpoints/`:

- `m4_source_closed_v1/manifest.json`, SHA256
  `5e16a861e2e484527bbe34457b7736427d05352f7b872c4d25174d430580ba33`:
  330 files,105 retained artifacts,1310249-byte verified source archive.
- `m4_preparation_complete_v1/manifest.json`, SHA256
  `42ff3aeb08e96a8675eae8e045fff6f195c528b46e1e10ce53bc72073050d44d`:
  330 files,119 retained artifacts,1310897-byte verified source archive.

Context, diff and existing V2 checkpoint tools passed at both boundaries.
Subsequent live status/release receipts postdate these immutable archives.

The released command uses existing Q2/Q5 overlays, domain181,
ROS_LOCALHOST_ONLY=1, and the observed desktop DISPLAY=:0. Its outer SIGINT
at15180s and120s kill grace retain a15300s total ceiling, with the dispatcher's
own original per-case/cleanup/science bounds active. First four cases are
visible; twelve holdouts stay sealed until the one-time development release.
Read `acquisition/started.json`, exact `slot_N.json`, final `acquisition.json`,
block receipts and the report to determine current progress.

Console output is retained at external
`builds/m4_pilot_runtime_v1/acquisition_dispatch_console_v1.log`. An initial
shell redirection attempted the already existing source-test `dispatch_v1.log`;
noclobber stopped it before any dispatcher/recording launched. The old log was
preserved, `preflight/console_destination.json` records the correction, and the
released executable argv/population remained unchanged. This was not a
replacement acquisition or retry of an attempted case.

These are preparation/release results, not scientific target acceptance. All
old failed evidence, selectable legacy behavior, V1 and physical work remain
unchanged. No commit or push has been made.
