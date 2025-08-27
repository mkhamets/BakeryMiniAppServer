#!/usr/bin/env python3
"""
Normalize cache parameters in WebApp files.
Removes duplicate ?v=&t= parameters and ensures only one exists per URL.
Handles various edge cases and corrupted cache parameters.
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

def clean_corrupted_cache_params(content: str) -> str:
    """Clean up corrupted cache parameters that might cause issues."""
    
    # Fix common corruption patterns
    fixes = [
        # Fix missing closing quotes in CSS background-image
        (r'background-image:\s*url\(([^)]*?)\?v=([^&\s]+)&t=([0-9]+)([^)]*)\);', 
         r'background-image: url(\1?v=\2&t=\3\4);'),
        
        # Fix missing closing quotes in JavaScript img.src
        (r'img\.src\s*=\s*([^;]*?)\?v=([^&\s]+)&t=([0-9]+)([^;]*);', 
         r'img.src = \1?v=\2&t=\3\4;'),
        
        # Fix duplicate cache parameters
        (r'\?v=([^&\s]+)&t=([0-9]+)[^&\s]*&v=([^&\s]+)&t=([0-9]+)', 
         r'?v=\3&t=\4'),
        
        # Fix malformed cache parameters
        (r'\?v=([^&\s]+)&t=([0-9]+)[^&\s]*&t=([0-9]+)', 
         r'?v=\1&t=\3'),
    ]
    
    cleaned = content
    for pattern, replacement in fixes:
        cleaned = re.sub(pattern, replacement, cleaned)
    
    return cleaned

def process_file(file_path: Path):
    """Process a single file to normalize cache parameters."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # First clean corrupted parameters
        content = clean_corrupted_cache_params(content)
        
        # Then normalize cache parameters
        normalized_content = normalize_cache_params(content)
        
        if normalized_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(normalized_content)
            print(f"✅ Normalized cache parameters in {file_path}")
            
            # Show what was fixed
            changes = []
            if content != original_content:
                changes.append("corrupted parameters")
            if normalized_content != content:
                changes.append("duplicate parameters")
            
            if changes:
                print(f"   Fixed: {', '.join(changes)}")
        else:
            print(f"ℹ️  No cache parameter issues found in {file_path}")
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def validate_cache_params(content: str, file_path: str) -> bool:
    """Validate that cache parameters are properly formatted."""
    issues = []
    
    # Check for duplicate cache parameters (this is a real issue)
    duplicate_pattern = r'\?v=([^&\s]+)&t=([0-9]+)[^&\s]*&v=([^&\s]+)&t=([0-9]+)'
    duplicate_matches = re.findall(duplicate_pattern, content)
    if duplicate_matches:
        issues.append(f"duplicate cache parameters: {len(duplicate_matches)} found")
    
    # Check for missing closing quotes in CSS (this is a real issue)
    if file_path.endswith('.css'):
        unclosed_quote_pattern = r'background-image:\s*url\([^)]*?\?v=([^&\s]+)&t=([0-9]+)[^)]*[^)]$'
        unclosed_matches = re.findall(unclosed_quote_pattern, content)
        if unclosed_matches:
            issues.append(f"unclosed quotes in CSS: {len(unclosed_matches)} found")
    
    # Check for missing closing quotes in JavaScript (this is a real issue)
    if file_path.endswith('.js'):
        unclosed_quote_pattern = r'img\.src\s*=\s*[^;]*?\?v=([^&\s]+)&t=([0-9]+)[^;]*[^;]$'
        unclosed_matches = re.findall(unclosed_quote_pattern, content)
        if unclosed_matches:
            issues.append(f"unclosed quotes in JavaScript: {len(unclosed_matches)} found")
    
    if issues:
        print(f"⚠️  Validation issues in {file_path}: {', '.join(issues)}")
        return False
    
    return True

def main():
    """Main function to normalize cache parameters in all WebApp files."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/normalize_cache.py <file1> [file2] ...")
        sys.exit(1)
    
    files = sys.argv[1:]
    processed_count = 0
    validation_issues = 0
    
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            process_file(path)
            processed_count += 1
            
            # Validate the processed file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not validate_cache_params(content, str(path)):
                    validation_issues += 1
            except Exception as e:
                print(f"❌ Error validating {path}: {e}")
                validation_issues += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Summary: Processed {processed_count} files, {validation_issues} validation issues")
    
    if validation_issues > 0:
        print("⚠️  Some validation issues remain. Consider running the script again.")
        sys.exit(1)
    else:
        print("🎉 All cache parameters normalized successfully!")

if __name__ == "__main__":
    main()