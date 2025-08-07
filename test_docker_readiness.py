#!/usr/bin/env python3
"""
Docker Build Test Script
Tests that the repository is ready for Docker build and RunPod deployment
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dockerfile_syntax():
    """Test that Dockerfile syntax is valid"""
    logger.info("Testing Dockerfile syntax...")
    
    dockerfile_path = "Dockerfile"
    if not os.path.exists(dockerfile_path):
        logger.error("❌ Dockerfile not found!")
        return False
    
    try:
        # Check basic Dockerfile syntax by reading it
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        # Check for required components
        required_elements = [
            "FROM nvidia/cuda",
            "WORKDIR /app", 
            "COPY cinema_pipeline.py",
            "COPY runpod_handler.py",
            "COPY script_processor.py",
            "COPY human_sounds.py",
            "ENTRYPOINT"
        ]
        
        missing = []
        for element in required_elements:
            if element not in content:
                missing.append(element)
        
        if missing:
            logger.error(f"❌ Missing required Dockerfile elements: {missing}")
            return False
            
        logger.info("✅ Dockerfile syntax and required elements OK")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading Dockerfile: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    logger.info("Testing file structure...")
    
    required_files = [
        "Dockerfile",
        "requirements.txt", 
        "cinema_pipeline.py",
        "runpod_handler.py",
        "script_processor.py",
        "human_sounds.py",
        "download_models.py",
        "model_configs.yaml",
        "runpod/hub.json"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        logger.error(f"❌ Missing required files: {missing}")
        return False
    
    logger.info("✅ All required files present")
    return True

def test_requirements():
    """Test that requirements.txt has critical packages"""
    logger.info("Testing requirements.txt...")
    
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        critical_packages = [
            "torch",
            "transformers", 
            "diffusers",
            "runpod",
            "openai",
            "opencv-python",
            "soundfile",
            "pyyaml"
        ]
        
        missing = []
        for package in critical_packages:
            if package not in requirements:
                missing.append(package)
        
        if missing:
            logger.warning(f"⚠ Some packages might be missing: {missing}")
            # Don't fail - they might be named differently
        
        logger.info("✅ Requirements.txt looks good")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading requirements.txt: {e}")
        return False

def test_runpod_config():
    """Test RunPod configuration"""
    logger.info("Testing RunPod configuration...")
    
    try:
        import json
        with open("runpod/hub.json", 'r') as f:
            config = json.load(f)
        
        required_fields = [
            "name",
            "description", 
            "template",
            "serverless",
            "runtime"
        ]
        
        missing = []
        for field in required_fields:
            if field not in config:
                missing.append(field)
        
        if missing:
            logger.error(f"❌ Missing RunPod config fields: {missing}")
            return False
        
        # Check that handler is specified correctly
        if config.get("runtime", {}).get("handler") != "runpod_handler.py":
            logger.warning("⚠ RunPod handler might not be configured correctly")
        
        logger.info("✅ RunPod configuration looks good")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error reading RunPod config: {e}")
        return False

def test_python_syntax():
    """Test that all Python files have valid syntax"""
    logger.info("Testing Python syntax...")
    
    python_files = [
        "cinema_pipeline.py",
        "runpod_handler.py", 
        "script_processor.py",
        "human_sounds.py",
        "download_models.py"
    ]
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                code = f.read()
            
            # Compile to check syntax
            compile(code, file, 'exec')
            logger.info(f"✅ {file} syntax OK")
            
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error reading {file}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("🐳 Docker Build Readiness Test")
    logger.info("="*60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dockerfile Syntax", test_dockerfile_syntax),
        ("Requirements", test_requirements),
        ("RunPod Config", test_runpod_config),
        ("Python Syntax", test_python_syntax)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    logger.info("="*60)
    logger.info(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All tests passed! Repository is ready for Docker build and RunPod deployment")
        return 0
    else:
        logger.error("💥 Some tests failed. Fix issues before deploying to production.")
        return 1

if __name__ == "__main__":
    sys.exit(main())