# Q1 discovery diagnosis — 2026-09-09 UTC

The unchanged detector's score rejects the observed bounded orbit; independent
label coverage is a separate limitation. These are development diagnostics of
the two already opened discovery inputs. Q1 remains CLOSED EVIDENCE_UNAVAILABLE;
confirmation and direction reference remain unopened at this boundary.

External diagnostic root is recovery4 `diagnostics/` under
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/`.
`discovery_residence_v1/extract.py` reads frozen labels, eligible source poses
and saved cell geometry only, with no geometry/model/label/detector computation.
It completed exit0 in0.53s under60s. Its retained plot script completed under60s
and saved `discovery_residence.png` and `.pdf`; the PNG was visually reviewed.

The residence input has one uninterrupted eligible SEARCH1/generation172 chain,
3673 knots from1.826 to126.674s and maximum34ms gap. Every eligible knot belongs
to the retained positive ring cells (1896) or the enclosed hole (1777); none
lies outside the outer component. Both positive visits end at the hole,
45.856s and98.148s. This knot classification describes the saved mask without
replacing the frozen continuous-segment labels. The whole eligible trajectory
has8.11948m path length and radius0.353917m around its time-weighted mean.
Its extent is x[0.803158,1.440014], y[0.870452,1.468207]m. This shows bounded
recurrent motion, not a certified attraction basin or accepted extremum.

The retained mask is a sampled near-minimum sublevel region with holes, not a
general oracle for positional confinement. Preserving the holes is essential
to the old claim. A future positional-settling oracle would need an explicitly
different prospective definition, not silent relabeling of Q1.

`discovery_detector_response_v1/extract.py` instruments the unchanged detector
through the existing Q1 admission owner at W6s/epsilon0.30m/R0.75m only. It
records every completion from both discovery inputs:20 per run,5 warmup and15
full36s histories. No parameter grid, label computation, M3 evaluation or
confirmation inspection occurred. Before/after hashes match. Exit0 in1.674s
under60s; exact command is in `command.log`. Result SHA256:
`44721a45c9ccaf5e7ab04973dc9644eba43b11d4ec1149b819de4e9e9f4fea6e`.

| Input | Full-history score min / median / max (m) | Radius gate |
| --- | --- | --- |
| Residence |0.777775 /1.017870 /1.158211 |15/15 pass;0.317713–0.387027m |
| Approach |1.178197 /1.208687 /1.900668 |12/15 pass; last7 all pass |

Every full-history score exceeds0.30m. Residence early/late score medians are
1.016307/1.017870m, so later support does not remove the effect. Admission has
no generation gaps. The means still follow the slow spatial orbit during each
6s window; the sum of their five shifts stays substantial despite confinement.

A larger epsilon alone cannot satisfy the approved negative family at W6:
straight0.02m/s motion gives S=5*6*0.02=0.60m and36s support radius0.36m. An
epsilon large enough for the observed residence scores would also admit that
negative at R0.75m. This analytic incompatibility does not establish that GESC
direction is wrong. Diagnose the second component independently before tuning
either implementation; preserve original numerical/scientific gates.
