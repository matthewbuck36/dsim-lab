# V2 M0 workflow validation

Verified 2026-09-08 on `feature/gesc-gaussian-robustness-v2`, with base HEAD
`3369cfc`. This record covers the three existing phase tools and their new
temporary-repository regression suite. It makes no algorithm or simulation
acceptance claim.

## Changes checked

- The context validator, status initializer, and checkpoint tool accept the
  exact `v2` token and resolve the new `docs/codex/gesc_gaussian/v2/` namespace.
  Numeric phases 00-10 keep their existing context rules and output paths.
- V2 planning requires shared baseline context, environment/navigation guides,
  the Phase 10 handoff, and the saved V2 plan. Implementation also requires the
  V2 live status and all six existing mandatory status headings.
- Initialization retains a nonempty existing status and refuses to overwrite
  an empty existing file, for V2 and numeric phases.
- V2 checkpoints include plan/status hashes, separate binary staged/unstaged
  diff hashes, and a deterministic dirty/untracked-file hash manifest. The
  manifest handles deletion, symlink targets without reading their destination,
  binary content, file modes, and filenames containing spaces/newlines. Git's
  ignored untracked files are outside the manifest. The generated checkpoint
  and its temporary file are explicitly excluded from content hashes.
- Checkpoint construction uses a temporary file in the destination directory;
  successful replacement stays on the same filesystem. Hashing failure leaves
  the previous checkpoint intact and removes the temporary file. The temporary
  file is excluded from the recorded Git state.

## Exact validation commands and results

Run from the repository root:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 plan
```

PASS before edits and after implementation: `Phase 10 plan context is complete.`

```bash
timeout 60s python3 -m unittest discover -s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/tests -p 'test_phase_workflow.py' -v
```

PASS: 10 tests in 1.238 seconds. Tests run the actual tools in disposable Git
repositories, including repositories and filenames with spaces. Coverage
includes plan validation for every numeric phase 0-10, numeric implementation
and checkpoint paths for 00/08/09/10, latest Phase 08 subphase selection,
V2 requirements and status headings, invalid tokens, overwrite protection,
binary/staged/untracked hash sensitivity, checkpoint self-exclusion, latest
milestone capture, failure preservation, and temporary-file cleanup. Temporary
repositories were removed after each test; no retained V1 file was mutated.

```bash
bash -n docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh
git diff --check
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

PASS: Bash syntax, whitespace check, current V2 planning context, and current
V2 implementation context. Python `ast.parse` also passed for the regression
test file without writing a bytecode artifact.

No ROS/Gazebo, hardware, Pi transfer, build, commit, or push was performed for
this bounded tooling validation. The main V2 live status/checkpoint records
the combined M0 milestone and subsequent Git boundary separately.
