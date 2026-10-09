# Rules for agents working in this repository

This repository follows [engineering-standards](https://gitea.xetk.co.uk/xetk/engineering-standards)
**v1**. Read `STANDARDS.md` there first. It is the definition of done.

1. Work only from an issue. Branch `<type>/<issue>-<short-name>`; Conventional
   Commits referencing the issue.
2. Open pull requests; never push to `main`. A human reviews, approves and merges.
3. Agents **propose** decisions (status `proposed`, or a decision request).
   Only the named decider sets `accepted`, or tells you to.
4. Never commit secrets. Reference them by name; values live in the secret store.
5. Never bypass hooks (`--no-verify`) and never commit code you know is broken.
6. No click-ops. If you need a manual change, stop and raise it in the issue.
7. Every behaviour change comes with unit tests (100 % line and branch
   coverage), Gherkin scenarios with tests, metrics/logs/alarms, and
   docs/runbooks.
8. Cross-reference issues in other repos with full URLs, not `#N`.
9. Run the checks before you push: `pre-commit run --all-files`.
10. **Communicate as in `COMMUNICATION.md`:** lead with the point, keep it
    short and structured. For decisions: recommendation first, at most 3
    lettered options, one question each, marked *blocking* or *can wait*, at
    most 3 at once.

Repo-specific notes go below this line.

## What this repo is

A Homebrew tap (`brew tap XeTK/mixxx`) for the xetk Mixxx fork. Today it holds
only the README and one workflow: no `Formula/` or `Casks/` yet. The cask
`mixxx-fork` is to be generated later by the update-feed CI of the fork (see
`README.md`, Status). Keep the layout Homebrew expects: `Formula/`, `Casks/`
and `README.md` at the root.

## Checks

There is no code, test suite, dev shell or pre-commit config yet (see
`docs/decisions/0002-*`). Until then, before you push:

- `gitleaks detect --no-banner`
- review the workflow YAML by hand

## Secrets

The only secret is `MIRROR_DEPLOY_KEY`, a Gitea Actions secret (write deploy
key for the GitHub mirror). Its backup lives in the owner's credential store.
Never put its value in the repo, an issue or a PR.

## What is deployed from here

Every push to `main` runs `.gitea/workflows/mirror-to-github.yml`, which
force-pushes `main` to `github.com/XeTK/homebrew-mixxx`, so `brew tap` works
anonymously. Gitea is the source of truth; never push to the GitHub copy.
