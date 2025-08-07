#!/usr/bin/env python3
"""
Create RunPod Template Directly
Since automatic detection isn't working, create template manually via API
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

API_KEY = os.getenv("RUNPOD_API_KEY")
API_BASE = "https://api.runpod.io/graphql"
GITHUB_REPO = "https://github.com/Flickinny11/ai-cinema-123"

def make_runpod_request(query, variables=None):
    """Make a GraphQL request to RunPod API"""
    if not API_KEY:
        logger.error("RUNPOD_API_KEY not found")
        return None
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        response = requests.post(API_BASE, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "errors" in result:
            logger.error(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
            return None
            
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"RunPod API request failed: {e}")
        return None

def create_template():
    """Create a new template from GitHub repository"""
    logger.info("🔨 Creating RunPod template from GitHub repository...")
    
    # First, let's try to find the correct mutation for creating templates
    # Let's test with a simple template creation
    
    query = """
    mutation {
        saveTemplate(input: {
            name: "Cinema AI Pipeline"
            imageName: "cinema-ai-pipeline"
            readme: "# Cinema AI Pipeline\\n\\nProduction-ready AI video generation with HunyuanVideo, LTX-Video, MusicGen, and voice cloning."
            isPublic: true
            githubUrl: "https://github.com/Flickinny11/ai-cinema-123"
            dockerfilePath: "Dockerfile"
            containerDiskInGb: 50
            volumeInGb: 100
            volumeMountPath: "/models"
            ports: "8000/http"
            env: [
                {
                    key: "HF_HOME"
                    value: "/models/cache"
                },
                {
                    key: "PYTORCH_CUDA_ALLOC_CONF"
                    value: "max_split_size_mb:512"
                }
            ]
        }) {
            id
            name
            imageName
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result and result["data"]["saveTemplate"]:
        template = result["data"]["saveTemplate"]
        logger.info(f"✅ Template created successfully!")
        logger.info(f"   ID: {template['id']}")
        logger.info(f"   Name: {template['name']}")
        logger.info(f"   Image: {template['imageName']}")
        return template
    else:
        logger.error("❌ Failed to create template")
        return None

def trigger_build(template_id):
    """Trigger a build for the template"""
    logger.info(f"🏗️  Triggering build for template {template_id}...")
    
    query = """
    mutation buildTemplate($templateId: String!) {
        buildTemplate(templateId: $templateId) {
            id
            status
        }
    }
    """
    
    variables = {"templateId": template_id}
    result = make_runpod_request(query, variables)
    
    if result and "data" in result:
        logger.info("✅ Build triggered successfully!")
        return True
    else:
        logger.error("❌ Failed to trigger build")
        return False

def create_serverless_endpoint(template_id):
    """Create a serverless endpoint from the template"""
    logger.info(f"🌐 Creating serverless endpoint from template {template_id}...")
    
    query = """
    mutation {
        createServerlessEndpoint(input: {
            name: "cinema-ai-serverless"
            templateId: "%s"
            gpuIds: "NVIDIA RTX A6000,NVIDIA A100-SXM4-40GB,NVIDIA A100-SXM4-80GB"
            workersMin: 0
            workersMax: 3
            idleTimeout: 600
            scaleType: QUEUE_DELAY
            scaleValue: 30
        }) {
            id
            name
        }
    }
    """ % template_id
    
    result = make_runpod_request(query)
    if result and "data" in result and result["data"]["createServerlessEndpoint"]:
        endpoint = result["data"]["createServerlessEndpoint"]
        logger.info(f"✅ Serverless endpoint created!")
        logger.info(f"   ID: {endpoint['id']}")
        logger.info(f"   Name: {endpoint['name']}")
        return endpoint
    else:
        logger.error("❌ Failed to create serverless endpoint")
        return None

def main():
    """Main deployment process"""
    logger.info("🚀 Direct RunPod Template Creation")
    logger.info("=" * 60)
    
    if not API_KEY:
        logger.error("❌ No API key found in .env file")
        return False
    
    # Create template
    template = create_template()
    if not template:
        logger.error("❌ Template creation failed")
        return False
    
    template_id = template["id"]
    
    # Trigger build
    if not trigger_build(template_id):
        logger.warning("⚠️  Build trigger failed, but template exists")
    
    # Wait a moment for build to start
    time.sleep(5)
    
    # Create serverless endpoint
    endpoint = create_serverless_endpoint(template_id)
    if not endpoint:
        logger.warning("⚠️  Endpoint creation failed, but template exists")
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 DEPLOYMENT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Template ID: {template_id}")
    logger.info(f"✅ Template Name: {template['name']}")
    
    if endpoint:
        logger.info(f"✅ Endpoint ID: {endpoint['id']}")
        logger.info(f"✅ Endpoint Name: {endpoint['name']}")
        logger.info(f"🔗 API URL: https://api.runpod.ai/v2/{endpoint['id']}/runsync")
    
    logger.info("🔗 RunPod Console: https://runpod.io/console")
    logger.info("🔗 Check status in RunPod dashboard")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            exit(1)
    except KeyboardInterrupt:
        logger.info("\n👋 Deployment stopped by user")
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        exit(1)