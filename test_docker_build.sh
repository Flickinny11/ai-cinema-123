#!/bin/bash

# Test Docker Build Script
echo "🐳 Testing Docker build for RunPod compatibility..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t cinema-ai-test . 2>&1 | tee build.log

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    # Test basic container startup
    echo "🧪 Testing container startup..."
    timeout 30s docker run --rm cinema-ai-test python3 -c "
import runpod_handler
print('✅ Handler imports successfully')
print('✅ RunPod handler ready')
" 2>&1 | tee test.log
    
    if [ $? -eq 0 ]; then
        echo "✅ Container test successful!"
    else
        echo "❌ Container test failed - check test.log"
    fi
    
else
    echo "❌ Docker build failed - check build.log"
    echo "Common issues:"
    echo "  - Missing dependencies in requirements.txt"
    echo "  - File copy order issues"
    echo "  - Base image problems"
fi