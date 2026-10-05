{
  description = "Myosotis community site validation toolchain";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python3.withPackages (ps: [
            ps.html5lib
            ps.selenium
            ps.tinycss2
          ]);
          ciToolchain = pkgs.symlinkJoin {
            name = "myosotis-community-ci-toolchain";
            paths = [
              python
              pkgs.chromium
              pkgs.chromedriver
              pkgs.curl
              pkgs.git
              pkgs.gitleaks
              pkgs.html-tidy
              pkgs.lychee
            ];
          };
        in
        {
          ci-toolchain = ciToolchain;
          default = ciToolchain;
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = [ self.packages.${system}.ci-toolchain ];
          };
        }
      );

      checks = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          toolchain = pkgs.runCommand "myosotis-community-toolchain-check" {
            nativeBuildInputs = [ self.packages.${system}.ci-toolchain ];
          } ''
            python3 - <<'PY'
            import html5lib
            import selenium
            import tinycss2
            print("python validation modules available")
            PY
            tidy -version
            lychee --version
            gitleaks version
            chromium --version
            chromedriver --version
            touch "$out"
          '';
        }
      );
    };
}
