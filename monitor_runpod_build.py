#!/usr/bin/env python3
"""
RunPod Build Monitor
Monitors RunPod API to check repository detection and build status
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

# RunPod API Configuration
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_BASE = "https://api.runpod.io/graphql"
GITHUB_REPO = "https://github.com/Flickinny11/ai-cinema-123"

def make_runpod_request(query, variables=None):
    """Make a GraphQL request to RunPod API"""
    if not RUNPOD_API_KEY:
        logger.error("RUNPOD_API_KEY not found in environment variables")
        return None
        
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        response = requests.post(RUNPOD_API_BASE, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "errors" in result:
            logger.error(f"GraphQL errors: {result['errors']}")
            return None
            
        return result
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
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result and result["data"]["myself"]:
        return result["data"]["myself"]
    return None

def list_templates():
    """List user's templates"""
    query = """
    query {
        myself {
            podTemplates {
                id
                name
                imageName
                isPublic
                createdAt
                updatedAt
            }
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result and result["data"]["myself"]:
        return result["data"]["myself"]["podTemplates"]
    return []

def list_serverless_endpoints():
    """List serverless endpoints"""
    query = """
    query {
        myself {
            endpoints {
                id
                name
                createdAt
            }
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result and result["data"]["myself"]:
        return result["data"]["myself"]["endpoints"]
    return []

def search_public_templates():
    """Search for public templates (to see if our repo is indexed)"""
    query = """
    query {
        podTemplates {
            id
            name
            imageName
            isPublic
        }
    }
    """
    
    result = make_runpod_request(query)
    if result and "data" in result:
        # Filter for cinema-related templates
        templates = result["data"]["podTemplates"]
        return [t for t in templates if "cinema" in t.get("name", "").lower()]
    return []

def check_github_webhook_status():
    """Check if GitHub webhook is properly configured"""
    try:
        # Check if repository is accessible
        response = requests.get(f"https://api.github.com/repos/Flickinny11/ai-cinema-123", timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            return {
                "accessible": True,
                "private": repo_data.get("private", True),
                "default_branch": repo_data.get("default_branch", "main"),
                "updated_at": repo_data.get("updated_at"),
                "size": repo_data.get("size", 0)
            }
        else:
            return {"accessible": False, "status_code": response.status_code}
    except Exception as e:
        return {"accessible": False, "error": str(e)}

def monitor_runpod_status():
    """Main monitoring function"""
    logger.info("🔍 RunPod Build Monitor Starting...")
    logger.info("=" * 60)
    
    # Check API connection
    logger.info("1️⃣ Checking RunPod API connection...")
    user_info = get_user_info()
    if not user_info:
        logger.error("❌ Failed to connect to RunPod API")
        logger.error("   Check your RUNPOD_API_KEY in .env file")
        return False
    
    logger.info(f"✅ Connected as: {user_info.get('username', 'unknown')}")
    logger.info(f"   Email: {user_info.get('email', 'unknown')}")
    logger.info(f"   Credit Balance: ${user_info.get('creditBalance', 0):.2f}")
    
    # Check GitHub repository status
    logger.info("\n2️⃣ Checking GitHub repository status...")
    github_status = check_github_webhook_status()
    if github_status.get("accessible"):
        logger.info("✅ Repository is accessible")
        logger.info(f"   Private: {github_status.get('private', 'unknown')}")
        logger.info(f"   Default Branch: {github_status.get('default_branch', 'unknown')}")
        logger.info(f"   Last Updated: {github_status.get('updated_at', 'unknown')}")
        logger.info(f"   Size: {github_status.get('size', 0)} KB")
    else:
        logger.error("❌ Repository not accessible")
        logger.error(f"   Error: {github_status.get('error', 'Unknown error')}")
    
    # List existing templates
    logger.info("\n3️⃣ Checking existing templates...")
    templates = list_templates()
    
    cinema_templates = []
    for template in templates:
        if "cinema" in template.get("name", "").lower() or "ai-cinema" in template.get("githubUrl", "").lower():
            cinema_templates.append(template)
    
    if cinema_templates:
        logger.info(f"✅ Found {len(cinema_templates)} Cinema AI template(s):")
        for template in cinema_templates:
            logger.info(f"   📋 {template['name']} (ID: {template['id']})")
            logger.info(f"      Status: {template.get('buildStatus', 'unknown')}")
            logger.info(f"      GitHub: {template.get('githubUrl', 'none')}")
            logger.info(f"      Created: {template.get('createdAt', 'unknown')}")
            logger.info(f"      Updated: {template.get('updatedAt', 'unknown')}")
    else:
        logger.warning("⚠️  No Cinema AI templates found")
    
    # List serverless endpoints
    logger.info("\n4️⃣ Checking serverless endpoints...")
    endpoints = list_serverless_endpoints()
    
    cinema_endpoints = []
    for endpoint in endpoints:
        if "cinema" in endpoint.get("name", "").lower():
            cinema_endpoints.append(endpoint)
    
    if cinema_endpoints:
        logger.info(f"✅ Found {len(cinema_endpoints)} Cinema AI endpoint(s):")
        for endpoint in cinema_endpoints:
            logger.info(f"   🌐 {endpoint['name']} (ID: {endpoint['id']})")
            logger.info(f"      Status: {endpoint.get('status', 'unknown')}")
            logger.info(f"      Created: {endpoint.get('createdAt', 'unknown')}")
            if endpoint.get('template'):
                logger.info(f"      Template: {endpoint['template'].get('name', 'unknown')}")
                logger.info(f"      Build Status: {endpoint['template'].get('buildStatus', 'unknown')}")
    else:
        logger.warning("⚠️  No Cinema AI endpoints found")
    
    # Search public templates
    logger.info("\n5️⃣ Searching RunPod Hub for Cinema AI...")
    public_templates = search_public_templates()
    
    if public_templates:
        logger.info(f"✅ Found {len(public_templates)} public template(s) matching 'cinema-ai':")
        for template in public_templates:
            logger.info(f"   🌍 {template['name']} by {template.get('author', {}).get('username', 'unknown')}")
            logger.info(f"      GitHub: {template.get('githubUrl', 'none')}")
    else:
        logger.warning("⚠️  No public Cinema AI templates found in RunPod Hub")
    
    # Summary and recommendations
    logger.info("\n" + "=" * 60)
    logger.info("📊 SUMMARY")
    logger.info("=" * 60)
    
    if cinema_templates:
        logger.info("✅ Status: Templates exist in your account")
        logger.info("🎯 Action: Check template build status and create endpoint if needed")
    elif public_templates:
        logger.info("✅ Status: Public templates found but not in your account")
        logger.info("🎯 Action: Fork or create new template from GitHub")
    else:
        logger.info("❌ Status: No Cinema AI templates found anywhere")
        logger.info("🎯 Action: Create new template from GitHub repository")
    
    logger.info(f"\n🔗 Repository: {GITHUB_REPO}")
    logger.info("🔗 RunPod Console: https://runpod.io/console")
    logger.info("🔗 RunPod Hub: https://runpod.io/console/hub")
    
    return True

if __name__ == "__main__":
    try:
        monitor_runpod_status()
    except KeyboardInterrupt:
        logger.info("\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitoring failed: {e}")
        import traceback
        logger.error(traceback.format_exc())