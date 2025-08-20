#!/usr/bin/env python3
"""
Normalize cache parameters in WebApp files.
Removes duplicate ?v=&t= parameters and ensures only one exists per URL.
"""

import re
import sys
from pathlib import Path

def normalize_cache_params(content: str) -> str:
    """Normalize cache parameters in content."""
    
    # Pattern to match URLs with multiple ?v=&t= parameters
    # This will match URLs like: script.js?v=1.3.37?v=1.3.37?v=1.3.36&t=1755625001t=1755424226t=1755424140
    pattern = r'([^"\s]+\.(?:css|js|jpg|svg|png|ico))\?v=[0-9.]+(?:\?v=[0-9.]+)*(?:&t=[0-9]+(?:\?v=[0-9.]+)*)*(?:&t=[0-9]+(?:\?v=[0-9.]+)*)*'
    
    def replace_url(match):
        url = match.group(0)
        base_url = re.sub(r'\?v=[0-9.]+(?:\?v=[0-9.]+)*', '', url)
        base_url = re.sub(r'&t=[0-9]+(?:\?v=[0-9.]+)*', '', base_url)
        base_url = re.sub(r'&t=[0-9]+', '', base_url)
        
        # Keep only the first v and t parameters
        v_match = re.search(r'\?v=([0-9.]+)', url)
        t_match = re.search(r'&t=([0-9]+)', url)
        
        if v_match and t_match:
            return f"{base_url}?v={v_match.group(1)}&t={t_match.group(1)}"
        elif v_match:
            return f"{base_url}?v={v_match.group(1)}"
        else:
            return base_url
    
    return re.sub(pattern, replace_url, content)

def process_file(file_path: Path):
    """Process a single file to normalize cache parameters."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        normalized_content = normalize_cache_params(content)
        
        if content != normalized_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(normalized_content)
            print(f"✅ Normalized cache parameters in {file_path}")
        else:
            print(f"ℹ️  No cache parameter issues found in {file_path}")
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main function to normalize cache parameters in all WebApp files."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/normalize_cache.py <file1> [file2] ...")
        sys.exit(1)
    
    files = sys.argv[1:]
    
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            process_file(path)
        else:
            print(f"⚠️  File not found: {file_path}")

if __name__ == "__main__":
    main()
