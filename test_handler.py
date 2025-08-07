#!/usr/bin/env python3
"""
Minimal RunPod Handler for Testing
This is a simple handler to test if RunPod can detect the handler script.
"""

import runpod
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(event):
    """
    Minimal RunPod serverless handler function
    """
    try:
        # Extract input data
        input_data = event.get("input", {})
        job_id = event.get("id", "unknown")
        
        logger.info(f"🎯 Job {job_id} started")
        logger.info(f"Input: {input_data}")
        
        # Simple response for testing
        result = {
            "status": "success",
            "message": "Minimal handler working",
            "job_id": job_id,
            "input_received": input_data
        }
        
        logger.info(f"✅ Job {job_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    logger.info("🚀 Starting Minimal RunPod Test Handler")
    logger.info("Version: 1.0 - Test Edition")
    
    # Start the serverless worker
    runpod.serverless.start({"handler": handler})
