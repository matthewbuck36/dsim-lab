# Phase 08.5 V5 Failure Report

## Terminal disposition

**V5 CLOSED — FAILED ACTIVATION; NOT SIMULATION-READY.**

V5 ran eight pass-eligible visible-Gazebo activation cases from the fresh
`phase08_v5c` evidence root. Every recording and cleanup completed, but all
eight cases failed the mandatory `route_blocker_encountered` predicate.

The first Gaussian fills were `1.2624-1.5782 m` from the committed blocking
basins, exceeding the `0.35 m` limit by a wide margin. The GESC trajectory
curved around the statically proven start-to-global blocker and first
converged elsewhere. V5 therefore did not test escape from the intended local
minimum.

## What worked

- Fresh V5 population generation and static route-basin proof.
- Exactly two or three lights in every committed case.
- Complete qualification from the isolated install.
- Actual visible Gazebo, ROS recording, final-zero evidence, and cleanup.
- Gaussian fill, escape, recenter, resumed search, and later global
  convergence in four of eight runs.

## What failed

- Runtime encounter with the intended route-blocking local basin: `0/8`.
- Full V5 behavior contract: `0/8`.
- Activation: required `10/10`, observed `0/8` contract passes with two cases
  not run.
- Case `15008` analysis integrity: partial because `state_durations` was
  invalid, despite complete recording and clean shutdown.
- Activation early-stop enforcement: the first contract miss did not halt the
  workflow, so seven additional failed activation cases ran before the
  integrity hard stop.

## Consequence

No headless development, freeze, holdout, validation, or reproducibility run
was authorized. The terminal total is `8 executed` and `112 not_run` out of
the declared 120.

Do not resume or relabel V5, modify its committed geometry, count these runs
as acceptance passes, create a simulation-readiness tag, start Phase 09, or
run physical hardware.

Any separately planned successor must force the local basin against the
observed GESC trajectory/envelope rather than relying only on a straight-line
projection, and must stop activation on the first route-blocker predicate
failure.
