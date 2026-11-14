{
  description = "homebrew-mixxx: Homebrew tap for the xetk Mixxx fork";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = f: lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs: {
        # Checks and the cask update (tools/update_cask.py). ruby only for
        # `ruby -c` on the generated cask; `brew style` needs a Homebrew
        # install and is run by hand (see AGENTS.md).
        default = pkgs.mkShell {
          packages = with pkgs; [
            (python3.withPackages (ps: [ ps.coverage ]))
            minisign
            ruby
            curl
            git
            actionlint
            yamllint
            markdownlint-cli2
            gitleaks
            pre-commit
            nixfmt
            statix
            deadnix
          ];
        };
      });

      formatter = forAllSystems (pkgs: pkgs.nixfmt);
    };
}
