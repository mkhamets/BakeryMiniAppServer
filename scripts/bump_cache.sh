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

echo "🔧 Normalizing cache parameters..."
python3 "$ROOT_DIR/scripts/normalize_cache.py" "$INDEX_HTML" "$STYLE_CSS" "$SCRIPT_JS"

echo "🔄 Applying new version ${VER}..."

# Use Python for reliable cache version updates
python3 << EOF
import re
from pathlib import Path

def update_cache_version(file_path, version, timestamp):
    """Update cache version in a file using robust regex."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match any resource with cache parameters
        # This will match and replace ALL cache parameters consistently
        pattern = r'([^"\s]+\.(?:css|js|jpg|jpeg|svg|png|ico))\?[^"\s;)]*'
        
        def replace_cache(match):
            base_url = match.group(0).split('?')[0]
            return f'{base_url}?v={version}&t={timestamp}'
        
        # Apply the replacement
        updated_content = re.sub(pattern, replace_cache, content)
        
        # Also update CACHE_VERSION constant in JavaScript files
        if file_path.endswith('.js'):
            updated_content = re.sub(
                r"const CACHE_VERSION = '[^']*';",
                f"const CACHE_VERSION = '{version}';",
                updated_content
            )
        
        # Write the updated content back
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated cache version in {file_path}")
        else:
            print(f"ℹ️  No updates needed in {file_path}")
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

# Update all files
update_cache_version('$INDEX_HTML', '$VER', '$TS')
update_cache_version('$STYLE_CSS', '$VER', '$TS') 
update_cache_version('$SCRIPT_JS', '$VER', '$TS')
EOF

echo "Bumped cache versions to ${VER} (t=${TS})."