# shell.nix
# Info from the wiki: https://nixos.wiki/wiki/Python
# And this video: https://www.youtube.com/watch?v=k7NKBfeYXCk
# run with nix-shell pyshell.nix
{ pkgs ? import <nixpkgs> {} }:
let
  my-python = pkgs.python3;
  python-with-my-packages = my-python.withPackages (p: with p; [
    # pandas
    beautifulsoup4
    requests
    lxml
    pillow
    # other python packages you want
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-my-packages
    # other dependencies
  ];
  shellHook = ''
    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
    # maybe set more env-vars
  '';
} 
