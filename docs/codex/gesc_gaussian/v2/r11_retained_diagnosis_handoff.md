# R11 retained diagnosis: complete

Completed 2026-09-11 UTC under the [prospective plan](r11_retained_diagnosis_plan.md).
No production source was changed and no simulation was launched. V12 remains
CLOSED_INCOMPLETE, with twelve complete recordings and four unstarted delay cases.
The broader research goal remains incomplete.

## Findings

1. **Import subprocess confirmed.** One import-only interpreter completed in
   1.408772 seconds, observing exactly one `git rev-parse --show-toplevel`
   subprocess from `run_scenario._repository_root()`. This contradicts the
   reference worker's single-process requirement. It does not identify the
   historical V12 child PID or retrospectively qualify that failed job.
2. **Noisy verification cancellation identified.** One filtered read per noisy
   C/D bag completed in 3.032655 seconds total. All eight recorded returns from
   verification report deadline expiry with last evidence
   `uninformative_raw_profiles`. The last reported signal margin was negative
   in every case, despite sufficient eligible cycles and passing reported
   trajectory and negative-cost margins.
3. **Arrival timestamp rejection identified without another bag read.** B/noise
   contains different valid live-monitor and recorded first-arrival poses.
   `_arrival_metrics` requires them to be identical, so it necessarily rejects
   this measurement. Preserve the unavailable recorded time; the live 283.201 s
   value is not a replacement. The precise callback-delivery difference and
   exact recorded sample's ROS timestamp remain unverified.

The verification owner uses the latest three eligible revolutions. It centers
each 12-sector median profile, computes RMS amplitude of the averaged profiles,
and compares that amplitude with three times their RMS pairwise disagreement.
The numerical floor only guards precision. This is a repeatability heuristic,
not a calibrated three-sigma statistical test. Both sensor noise and physical
profile changes can increase disagreement. More eligible revolutions do not
currently accumulate into a more precise estimate.

All eight deadline records occur 12 seconds after collection admission. The
supervisor checks expiry before reevaluating and appends its previous evidence.
Therefore these are the last available snapshots: they do not identify every
earlier triplet, exact prior evaluation time, or separate amplitude/disagreement.
Do not attribute the entire attempt history solely to sensor noise. Noisy minima
can also bias the negative-cost guards, which are not independent proof of an
extremum.

## Validation and evidence

See [exact validation](validation/r11_retained_diagnosis.md). External work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r11_retained_diagnosis_v1/`.

- `import_result.json`: root session 35163, terminal/reaped 0; six stable pins.
- `arrival_static_result.json`: saved predicates, original samples and source
  hashes; conditional additional bag read skipped as unnecessary.
- `verification_result.json`: root session 55523, terminal/reaped 0; exactly two
  filtered reads, 36,371 selected rows, 129 stable source/small-input hashes.
  Raw bag hashes are inherited from acquisition receipts; only raw stat stability
  was newly checked. This is explicitly not a fresh raw-hash verification.
- `verification_summary.json`: compact exact cancellation evidence. Independent
  cached/source review confirmed the last-three-cycle calculation and limits.

No ROS/Gazebo job remains active. V12 and its failed numerical-process receipt
are unchanged. No full analysis, reference model, matrix or production test was
rerun during R11. Branch remains `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; changes remain uncommitted. No physical,
Pi, snapshot, V1, commit or push action was performed.

## Next prospective work

Use the existing owners for bounded corrections to subprocess-free repository
discovery and independent recorded arrival timestamp binding, with focused
compatibility checks. Preserve the old process gate and failed V12 results.

For the research question, separate within-sector noise, repeatable phase signal
and remaining geometric variation on retained development inputs. Compare a
profile test that accounts for uncertainty against noisy flat-signal and known-
signal controls before changing moving verification. More cycles or a lower
multiplier alone are not justified. Declare the method, finite budget and
decision rule before implementation or a new integrated case. No new matrix is
released by R11.
