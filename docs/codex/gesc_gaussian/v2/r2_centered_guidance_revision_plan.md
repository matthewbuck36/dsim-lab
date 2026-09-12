# R2 centered guidance publication revision correction

ADOPTED, 2026-09-10, source-only correction under the current method-development
authorization. Preserve the completed centered runtime v1 source result. Root
review found an actual repeated-publication path: MovingSupervisor publishes
DESIGN before issuing PREPARE, then the regular supervisor timer publishes again
at the same ROS tick after preparation. Existing controller ClockAdmission
intentionally admits distinct state/filter revisions at the same tick. Guidance
keyed by stamp alone instead treats these legitimate publications as conflicting.

First retain a focused actual SupervisorNode publication/MovingSupervisor DESIGN
transition and actual controller callback reproducer under the existing interface
overlay, bounded by 60 s. Do not edit numerical/control behavior before reproducing
the failure. Also verify ControlDiagnostics' GESC proposal, supervisor adjustment,
combined command and final command against the published centered command. If
those fields already retain correct values, make no diagnostics source change.

After reproduction, change only the new, not-yet-recorded VerificationGuidance
wire protocol to explicit schema_version 2. Add uint64 `publication_sequence`
and string `state_sha256`. The supervisor monotonically numbers every guidance
publication for its run and hashes the exact AlgorithmState using existing
message_payload/hash_payload owners. Preserve DESIGN-before-PREPARE publication
ordering; its guidance must be invalid/zero until initial preparation exists.
Subsequent selected guidance retains the immutable preparation expiry.

The controller binds each proposal to (state_stamp, state_sha256). It retains
the latest monotone guidance publication for each exact state revision. Repeated
identical sequence/payload never refreshes original source/ROS/steady receipts;
conflicting reused sequence or older sequence rollback rejects authority. A
later fresh sequence may clear that input fault after all normal checks. Do not
change the existing AlgorithmState publication-revision admission owner, any
old message layouts, numerical law, immutable stage clocks or motion limits.

The lifecycle validator separately indexes all full state revisions, validates
guidance sequence order/repeats/conflicts, and retains all current candidate,
admission, pose, PREPARE and command-expiry checks. D3 owns that edit after its
separately bounded historical-data benchmark releases source; no source changes
under the benchmark pins. Root owns scenario/recording integration.

Build interfaces once in a fresh `development/20260910/centered_runtime_v2/`
overlay, <=240 s, retaining the earlier overlay. Focused correction tests <=90 s
cover the actual duplicate-tick DESIGN path, both companion orders, distinct
state revisions, exact repeated receipt retention, sequence conflicts/rollback,
pre-PREPARE zero, rejected stale guidance and correct final diagnostics. Run the
changed centered/controller cases once under <=180 s, preserving prior failures
and exact logs/source pins. No Gazebo or new empirical release is included.
