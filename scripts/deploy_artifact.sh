#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ARTIFACT_BUCKET=<bucket> [ARTIFACT_PREFIX=riddim-website] \
  VALIDATION_BUCKET=<bucket> VALIDATION_DISTRIBUTION_ID=<id> VALIDATION_BASE_URL=<url> \
    scripts/deploy_artifact.sh validation <commit-sha>

  ARTIFACT_BUCKET=<bucket> [ARTIFACT_PREFIX=riddim-website] \
  PRODUCTION_BUCKET=<bucket> PRODUCTION_DISTRIBUTION_ID=<id> PRODUCTION_BASE_URL=<url> \
    scripts/deploy_artifact.sh production <commit-sha>

Downloads an existing immutable artifact, deploys it to the requested hosting
bucket, writes version.json, invalidates CloudFront, waits for the invalidation,
and runs smoke checks against the CloudFront URL or approved production URL.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || $# -ne 2 ]]; then
  usage
  exit 64
fi

: "${ARTIFACT_BUCKET:?ARTIFACT_BUCKET is required}"

environment="$1"
commit_sha="$2"
artifact_prefix="${ARTIFACT_PREFIX:-riddim-website}"
artifact_key="${artifact_prefix%/}/${commit_sha}.tar.gz"

case "$environment" in
  validation)
    : "${VALIDATION_BUCKET:?VALIDATION_BUCKET is required}"
    : "${VALIDATION_DISTRIBUTION_ID:?VALIDATION_DISTRIBUTION_ID is required}"
    : "${VALIDATION_BASE_URL:?VALIDATION_BASE_URL is required}"
    deploy_bucket="$VALIDATION_BUCKET"
    distribution_id="$VALIDATION_DISTRIBUTION_ID"
    base_url="$VALIDATION_BASE_URL"
    ;;
  production)
    : "${PRODUCTION_BUCKET:?PRODUCTION_BUCKET is required}"
    : "${PRODUCTION_DISTRIBUTION_ID:?PRODUCTION_DISTRIBUTION_ID is required}"
    : "${PRODUCTION_BASE_URL:?PRODUCTION_BASE_URL is required}"
    deploy_bucket="$PRODUCTION_BUCKET"
    distribution_id="$PRODUCTION_DISTRIBUTION_ID"
    base_url="$PRODUCTION_BASE_URL"
    ;;
  *)
    echo "Unknown environment: ${environment}" >&2
    usage
    exit 64
    ;;
esac

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
artifact_path="$tmp_dir/artifact.tar.gz"
dist_dir="$tmp_dir/site"
mkdir -p "$dist_dir"

aws s3 cp "s3://${ARTIFACT_BUCKET}/${artifact_key}" "$artifact_path" --no-progress
tar -C "$dist_dir" -xzf "$artifact_path"

deployed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
build_time="$(python3 - "$dist_dir/artifact-manifest.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle).get("buildTime", ""))
PY
)"
python3 - "$dist_dir/version.json" "$commit_sha" "$build_time" "$deployed_at" "$environment" "$artifact_key" <<'PY'
import json
import sys

path, commit_sha, build_time, deployed_at, environment, artifact_key = sys.argv[1:7]
with open(path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "artifactKey": artifact_key,
            "buildTime": build_time,
            "commitSha": commit_sha,
            "deployedAt": deployed_at,
            "environment": environment,
        },
        handle,
        indent=2,
        sort_keys=True,
    )
    handle.write("\n")
PY

aws s3 sync "$dist_dir/" "s3://${deploy_bucket}/" --delete --no-progress

content_type_for() {
  case "$1" in
    *.css) echo "text/css; charset=utf-8" ;;
    *.html) echo "text/html; charset=utf-8" ;;
    *.ico) echo "image/x-icon" ;;
    *.jpeg|*.jpg) echo "image/jpeg" ;;
    *.json|*/apple-app-site-association) echo "application/json" ;;
    *.png) echo "image/png" ;;
    *.svg) echo "image/svg+xml" ;;
    *.txt) echo "text/plain; charset=utf-8" ;;
    *.webp) echo "image/webp" ;;
    *.xml) echo "application/xml; charset=utf-8" ;;
    *) echo "application/octet-stream" ;;
  esac
}

cache_control_for() {
  case "$1" in
    index.html|*.html|version.json|artifact-manifest.json)
      echo "public,max-age=60,must-revalidate"
      ;;
    .well-known/apple-app-site-association)
      echo "public,max-age=3600,must-revalidate"
      ;;
    apple-app-site-association.json)
      echo "public,max-age=300,must-revalidate"
      ;;
    robots.txt|sitemap.xml)
      echo "public,max-age=300,must-revalidate"
      ;;
    *.[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F].*)
      echo "public,max-age=31536000,immutable"
      ;;
    *)
      echo "public,max-age=3600,must-revalidate"
      ;;
  esac
}

while IFS= read -r -d '' file_path; do
  key="${file_path#"$dist_dir"/}"
  content_type="$(content_type_for "$key")"
  cache_control="$(cache_control_for "$key")"
  aws s3 cp "$file_path" "s3://${deploy_bucket}/${key}" \
    --content-type "$content_type" \
    --cache-control "$cache_control" \
    --no-progress
done < <(find "$dist_dir" -type f -print0)

invalidation_id="$(aws cloudfront create-invalidation \
  --distribution-id "$distribution_id" \
  --paths "/*" \
  --query "Invalidation.Id" \
  --output text)"
echo "Created CloudFront invalidation ${invalidation_id} for ${distribution_id}"
aws cloudfront wait invalidation-completed \
  --distribution-id "$distribution_id" \
  --id "$invalidation_id"

echo "Deployed ${artifact_key} to ${environment} at ${base_url}"
SMOKE_BASE_URL="$base_url" SMOKE_EXPECTED_SHA="$commit_sha" SMOKE_EXPECTED_ENV="$environment" \
  "$(dirname "${BASH_SOURCE[0]}")/smoke_check.sh"
