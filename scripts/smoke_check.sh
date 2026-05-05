#!/usr/bin/env bash
set -euo pipefail

base_url="${SMOKE_BASE_URL:-${1:-}}"
expected_sha="${SMOKE_EXPECTED_SHA:-${2:-}}"
expected_env="${SMOKE_EXPECTED_ENV:-${3:-}}"

if [[ -z "$base_url" || -z "$expected_sha" || -z "$expected_env" ]]; then
  echo "Usage: SMOKE_BASE_URL=<url> SMOKE_EXPECTED_SHA=<sha> SMOKE_EXPECTED_ENV=<environment> scripts/smoke_check.sh" >&2
  exit 64
fi

base_url="${base_url%/}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

curl_flags=(--silent --show-error --fail --location --max-time 20)

curl "${curl_flags[@]}" "${base_url}/" -o "$tmp_dir/index.html"
curl "${curl_flags[@]}" "${base_url}/version.json" -o "$tmp_dir/version.json"
curl "${curl_flags[@]}" "${base_url}/.well-known/apple-app-site-association" -o "$tmp_dir/aasa.json"
curl "${curl_flags[@]}" "${base_url}/__riddim_smoke_missing_route_${expected_sha}" -o "$tmp_dir/fallback.html"

python3 - "$tmp_dir/version.json" "$expected_sha" "$expected_env" <<'PY'
import json
import sys

path, expected_sha, expected_env = sys.argv[1:4]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)

errors = []
if data.get("commitSha") != expected_sha:
    errors.append(f"commitSha={data.get('commitSha')} expected {expected_sha}")
if data.get("environment") != expected_env:
    errors.append(f"environment={data.get('environment')} expected {expected_env}")
for required in ("artifactKey", "buildTime", "deployedAt"):
    if not data.get(required):
        errors.append(f"missing {required}")

if errors:
    raise SystemExit("; ".join(errors))
PY

aasa_content_type="$(curl --silent --output /dev/null --write-out "%{content_type}" --max-time 20 \
  "${base_url}/.well-known/apple-app-site-association")"
if [[ "${aasa_content_type,,}" != *"json"* ]]; then
  echo "Expected JSON content type for apple-app-site-association, got '${aasa_content_type}'." >&2
  exit 1
fi

if ! grep -qi "<html" "$tmp_dir/fallback.html"; then
  echo "Expected unknown routes to fall back to index.html content." >&2
  exit 1
fi

echo "Smoke checks passed for ${base_url} (${expected_env}, ${expected_sha})."
