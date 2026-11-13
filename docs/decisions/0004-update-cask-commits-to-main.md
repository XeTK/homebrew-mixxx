---
id: "0004"
title: The update-cask workflow commits the generated cask straight to main
status: proposed
date: 2026-11-13
deciders: [owner]
consulted: []
supersedes: []
superseded_by: null
tags: [deviation, ci, release]
links:
  - https://gitea.xetk.co.uk/xetk/homebrew-mixxx/issues/5
---

# The update-cask workflow commits the generated cask straight to main

## Context

`Casks/mixxx-fork.rb` has to follow every build the fork publishes, or
`brew upgrade` never offers it. STANDARDS says changes reach `main` through
reviewed pull requests. A pull request per build would leave the cask stale
until someone merges it, which is most of the time.

## Decision

`.gitea/workflows/update-cask.yml` commits the regenerated cask to `main`
with the Actions token, then mirrors to GitHub in the same job. It changes
only `Casks/mixxx-fork.rb`, and only to content produced by
`tools/update_cask.py` from a manifest whose minisign signature matches the
key the Mixxx app trusts, with a URL and checksum that pass validation. The
generator and the workflow themselves change only through reviewed PRs.

## Consequences

- A compromised feed signing key could push a malicious cask; the same key
  already controls what the app's own update check offers.
- Gherkin scenarios for the generator are not added; its unit tests (100 %
  line and branch coverage) describe the behaviour. Revisit if the tap grows.
- With this PR the repo has the flake, pre-commit and PR CI that 0002 asked
  for; 0002 can be closed once the owner accepts.
