#!/usr/bin/env bash
set -euo pipefail

rm -rf artifacts .lighthouseci
mkdir -p artifacts

npm run build

export LIGHTHOUSE_BASE_URL="${LIGHTHOUSE_BASE_URL:-http://127.0.0.1:8080}"
export CHROME_PATH="${CHROME_PATH:-$(node scripts/resolve-chrome-path.mjs)}"

python3 -m http.server 8080 --directory _site >/tmp/riddim-website-quality-audits.log 2>&1 &
server_pid=$!

cleanup() {
  kill "$server_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

python3 - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:8080/"
deadline = time.time() + 15
while time.time() < deadline:
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                raise SystemExit(0)
    except Exception:
        time.sleep(0.5)
raise SystemExit("Timed out waiting for local audit server")
PY

status=0

npm run lighthouse:mobile || status=1
npm run lighthouse:desktop || status=1
npm run a11y:baseline || status=1

exit "$status"
