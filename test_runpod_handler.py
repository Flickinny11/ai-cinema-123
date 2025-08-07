#!/usr/bin/env python3
"""
Test RunPod Handler Structure
Tests that the handler works correctly with RunPod patterns
"""

import logging
import sys
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_handler_import():
    """Test that handler can be imported"""
    try:
        import runpod_handler
        logger.info("✅ Handler imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Handler import failed: {e}")
        return False

def test_handler_function():
    """Test that handler function exists and is callable"""
    try:
        import runpod_handler
        
        # Check if handler function exists
        if not hasattr(runpod_handler, 'handler'):
            logger.error("❌ Handler function not found")
            return False
            
        # Check if it's callable
        if not callable(runpod_handler.handler):
            logger.error("❌ Handler is not callable")
            return False
            
        logger.info("✅ Handler function exists and is callable")
        return True
    except Exception as e:
        logger.error(f"❌ Handler function test failed: {e}")
        return False

def test_health_check():
    """Test health check functionality"""
    try:
        import runpod_handler
        
        # Create a health check job
        job = {
            "id": "test_health_check",
            "input": {
                "type": "health_check"
            }
        }
        
        # Call handler
        result = runpod_handler.handler(job)
        
        # Check result
        if not isinstance(result, dict):
            logger.error("❌ Handler didn't return a dict")
            return False
            
        if "status" not in result:
            logger.error("❌ Handler result missing status field")
            return False
            
        logger.info("✅ Health check works")
        logger.info(f"Health check result: {json.dumps(result, indent=2)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    try:
        import runpod_handler
        
        # Test invalid request type
        job = {
            "id": "test_invalid",
            "input": {
                "type": "invalid_type"
            }
        }
        
        result = runpod_handler.handler(job)
        
        # Should return error
        if not isinstance(result, dict):
            logger.error("❌ Handler didn't return a dict for invalid request")
            return False
            
        if "error" not in result:
            logger.error("❌ Handler didn't return error for invalid request")
            return False
            
        logger.info("✅ Error handling works correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False

def test_runpod_start():
    """Test that runpod.serverless.start is properly called"""
    try:
        import runpod_handler
        
        # Check if the file contains the required runpod.serverless.start call
        with open("runpod_handler.py", "r") as f:
            content = f.read()
            
        if "runpod.serverless.start" not in content:
            logger.error("❌ runpod.serverless.start not found in handler")
            return False
            
        if '{"handler": handler}' not in content:
            logger.error("❌ Proper handler configuration not found")
            return False
            
        logger.info("✅ RunPod serverless start configuration found")
        return True
        
    except Exception as e:
        logger.error(f"❌ RunPod start test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("🧪 Testing RunPod Handler Structure")
    logger.info("="*60)
    
    tests = [
        ("Handler Import", test_handler_import),
        ("Handler Function", test_handler_function),
        ("Health Check", test_health_check),
        ("Error Handling", test_error_handling),
        ("RunPod Start", test_runpod_start)
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
        logger.info("🎉 All tests passed! Handler is ready for RunPod deployment")
        return 0
    else:
        logger.error("💥 Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())