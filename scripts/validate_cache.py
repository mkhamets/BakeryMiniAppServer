#!/usr/bin/env python3
"""
Cache Validator - Validate cache version consistency across all files
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class CacheValidator:
    """Validate cache version consistency"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.webapp_dir = self.root_dir / "bot" / "web_app"
        self.issues: List[Dict] = []
        
        # Define all files to check
        self.files = [
            self.webapp_dir / "index.html",
            self.webapp_dir / "style.css", 
            self.webapp_dir / "main.min.css",
            self.webapp_dir / "script.js",
            self.webapp_dir / "sprite.svg"
        ]
        
        # Add SVG files in images directory
        self.images_dir = self.webapp_dir / "images"
        if self.images_dir.exists():
            for svg_file in self.images_dir.glob("*.svg"):
                self.files.append(svg_file)
    
    def validate_all(self) -> bool:
        """Validate all files for cache consistency"""
        print("🔍 Validating cache version consistency...")
        
        all_valid = True
        
        for file_path in self.files:
            if not file_path.exists():
                self.issues.append({
                    'file': str(file_path),
                    'type': 'missing_file',
                    'message': 'File not found'
                })
                all_valid = False
                continue
            
            file_valid = self._validate_file(file_path)
            if not file_valid:
                all_valid = False
        
        return all_valid
    
    def _validate_file(self, file_path: Path) -> bool:
        """Validate a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_valid = True
            
            # Check for duplicate cache parameters
            duplicate_pattern = r'\?v=([^&\s]+)&t=([0-9]+)[^&\s]*&v=([^&\s]+)&t=([0-9]+)'
            duplicates = re.findall(duplicate_pattern, content)
            if duplicates:
                self.issues.append({
                    'file': str(file_path),
                    'type': 'duplicate_params',
                    'message': f'Found {len(duplicates)} duplicate cache parameters',
                    'details': duplicates
                })
                file_valid = False
            
            # Check for malformed cache parameters
            malformed_pattern = r'\?v=([^&\s]+)&t=([0-9]+)[^&\s]*&t=([0-9]+)'
            malformed = re.findall(malformed_pattern, content)
            if malformed:
                self.issues.append({
                    'file': str(file_path),
                    'type': 'malformed_params',
                    'message': f'Found {len(malformed)} malformed cache parameters',
                    'details': malformed
                })
                file_valid = False
            
            # Check for unclosed quotes in CSS
            if file_path.suffix == '.css':
                unclosed_pattern = r'background-image:\s*url\([^)]*?\?v=([^&\s]+)&t=([0-9]+)[^)]*[^)]$'
                unclosed = re.findall(unclosed_pattern, content, re.MULTILINE)
                if unclosed:
                    self.issues.append({
                        'file': str(file_path),
                        'type': 'unclosed_quotes',
                        'message': f'Found {len(unclosed)} unclosed quotes in CSS',
                        'details': unclosed
                    })
                    file_valid = False
            
            # Check for unclosed quotes in JavaScript
            if file_path.suffix == '.js':
                unclosed_pattern = r'img\.src\s*=\s*[^;]*?\?v=([^&\s]+)&t=([0-9]+)[^;]*[^;]$'
                unclosed = re.findall(unclosed_pattern, content, re.MULTILINE)
                if unclosed:
                    self.issues.append({
                        'file': str(file_path),
                        'type': 'unclosed_quotes',
                        'message': f'Found {len(unclosed)} unclosed quotes in JavaScript',
                        'details': unclosed
                    })
                    file_valid = False
            
            # Check for version consistency in JS files
            if file_path.suffix == '.js':
                cache_version_matches = re.findall(r"const CACHE_VERSION = '([^']*)';", content)
                if cache_version_matches:
                    versions = set(cache_version_matches)
                    if len(versions) > 1:
                        self.issues.append({
                            'file': str(file_path),
                            'type': 'version_inconsistency',
                            'message': f'Multiple CACHE_VERSION values found: {versions}',
                            'details': cache_version_matches
                        })
                        file_valid = False
            
            # Count cache parameters
            cache_params = re.findall(r'\?v=([^&\s]+)&t=([0-9]+)', content)
            if cache_params:
                print(f"✅ {file_path.name}: {len(cache_params)} cache parameters")
            
            return file_valid
            
        except Exception as e:
            self.issues.append({
                'file': str(file_path),
                'type': 'read_error',
                'message': f'Error reading file: {e}'
            })
            return False
    
    def print_issues(self):
        """Print all found issues"""
        if not self.issues:
            print("🎉 No cache validation issues found!")
            return
        
        print(f"\n⚠️  Found {len(self.issues)} validation issues:")
        
        for i, issue in enumerate(self.issues, 1):
            print(f"\n{i}. {issue['type'].upper()}")
            print(f"   File: {Path(issue['file']).name}")
            print(f"   Issue: {issue['message']}")
            
            if 'details' in issue:
                print(f"   Details: {issue['details']}")
    
    def get_version_consistency_report(self) -> Dict:
        """Get a report on version consistency across files"""
        version_report = {
            'cache_versions': set(),
            'timestamps': set(),
            'files_with_versions': {},
            'inconsistencies': []
        }
        
        for file_path in self.files:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract all cache parameters
                cache_params = re.findall(r'\?v=([^&\s]+)&t=([0-9]+)', content)
                
                if cache_params:
                    file_versions = set()
                    file_timestamps = set()
                    
                    for version, timestamp in cache_params:
                        file_versions.add(version)
                        file_timestamps.add(timestamp)
                        version_report['cache_versions'].add(version)
                        version_report['timestamps'].add(timestamp)
                    
                    version_report['files_with_versions'][file_path.name] = {
                        'versions': list(file_versions),
                        'timestamps': list(file_timestamps),
                        'count': len(cache_params)
                    }
                    
                    # Check for inconsistencies within file
                    if len(file_versions) > 1:
                        version_report['inconsistencies'].append({
                            'file': file_path.name,
                            'type': 'multiple_versions',
                            'versions': list(file_versions)
                        })
                    
                    if len(file_timestamps) > 1:
                        version_report['inconsistencies'].append({
                            'file': file_path.name,
                            'type': 'multiple_timestamps',
                            'timestamps': list(file_timestamps)
                        })
                        
            except Exception as e:
                print(f"❌ Error analyzing {file_path.name}: {e}")
        
        return version_report
    
    def print_version_report(self):
        """Print version consistency report"""
        report = self.get_version_consistency_report()
        
        print("\n📊 Version Consistency Report:")
        print(f"   Unique versions found: {len(report['cache_versions'])}")
        print(f"   Unique timestamps found: {len(report['timestamps'])}")
        print(f"   Files with cache parameters: {len(report['files_with_versions'])}")
        
        if report['cache_versions']:
            print(f"   Versions: {sorted(report['cache_versions'])}")
        
        if report['timestamps']:
            print(f"   Timestamps: {sorted(report['timestamps'])}")
        
        if report['inconsistencies']:
            print(f"\n⚠️  Found {len(report['inconsistencies'])} inconsistencies:")
            for inconsistency in report['inconsistencies']:
                print(f"   - {inconsistency['file']}: {inconsistency['type']} - {inconsistency.get('versions', inconsistency.get('timestamps', []))}")
        
        print(f"\n📋 Files with cache parameters:")
        for filename, data in report['files_with_versions'].items():
            print(f"   - {filename}: {data['count']} parameters, versions: {data['versions']}")

def main():
    """Main function"""
    validator = CacheValidator()
    
    if validator.validate_all():
        print("🎉 All cache validations passed!")
        validator.print_version_report()
        sys.exit(0)
    else:
        print("❌ Cache validation failed!")
        validator.print_issues()
        validator.print_version_report()
        sys.exit(1)

if __name__ == "__main__":
    main()

