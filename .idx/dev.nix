{ pkgs, ... }: {
  channel = "stable-24.05";
  packages = [
    pkgs.python312
  ];
  env = {};
  idx = {
    extensions = [
      "ms-python.python"
      "ms-python.black-formatter"
      "ms-python.debugpy"
    ];
    workspace = {
    };
    previews = {
      enable = false;
      previews = {
      };
    };
  };
}
