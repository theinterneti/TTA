nix
{
  description = "A basic flake for the project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"; # Or your preferred channel
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.${builtins.currentSystem};
    in
    {
      devShells.${builtins.currentSystem}.default = pkgs.mkShell {
        packages = with pkgs; [
 firebase-tools
        ];

        # Set environment variables if needed
        # shellHook = ''
        #   export MY_VARIABLE="some_value"
        # '';
      };
    };
}
