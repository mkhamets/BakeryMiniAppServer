#!/usr/bin/env python3
"""
Cache Manager - Comprehensive cache version management for Bakery Mini App
Handles all file types including SVG files, main.min.css, and sprite.svg references
"""

import os
import re
import sys
import time
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CacheUpdateResult:
    """Result of cache update operation"""
    file_path: str
    updated: bool
    changes_count: int
    errors: List[str]

class CacheManager:
    """Main cache management class"""
    
    def __init__(self, version: str, timestamp: Optional[int] = None, backup: bool = True):
        self.version = version
        self.timestamp = timestamp or int(time.time())
        self.backup = backup
        self.backup_dir = None
        self.results: List[CacheUpdateResult] = []
        
        # Define all files that need cache version updates
        self.root_dir = Path(__file__).parent.parent
        self.webapp_dir = self.root_dir / "bot" / "web_app"
        
        self.files = [
            self.webapp_dir / "index.html",
            self.webapp_dir / "style.css", 
            self.webapp_dir / "main.min.css",
            self.webapp_dir / "script.js",
            self.webapp_dir / "sprite.svg"
        ]
        
        # SVG files in images directory
        self.images_dir = self.webapp_dir / "images"
        if self.images_dir.exists():
            for svg_file in self.images_dir.glob("*.svg"):
                self.files.append(svg_file)
    
    def create_backup(self) -> bool:
        """Create backup of all files before modification"""
        if not self.backup:
            return True
            
        try:
            backup_timestamp = int(time.time())
            self.backup_dir = self.root_dir / f"backup_cache_{backup_timestamp}"
            self.backup_dir.mkdir(exist_ok=True)
            
            for file_path in self.files:
                if file_path.exists():
                    backup_file = self.backup_dir / file_path.name
                    shutil.copy2(file_path, backup_file)
            
            print(f"✅ Backup created: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def rollback(self) -> bool:
        """Rollback changes from backup"""
        if not self.backup_dir or not self.backup_dir.exists():
            print("❌ No backup found for rollback")
            return False
            
        try:
            for backup_file in self.backup_dir.glob("*"):
                original_file = self.webapp_dir / backup_file.name
                if original_file.exists():
                    shutil.copy2(backup_file, original_file)
            
            print(f"✅ Rollback completed from {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def update_cache_versions(self) -> bool:
        """Update cache versions in all files"""
        print(f"🚀 Starting cache version bump to {self.version} (t={self.timestamp})")
        print(f"📁 Working directory: {self.root_dir}")
        
        # Validate files exist
        missing_files = [f for f in self.files if not f.exists()]
        if missing_files:
            print(f"❌ Missing files: {[str(f) for f in missing_files]}")
            return False
        
        # Create backup if requested
        if self.backup and not self.create_backup():
            return False
        
        # Update each file
        all_success = True
        for file_path in self.files:
            result = self._update_file(file_path)
            self.results.append(result)
            
            if result.errors:
                all_success = False
                print(f"❌ Errors in {file_path.name}: {result.errors}")
            elif result.updated:
                print(f"✅ Updated {file_path.name}: {result.changes_count} changes")
            else:
                print(f"ℹ️  No updates needed in {file_path.name}")
        
        return all_success
    
    def _update_file(self, file_path: Path) -> CacheUpdateResult:
        """Update cache version in a single file"""
        result = CacheUpdateResult(
            file_path=str(file_path),
            updated=False,
            changes_count=0,
            errors=[]
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply updates based on file type
            if file_path.suffix == '.html':
                content = self._update_html_file(content)
            elif file_path.suffix == '.css':
                content = self._update_css_file(content)
            elif file_path.suffix == '.js':
                content = self._update_js_file(content)
            elif file_path.suffix == '.svg':
                content = self._update_svg_file(content)
            
            # Count changes
            if content != original_content:
                result.updated = True
                result.changes_count = len(re.findall(rf'v={re.escape(self.version)}&t={self.timestamp}', content))
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
        except Exception as e:
            result.errors.append(str(e))
        
        return result
    
    def _update_html_file(self, content: str) -> str:
        """Update cache versions in HTML file"""
        # Update script and link tags
        patterns = [
            # Script tags
            (r'(<script[^>]*src=["\'])([^"\']*\.(?:js|css))(\?[^"\']*)?(["\'])', 
             r'\1\2?v=' + self.version + '&t=' + str(self.timestamp) + r'\4'),
            # Link tags
            (r'(<link[^>]*href=["\'])([^"\']*\.(?:css|js|svg|png|jpg|jpeg|ico))(\?[^"\']*)?(["\'])', 
             r'\1\2?v=' + self.version + '&t=' + str(self.timestamp) + r'\4'),
            # Img tags
            (r'(<img[^>]*src=["\'])([^"\']*\.(?:svg|png|jpg|jpeg|ico))(\?[^"\']*)?(["\'])', 
             r'\1\2?v=' + self.version + '&t=' + str(self.timestamp) + r'\4')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _update_css_file(self, content: str) -> str:
        """Update cache versions in CSS file"""
        # Update url() references
        pattern = r'(url\(["\']?)([^"\']*\.(?:css|js|svg|png|jpg|jpeg|ico))(\?[^"\']*)?(["\']?\))'
        replacement = r'\1\2?v=' + self.version + '&t=' + str(self.timestamp) + r'\4'
        content = re.sub(pattern, replacement, content)
        
        return content
    
    def _update_js_file(self, content: str) -> str:
        """Update cache versions in JavaScript file"""
        # Update CACHE_VERSION constant
        content = re.sub(
            r"const CACHE_VERSION = '[^']*';",
            f"const CACHE_VERSION = '{self.version}';",
            content
        )
        
        # Update any other CACHE_VERSION references
        content = re.sub(
            r"CACHE_VERSION = '[^']*'",
            f"CACHE_VERSION = '{self.version}'",
            content
        )
        
        # Update existing cache parameters only (ultra-safe approach)
        # Only update URLs that already have the exact pattern ?v=1.3.xxx&t=xxxxx
        cache_param_pattern = r'\?v=1\.3\.\d+&t=\d+'
        
        # Find all existing cache parameters and replace them
        def replace_cache_param(match):
            return f'?v={self.version}&t={self.timestamp}'
        
        content = re.sub(cache_param_pattern, replace_cache_param, content)
        
        return content
    
    def _update_svg_file(self, content: str) -> str:
        """Update cache versions in SVG file"""
        # SVG files typically don't have cache parameters, but we check for any references
        # This is mainly for sprite.svg which might reference other files
        pattern = r'(["\'])([^"\']*\.(?:css|js|svg|png|jpg|jpeg|ico))(\?[^"\']*)?(["\'])'
        replacement = r'\1\2?v=' + self.version + '&t=' + str(self.timestamp) + r'\4'
        content = re.sub(pattern, replacement, content)
        
        return content
    
    def validate_changes(self) -> bool:
        """Validate that all changes were applied correctly"""
        print("🔍 Validating cache version updates...")
        
        all_valid = True
        
        for result in self.results:
            if result.errors:
                continue
                
            try:
                with open(result.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check file integrity - basic syntax validation
                if not self._validate_file_integrity(Path(result.file_path), content):
                    print(f"❌ File integrity check failed for {Path(result.file_path).name}")
                    all_valid = False
                    continue
                
                # Check for old version patterns
                old_pattern = rf'v=1\.3\.(?!{self.version.split(".")[-1]})[0-9]+'
                old_matches = re.findall(old_pattern, content)
                
                if old_matches:
                    print(f"⚠️  Found old version patterns in {Path(result.file_path).name}: {old_matches}")
                    all_valid = False
                
                # Check for CACHE_VERSION in JS files
                if result.file_path.endswith('.js'):
                    cache_version_match = re.search(r"const CACHE_VERSION = '([^']*)';", content)
                    if cache_version_match:
                        actual_version = cache_version_match.group(1)
                        if actual_version != self.version:
                            print(f"⚠️  CACHE_VERSION mismatch in {Path(result.file_path).name}: expected {self.version}, got {actual_version}")
                            all_valid = False
                        else:
                            print(f"✅ CACHE_VERSION correctly set to {actual_version} in {Path(result.file_path).name}")
                
                # Count cache parameters
                cache_params = re.findall(rf'\?v={re.escape(self.version)}&t={self.timestamp}', content)
                if cache_params:
                    print(f"✅ Found {len(cache_params)} cache parameters in {Path(result.file_path).name}")
                
            except Exception as e:
                print(f"❌ Error validating {Path(result.file_path).name}: {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_file_integrity(self, file_path: Path, content: str) -> bool:
        """Basic file integrity validation"""
        try:
            # Check for basic syntax issues
            if file_path.suffix == '.js':
                # Check for unmatched quotes
                single_quotes = content.count("'")
                double_quotes = content.count('"')
                backticks = content.count('`')
                
                # Check for unmatched braces
                open_braces = content.count('{')
                close_braces = content.count('}')
                
                # Check for unmatched parentheses
                open_parens = content.count('(')
                close_parens = content.count(')')
                
                # Basic validation - these should be roughly balanced
                if abs(open_braces - close_braces) > 5:
                    print(f"⚠️  Unmatched braces in {file_path.name}: {open_braces} open, {close_braces} close")
                    return False
                
                if abs(open_parens - close_parens) > 10:
                    print(f"⚠️  Unmatched parentheses in {file_path.name}: {open_parens} open, {close_parens} close")
                    return False
                
                # Check for obvious truncation (file ends abruptly)
                if content.strip().endswith(('{', '(', '=', '+', '-', '*', '/', '\\')):
                    print(f"⚠️  File appears truncated in {file_path.name}")
                    return False
            
            elif file_path.suffix == '.html':
                # Check for basic HTML structure
                if '<html' not in content.lower() or '</html>' not in content.lower():
                    print(f"⚠️  Missing HTML structure in {file_path.name}")
                    return False
            
            elif file_path.suffix == '.css':
                # Check for unmatched braces
                open_braces = content.count('{')
                close_braces = content.count('}')
                
                if abs(open_braces - close_braces) > 2:
                    print(f"⚠️  Unmatched braces in {file_path.name}: {open_braces} open, {close_braces} close")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error in integrity check for {file_path.name}: {e}")
            return False
    
    def print_summary(self):
        """Print summary of changes"""
        print("\n📋 Summary of changes:")
        print(f"Version: {self.version}")
        print(f"Timestamp: {self.timestamp}")
        print(f"Files processed: {len(self.files)}")
        
        updated_files = [r for r in self.results if r.updated]
        print(f"Files updated: {len(updated_files)}")
        
        for result in updated_files:
            try:
                relative_path = Path(result.file_path).relative_to(self.root_dir)
                print(f"   - {relative_path} ({result.changes_count} changes)")
            except ValueError:
                # Handle case where file is not in root_dir (e.g., test files)
                print(f"   - {Path(result.file_path).name} ({result.changes_count} changes)")
        
        if self.backup_dir:
            print(f"Backup location: {self.backup_dir}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Cache Manager for Bakery Mini App')
    parser.add_argument('version', help='Version number (e.g., 1.3.109)')
    parser.add_argument('--timestamp', type=int, help='Custom timestamp (default: current time)')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not update')
    parser.add_argument('--rollback', action='store_true', help='Rollback from backup')
    
    args = parser.parse_args()
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', args.version):
        print("❌ Invalid version format. Use format like 1.3.109")
        sys.exit(1)
    
    manager = CacheManager(
        version=args.version,
        timestamp=args.timestamp,
        backup=not args.no_backup
    )
    
    if args.rollback:
        if manager.rollback():
            print("🎉 Rollback completed successfully!")
        else:
            print("❌ Rollback failed!")
            sys.exit(1)
    elif args.validate_only:
        if manager.validate_changes():
            print("🎉 All cache versions are consistent!")
        else:
            print("⚠️  Some validation issues found!")
            sys.exit(1)
    else:
        if manager.update_cache_versions():
            if manager.validate_changes():
                print("🎉 Cache version update completed successfully!")
                manager.print_summary()
            else:
                print("⚠️  Update completed but validation issues found!")
                sys.exit(1)
        else:
            print("❌ Cache version update failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
