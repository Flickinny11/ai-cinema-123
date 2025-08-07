#!/bin/bash

echo "🚀 Setting up new GitHub repository: ai-cinema-test-1"
echo "=================================================="

echo ""
echo "📋 Steps to create the new repository:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: ai-cinema-test-1"
echo "3. Description: Cinema AI Production Pipeline - Test Repository"
echo "4. Make it Public"
echo "5. DO NOT initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo ""

echo "⏳ Waiting for you to create the repository..."
echo "Press Enter when you've created the repository on GitHub..."
read

echo ""
echo "🔄 Pushing code to new repository..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to new repository!"
    echo "🔗 Repository URL: https://github.com/Flickinny11/ai-cinema-test-1"
    echo ""
    echo "🎬 Next steps for RunPod deployment:"
    echo "1. Go to RunPod Console: https://runpod.io/console"
    echo "2. Navigate to Serverless → Templates"
    echo "3. Create new template with Dockerfile URL:"
    echo "   https://github.com/Flickinny11/ai-cinema-test-1/blob/main/Dockerfile"
    echo "4. Follow the MANUAL_DEPLOYMENT.md guide"
else
    echo ""
    echo "❌ Failed to push to repository"
    echo "Please check that the repository exists and you have access"
fi
