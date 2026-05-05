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

product_routes=(
  "/blindfold/|Blindfold - Riddim Software"
  "/epac/|epac - Riddim Software"
  "/bubble-bop/|Bubble Bop — Riddim Software"
  "/reach/|Reach - Riddim Software"
  "/portal-door/|Portal Door - Riddim Software"
  "/sonnio/|Sonnio - Riddim Software"
  "/double-dozen/|Double Dozen - Riddim Software"
)

for route_spec in "${product_routes[@]}"; do
  route="${route_spec%%|*}"
  expected_title="${route_spec#*|}"
  output_path="$tmp_dir$(echo "${route}" | tr '/' '_').html"
  curl "${curl_flags[@]}" "${base_url}${route}" -o "$output_path"

  if ! grep -q "<title>${expected_title}</title>" "$output_path"; then
    echo "Expected ${base_url}${route} to render title '${expected_title}'." >&2
    exit 1
  fi

  if ! grep -q "<link rel=\"canonical\" href=\"${base_url}${route}\">" "$output_path"; then
    echo "Expected ${base_url}${route} to render its canonical URL." >&2
    exit 1
  fi
done

missing_route="__riddim_smoke_missing_route_${expected_sha}"
missing_status="$(curl --silent --show-error --location --output "$tmp_dir/fallback.html" \
  --write-out "%{http_code}" --max-time 20 "${base_url}/${missing_route}")"
if [[ "$missing_status" != "404" ]]; then
  echo "Expected unknown routes to return HTTP 404, got ${missing_status}." >&2
  exit 1
fi

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

if ! grep -q "That page doesn’t exist." "$tmp_dir/fallback.html"; then
  echo "Expected unknown routes to render the dedicated 404 page." >&2
  exit 1
fi

echo "Smoke checks passed for ${base_url} (${expected_env}, ${expected_sha})."
