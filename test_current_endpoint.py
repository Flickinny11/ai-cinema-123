#!/usr/bin/env python3
"""
Test Current RunPod Endpoint Status
"""

import requests
import json
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID = "31darpauhivyft"

def test_endpoint():
    """Test the endpoint"""
    endpoint_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "type": "health_check"
        }
    }
    
    try:
        logger.info("🔍 Testing endpoint...")
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=60)
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Request submitted: {result}")
            
            if 'id' in result:
                job_id = result['id']
                return check_job_status(job_id)
            else:
                return result
        else:
            logger.error(f"❌ Request failed: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Request error: {e}")
        return None

def check_job_status(job_id):
    """Check job status"""
    status_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"🔍 Monitoring job: {job_id}")
    
    for attempt in range(20):
        try:
            time.sleep(15)
            response = requests.get(status_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', 'unknown')
                
                logger.info(f"Attempt {attempt + 1}: Status = {status}")
                
                if status == 'COMPLETED':
                    output = result.get('output', {})
                    logger.info("✅ Job completed!")
                    logger.info(f"Output: {json.dumps(output, indent=2)}")
                    return output
                elif status == 'FAILED':
                    error = result.get('error', 'Unknown error')
                    logger.error(f"❌ Job failed: {error}")
                    return {"error": error}
                elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                    logger.info(f"⏳ Job {status.lower()}...")
                else:
                    logger.warning(f"Unknown status: {status}")
            else:
                logger.error(f"❌ Status check failed: HTTP {response.status_code}")
                break
                
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            break
    
    return None

def main():
    """Main testing process"""
    logger.info("🚀 Testing Current RunPod Endpoint")
    logger.info("="*50)
    logger.info(f"Endpoint ID: {ENDPOINT_ID}")
    logger.info("="*50)
    
    if not RUNPOD_API_KEY:
        logger.error("❌ No RUNPOD_API_KEY found in environment")
        return False
    
    result = test_endpoint()
    
    if result:
        if result.get('status') == 'healthy':
            logger.info("✅ ENDPOINT IS HEALTHY!")
            logger.info("="*50)
            logger.info("📊 Status: SUCCESS")
            logger.info(f"Pipeline Mode: {result.get('pipeline_mode', 'unknown')}")
            logger.info(f"GPU Available: {result.get('gpu_available', False)}")
            logger.info(f"Volume Mounted: {result.get('volume_mounted', False)}")
            logger.info("="*50)
            return True
        else:
            logger.warning(f"⚠️ Endpoint status: {result.get('status', 'unknown')}")
            if 'error' in result:
                logger.error(f"Error: {result['error']}")
            return False
    else:
        logger.error("❌ Endpoint test failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)