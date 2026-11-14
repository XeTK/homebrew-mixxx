# homebrew-mixxx

Homebrew tap for the **xetk Mixxx fork** (accessibility-focused build).

```sh
brew tap xetk/mixxx
brew trust xetk/mixxx            # Homebrew 7 loads third-party casks only once trusted
brew install --cask mixxx-fork
```

`brew upgrade` keeps it on the newest build.

## How the cask stays current

`.gitea/workflows/update-cask.yml` runs hourly. It fetches the fork's update manifest
(<https://mixxx.xetk.co.uk/updates/latest.json>) and its minisign signature, checks
the signature against the key the Mixxx app trusts, and regenerates
`Casks/mixxx-fork.rb` with `tools/update_cask.py`. When the build changed it commits
to `main` and mirrors to GitHub (see `docs/decisions/0004-*`). Don't edit the cask
by hand; change the template in `tools/update_cask.py`.

- The cask is named `mixxx-fork` because `mixxx` is taken by the official cask, and
  it conflicts with that cask (both install `Mixxx.app`).
- The macOS build is **ad-hoc signed and not notarized**, and arm64 only. macOS
  blocks the first launch: open it once, then choose Open Anyway in System Settings
  \> Privacy & Security (the cask's caveats say so too).
- Installers are downloaded from `mixxx.xetk.co.uk` (public), not from this repo.

## Where this lives

The source of truth is <https://gitea.xetk.co.uk/xetk/homebrew-mixxx>. This GitHub repo is
a read-only mirror, updated by `.gitea/workflows/mirror-to-github.yml` on every push to
`main`, so that `brew tap` works anonymously. Do not push here directly: the next
mirror run force-overwrites it.

## Standards

Follows [engineering-standards](https://gitea.xetk.co.uk/xetk/engineering-standards) **v1**, profiles: stack-defaults, homelab.

Deviations are recorded in [`docs/decisions/`](docs/decisions/).
