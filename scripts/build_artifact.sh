#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/build_artifact.sh <commit-sha> <artifact-path>

Builds the 11ty static site and packages an immutable tar.gz artifact.
Generated deployment-only files are added under a temporary staging directory;
the source tree is not modified.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -ne 2 ]]; then
  usage
  exit 64
fi

commit_sha="$1"
artifact_path="$2"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

dist_dir="$tmp_dir/site"
mkdir -p "$dist_dir/.well-known"

(
  cd "$repo_root"
  npm install --package-lock=false
  npm run build
)

rsync -a --delete "$repo_root/_site/" "$dist_dir/"

if [[ -f "$repo_root/apple-app-site-association.json" ]]; then
  cp -f "$repo_root/apple-app-site-association.json" \
    "$dist_dir/.well-known/apple-app-site-association"
fi

build_time="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
python3 - "$dist_dir/artifact-manifest.json" "$commit_sha" "$build_time" <<'PY'
import json
import sys

path, commit_sha, build_time = sys.argv[1:4]
with open(path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "commitSha": commit_sha,
            "buildTime": build_time,
            "artifactFormat": "tar.gz",
        },
        handle,
        indent=2,
        sort_keys=True,
    )
    handle.write("\n")
PY

mkdir -p "$(dirname "$artifact_path")"
tar -C "$dist_dir" -czf "$artifact_path" .
echo "Built ${artifact_path} for ${commit_sha}"
