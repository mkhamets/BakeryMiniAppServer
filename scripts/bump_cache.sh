#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <version-like-1.3.37>"
  exit 1
fi

VER="$1"
TS="$(date +%s)"

# Root directory of this repo
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

INDEX_HTML="$ROOT_DIR/bot/web_app/index.html"
STYLE_CSS="$ROOT_DIR/bot/web_app/style.css"
SCRIPT_JS="$ROOT_DIR/bot/web_app/script.js"

# Normalize existing ?v=&t= chains to a single one before applying new version
echo "🔧 Normalizing cache parameters..."
python3 "$ROOT_DIR/scripts/normalize_cache.py" "$INDEX_HTML" "$STYLE_CSS" "$SCRIPT_JS"

# index.html: bump all v&t query params
sed -i '' -E "s/\?v=[0-9.]+&t=[0-9]+/?v=${VER}&t=${TS}/g" "$INDEX_HTML"

# style.css: background image
sed -i '' -E "s/(Hleb\.jpg\?v=)[0-9.]+(&t=)[0-9]+/\1${VER}\2${TS}/g" "$STYLE_CSS"

# script.js: category icons (use character classes instead of groups for BSD sed)
# Replace bakery.svg, crouasan.svg, bread1.svg, cookie.svg version params
sed -i '' -E "s|(images/bakery\.svg\?v=)[0-9.]+(&t=)[0-9]+|\1${VER}\2${TS}|g" "$SCRIPT_JS"
sed -i '' -E "s|(images/crouasan\.svg\?v=)[0-9.]+(&t=)[0-9]+|\1${VER}\2${TS}|g" "$SCRIPT_JS"
sed -i '' -E "s|(images/bread1\.svg\?v=)[0-9.]+(&t=)[0-9]+|\1${VER}\2${TS}|g" "$SCRIPT_JS"
sed -i '' -E "s|(images/cookie\.svg\?v=)[0-9.]+(&t=)[0-9]+|\1${VER}\2${TS}|g" "$SCRIPT_JS"

# script.js: background image
sed -i '' -E "s|(Hleb\.jpg\?v=)[0-9.]+(&t=)[0-9]+|\1${VER}\2${TS}|g" "$SCRIPT_JS"

# script.js: any other v&t occurrences
sed -i '' -E "s/\?v=[0-9.]+&t=[0-9]+/?v=${VER}&t=${TS}/g" "$SCRIPT_JS"

echo "Bumped cache versions to ${VER} (t=${TS})."
