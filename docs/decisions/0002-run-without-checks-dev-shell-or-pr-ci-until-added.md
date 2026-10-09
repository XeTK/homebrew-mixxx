---
id: "0002"
title: Run without checks, dev shell or PR CI until they are added
status: proposed
date: 2026-10-08
deciders: [owner]
consulted: []
supersedes: []
superseded_by: null
tags: [deviation, ci, lint]
links:
  - https://gitea.xetk.co.uk/xetk/homebrew-mixxx/issues/3
---

# Run without checks, dev shell or PR CI until they are added

## Context

STANDARDS sections 2, 8, 10 and 11 ask for pre-commit covering every format,
`gitleaks` on every commit, CI that runs the same checks, and a flake with
`flake.lock` and `.envrc`. This repo has none of these: it has no
`flake.nix`, `flake.lock`, `.envrc` or `.pre-commit-config.yaml`, and its
only workflow is the GitHub mirror. There is no code to unit test and no
`features/`; those rules apply once a cask or script lands.

## Decision

Accept the gap while the repo holds one workflow and a README. New code
(cask generator, scripts) must come with the standard checks.

## Consequences

Removal plan, target 2027-03-31: add a flake with a dev shell (`gitleaks`,
`yamllint`, `pre-commit`), `.envrc`,
`.pre-commit-config.yaml`, and a PR workflow on a `nixos` runner. Add the
Homebrew cask audit once `Casks/mixxx-fork.rb` exists.
