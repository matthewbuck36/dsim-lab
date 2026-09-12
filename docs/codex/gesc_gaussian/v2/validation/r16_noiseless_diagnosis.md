# R16 noise-free diagnosis validation

Prospective plan adopted after complete R15 closure. Preparing one finite
evaluator-only retained job; no source change/model evaluation/fit has run.

Read-only owner/input review confirmed selected geometry for allsix runs:
/odom, zero jointXY, identity mountrotation and0.18m radial offset. Slots3/4/7/8
select No_Noise;11/12 select Gaussian standarddeviation0.015/seed26091133.
Each detached model must use its own resolved two-source scenario (development
and confirmation source locations differ), not the captured JSON default list.
Authoritative selected cost path/hash is present even where the optional newer
captured_cost_configuration wrapper is absent. The nominal reconstruction
premise is checked per run on unique complete source keys; repeated-support
counts remain separately reported. No model invocation or fit yet.

Before any numerical execution, independent actual-model source review found
absolute-angle polynomial/clipping/nonlinear aggregation can introduce higher
harmonics. The plan prospectively adds a third model control with base fixed
at each original anchor and identical phase/time waveform, separately fixing
copied fit XY there. This distinguishes angular/phase approximation from motion
without another experiment. Bounds become36000 model calls/288 fits;120s overall
unchanged. The original two geometry interpretations and all R15 results stay.

Independent final static review PASS. Captured noise configuration paths differ
from planned preflight copies but match content hashes; both copies are pinned.
Root rechecked70 held source/input pins, matching exact `command` lists and
absent exclusive outputs. Sole session4214 dispatched under115s SIGINT+5s kill,
internal108s,36000 model evaluations/288 fits maximum. No ROS/Gazebo launch.
Prepared SHA256 `98309ced3affadc05191bd1838d94858aa7f83a900544eec529400942ff1bbad`.
Ready SHA256 `c301106eafff75d88b79ca3a31c79281eaa3b967a06d83f89fe21e6abb744a7c`.


## Sole execution completed

Session 4214 terminal/reaped 0; outer 15.398277635s, helper 14.172489873s.
All 71 execution pins stable; errors=[] and subprocess_events=[]. Six models,
34,520 scalar model evaluations (11,702 fixed-anchor), 288 fits; 9,775 target
sample uses and 1,927 verification sample uses. Original 144 scheduled targets,
46 eligible and 40 supported matrices remain unchanged. No source/model/reference
or recorded-fit retry, bag read, new quadrature, geometry solve or ROS/Gazebo run.

Exact actual argv (execution.json records the argument array):

```bash
timeout --signal=INT --kill-after=5s 115s env -u PYTHONPATH \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  PYTHONDONTWRITEBYTECODE=1 ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 \
  bash --noprofile --norc -c \
  'source "$1" || exit; exec /usr/bin/python3 -B "$2" --prepared "$3"' \
  r16-noiseless \
  /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh \
  /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r16_noiseless_diagnosis_v1/run.py \
  /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r16_noiseless_diagnosis_v1/prepared.json
```

Outer subprocess timeout was 125s, internal scientific budget 108s. Actual
execution stayed below all prospective bounds. Root inspected retained outputs;
all four nominal reconstruction checks PASS, RMS 1.36e-15 through 4.96e-15 V.
Noisy residual RMS is 0.014951681 V (C) and 0.015004140 V (D). Moving no-noise
errors remain large; all-supported fixed-anchor per-run medians 0.09–1.88 degrees,
P90 0.62–6.14 degrees. Frozen admission is descriptive, not a transferred
calibration claim. Verification is separately noise-sensitive: both variants
pass 1/8 actual noisy, 6/8 noiseless moving and 8/8 fixed-anchor supports.
See the handoff and result.json for complete populations, errors and limitations.

Result SHA256 `f0028b107117ae5a36bf44388496d475174a5ecb40a6972261a8c4e9cb3c0d6a`.
Execution SHA256 `9efbc1a145c58455ccf09f9f8e3e5a7573720430e3858829c9c02ca99aa4a938`.
Independent cached review and material checkpoint pending; no new estimator or
simulation release follows from this offline diagnosis.


## Independent review and closure checks

Independent cached review PASS, sole finite command:

```bash
timeout --signal=INT --kill-after=2s 28s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r16_noiseless_diagnosis_v1/cached_review.py
```

Terminal exit 0, 0.880103918s outer / 0.860566120s helper, 181 stable selected
review inputs. The 14,804 assertions include per-source residual arithmetic,
164 partials, original 144/46/40/8 populations, all cached summaries and 240
q/Cq compositions. All 34,520 model calls and 288 fits are accounted for without
new evaluations or fits. Original guards, references and two historical
terminal-diagnostic mismatches remain unchanged. The review confirms that the
fixed-anchor control changes both cost geometry and nuisance design; it supports
a motion-related difference, not a unique causal mechanism.

Review result SHA256 `081909873b48553156321a8253942afccebde8f37d4f080dfb514a38c0ac9760`.
Review receipt SHA256 `6d9a98b989f06d8cee8d3c3f8101845ff76ac692c276ad1d84ab6dae285b8823`.

Recovery context validator and git diff --check PASS. Source inspection and
retained execution support no new runtime launch. closure_runtime.json finds
no selected runtime among inspectable procfs entries and explicitly retains
permission-denied PIDs; it is not a claim to have inspected every system process.
An initial read-only scan matched its own shell command text; the retained scan
restricts matching to actual executable names and absolute entrypoint argv.
Study complete; checkpoint/archive receipt follows. Full research goal remains
incomplete. No source method change, simulation, commit or push was performed.


R16 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r16_noiseless_diagnosis_v1/`: 624 verified source
members in 0.990254893s; manifest SHA256
`e28bbb50514e475fa699d698715885d52339f6da8082b02fa7ff39bf534998bf`.
This live receipt postdates the immutable archive. All retained measurements and
candidate failures remain preserved. No new runtime, commit or push occurred.
