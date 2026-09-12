# R23 retained guidance/admission evidence

Capture sole56208 terminal/reaped0 in2.945496s under45s INT plus5s kill. Exact command:
clean initial PYTHONPATH/RMW, source the existing R21 runtime_environment.sh, then
`timeout --signal=INT --kill-after=5s 45s /usr/bin/python3 -B` followed by external
`development/20260911/r23_guidance_admission_v1/capture_once.py`.

One existing read_run_bag call selected guidance, events, state and automatic
readiness. Selected counts:7224 guidance,27 events,7227 states,3705 readiness.
Full detached wire projections and hashes remain in capture_v1/selected_records.json.
All14small direct/source pins and bag file stats remained stable. No raw hash
rescan, full lifecycle validation, models, references or simulations ran.
Capture receipt SHA256
`50eabf33b48f642806227a9585e54d1384b5c7353a6cabebc6a50669440d99fd`.

Exactly one valid approach message fails the original predicate: candidate2,
epoch2, accepted161.9s, publication sequence3234 at162.0s, collection_started=False,
collection_admitted_at=0, verification deadline169.9s. Its exact state companion
hash is `dff42c237325fcc2f8a6aebff74425ab2b5373faedd0d465b7108469bf6ba05b`.
The unique admission event also has162.0s. The next publication, sequence3235,
is valid COLLECT for the same candidate at162.0s and admitted_at162.0s. Later
3236/3237 remain COLLECT. No candidate regresses from COLLECT to APPROACH anywhere
in the selected stream. Cross-topic bag receipt order is not used as causal proof.

Source audit confirms guidance uses one monotone publisher sequence and copies
the candidate's admitted fields. The runtime sets admission before publishing
its stage event. Separate callbacks can share a simulation-clock timestamp;
the validator precollects all events before auditing guidance, losing that
earlier/later distinction when it uses only strict timestamp comparison.

This is evidence for an equality-boundary validator correction, not a blanket
timestamp relaxation or an algorithmic success claim. The proposed proof would
defer only the equal-timestamp approach until a later fully validated same-tick
COLLECT publication establishes the transition. All immutable identity, state,
pose, deadline and sequence checks remain necessary. Independently reviewed
capture evidence and a prospective correction plan precede edits/tests.
Original C11/V14 recording failure and C11's separate behavioral nonarrival remain.

R23 source correction COMPLETE: focused187PASS (13new), independent source review
PASS. Validation receipt5628194dc82f6a520b132306871fed28e987941fc533f51da428559b7cb79413.
Material archive688verified members,1.002444s, manifest
91e4e9f3f885a76d24b4ca1c93413a3019064ef15fc33fc92fa90db4431d91f2
at checkpoints/r23_guidance_admission_closed_v1/. The unchanged existing
save_source_checkpoint.py implementation was scoped to this exclusive OUT and
the R23 EVIDENCE directory under a30s bound; no helper source was modified.
Current phase plan updated after V14 closure; V14 archived plan/source unchanged.
Context and diff checks pass. This annotation follows the archived source snapshot.
No simulation is running; full goal and missing comparison conditions stay open.
