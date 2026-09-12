# Fresh Q2 acquisition v2 evidence

Status: CLOSED_EVIDENCE_UNAVAILABLE; detector EVIDENCE_UNAVAILABLE, discovery
direction COMPLETE_DIAGNOSTIC. Confirmation remains SEALED and M4 unreleased.
Independent saved-result audits and immutable closeout are recorded below.
Authority: `../q2_acquisition_path_correction_plan.md` and the unchanged
scientific requirements in `../q2_qualification_plan.md`.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/`.
Contract SHA256 `f3e31a16b6008e11ae953813f0188e52a451e275a653fb865d88d50922704fa6`;
dispatch release SHA256 `be1a6a42a71e5b081614088b5ec0b58bba62873ce9981b1163d90a9be3327328`;
source checkpoint SHA256 `dd58bf51154efdfbfeff2240770c2c66a92abfde512882d6a3917d1685d4582d`.
The incomplete21-series attempt remains closed and contributes no imported input.

## Acquisition

Four fixed31-series cases,125 simulated seconds after readiness each. First
visible, later cases batch. Corrected dated-path validation precedes input
acceptance; safety/completeness/input/cleanup failure halts dispatch. Exact
release command, executed once through its pinned wrapper:

```bash
timeout --signal=INT --kill-after=60s 1140s python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/acquire_q1.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/preflight/contract.json
```

The release binds Humble/Q2 overlay/domain191 and current source/build/audits.
`preflight/acquisition.log`, `preflight/dispatch_completion.json`, per-case
acquisition receipts and final `acquisition/acquisition.json` preserve the
outcome. Only four complete accepted inputs produce `study_manifest.json`.

Result: COMPLETE,4 accepted inputs/4 new dispatches/0 imports, no failure.
Acquisition elapsed639.006260s; wrapper641.103203s, exit0. All four runner
classifications and cleanup checks passed. Confirmation science stayed unopened.
The exact4-row `study_manifest.json` is saved. Scientific release
`preflight/label_dispatch.json`, SHA256
`d74c3a1d36f3c4dba883994eca12c9a6dee7583ab8275584882fbe9251cff3f2`,
binds the completed acquisition, zero exit, manifest, contract and one600s
label/target/nomination argv. Material acquisition checkpoint precedes dispatch.

Independent acquisition integrity audit PASS,
`preflight/acquisition_integrity_audit_v1.json`, SHA256
`805c4e90168ed6b306dde60f39418a7465f1cb4985d5eea905a4a2b7ccbd96f4`.
All61 completeness checks per run, final-zero, spawn and cleanup passed.
573 source receipts and62 allowed acquisition artifacts were unchanged. No
scientific-stage outputs or bag semantics were opened by this audit.

## Completed scientific jobs

Executed once each in the released Humble/Q2 environment, with the exact frozen
contract above:

```bash
timeout 600s python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/evaluate_q1.py labels --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/preflight/contract.json
timeout 300s python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/evaluate_q1.py references --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/preflight/contract.json
```

Both processes exited0. No complete elapsed-wall measurement was retained for
these two jobs; do not infer one from file timestamps. Logs are
`preflight/labels.log` and `preflight/references.log`. The label job completed
with no integrity errors: `analysis/label_job.json`, SHA256
`74379de03506f61e0d39c156ada39ab9ad2fdee7f0cf98ee49d0853536216503`.
Discovery nomination was EVIDENCE_UNAVAILABLE with null parameters, so the
predeclared `discovery24_diagnostic` reference branch alone was released.
`preflight/reference_dispatch.json`, SHA256
`863e6e00169f68894ea776a7df70f5e8dcb3ff89e6de7842660def0ebb3408da`,
binds the completed job and nomination before any reference calculation.

## Detector and neighborhood result

Neither discovery recording contains a saved positive basin-residence episode,
supported positive opportunity, or censored positive opportunity. Thus the
residence case has no genuine positive episode of even12s; this is not a
short42s opportunity that could qualify by changing the timing gate. The
certified annular mask and its excluded hole are unchanged.

All nine fixed settings produce EVIDENCE_UNAVAILABLE for the residence case
solely because `no_uncensored_first_42_second_positive_opportunity`. All nine
approach evaluations pass their available negative exposure. Each aggregate is
EVIDENCE_UNAVAILABLE, with no measured FAIL and no nominee. Eligible negative
support totals8.176s in residence and17.816s in approach; approach spatial
negative support is20.416s before source/readiness eligibility clipping.

All18 run/setting evaluations contain zero detector events and zero M3
evaluations. There is no measured positive detection latency, sensitivity,
verification success or verification failure. Missing positive exposure is not
evidence that the detector would detect a supported positive. Negative results
apply only to the stated eligible support.

Independent saved-row audit PASS:
`diagnostics/discovery_label_audit_v1.json`, SHA256
`f1c42bf7b5ef3509f111b196da5875e70018a3b3e812e1d7cc54939d5987e710`.
All14 authorized discovery/job receipts were checked and rechecked; exact nine
settings, per-run failure/unavailable precedence and nomination agree. No bag,
detector/filter rerun, model computation or confirmation science was used.
The old `labels[].common_support_eligible` field describes54s support; Q2 uses
the explicit42s `supported_positives` owner. Do not substitute that legacy field.

## Discovery direction diagnostic

`analysis/references/references.json`, SHA256
`401efcfe2afe708abe14bfe05bebadb91222c9ecddd2cfd426b5009d083a7090`,
completed COMPLETE_DIAGNOSTIC with all24 fixed discovery targets causal,
cycle-qualified, informative and eligible. Actual75% averaging was applied
and usable at24/24 targets: availability1.0, fallback0, weak/missing outputs0.

| Population | Eligible / usable averaging | Actual median error | Actual p90 error | Aligned instantaneous median |
| --- | ---: | ---: | ---: | ---: |
| Discovery residence26090931 | 12 / 12 | 31.664092deg | 84.240833deg | 58.560725deg |
| Discovery approach26090932 | 12 / 12 | 31.382171deg | 116.115047deg | 63.457332deg |
| Pooled discovery | 24 / 24 | 31.664092deg | 113.393071deg | 58.560725deg |

The pooled actual median improves descriptively over aligned instantaneous
GESC, while the upper tail remains large. All planned48 slots are retained;
24 confirmation slots remain symbolic and SEALED, without derived source times.
Detector qualification is EVIDENCE_UNAVAILABLE, direction qualification and
combined qualification are NOT_EVALUATED. These discovery errors do not release
confirmation, nominate another weight, or establish the30deg/60deg held-case
targets. Target availability is not time-weighted whole-run availability.

## Evidence boundary

Independent reference audit PASS347 checks in0.180s under timeout60s:
`diagnostics/reference_arithmetic_v1/audit.json`, SHA256
`87bd6ba3c972836532eca63d3e69f2e478c8c893d6af5eb175f5245ed34d9c62`.
All33 allowed receipts,24 exact target/anchor identities, vector angles and
pooled/per-run summaries agree. Independent atan2 arithmetic differs by at most
3.64875e-13deg. No model, filter, raw bag or confirmation input was opened.

Immutable `qualification_closed.json`, SHA256
`51d73de197aa24f2aba8cb9f1eac576aaaa38e7519d6abc672f5113a9acfa137`,
records CLOSED_EVIDENCE_UNAVAILABLE,120 retained artifact hashes and573 unchanged
source receipts through all acquisition/scientific work. The closure command
`timeout 60s python3 /tmp/close_q2_qualification_v2.py` exited0. This closes the
fixed experiment, not the full approved V2 implementation goal.

Detector, direction and combined results remain separately reported. This
primary-field study does not replace the16-run M4 pilot or establish broad
robustness, matched latency improvement, false-decision rates or the full
fill/escape/SEARCH/stronger-candidate sequence.
