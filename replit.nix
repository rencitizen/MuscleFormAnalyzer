{ pkgs }: {
  deps = [
    pkgs.python39Full  # Python環境
    pkgs.nodejs-18_x   # Node.js v18環境
    pkgs.git           # Gitを使えるようにする
    pkgs.jq            # (必要に応じて) JSON整形ツール
  ];
}
