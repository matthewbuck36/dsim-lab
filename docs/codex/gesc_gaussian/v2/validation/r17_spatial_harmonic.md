# R17 spatial harmonic study validation

The prospective plan was adopted after the independently reviewed R16 closure.
The previous goal turn made progress by completing R16 review, exact evidence
recording and the 624-member material archive. R17 is the next declared method
milestone; no simulation or full comparison is released.

Recovery read AGENTS, the attachment, current plan/status/handoff and R16
measurements; phase context passed and Git remains on V2 at 3369cfc with task
changes preserved. The email PDF in Downloads was read as method context.

Read-only source and cached-data findings:

- R14 includes x/y interactions for H1 only; R15 includes none. R17 prospectively
  tests x/y interactions for H1–H3 with quadratic spatial nuisance and an explicit
  anchor-output estimability check before regularization.
- R16 cached adequacy supplement retained in its external work root at
  `supported_data_adequacy_supplement_v1.json`, SHA256
  `c318efd58036b170e2975d088accab7db5962cdd626db947f7cf73b99bc7cb2a`.
  It postdates the immutable R16 archive. Forty supported target histories have
  218–271 samples, duration 7.378–9.180s, median path length 0.318m and maximum
  0.652m. Phase coverage is dense: minimum five samples per sector per cycle;
  pooled sector-count coefficient of variation has median 0.054 and maximum
  0.087. Noiseless error versus path length Spearman correlation is 0.595 linear
  and 0.668 quadratic, descriptive and confounded by trajectory/field. Reference
  magnitude is well above numerical uncertainty; this does not prove every
  direction is statistically identifiable from noisy moving samples.
- Effective selected C/D runtime remains 20rpm body-relative sensor rotation,
  callback-driven nominal 30Hz acquisition, SEARCH speed ceiling 0.1m/s and
  centered collection target radius 0.03m at 0.3rad/s (0.009m/s feedforward).
  A collection-only speed/radius change would leave SEARCH bias unresolved;
  none was adopted in R17. A faster spin would change both sample density and
  temporal filtering and would need fresh observed-phase reference evidence.

Pre-execution plan review corrected the synthetic accuracy wording to retain
R15's median15/P90 30-degree limits, with both per-family and total null caps.
R17's quadratic-null cap is prospectively stricter. The initially suggested
near-confounded positive trajectory was replaced by a declared S-curve because
near-confounding lacks a justified positive availability assumption; the original
near/exact stress populations remain unchanged. No fitted or generated outcome
motivated either correction. Actual retained-map admission is explicitly a
development projection of the H1-selector synthetic cutoff, not a proven null
rate for arbitrary maps or real noise laws.

Source, synthetic and retained execution receipts will be appended after their
sole finite jobs. Current work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r17_spatial_harmonic_v1/`.


## Source implementation and focused validation

Existing harmonic_gesc.py extended additively with fit_spatial_profile; historical
source remains an exact byte prefix. Independent static algebra review found no
blocker. Sole source session 19866 terminal/reaped 0: 89/89 checks PASS in 1.77s
pytest / 2.569950144s outer. All nine source/test/plan/environment pins remained
stable. The selection is 57 prior R14/R15/map cases plus 32 new spatial-fit cases.
Exact timeout55s SIGINT+5s kill argv and before/after hashes are retained in
focused_prepared.json/focused_result.json, with focused_console.log. New checks
cover requested-output estimability, spatial/harmonic equivariance, mean-SSE
penalty scaling, actual influence, HAC covariance and unchanged support guards.
These source checks do not establish scientific acceptance.

Core SHA256 `449f4403edef7867b11a22f1715d346158f5ff8d719ec949fde084ac18604b1a`.
New tests SHA256 `875a645a8ef4c49eeddf85b2feecadd2f8ff55f2ef0834597b75a5340aae460d`.
Source/helper owners are held. Final synthetic preparation completed after root
static review and the focused PASS; root verified its exact argv and stable pins.
No controls were generated or fitted during preparation. Sole finite controls
execution is next; no simulation or runtime selection is released.


## Independent controls completed; candidate rejected

Sole session 80109 terminal/reaped 0, 16.000572940s outer. The helper's result
work time is 13.873499347s; closed receipt time 15.751918414s includes serialization.
All 1,884 generated inputs and 4,152 public fits completed with errors=[] and
subprocess_events=[]. Exact argv is in synthetic_execution.json; configured
235s SIGINT+5s kill and internal210s limits were respected. Source/input pins
remained stable. This is the only controls execution, with no retry or retuning.

Separate positive calibration selected lambda=0.01 after 576 calls: capped mean
angle loss at lambda1e-4/1e-3/1e-2 is 20.552775254/13.576788855/8.316221327 degrees.
Then four199-episode null families froze cutoff=6.449624183670948 after 2,168 calls,
with zero evaluation fits completed at that boundary. Evaluation used fresh seeds.

Static positives: 59/64 stronger detections (71/96 overall), accepted median/P90
3.359623/12.295283 degrees. New spatial positives: 63/64 stronger (78/96 overall),
accepted median/P90 4.991960/14.265018 degrees. Both meet their fixed gates.
Quadratic spatial nulls have 0/64 accepts, including all16half-phase cases
unavailable. All16exact and16near-confounded stress episodes are unavailable.

Candidate REJECTED: AR1 nulls have3/128 accepts, exceeding the per-family2 cap
(total3/512 meets its separate cap); hard loss-of-signal cases have4/16 accepts,
so the combined hard-change population has4/32, exceeding2. Hard reversals have
0/16 accepts. Mature late-change looks have0/16 accepts; pre-change16/16 and
transient21/32 are reported separately. Gray smooth-change59/64 and quadratic
angular62/64 admits are descriptive. No criterion, label, cutoff or lambda changed.

Synthetic result SHA256 `ffb288abb2d853001f43b32f1d4e710d93b73695b8993d3655b5124a19022ba2`.
Receipt SHA256 `0aa0e0bfb21a4d407c962fa9ec1240aa9c0156b6ed6467e604ebf97149b2e933`.
Execution SHA256 `901e5b26ba0252d32fbf2027144f67aab03296312a8f80deab7c2013c94b1ccb`.
Independent cached review pending. The planned retained diagnostic is allowed
regardless of candidate rejection; its measurements cannot override it.

## Retained diagnostic dispatched

Final cached shape/preparation checks pass all144 target identities and fields,
40 operators, six by-stamp source tables and eight verification restorations.
Root verified53 preparation pins and exact `command` arrays. Sole session99659
uses115s SIGINT+5s kill, internal105s, at most192 fits, no new model/reference
or bag evaluation. Prepared SHA256
`e634845a1d06cf72189d50bd0bd7bcd25c431185088a4763f0ef21149b29f1bd`;
ready SHA256 `88d5f250b4e67da0831bf5ab52e2edad430d62a385185c584803c2cc7be8fe77`.


Retained session99659 terminal/reaped 0: 3.921781497s outer / 3.218837949s helper.
All54 execution pins stable, errors=[] and subprocess_events=[]. Exactly192 fits,
160 target and32 verification; all finite. Forty supported targets retain the
same six unavailable eligible excursion failures,144 scheduled/46eligible.
No new model, map, reference, quadrature, geometry or bag operation occurred.

Recorded admission3/46; every per-run availability result FAIL or unavailable.
Against R15 on the same40 supported matrices,12 improved/28degraded versus linear
and16improved/24degraded versus quadratic. Noiseless moving admission10/46 under
either geometry interpretation; large unscreened errors persist. Fixed-anchor
admission30/46 and small angular errors remain diagnostic. Raw verification
projects1/8 recorded,6/8 noiseless moving,8/8 fixed-anchor; originalguards and
historicalmismatches unchanged. Complete per-run errors are in the R17 handoff.

Retained result SHA256 `46a539884ef412a2d02ee63ce79823ba07f51e42e21b1c61e7e21189616f3d76`.
Execution SHA256 `c395c4899381cf55443f1499aac9717f07561493e0ea7b6e2ab69c8f0737fd5b`.

Independent cached synthetic review PASS, sole session26699 terminal/reaped0,
2.608136548s outer /2.607700555s helper.72,435 arithmetic/identity assertions
verify all1884 inputs,2076 fit records,4152 calls, separate freezes and gates.
No fit, generator, field model or project import was executed. Command:
`timeout --signal=INT --kill-after=2s 28s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r17_spatial_harmonic_v1/cached_review_synthetic.py`.
Review SHA256 `9648dbba34a22e4606dc2f781d7c381500c5d7a30ceaf855dbf444b45b6a7f16`;
receipt `68344f4bd1605dda8bc30e76dbe0fabfbaeb4266f24f8a4e4f6abf2a34a4b8de`.
Retained review and material closure remain pending. No method correction is
released to runtime; full research goal remains incomplete.


Independent retained cached review PASS, terminal0 in1.381493s:91,179 cached
arithmetic/identity assertions,209stable selected inputs. All144/46/40/8 counts,
192fits,9775target+1927verification sample uses,152partials,160q/Cq/error
compositions,192score calculations, originalmaps/refs/guards and summaries match.
No fit/model/bag or projectowner import. Exact finite command is in
retained_cached_review_receipt.json. Result SHA256
`1e088971bb0e7b58e8e669702ab9be504017fec99d0969f40bda67950755608f`;
receipt `f962e5c4158e141c46987e06084d35f093ea0b6c1c469288e3c26cb2870d70ec`.
Both independent reviews pass; study COMPLETE, candidate REJECTED. No runtime
selection changed. Final context/diff/checkpoint/archive receipts follow.


R17 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r17_spatial_harmonic_v1/`:628 verified source members
in1.097555136s; manifest SHA256
`26bb7b63c3a09d2a523fcad9e61dd463c0722488b973855eff3a6c27bcec2624`.
This live receipt postdates the immutable archive. All three scientific/source
sessions are terminal/reaped0; both independent cached reviews pass. Candidate
remains REJECTED and unwired. No runtime, commit or push was performed.
