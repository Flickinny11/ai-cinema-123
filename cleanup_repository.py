#!/usr/bin/env python3
"""
Repository Cleanup Script
Removes unnecessary files and organizes the repository
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Files to remove (documentation and test files we no longer need)
FILES_TO_REMOVE = [
    # Old documentation files
    "GITHUB_RELEASE_CREATED.md",
    "NEW_RELEASE_CREATED.md", 
    "PRODUCTION_READY.md",
    "REPOSITORY_RENAME_COMPLETE.md",
    "RUNPOD_FIX_SUMMARY.md",
    "RUNPOD_FIXES_COMPLETED.md",
    "RUNPOD_FIXES_VERIFICATION.md",
    "RUNPOD_ISSUE_ANALYSIS.md",
    "RUNPOD_MAIN_BRANCH_READY.md",
    "RUNPOD_NAME_ISSUE_ANALYSIS.md",
    "RUNPOD_STRUCTURE_ANALYSIS.md",
    "SIMPLIFIED_CONFIGURATION_TEST.md",
    "MANUAL_DEPLOYMENT.md",
    "quickstart.md",
    
    # Old test files
    "test_basic.py",
    "test_production.py",
    "test_docker_readiness.py",
    
    # Old deployment scripts
    "create_release.sh",
    "deploy_complete.py",
    "deploy_runpod.sh",
    "setup_new_repo.sh",
    
    # Redundant handlers
    "simple_handler.py",
    "test_handler.py",
    "test_minimal.py",
    
    # IDE/Extension files
    ".extension/",
    ".claude/"
]

# Files to keep (essential for production)
ESSENTIAL_FILES = [
    # Core pipeline files
    "cinema_pipeline.py",
    "runpod_handler.py", 
    "fallback_handler.py",
    "script_processor.py",
    "human_sounds.py",
    "download_models.py",
    "model_configs.yaml",
    
    # Configuration files
    ".runpod/hub.json",
    ".runpod/tests.json",
    "Dockerfile",
    "requirements.txt",
    "requirements_core.txt",
    ".gitignore",
    ".env.template",
    
    # Documentation (keep essential ones)
    "README.md",
    "RUNPOD_DEPLOYMENT_COMPLETE.md",
    "DOCKER_BUILD_FIXED.md",
    "RUNPOD_SYNC_FIXED.md",
    
    # Deployment tools
    "deploy_to_runpod.py",
    "push_to_runpod_registry.sh",
    "runpod.toml",
    "validate_runpod_config.py",
    "install_packages.py",
    
    # Test tools (keep essential ones)
    "test_build.sh",
    "test_docker_build.sh",
    "test_runpod_handler.py"
]

def cleanup_repository():
    """Clean up unnecessary files"""
    logger.info("🧹 Starting repository cleanup...")
    
    removed_count = 0
    
    for item in FILES_TO_REMOVE:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    logger.info(f"✅ Removed directory: {item}")
                else:
                    os.remove(item)
                    logger.info(f"✅ Removed file: {item}")
                removed_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to remove {item}: {e}")
    
    logger.info(f"🎉 Cleanup complete! Removed {removed_count} items")
    
    # List remaining files
    logger.info("\n📋 Remaining files:")
    for root, dirs, files in os.walk("."):
        # Skip .git directory
        if ".git" in root:
            continue
            
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        logger.info(f"{indent}{os.path.basename(root)}/")
        
        subindent = " " * 2 * (level + 1)
        for file in files:
            logger.info(f"{subindent}{file}")

if __name__ == "__main__":
    cleanup_repository()