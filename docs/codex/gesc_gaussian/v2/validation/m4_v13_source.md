# M4v13 source validation

Plan:[M4v13](../m4_v13_integrated_comparison_plan.md), ADOPTED after R21 D02
complete integrated success and independent review. Current state: implementation
and independent static review complete; no source test, preparation or V13
simulation has run.

External source root:
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/.
Six potential orchestration owners have exact before copies under before/ and
before.json. No numerical detector, direction, verification, controller, fill,
clock or ROS-interface change is authorized by this comparison version.

Existing V12 helper copies were adapted to this version before execution:
validate_source.py,prepare_once.py,save_source_checkpoint.py,
archive_preparation.py,release_dispatch.py,acquire_once.py. helper_origins.json
records original and adapted hashes. All six parse; preparation/acquisition
release still uses the existing M4 workflow and dispatcher. The two old fixture
corrections in V12 are historical and are not copied into V13 preparation.

One source bundle is planned with230s pytest work,5s termination and260s
inclusive. Exact named test selection, source/environment/21 installed entrypoint
pins, command, logs, JUnit cases and result will be retained before/after the job.
Existing V12 real-preparation tests require the old R10 whole-file launch/lifecycle
pins and therefore do not represent preparation under the current R21 checkout;
preserve that historical fail-closed behavior and verify historical resolved
scenario/metric behavior through focused fixtures. V13 must bind its explicit
R10-to-R21/D02 source bridge, not weaken the old prerequisite.

No commit/push, physical, Pi, snapshot or V1 changes. Branch
feature/gesc-gaussian-robustness-v2; HEAD3369cfc83a64ff5d8354827fd5310caaf0c8e945.
Full goal remains open, including the explicit unachieved original basin-entry
latency target in the acceptance ledger.

Static review PASS is retained in static_review_v1.json with current source,
three owner readiness receipts, helpers and fixture bridge hashes. Review caught
and corrected copied pilot/source-root spellings, the exact D02 source population
and explicit recorded-arrival selection for every release row before execution.
The initial unexecuted helper versions remain under before_helpers/.
The fixed tests_v1.json selects31 unique modules/named regressions; exact expanded
case count will come from the sole JUnit result. Numerical runtime sources stay
unchanged from the completed D02 case. Source validation is next.

Sole source validation session45897 is running under260s inclusive. Outer argv:
`timeout --signal=INT --kill-after=5s 255s env -u PYTHONPATH -u RMW_IMPLEMENTATION
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1 MPLBACKEND=Agg ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0
bash --noprofile --norc -c 'source "$1" || exit; exec /usr/bin/python3 -B "$2"
--version focused_v1 --tests "$3"' m4-v13-source
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/runtime_environment.sh
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/validate_source.py
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/tests_v1.json`.
Source/helper/test files and root plan are held until terminal evidence. Internal
command and all before pins are retained in focused_v1/started.json, outputs in
focused_v1/pytest.log,pytest.xml,source_validation.json when terminal.

## First job terminal and isolated fixture correction

Session45897 terminal/reaped1:637passed/3failed out640 unique cases,
144.097535851s total,141.13s pytest. All961sourcepins and21installedentrypoints
remained stable. Full log/JUnit/source_validation.json are retained unchanged
under focused_v1/. No scientific or runtime owner needs a change.

The prospectively adopted correction addresses only absent optional execution,
missing reference rows after deliberate timeout, and a B mutation fixture caught
by the earlier label/summary join. Tests are preserved before correction; three
unexecuted preparation/archive/release helpers now select focused_v2 receipts.
The second identical selection is permitted once under the same260s inclusive
cap. This produces a coherent full selection without inventing an aggregate PASS
receipt or rerunning any empirical experiment. All six production owner hashes
still equal the first validation's after pins.

Second source validation session59696 is RUNNING under260s inclusive. Exact outer
argv is the first command above with only --version focused_v2 and
m4_v13_source_v1/tests_v2.json substituted. The test selection bytes are identical;
source is unchanged and the two fixture corrections are retained. Outputs are
focused_v2/started.json,pytest.log,pytest.xml,source_validation.json. All source,
helper and test files are held until terminal; no preparation or simulation.

## Second job terminal: full selected bundle PASS

Session59696 terminal/reaped0:640passed/640 unique cases,148.800668155s inclusive
helper elapsed and145.82s pytest. All source pins, before/after maps and21installed
entrypoints remain stable. There are no failures or skips. Both identical640-case
populations remain preserved; no aggregate/mixed PASS receipt was needed.
The actual V13 prerequisite chain, R21 interface selection, all sixteen scenario
routes, historical scenario/metric parity, every release guard and exact recorded
arrival selection passed the selected checks. This is source validation; it does
not claim a sixteen-run empirical result. Independent cached review and material
checkpoint precede the one existing preparation job. No V13 simulation has run.

Second validation has963 stable pins. Source-validation SHA256:
`5591b1cbbfbf207d02104fe4975b8d1bbfb7221c008f6a09dc40e41bcf7dfcda`.
Context validator, git diff --check and existing checkpoint tool PASS after the
terminal source job. Independent cached review is pending; no files in the
validated source map changed during live-status updates.

Independent cached source review PASS: source_validation_review_v2.json,
SHA256a3f0fffec4d3ac9f9d0ae820180a29ae9935d4e6ad2913f3c0efbd0742a7eb1f.
The same640case identities and JUnit outcomes, original637/3failure retention,
unchanged six production owners, exact declared fixture/helper/plan differences,
963currentpins and21entrypoints are verified. Review uses only cached files;
no scientific execution or new helper. Material source checkpoint follows.

Material source archive COMPLETE:checkpoints/m4_v13_source_v1/,666verified source
members,0.932406091s; manifest SHA256
`5b7eb1ab46f840a2243c011a5be5a9cadb921819a8fddd5cd89fd7ed95b0f587`.
Exact command:timeout --signal=INT --kill-after=5s 25s python3
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/save_source_checkpoint.py. Live receipt postdates archive.
Source milestone is COMPLETE; one600s existing-owner preparation is next.
