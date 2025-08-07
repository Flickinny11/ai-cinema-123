#!/bin/bash

# RunPod Deployment Script for Cinema AI Pipeline
# This script ensures proper deployment to RunPod Hub

echo "🚀 Cinema AI Pipeline - RunPod Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "runpod_handler.py" ]; then
    echo "❌ Error: runpod_handler.py not found. Run this script from the project root."
    exit 1
fi

# Check if .runpod directory exists
if [ ! -d ".runpod" ]; then
    echo "❌ Error: .runpod directory not found."
    exit 1
fi

# Verify required files
echo "📋 Checking required files..."

required_files=(
    ".runpod/hub.json"
    ".runpod/tests.json"
    "runpod_handler.py"
    "Dockerfile"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
        exit 1
    fi
done

# Check git status
echo ""
echo "📋 Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Uncommitted changes detected. Committing..."
    git add .
    git commit -m "Update RunPod configuration for deployment"
else
    echo "✅ Git status clean"
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Not on main branch. Current: $current_branch"
    echo "   RunPod typically syncs from main branch."
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push origin main

# Create a new release
echo ""
echo "🏷️  Creating new release..."
current_time=$(date +"%Y%m%d_%H%M%S")
tag_name="v1.0.5_${current_time}"

git tag -a "$tag_name" -m "RunPod deployment configuration update - $(date)"
git push origin "$tag_name"

echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📊 Summary:"
echo "   Repository: https://github.com/Flickinny11/ai-cinema-123"
echo "   Latest tag: $tag_name"
echo "   Handler: runpod_handler.py"
echo "   Config: .runpod/hub.json"
echo ""
echo "🎯 Next steps:"
echo "   1. Wait 5-10 minutes for GitHub to process the release"
echo "   2. Go to RunPod Hub: https://runpod.io/console/hub"
echo "   3. Search for 'ai-cinema-123' or 'Cinema AI Pipeline'"
echo "   4. The repository should now be detectable for sync"
echo ""
echo "🔍 If still not detected, check:"
echo "   - Repository is public"
echo "   - No typos in git_url in hub.json"
echo "   - Handler file exists and is valid Python"
echo "   - Dockerfile builds successfully"