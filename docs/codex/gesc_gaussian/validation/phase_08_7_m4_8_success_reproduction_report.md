# Phase 08.7 M4.8 retained-success reproduction report

## Result

**PASS for the user-defined retained-success reproduction observation:
`13/17` fresh formal combined passes, exceeding the fixed `9/17`
“most pass again” threshold.**

All `17` evidence-selected historical definitions ran exactly once, in
their sealed order, with no retry or parameter change. Fourteen repeated
the historical successful robot behavior. One of those fourteen had an
independent recording-evidence failure, leaving:

```text
fresh formal combined pass:             13/17
fresh behavioral pass:                  14/17
fresh behavioral failure:                3/17
formal classification agreement:        13/17
behavioral agreement:                    14/17
user-defined most threshold:              PASS (13 >= 9)
```

This is a retrospective reproduction result for known-successful
conditions, all at the fixed simulator-relative local/global light inputs
`400/1600`. It is not an unbiased robustness population, does not repair
the failed Phase 08 suite gates, and does not establish three-light or
physical readiness.

The automatic `1.20 m` or `1.00 m` global-proximity stop used here belongs
only to the simulation runner. Physical testing must not inherit any
automatic distance stop: termination remains under manual operator
control, and the robot is to continue until the operator judges it
sufficiently close and presses `Ctrl+C`.

## Fixed execution boundary

Every run identifies clean campaign commit:

```text
1550d3377a6434524aab9ea2f764b7024d41c912
phase 08.7: qualify retained-success reproduction
```

The source/install qualification, exact cases, scenario hashes, original
run IDs, GUI/headless modes, ROS domains, time bounds, and dry-run commands
are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_no_gazebo_qualification.md
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_success_reproduction_manifest.json
```

Fresh evidence is isolated below:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_v7_success_reproduction_1
```

No original run, summary, completeness document, or analysis was
overwritten. The original M4 and M4.2 evidence failures remain failed.

## Case-by-case outcome

“Formal match” compares the original and fresh combined classification.
M4 is a formal match only because both attempts were formally failed; its
fresh failure mechanism changed from the original evidence-only failure to
a behavioral Stage B miss.

| Case | Mode | Original | Fresh | Stage A / fill | Fresh Stage B | Completeness | Analyzer | Recovery | Formal match |
|---|---|---|---|---|---|---|---|---|---|
| `v7_m2_3_diagonal_r1p5_h25_18001` | GUI | formal pass | formal pass | pass / pass | pass, `1.199688 m` | pass | complete | direct | yes |
| `v7_m3_r1p0_a45_h25_18101` | headless | formal pass | formal pass | pass / pass | pass, `0.999756 m` | pass | complete | direct | yes |
| `v7_m4_probe_r1p5_a45_h25_18201` | GUI | behavior pass / evidence fail | behavior fail | pass / pass | fail; best `2.270542 m` | pass | complete | direct | yes |
| `v7_m4_2_probe_r1p5_a45_h25_18208` | GUI | behavior pass / evidence fail | formal pass | pass / pass | pass, `1.199281 m` | pass | complete | direct | no |
| `v7_m4_3_probe_r1p5_a45_h25_18308` | GUI | formal pass | formal pass | pass / pass | pass, `1.197980 m` | pass | complete | direct | yes |
| `v7_m4_3_r1p5_a45_h25_18309` | headless | formal pass | formal pass | pass / pass | pass, `1.199969 m` | pass | complete | direct | yes |
| `v7_m4_3_r1p5_a67p5_h25_18309` | headless | formal pass | formal pass | pass / pass | pass, `1.197247 m` | pass | partial | direct | yes |
| `v7_m4_3_r2p0_a45_h25_18309` | headless | formal pass | behavior fail | pass / pass | fail; best `1.213880 m` | pass | complete | direct | no |
| `v7_m4_3_repeat_r1p5_a45_h25_18310` | headless | formal pass | formal pass | pass / pass | pass, `1.198398 m` | pass | complete | direct | yes |
| `v7_m4_3_repeat_r1p5_a45_h25_18311` | headless | formal pass | behavior pass / evidence fail | pass / pass | pass, `1.197368 m` | fail | unavailable | direct | no |
| `v7_m4_3_repeat_r1p5_a45_h25_18312` | headless | formal pass | formal pass | pass / pass | pass, `1.197733 m` | pass | complete | direct | yes |
| `v7_m4_4_probe_r1p5_a45_h25_18408` | GUI | formal pass | formal pass | pass / pass | pass, `1.199240 m` | pass | complete | direct | yes |
| `v7_m4_4_r1p0_a45_h25_18409` | headless | formal pass | behavior fail | fail / fail | unavailable; final `3.720754 m` | pass | partial | not completed | no |
| `v7_m4_4_r1p5_a45_h25_18409` | headless | formal pass | formal pass | pass / pass | pass, `1.199309 m` | pass | complete | direct | yes |
| `v7_m4_4_r1p5_a67p5_h25_18409` | headless | formal pass | formal pass | pass / pass | pass, `1.199618 m` | pass | complete | direct | yes |
| `v7_m4_4_repeat_r1p5_a45_h25_18411` | headless | formal pass | formal pass | pass / pass | pass, `1.199739 m` | pass | complete | direct | yes |
| `v7_m4_4_repeat_r1p5_a45_h25_18412` | headless | formal pass | formal pass | pass / pass | pass, `1.199861 m` | pass | complete | direct | yes |

Aggregate behavioral and evidence predicates:

```text
Stage A local recovery:                16/17 pass
exact one-fill cardinality:           16/17 pass
Stage B, all cases:                   14 pass, 2 fail, 1 unavailable
Stage B after completed Stage A:      14/16 pass, 2 fail
collision/forbidden evidence:         17/17 pass
final command zero:                   17/17 pass
scoped cleanup:                       17/17 pass
SQLite PRAGMA quick_check:            17/17 ok
recording completeness:               16/17 pass
```

All sixteen completed Stage A paths were direct:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL ->
ESCAPE_REPULSE -> RECENTER -> SEARCH
```

No fresh run entered `ESCAPE_ASSIST`. The campaign therefore reproduces
direct recoveries but does not exercise the redesign-assisted path.

## Behavioral disagreement diagnosis

### M4 visible: late Stage A left only a short fixed horizon

The fresh M4 attempt completed Stage A at simulation time `294.834 s`.
Its fixed total horizon ended at `361.644 s`, leaving only `66.810 s` of
post-recovery search. It began Stage B `2.719234 m` from the global, reached
a best `2.270542 m`, and ended at `2.311372 m`.

This was not a wall-margin, collision, or `FAILSAFE` stop. Recording,
final-zero, SQLite integrity, and cleanup all passed. The direct local
escape succeeded, but the older M4 fixed-horizon behavior neither acquired
the global nor made enough sustained progress before the total run budget
ended.

### M4.3 radius 2.0: full-budget near miss

The radius-2.0 case completed Stage A at `155.302 s` and consumed the full
declared `120.020 s` Stage B budget. The live timeout sample was
`1.221840 m` from the global. During ordered shutdown the final recorded
pose reached `1.213880 m`, still `0.013880 m` outside the fixed `1.20 m`
gate.

This is a time-budget-limited near miss, not a collision or safety
intervention. It must remain failed because no valid sample entered the
unchanged acceptance radius.

### M4.4 radius 1.0: convergence confirmation did not complete

The fresh radius-1.0 case remained in `SEARCH` for the full run, traveled
`29.129297 m` around the local field, and emitted only two convergence
candidates:

```text
t=73.1 s:  count_remaining=2
t=124.8 s: count_remaining=1
```

No third candidate or `CONVERGENCE_CONFIRMED` event occurred, so no fill was
created and Stage A never opened. The retained original run reached its
third candidate at `127.6 s` and passed. The same seed therefore does not
make continuous Gazebo/ROS timing and numerical phase deterministic enough
to guarantee identical detector confirmation. The fresh failure is at the
detector-to-supervisor handoff, before recovery, not in wall, collision,
recenter, affine, or global-stop logic.

## Independent evidence-only failure

M4.3 repeat seed `18311` passed all behavioral predicates and reached
`1.197368 m`. Its only failed completeness check is `console_clean`.

The console proves the velocity controller itself activated:

```text
21:16:35.013  velocity_controller: activate successful
21:16:35.124  failed to send switch_controller response to the client
21:17:04.523  spawner timed out waiting for the response
21:17:04.524  retry found the controller already active and could not
               activate it again
21:17:04.691  spawner exited with code 1
```

Motion preflight subsequently passed, the complete behavioral path ran,
the bag contains `539383` readable messages on `34` topics, final commands
are zero, final readiness is false, and cleanup passed. The failure is a
controller-spawner response/idempotency evidence defect in the preserved
historical M4.3 launch behavior, not a robot-behavior failure. It remains
formally failed; M4.8 does not weaken `console_clean` or rerun it with a
later startup correction.

## Presentation and geometry groupings

```text
visible GUI:               4/5 formal, 4/5 behavioral
headless:                 9/12 formal, 10/12 behavioral

r=1.5, 45 deg:           10/12 formal, 11/12 behavioral
r=1.5, 67.5 deg:           2/2 formal, 2/2 behavioral
r=1.0, 45 deg:             1/2 formal, 1/2 behavioral
r=2.0, 45 deg:             0/1 formal, 0/1 behavioral
```

The M3 radius-1.0 case passed the stricter `1.00 m` gate while the M4.4
radius-1.0 case never completed detector confirmation. Radius alone is
therefore not a sufficient outcome predictor. The two `67.5 deg` cases
both reproduced. The one radius-2.0 case nearly reached the global but
remained formally outside its boundary.

The fixed `400/1600` ratio produced thirteen formal and fourteen behavioral
passes in this evidence-selected set. That supports using this ratio as a
known-good two-light test condition; it does not turn the selected sample
into a broad robustness claim.

## Standalone validation and analysis

The isolated installed `validate_run` owner was invoked once for every
fresh run. It returned the expected `0` for all sixteen complete recordings
and the expected `1` for seed `18311`. That failure remained exactly the
single `console_clean` check above.

The isolated installed `analyze_run` owner was then invoked once for every
complete recording, writing below each run at
`analysis/phase07`. Results:

```text
complete analysis:       14
partial analysis:         2
unavailable by contract:  1
analysis failures:        0
recording failures in
  analyzed bags:          0
outputs per analyzed bag: 8 plots, 11 tables
```

The two partial outputs are explicit and non-gating:

- M4.3 `r=1.5, 67.5 deg` has two `/algorithm_state` gaps exceeding
  `0.150000 s`, invalidating only derived state durations.
- M4.4 `r=1.0, 45 deg` has no escape attempt, so the escape-duration,
  orbit-count, and radial-progress metrics declared applicable to that
  scenario are unavailable. This agrees with the Stage A failure.

The seed-18311 analyzer was intentionally not run because its standard
completeness gate failed. Its readable bag was not forced through a weaker
analysis path.

## Retained hash inventory

Each line is:

```text
case_id | scenario_result.yaml | completeness.json |
summary_metrics.json | analysis_completeness.json
```

The last two entries are `UNAVAILABLE` for the one completeness-failed
run. In manifest order, the SHA-256 of the newline-terminated inventory
below is:

```text
4445e970ba77b879798cfda841941442dcfbc6c48c108a92bb5e6480db861f73
```

```text
v7_m2_3_diagonal_r1p5_h25_18001|0cfa691f37905fa2afeaa8b2f87a033166211bbca65532ecf3385ca2f2a869d4|0e8e832965e2f01d19cec0e400829c222cf4809e349c084bfb3b577a81441a92|9da07f210aee6be624180d43fae63eb04cc13fdb5fcb86b5b0a934bbf1151655|6a951764ff8b6f15ddd25c56f959cca93e56112c27cddf57bdaaae5527020d81
v7_m3_r1p0_a45_h25_18101|ebbe11a28f43923b6b29d2bf85c292bf50750f6d4d857a1469677157b1109ba5|7746b2a086a5779129cd4901a1d5e0d83857fcc35e7461da92797a32067ac697|38c325c043d8045778a7f8df656c68e93836c4e8317bd96cb1183ec82284762b|ed2286cd12cb273385a58e863852a9cc5952b4f2349f523c7f2e77a20a12d6d0
v7_m4_probe_r1p5_a45_h25_18201|aeb6b3cf3137fd798c77cea40ca65ea92e55caab9c855d8d3c791a3177c95947|87c2439d153b3231cdea1234f0854b1f3e545b83e9740a96b244aede8f3ebe81|d2161aaddb3f9673937e6dce8a4c839903cf3a0e6d83406cd185f3c51b34da7b|d14a459393dd893d8756206d9dc7542d3b5289ab0cd422c80f4b4d88dca3ee98
v7_m4_2_probe_r1p5_a45_h25_18208|af1853d0bd9ef407b9e2916243aab3614c5b82a4a6e93cf6c22ca6864206cb96|508898f449bc4ad3f45289ae95e22d7ce9f96cbab538ea635b2dee1870cf25da|356764dd523751aeb38e38c3bf12de95a91835334e7cfb0175ae6ca8a147292f|fd8ea2587825f2632c27cc7b3eb53ec26697e1fc9065ccbcbe1b3df18d02b2c8
v7_m4_3_probe_r1p5_a45_h25_18308|6eb07c3666b123206ceff096b8063487454c1549a9266ef8aa40dde1348d5fa6|f80d9fa332235ed61301008167797af232b1ada61747d336d3ac3580792ebb7f|a39972f8ce81d2f21e3d21acbdb176948f72c8bfa7390b155dcfdc26708c8773|03d4cae10103fa49d11ac3de6eb7a13b214990de1f8f2b11f79380c6ad9e9198
v7_m4_3_r1p5_a45_h25_18309|02db70f1d0bf067f8f736bf805ea0f01e04f5ada4b4b8cd7a2bfa7e5a4078e04|6943b8968153b801293554a953fe49361fdfa657c955a03ed6479be8c8d99b0f|21fa42b644b08eb9ed257435f62b84935428f06617bd02b4fbb62cace1980e97|bc1a770fd3279be0c98495e9208fe4b8e7586fc9feefe68bbe6e593d53a1e7ed
v7_m4_3_r1p5_a67p5_h25_18309|da24de974419029c1786abd7c995cd31763aef4741252b03422ef45559f6aab0|f3a207eb6580911843a00dfd5940196612eb88535bc67da880a77b0b1096a1e0|c674cb8748fc700e51a4e29b9e121122ef1891dcd8c60bc4ebab60536b7fddf0|4c6c38ea4d6c3d3c8953e2bdf32b6f461bd09f4ffdcd5a6f224a1d4d292952a0
v7_m4_3_r2p0_a45_h25_18309|3ca47ad66c3c0c4cc4455b0938a5a5e6064c9e9eb9067f2c8dd26e5281a3a0b7|019ea1c237de383b59d187a546a53bc9ce2102e0ce6faa4feab2d702d9708541|279fa7e03495619b12275a4821030f376ee8c8da9fff63c66bf6cda1650bf5c3|014215a9d650de469293453d70222059cca5b174b05b85256f7f8d87f1a64502
v7_m4_3_repeat_r1p5_a45_h25_18310|c8fe0162095bc167a678ae1f63dfea5be71f29216f6f89f49cc41d3ce976cfa8|4139053d178cf438440d64dcf75ec9db048b5db8191a9561c5a0e94f35dd810c|0e910c62f826d5c0f90c0a9cb61325e48568af06288ab985ac167675b239832b|0aa3a754188ef2711938c13ee6d6c472f5dfc49b941285faa4f56d7e45d0ae62
v7_m4_3_repeat_r1p5_a45_h25_18311|adbd3e0fec668a18ab3d5b0c93920b8c796a535a8137cc72ac9bad630aea0c14|2eb795b6efa3e6f71e9a7932d92a88e0293ca914d0bc6b922f4763d28d77548e|UNAVAILABLE|UNAVAILABLE
v7_m4_3_repeat_r1p5_a45_h25_18312|c3da77a73ad090da296217274df50d6f4844114a0e419fb022db5db72cf844ee|95bea3eab07f72b2d79db7f581dae07d6a11e230a6520e8aff0324e6c3545c73|5411f00e7a16c8412f4ad3c9265e35d0b8ddbab43686a747854b8f8db7d5f7d0|56ec708405577f398415d3622e1ec8ceff406f4b1eb4f7d2ae33b83d3a95459f
v7_m4_4_probe_r1p5_a45_h25_18408|f724119646e96f3c8e7eeb172287771457865767ea1729afe1968aee600007c5|ead35d1bbe8c436809cd187c60bd1176bf35aaaf370f1ad2dfe0e5bc6f697445|4bfeb1d9a37ca21a8d74eb71c62190deaaaa4e75f4e1724785fae8c4e0da9542|b6587f91a6736f436945dcabee02cfd0b6a96dca91c8aa275248fef87f1886b2
v7_m4_4_r1p0_a45_h25_18409|4aca80a9b054972e40fd3e32002395f959adec4aef9109f08c8fa4eee16d12b2|ba1ab290a73f678341b87daa12535bceeaf4063296c0f59ec9fd0ea49034a112|0b69a9ed66c241230b2e65e7deea1d81d8dd724a664cfa913752c67c06042845|2f47353b478a4ead855670538d1f317ead37ce360188a2db5962d3f9019e20f9
v7_m4_4_r1p5_a45_h25_18409|bda48de563659eaa1cdd524ee015f954cfb384057f3cd6005f142704b5cc38a9|5c2ed7d6c908d937a2c59539c8116d2882f1f598619b14420c13488354575f19|887636b323c1b565b5d86ca437ce4a1fde0e336df10d82662a5ae69f685ceb8a|91fa91099f220959f5b6ffaf6e56b38d0997428b553f3f7f7b50e32f60aa8fa5
v7_m4_4_r1p5_a67p5_h25_18409|d02f2f0535a0b8407fd04f19f5de4b6ce156517fdbb9dba9c0aa1cec8d12e384|a3f4f4840a978511b1d2f3ed42ae91604f5d78c891ef62a663694be94f922eb7|677a61bf22ecd9050423d0d4c6cef72cd1756e5b949e6b5f1c4768dbf2dde3e5|05ed22ab9f2a3f65627f78b1e06eb74364526d17642942a2c5cb8c790a5519b0
v7_m4_4_repeat_r1p5_a45_h25_18411|d39f095d34e2f7094060c1574b974ed15eff889ef64226b4829d178eaec7ae92|145445189e11e35c7c2da0cfc09cb7692119228269a0977717ff6e4607f7a5fb|4e3efa665487d09d41a74f9dd3e67a5ea0abc64e2818939645c6f55a2020bc9e|86c38f205f4e8ffda56543681c1df69ef59c29d30d75f4929d5c7e3fb88e18a3
v7_m4_4_repeat_r1p5_a45_h25_18412|f0bff3bd9f3fc37b3c5ff23b7a260382b18ebedbb4e1d8694ae7b5408da162b0|bfb4f0db8333f4f5d0378ce5ae64513d3013ce71ce0d78567041fd0963b56982|f8f2779c8fac42b519418bb5a8560a049ae8d3b44274983fb901d161cdd56ec6|ae2f776b10bb01e0503ae5523ddaf16c0c1b433793a90d00b5c3f9ff5075ef76
```

## Physical termination boundary

The simulation monitor stopped passing cases on the first valid
post-Stage-A odometry sample inside the case-specific radius. That policy
does not belong to the controller and must not be used by the physical
launch or recorder.

For Phase 09 physical testing:

- no `1.20 m`, `1.00 m`, or other automatic global-distance termination is
  authorized;
- global distance may be recorded as diagnostic evidence only;
- the robot continues until the operator presses `Ctrl+C`;
- `Ctrl+C` must enter the audited ordered shutdown path: readiness false,
  stop request, final-zero verification, bag finalization, and scoped
  descendant cleanup.

No physical command or hardware process occurred during M4.8.

## Closeout

M4.8 achieved its declared observation: most historically successful
definitions passed again. The retained result is `13/17` formal and
`14/17` behavioral, with three distinct behavioral disagreement mechanisms
and one independent evidence-only startup-response failure.

No additional Gazebo run, automatic retry, three-light case, Phase 09
implementation, physical command, or whole-Phase-08 report is part of this
milestone.
