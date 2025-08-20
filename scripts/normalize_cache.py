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
    
    # Pattern to match URLs with cache parameters
    pattern = r'([^"\s]+\.(?:css|js|jpg|jpeg|svg|png|ico))\?v=[0-9.]+&t=[0-9]+(?:t=[0-9]+)*'
    
    def replace_url(match):
        url = match.group(0)
        
        # Extract base URL (everything before ?v=)
        base_url = url.split('?v=')[0]
        
        # Extract first version parameter
        v_match = re.search(r'\?v=([0-9.]+)', url)
        if not v_match:
            return url
        
        version = v_match.group(1)
        
        # Extract first timestamp parameter (after &t=)
        t_match = re.search(r'&t=([0-9]+)', url)
        if not t_match:
            return f"{base_url}?v={version}"
        
        timestamp = t_match.group(1)
        
        # Return normalized URL with only first v and t parameters
        return f"{base_url}?v={version}&t={timestamp}"
    
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
