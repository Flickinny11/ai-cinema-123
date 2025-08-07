#!/usr/bin/env python3
"""
RunPod Configuration Validator
Validates that the repository is properly configured for RunPod Hub
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and return status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def validate_json_file(filepath, description):
    """Validate JSON file format"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"✅ {description}: Valid JSON")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ {description}: Invalid JSON - {e}")
        return None
    except FileNotFoundError:
        print(f"❌ {description}: File not found")
        return None

def check_handler_file(filepath):
    """Check if handler file is properly structured"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        checks = [
            ("import runpod", "runpod import"),
            ("def handler(", "handler function"),
            ("runpod.serverless.start", "serverless start call"),
            ('{"handler": handler}', "handler configuration")
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ Handler {description}: Found")
            else:
                print(f"❌ Handler {description}: Missing")
                all_good = False
        
        return all_good
    except FileNotFoundError:
        print(f"❌ Handler file not found: {filepath}")
        return False

def validate_hub_config(config):
    """Validate hub.json configuration"""
    required_fields = [
        "version", "name", "description", "author", "git_url",
        "build", "template", "serverless", "runtime", "schema"
    ]
    
    all_good = True
    for field in required_fields:
        if field in config:
            print(f"✅ Hub config {field}: Present")
        else:
            print(f"❌ Hub config {field}: Missing")
            all_good = False
    
    # Check specific values
    if "runtime" in config:
        runtime = config["runtime"]
        if "handler" in runtime:
            handler_file = runtime["handler"]
            if os.path.exists(handler_file):
                print(f"✅ Handler file reference: {handler_file} exists")
            else:
                print(f"❌ Handler file reference: {handler_file} not found")
                all_good = False
        else:
            print("❌ Runtime handler: Not specified")
            all_good = False
    
    # Check git_url format
    if "git_url" in config:
        git_url = config["git_url"]
        if git_url.startswith("https://github.com/") and git_url.endswith("ai-cinema-123"):
            print(f"✅ Git URL format: {git_url}")
        else:
            print(f"❌ Git URL format: {git_url} - Should be GitHub HTTPS URL")
            all_good = False
    
    return all_good

def check_git_status():
    """Check git repository status"""
    try:
        # Check if we're in a git repo
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Git status: Uncommitted changes detected")
            print("   Recommendation: Commit and push changes before deployment")
            return False
        else:
            print("✅ Git status: Clean")
            return True
    except subprocess.CalledProcessError:
        print("❌ Git status: Not a git repository or git not available")
        return False

def check_github_connectivity():
    """Check if GitHub repository is accessible"""
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True, check=True)
        remote_url = result.stdout.strip()
        print(f"✅ GitHub remote: {remote_url}")
        
        # Test connectivity
        result = subprocess.run(["git", "ls-remote", "origin", "HEAD"], 
                              capture_output=True, text=True, check=True)
        print("✅ GitHub connectivity: Repository accessible")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub connectivity: Failed - {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 RunPod Configuration Validator")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check required files
    print("\n📁 File Structure Check:")
    required_files = [
        (".runpod/hub.json", "Hub configuration"),
        (".runpod/tests.json", "Test configuration"),
        ("runpod_handler.py", "Handler script"),
        ("Dockerfile", "Docker configuration"),
        ("requirements.txt", "Python requirements")
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Validate JSON files
    print("\n📋 JSON Validation:")
    hub_config = validate_json_file(".runpod/hub.json", "Hub configuration")
    tests_config = validate_json_file(".runpod/tests.json", "Tests configuration")
    
    if not hub_config or not tests_config:
        all_checks_passed = False
    
    # Validate hub configuration
    if hub_config:
        print("\n⚙️  Hub Configuration Validation:")
        if not validate_hub_config(hub_config):
            all_checks_passed = False
    
    # Check handler file
    print("\n🐍 Handler File Validation:")
    if not check_handler_file("runpod_handler.py"):
        all_checks_passed = False
    
    # Check git status
    print("\n📤 Git Repository Check:")
    if not check_git_status():
        all_checks_passed = False
    
    # Check GitHub connectivity
    if not check_github_connectivity():
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 All checks passed! Repository is ready for RunPod deployment.")
        print("\n🚀 Next steps:")
        print("   1. Run: ./deploy_runpod.sh")
        print("   2. Wait 5-10 minutes for GitHub processing")
        print("   3. Check RunPod Hub for your repository")
    else:
        print("❌ Some checks failed. Fix the issues above before deployment.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())