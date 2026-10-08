---
id: "0003"
title: Mirror workflow uses the legacy runner label and host tools
status: proposed
date: 2026-10-08
deciders: [owner]
consulted: []
supersedes: []
superseded_by: null
tags: [deviation, ci, nix]
links:
  - https://gitea.xetk.co.uk/xetk/homebrew-mixxx/issues/3
---

# Mirror workflow uses the legacy runner label and host tools

## Context

`.gitea/workflows/mirror-to-github.yml` runs on label `linux-x86`, not one
of the homelab labels (`nixos`, `nixos-deploy`, `nixos-hil`). Its steps use
the tools already on the runner (`git`, `ssh`, `curl`, `python3`) instead of
`nix develop --command …`, and it uses `actions/checkout@v4` by tag, not by
digest. It handles a credential (`MIRROR_DEPLOY_KEY`) so it belongs on the
`nixos-deploy` label.

## Decision

Accept the gap until the repo has a flake. The workflow works today and the
key is scoped to this one GitHub repository.

## Consequences

Removal plan, target 2027-03-31: after 0002 adds a flake, move the job to
`nixos-deploy`, run its steps via `nix develop --command`, and pin the
checkout action. Check that the `nixos-deploy` label is allowed for this
repo first.
