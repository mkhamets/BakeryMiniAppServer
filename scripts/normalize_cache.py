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
    
    # More aggressive pattern to match corrupted cache parameters
    # Matches any file with multiple ?v= or &t= or t= parameters
    pattern = r'([^"\s]+\.(?:css|js|jpg|jpeg|svg|png|ico))\?[^"\s]*'
    
    def replace_url(match):
        url = match.group(0)
        
        # Extract base URL (everything before first ?)
        base_url = url.split('?')[0]
        
        # Extract ALL version numbers and take the LAST one (most recent)
        v_matches = re.findall(r'v=([0-9.]+)', url)
        if not v_matches:
            return base_url
        
        version = v_matches[-1]  # Take the last (most recent) version
        
        # Extract ALL timestamps and take the LAST one (most recent)  
        t_matches = re.findall(r't=([0-9]+)', url)
        if not t_matches:
            return f"{base_url}?v={version}"
        
        timestamp = t_matches[-1]  # Take the last (most recent) timestamp
        
        # Return clean normalized URL
        return f"{base_url}?v={version}&t={timestamp}"
    
    # Apply the normalization
    normalized = re.sub(pattern, replace_url, content)
    
    return normalized

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