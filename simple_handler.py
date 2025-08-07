#!/usr/bin/env python3
"""
Simple RunPod Handler for Testing
"""

import runpod
import json

def handler(event):
    """
    Simple RunPod serverless handler function
    """
    try:
        # Extract input data
        input_data = event.get("input", {})
        job_id = event.get("id", "unknown")
        
        # Simple response for testing
        result = {
            "status": "success",
            "message": "Simple handler working",
            "job_id": job_id,
            "input_received": input_data
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    # Start the serverless worker
    runpod.serverless.start({"handler": handler})
