#!/usr/bin/env python3
"""
Direct RunPod Deployment Script
Uses RunPod API to deploy the Cinema AI pipeline directly
"""

import requests
import json
import time
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RunPod API Configuration - Use environment variables
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "your_api_key_here")
RUNPOD_REGISTRY_ID = os.getenv("RUNPOD_REGISTRY_ID", "your_registry_id_here")
RUNPOD_USERNAME = os.getenv("RUNPOD_USERNAME", "your_username_here")
RUNPOD_PASSWORD = os.getenv("RUNPOD_PASSWORD", "your_password_here")

RUNPOD_API_BASE = "https://api.runpod.io/graphql"
GITHUB_REPO = "https://github.com/Flickinny11/ai-cinema-123"

def make_runpod_request(query, variables=None):
    """Make a GraphQL request to RunPod API"""
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        response = requests.post(RUNPOD_API_BASE, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"RunPod API request failed: {e}")
        return None

def get_user_info():
    """Get current user information"""
    query = """
    query {
        myself {
            id
            email
            username
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result:
        return result["data"]["myself"]
    return None

def list_templates():
    """List existing templates"""
    query = """
    query {
        myself {
            templates {
                id
                name
                imageName
                isPublic
            }
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result:
        return result["data"]["myself"]["templates"]
    return []

def create_template():
    """Create a new template from GitHub repository"""
    query = """
    mutation createTemplate($input: TemplateInput!) {
        createTemplate(input: $input) {
            id
            name
            imageName
        }
    }
    """
    
    variables = {
        "input": {
            "name": "Cinema AI Pipeline",
            "imageName": "cinema-ai-pipeline",
            "dockerArgs": "",
            "containerDiskInGb": 50,
            "volumeInGb": 100,
            "volumeMountPath": "/models",
            "ports": "8000/http",
            "env": [
                {
                    "key": "HF_HOME",
                    "value": "/models/cache"
                },
                {
                    "key": "PYTORCH_CUDA_ALLOC_CONF", 
                    "value": "max_split_size_mb:512"
                }
            ],
            "isPublic": True,
            "readme": "# Cinema AI Pipeline\n\nProduction-ready AI video generation with HunyuanVideo, LTX-Video, MusicGen, and voice cloning.",
            "githubUrl": GITHUB_REPO,
            "dockerfilePath": "Dockerfile"
        }
    }
    
    result = make_runpod_request(query, variables)
    if result and "data" in result:
        return result["data"]["createTemplate"]
    return None

def create_serverless_endpoint(template_id):
    """Create a serverless endpoint from template"""
    query = """
    mutation createServerlessEndpoint($input: ServerlessEndpointInput!) {
        createServerlessEndpoint(input: $input) {
            id
            name
        }
    }
    """
    
    variables = {
        "input": {
            "name": "cinema-ai-serverless",
            "templateId": template_id,
            "gpuIds": "NVIDIA RTX A6000,NVIDIA A100-SXM4-40GB,NVIDIA A100-SXM4-80GB",
            "workersMin": 0,
            "workersMax": 3,
            "idleTimeout": 600,
            "scaleType": "QUEUE_DELAY",
            "scaleValue": 30
        }
    }
    
    result = make_runpod_request(query, variables)
    if result and "data" in result:
        return result["data"]["createServerlessEndpoint"]
    return None

def build_template(template_id):
    """Trigger a template build"""
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
        return result["data"]["buildTemplate"]
    return None

def get_build_status(template_id):
    """Get template build status"""
    query = """
    query getTemplate($templateId: String!) {
        template(id: $templateId) {
            id
            name
            buildStatus
            buildLogs
        }
    }
    """
    
    variables = {"templateId": template_id}
    result = make_runpod_request(query, variables)
    if result and "data" in result:
        return result["data"]["template"]
    return None

def main():
    """Main deployment process"""
    logger.info("🚀 Starting direct RunPod deployment")
    logger.info("="*60)
    
    # Check API connection
    logger.info("🔍 Checking RunPod API connection...")
    user_info = get_user_info()
    if not user_info:
        logger.error("❌ Failed to connect to RunPod API")
        return False
    
    logger.info(f"✅ Connected as: {user_info.get('username', 'unknown')}")
    
    # List existing templates
    logger.info("📋 Checking existing templates...")
    templates = list_templates()
    
    cinema_template = None
    for template in templates:
        if "cinema" in template.get("name", "").lower():
            cinema_template = template
            logger.info(f"✅ Found existing template: {template['name']} (ID: {template['id']})")
            break
    
    # Create new template if needed
    if not cinema_template:
        logger.info("🔨 Creating new template...")
        cinema_template = create_template()
        if not cinema_template:
            logger.error("❌ Failed to create template")
            return False
        logger.info(f"✅ Template created: {cinema_template['name']} (ID: {cinema_template['id']})")
    
    template_id = cinema_template["id"]
    
    # Trigger build
    logger.info("🏗️  Triggering template build...")
    build_result = build_template(template_id)
    if not build_result:
        logger.error("❌ Failed to trigger build")
        return False
    
    logger.info("✅ Build triggered successfully")
    
    # Monitor build status
    logger.info("⏳ Monitoring build progress...")
    max_wait_time = 1800  # 30 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        status = get_build_status(template_id)
        if not status:
            logger.error("❌ Failed to get build status")
            break
            
        build_status = status.get("buildStatus", "unknown")
        logger.info(f"📊 Build status: {build_status}")
        
        if build_status == "COMPLETED":
            logger.info("✅ Build completed successfully!")
            break
        elif build_status == "FAILED":
            logger.error("❌ Build failed!")
            if "buildLogs" in status:
                logger.error(f"Build logs: {status['buildLogs']}")
            return False
        
        time.sleep(30)  # Check every 30 seconds
    
    # Create serverless endpoint
    logger.info("🌐 Creating serverless endpoint...")
    endpoint = create_serverless_endpoint(template_id)
    if not endpoint:
        logger.error("❌ Failed to create serverless endpoint")
        return False
    
    logger.info(f"✅ Serverless endpoint created: {endpoint['name']} (ID: {endpoint['id']})")
    
    logger.info("="*60)
    logger.info("🎉 Deployment completed successfully!")
    logger.info(f"📊 Template ID: {template_id}")
    logger.info(f"🌐 Endpoint ID: {endpoint['id']}")
    logger.info("🔗 Check your RunPod console for the endpoint URL")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)