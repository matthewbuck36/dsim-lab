# R2 geometric v2: negative rejection improves, slow-circle sensitivity fails

2026-09-10 UTC. Single job terminal0,36.220616065s inclusive and36.077916473s
work, within the prospective180s allowance. Artifact integrity PASS. **No runtime
nomination:** all54 negatives are rejected, but19 of26 circle/static positives
are missed. Both previous failed prototypes remain retained and unchanged.

Prospective method: [v2 plan](../r2_geometric_detector_v2_plan.md).
External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/geometric_detector_v2/`.
This is offline development evidence only. No production owner, bag, field
model, simulation, hardware or holdout changed. Root owns status/handoff updates.

## Complete fixed-population result

| Scope | Count | Result |
|---|---:|---|
| Circle/static positives | 26 | 7 detected;19 missed |
| Drift/translating-circle/large-loop negatives | 54 | All rejected |
| Oscillations | 8 | Unsupported; no trigger |
| .005m/s gray drift | 1 | Separate scope-withheld diagnostic |

The seven detected positives are the three static traces and the P12/P18/P24/
P36 original circles. P12–24 detect at18s, P36 at36s; static detects at12s
without noise/.002m noise and30s with .01m noise. All P48–72 circle positives,
including the fixed-phase/noise variants, are missed by competing-drift veto.
No control was dropped or reclassified to change this outcome. The16 newly
declared off-grid negatives are included in the54-negative denominator.

V5 B produces4 candidate endpoints/6 accepted supports, first source117.8s
(114s after readiness), using30s support.135 of141 zero-geometry-pass supports
are vetoed as ambiguous. Fresh V9 B produces only one candidate endpoint and
support: source272.8s (270s after readiness), using36s support;120 of121
zero-geometry-pass supports are vetoed. Neither recorded trajectory has an
independent settling-entry label here, so these are observation-relative
candidate times, not qualified detection latencies or latency improvements.
No altered trajectory following an earlier intervention was simulated.

## What the retained rivals show

The corrected asymmetric veto resolves the v1 false-positive issue within this
finite control set but admits large-radius translating explanations for slow
stable circles. For the noiseless P60/radius.25m circle at endpoint36s with36s
support, a .04m/s x-direction rival has:

- radius1.567203208m and center(.120510888,-1.316533122)m;
- radialRMS .000492968m versus the .002000000m comparison limit;
- angular span1.301163160rad, below the candidate's2*pi/3 requirement;
- finite rank3, condition5.9684; the actual measured-path radius is .312889170m.

It therefore legitimately vetoes under the newly declared radius<=2m,
span-independent rival rule. A45-degree rival similarly fits with .000499749m
RMS. These are retained grid rows, not a post hoc recomputation. The original
stable-circle geometry fits essentially exactly, but the allowed competing
model can explain this partial trajectory almost as well. This explains why
most misses do not depend on optimizer convergence or execution speed.

The finite continuous refinements comprise873 optimizer calls, maximum60nfev
per seed:466 gradient-tolerance exits,292 cost-tolerance exits and115 declared
evaluation-limit exits. Valid resulting rivals remain eligible to veto even at
the limit, as fixed prospectively. A bounded local search finding no rival is
not proof of global infeasibility; no such proof is claimed.

The result exposes a sensitivity/ambiguity tradeoff rather than supporting a
residual-threshold increase. A future changed method may track stable fitted
centers across successive arcs or use repeated shape/turning observations to
reject transient translations while recognizing slow confinement. It must
explicitly test both positive responsiveness and independent drift negatives;
there is no permission or implementation implied by this suggestion alone.

## Command, hashes and complete artifacts

The plan/helper/command were saved before this sole execution:

```bash
timeout --signal=INT --kill-after=2s 178s env PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/geometric_detector_v2/run.py
```

`execution_receipt.json` preserves returncode0, argv, elapsed time and log hash.
A single30s read-only artifact audit verifies15 published-file hashes, all12
selected input/helper/plan pins, all89 control rows and complete output counts;
`audit.json` retains the proof. No numerical replay was repeated for that audit.

- `decisions.jsonl`:1807 endpoint rows across89 controls and both B traces.
- `competing_velocity_fits.jsonl`:55849 grid/refined rows, with fit geometry,
  optimizer status, seeds, costs, evaluation counts and veto reasons.
- `new_control_samples.jsonl`:19216 fixed new samples.
- `control_contract.json`, `control_results.json`:all89 controls.
- `b_results.json`, `v9_b_input_summary.json`, `v9_b_readiness_poses.jsonl`.
- `prepared.json`, `pins_{before,after}.json`, `result.json`, `receipt.json`,
  `execution_receipt.json`, `execution.log`, `audit.json`.

Result SHA256:
`1793b465301e32ff0f220c673c8928f1656a768852b3aa7536ca916b2759b2e5`.
Receipt SHA256:
`62d853618ec51ae6c8ac7fb517f8852ac96c63e8b00c3d5c7bd05ed60d0afa63`.
Exact selected source/input hashes remain in the verified before/after maps;
unrelated concurrent source edits do not imply a whole-tree stability claim.
Phase context and diff checks passed before this independently versioned work.

The full V2 objective remains open. Strong negative rejection alone does not
make this prototype useful for fast slow-circle detection, and the separate
oscillation method is still unfinished.
