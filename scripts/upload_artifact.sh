#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ARTIFACT_BUCKET=<bucket> [ARTIFACT_PREFIX=riddim-website] \
    scripts/upload_artifact.sh <commit-sha> <artifact-path>

Uploads riddim-website/<sha>.tar.gz only when that key is absent. If the key
already exists, the script compares its stored sha256 metadata with the local
artifact and exits successfully only when they match.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -ne 2 ]]; then
  usage
  exit 64
fi

: "${ARTIFACT_BUCKET:?ARTIFACT_BUCKET is required}"

commit_sha="$1"
artifact_path="$2"
artifact_prefix="${ARTIFACT_PREFIX:-riddim-website}"
artifact_key="${artifact_prefix%/}/${commit_sha}.tar.gz"
local_sha256="$(shasum -a 256 "$artifact_path" | awk '{print $1}')"

if aws s3api head-object --bucket "$ARTIFACT_BUCKET" --key "$artifact_key" >/tmp/riddim-artifact-head.json 2>/dev/null; then
  remote_sha256="$(python3 - <<'PY'
import json

with open("/tmp/riddim-artifact-head.json", encoding="utf-8") as handle:
    data = json.load(handle)
print(data.get("Metadata", {}).get("sha256", ""))
PY
)"
  rm -f /tmp/riddim-artifact-head.json
  if [[ "$remote_sha256" == "$local_sha256" ]]; then
    echo "Artifact s3://${ARTIFACT_BUCKET}/${artifact_key} already exists with matching sha256=${local_sha256}."
    echo "ARTIFACT_KEY=${artifact_key}"
    exit 0
  fi
  echo "Artifact s3://${ARTIFACT_BUCKET}/${artifact_key} already exists with sha256=${remote_sha256}, expected ${local_sha256}." >&2
  exit 1
fi

rm -f /tmp/riddim-artifact-head.json
aws s3 cp "$artifact_path" "s3://${ARTIFACT_BUCKET}/${artifact_key}" \
  --content-type "application/gzip" \
  --metadata "commit-sha=${commit_sha},sha256=${local_sha256}" \
  --no-progress

echo "Uploaded s3://${ARTIFACT_BUCKET}/${artifact_key}"
echo "ARTIFACT_KEY=${artifact_key}"
