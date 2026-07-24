# Phase XX Plan — Title

## Objective and scope

State the bounded objective, success criteria, in-scope work, and explicit
exclusions.

## Repository findings

Record the exact packages, existing owners, paths, interfaces, dependencies,
configuration, tests, and repository state that govern this phase.

## Existing implementation to reuse or extend

Identify each existing node, class, module, launch path, or script that will be
extended. Explain why no parallel replacement is needed.

## Files to modify

List exact repository-relative paths and the intended change in each file.

## Files to create

List exact repository-relative paths. Justify every new node, package, message,
topic, dependency, or tool.

## Public interfaces and parameters

Define affected topics, message/service/action types, parameters, defaults,
units, timestamps, rates, launch arguments, command-line interfaces, and data
formats.

## Backward compatibility and migration

Describe the legacy profile or feature flag, preserved interfaces, rollout
order, and any migration effect.

## Implementation sequence

Provide a decision-complete ordered sequence that another engineer or Codex
chat can execute without choosing architecture or behavior.

## Tests and acceptance criteria

List exact tests, fixtures, commands, expected results, and regression checks.

## Risks and stop conditions

State when implementation must stop rather than guess, silently redesign, use
physical hardware, or overwrite unrelated work.

## Implementation-time verification

List assumptions that the Implement chat must verify against the current
repository before editing. A contradiction must be reported with exact
repository evidence.
