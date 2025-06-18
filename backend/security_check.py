#!/usr/bin/env python
"""
Security vulnerability check for backend
Checks for common security issues and best practices
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityChecker:
    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.issues = []
        self.warnings = []
        self.info = []
        
    def check_all(self):
        """Run all security checks"""
        print("🔐 Running Security Vulnerability Check...")
        print("=" * 50)
        
        self.check_environment_variables()
        self.check_hardcoded_secrets()
        self.check_sql_injection()
        self.check_dependencies()
        self.check_authentication()
        self.check_cors_configuration()
        self.check_rate_limiting()
        self.check_input_validation()
        self.check_error_handling()
        self.check_file_operations()
        
        self.print_results()
        
    def check_environment_variables(self):
        """Check for exposed environment variables"""
        print("\n📋 Checking environment variables...")
        
        # Check for .env files
        env_files = list(self.root_path.glob("**/.env*"))
        for env_file in env_files:
            if env_file.name == ".env.example":
                continue
            if ".gitignore" not in env_file.parent.glob(".gitignore"):
                self.issues.append(f"Environment file {env_file} may not be in .gitignore")
        
        # Check for environment variable usage
        py_files = list(self.root_path.glob("**/*.py"))
        for py_file in py_files:
            if "test" in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for os.environ without defaults
            if re.search(r'os\.environ\[["\']([^"\']+)["\']\](?!\s*\|\s*)', content):
                self.warnings.append(f"os.environ access without default in {py_file}")
            
            # Check for proper settings usage
            if "settings." in content and "from .config import settings" not in content:
                if "from app.config import settings" not in content:
                    self.warnings.append(f"Direct settings access without import in {py_file}")
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets and credentials"""
        print("\n🔑 Checking for hardcoded secrets...")
        
        secret_patterns = [
            (r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', "API Key"),
            (r'["\']?secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', "Secret Key"),
            (r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']', "Password"),
            (r'["\']?token["\']?\s*[:=]\s*["\'][^"\']+["\']', "Token"),
            (r'["\']?private[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']', "Private Key"),
        ]
        
        py_files = list(self.root_path.glob("**/*.py"))
        for py_file in py_files:
            if "test" in str(py_file) or "example" in str(py_file):
                continue
                
            content = py_file.read_text(encoding='utf-8', errors='ignore').lower()
            
            for pattern, secret_type in secret_patterns:
                if re.search(pattern, content):
                    # Check if it's a placeholder
                    match = re.search(pattern, content)
                    if match and not any(placeholder in match.group() for placeholder in ['xxx', 'your-', 'example', 'test']):
                        self.issues.append(f"Potential hardcoded {secret_type} in {py_file}")
    
    def check_sql_injection(self):
        """Check for SQL injection vulnerabilities"""
        print("\n💉 Checking for SQL injection risks...")
        
        sql_patterns = [
            r'\.execute\s*\(\s*["\'].*%[s\d].*["\'].*%',  # String formatting in SQL
            r'\.execute\s*\(\s*f["\']',  # f-strings in SQL
            r'\.execute\s*\([^,)]*\+[^,)]*\)',  # String concatenation in SQL
        ]
        
        py_files = list(self.root_path.glob("**/*.py"))
        for py_file in py_files:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for pattern in sql_patterns:
                if re.search(pattern, content):
                    self.issues.append(f"Potential SQL injection risk in {py_file}")
            
            # Check for proper parameterized queries
            if ".execute(" in content and "text(" not in content:
                self.warnings.append(f"Direct SQL execution without text() wrapper in {py_file}")
    
    def check_dependencies(self):
        """Check for vulnerable dependencies"""
        print("\n📦 Checking dependencies...")
        
        requirements_file = self.root_path / "requirements.txt"
        if requirements_file.exists():
            content = requirements_file.read_text()
            
            # Check for unpinned dependencies
            unpinned = []
            for line in content.splitlines():
                if line and not line.startswith("#") and "==" not in line and ">=" not in line:
                    unpinned.append(line.strip())
            
            if unpinned:
                self.warnings.append(f"Unpinned dependencies: {', '.join(unpinned)}")
            
            # Check for known vulnerable versions
            vulnerable_packages = {
                "pyyaml": "5.4",  # CVE-2020-14343
                "pillow": "8.2.0",  # Multiple CVEs
                "werkzeug": "2.0.0",  # CVE-2021-23336
            }
            
            for package, min_version in vulnerable_packages.items():
                if package in content.lower():
                    self.info.append(f"Ensure {package} is at least version {min_version}")
    
    def check_authentication(self):
        """Check authentication implementation"""
        print("\n🔐 Checking authentication...")
        
        auth_file = self.root_path / "api" / "auth.py"
        if auth_file.exists():
            content = auth_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for proper token validation
            if "verify_id_token" in content:
                self.info.append("✅ Firebase token validation found")
            else:
                self.warnings.append("Token validation not found in auth.py")
            
            # Check for rate limiting on auth endpoints
            if "rate_limit" not in content.lower():
                self.warnings.append("No rate limiting found on authentication endpoints")
    
    def check_cors_configuration(self):
        """Check CORS configuration"""
        print("\n🌐 Checking CORS configuration...")
        
        main_file = self.root_path / "app" / "main.py"
        if main_file.exists():
            content = main_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for wildcard CORS
            if 'allow_origins=["*"]' in content or "allow_origins=['*']" in content:
                self.issues.append("CORS allows all origins (security risk)")
            
            # Check for credentials with wildcard
            if "allow_credentials=True" in content and "*" in content:
                self.issues.append("CORS allows credentials with wildcard origin")
    
    def check_rate_limiting(self):
        """Check rate limiting implementation"""
        print("\n⏱️ Checking rate limiting...")
        
        middleware_file = self.root_path / "app" / "middleware.py"
        if middleware_file.exists():
            content = middleware_file.read_text(encoding='utf-8', errors='ignore')
            
            if "RateLimitMiddleware" in content:
                self.info.append("✅ Rate limiting middleware found")
                
                # Check configuration
                if "calls=100" in content:
                    self.info.append("Rate limit: 100 calls per 60 seconds")
            else:
                self.warnings.append("Rate limiting middleware not found")
    
    def check_input_validation(self):
        """Check input validation"""
        print("\n✅ Checking input validation...")
        
        api_files = list((self.root_path / "api").glob("*.py"))
        for api_file in api_files:
            content = api_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for Pydantic models
            if "BaseModel" in content:
                self.info.append(f"✅ Pydantic validation in {api_file.name}")
            
            # Check for file upload validation
            if "UploadFile" in content:
                if "content_type" in content:
                    self.info.append(f"✅ File type validation in {api_file.name}")
                else:
                    self.warnings.append(f"No file type validation in {api_file.name}")
    
    def check_error_handling(self):
        """Check error handling"""
        print("\n⚠️ Checking error handling...")
        
        exceptions_file = self.root_path / "app" / "exceptions.py"
        if exceptions_file.exists():
            self.info.append("✅ Custom exception handling implemented")
            
            content = exceptions_file.read_text(encoding='utf-8', errors='ignore')
            if "request_id" in content:
                self.info.append("✅ Request ID tracking implemented")
    
    def check_file_operations(self):
        """Check file operation security"""
        print("\n📁 Checking file operations...")
        
        patterns = [
            (r'open\s*\([^)]*\)', "file open"),
            (r'os\.path\.join', "path join"),
            (r'Path\s*\(', "Path usage"),
        ]
        
        py_files = list(self.root_path.glob("**/*.py"))
        for py_file in py_files:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            for pattern, operation in patterns:
                if re.search(pattern, content):
                    # Check for path traversal protection
                    if "../" in content or "..\\" in content:
                        self.issues.append(f"Potential path traversal in {py_file}")
                    
                    # Check for proper file handling
                    if "with open" not in content and "open(" in content:
                        self.warnings.append(f"File not opened with context manager in {py_file}")
    
    def print_results(self):
        """Print security check results"""
        print("\n" + "=" * 50)
        print("Security Check Results")
        print("=" * 50)
        
        if self.issues:
            print(f"\n🚨 Critical Issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   ❌ {issue}")
        else:
            print("\n✅ No critical security issues found!")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")
        
        if self.info:
            print(f"\n📋 Information ({len(self.info)}):")
            for info in self.info:
                print(f"   ℹ️  {info}")
        
        print("\n📊 Summary:")
        print(f"   Critical Issues: {len(self.issues)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Info: {len(self.info)}")
        
        if self.issues:
            print("\n🔧 Recommendations:")
            print("   1. Fix all critical issues before deployment")
            print("   2. Review and address warnings")
            print("   3. Consider implementing additional security measures")
        
        return len(self.issues) == 0

if __name__ == "__main__":
    checker = SecurityChecker()
    checker.check_all()