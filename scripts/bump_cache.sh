#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

if [ $# -lt 1 ]; then
    echo "Usage: $0 <version-like-1.3.37> [timestamp]"
    echo "Example: $0 1.3.93"
    echo "Example: $0 1.3.93 1756280000"
    exit 1
fi

VER="$1"
TS="${2:-$(date +%s)}"

# Root directory of this repo
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Define all files that need cache version updates
WEBAPP_DIR="$ROOT_DIR/bot/web_app"
INDEX_HTML="$WEBAPP_DIR/index.html"
STYLE_CSS="$WEBAPP_DIR/style.css"
SCRIPT_JS="$WEBAPP_DIR/script.js"
FILES=(
    "$INDEX_HTML"
    "$STYLE_CSS"
    "$SCRIPT_JS"
)

echo "🚀 Starting cache version bump to ${VER} (t=${TS})..."
echo "📁 Working directory: $ROOT_DIR"

# Validate that all files exist
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "File not found: $file"
        exit 1
    fi
done

print_info "🔧 Normalizing cache parameters first..."
python3 "$ROOT_DIR/scripts/normalize_cache.py" "${FILES[@]}"

print_info "🔄 Applying new version ${VER} to all files..."

# Use Python for reliable cache version updates
python3 << EOF
import re
import sys
from pathlib import Path

def update_cache_version(file_path, version, timestamp):
    """Update cache version in a file using robust regex."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match any resource with cache parameters
        # This will match and replace ALL cache parameters consistently
        pattern = r'([^"\s]+\.(?:css|js|jpg|jpeg|svg|png|ico))\?[^"\s;)]*'
        
        def replace_cache(match):
            base_url = match.group(0).split('?')[0]
            return f'{base_url}?v={version}&t={timestamp}'
        
        # Apply the replacement
        content = re.sub(pattern, replace_cache, content)
        
        # Update CACHE_VERSION constant in JavaScript files
        if file_path.endswith('.js'):
            # Update const CACHE_VERSION = 'x.x.x';
            content = re.sub(
                r"const CACHE_VERSION = '[^']*';",
                f"const CACHE_VERSION = '{version}';",
                content
            )
            
            # Update any other CACHE_VERSION references
            content = re.sub(
                r"CACHE_VERSION = '[^']*'",
                f"CACHE_VERSION = '{version}'",
                content
            )
        
        # Write the updated content back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated cache version in {file_path}")
            return True
        else:
            print(f"ℹ️  No updates needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

# Update all files
updated_count = 0
files_list = ['$INDEX_HTML', '$STYLE_CSS', '$SCRIPT_JS']
for file_path in files_list:
    if update_cache_version(file_path, '$VER', '$TS'):
        updated_count += 1

print(f"📊 Updated {updated_count} out of {len(files_list)} files")
EOF

# Verify the updates
print_info "🔍 Verifying cache version updates..."

python3 << EOF
import re
import sys
from pathlib import Path

def verify_cache_version(file_path, expected_version):
    """Verify that cache version was updated correctly."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for any remaining old version patterns
        old_pattern = r'v=1\.3\.(?!' + expected_version.split(".")[-1] + r')[0-9]+'
        old_matches = re.findall(old_pattern, content)
        
        if old_matches:
            print(f"⚠️  Found old version patterns in {file_path}: {old_matches}")
            return False
        
        # Check for CACHE_VERSION constant in JS files
        if file_path.endswith('.js'):
            cache_version_match = re.search(r"const CACHE_VERSION = '([^']*)';", content)
            if cache_version_match:
                actual_version = cache_version_match.group(1)
                if actual_version != expected_version:
                    print(f"⚠️  CACHE_VERSION mismatch in {file_path}: expected {expected_version}, got {actual_version}")
                    return False
                else:
                    print(f"✅ CACHE_VERSION correctly set to {actual_version} in {file_path}")
        
        # Count cache parameters
        cache_params = re.findall(r'\?v=[^&\s]+&t=[0-9]+', content)
        print(f"✅ Found {len(cache_params)} cache parameters in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying {file_path}: {e}")
        return False

# Verify all files
all_good = True
files_list = ['$INDEX_HTML', '$STYLE_CSS', '$SCRIPT_JS']
for file_path in files_list:
    if not verify_cache_version(file_path, '$VER'):
        all_good = False

if all_good:
    print("🎉 All cache version updates verified successfully!")
else:
    print("⚠️  Some verification issues found. Please check the output above.")
    sys.exit(1)
EOF

print_status "Cache version bump completed successfully!"
print_info "Version: ${VER}"
print_info "Timestamp: ${TS}"
print_info "Files updated: ${#FILES[@]}"

# Show summary of changes
echo ""
print_info "📋 Summary of changes:"
for file in "${FILES[@]}"; do
    relative_path="${file#$ROOT_DIR/}"
    echo "   - $relative_path"
done

echo ""
print_info "🚀 Ready for deployment! Use: git add . && git commit -m 'Bump cache to ${VER}' && git push"