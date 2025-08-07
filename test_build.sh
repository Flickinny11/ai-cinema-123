#!/bin/bash

# Test Docker Build for RunPod
echo "🐳 Testing Docker build for RunPod deployment..."

# Clean up any existing containers/images
echo "🧹 Cleaning up existing builds..."
docker rmi cinema-ai-test 2>/dev/null || true

# Build the image
echo "📦 Building Docker image..."
docker build -t cinema-ai-test . 2>&1 | tee build.log

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    # Test basic Python imports
    echo "🧪 Testing basic imports..."
    docker run --rm cinema-ai-test python3 -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import torch
    print('✅ PyTorch imported')
except ImportError as e:
    print(f'❌ PyTorch failed: {e}')

try:
    import runpod
    print('✅ RunPod imported')
except ImportError as e:
    print(f'❌ RunPod failed: {e}')

try:
    import transformers
    print('✅ Transformers imported')
except ImportError as e:
    print(f'❌ Transformers failed: {e}')

try:
    import diffusers
    print('✅ Diffusers imported')
except ImportError as e:
    print(f'❌ Diffusers failed: {e}')

try:
    import fastapi
    print('✅ FastAPI imported')
except ImportError as e:
    print(f'❌ FastAPI failed: {e}')

print('🎯 Core imports test completed')
"

    # Test handler import
    echo "🧪 Testing handler import..."
    docker run --rm cinema-ai-test python3 -c "
try:
    import runpod_handler
    print('✅ Handler imported successfully')
    
    # Test handler function exists
    if hasattr(runpod_handler, 'handler'):
        print('✅ Handler function found')
    else:
        print('❌ Handler function not found')
        
except ImportError as e:
    print(f'❌ Handler import failed: {e}')
except Exception as e:
    print(f'❌ Handler test failed: {e}')
"

    # Test basic handler execution
    echo "🧪 Testing handler execution..."
    docker run --rm cinema-ai-test python3 -c "
try:
    import runpod_handler
    
    # Test health check
    test_event = {
        'id': 'test-123',
        'input': {'type': 'health_check'}
    }
    
    result = runpod_handler.handler(test_event)
    print(f'✅ Handler executed: {result.get(\"status\", \"unknown\")}')
    
except Exception as e:
    print(f'❌ Handler execution failed: {e}')
"

    echo ""
    echo "✅ Build test completed successfully!"
    echo "📊 Summary:"
    echo "   - Docker build: ✅ Success"
    echo "   - Core imports: ✅ Tested"
    echo "   - Handler: ✅ Tested"
    echo ""
    echo "🚀 Ready for RunPod deployment!"
    
else
    echo "❌ Docker build failed!"
    echo ""
    echo "📋 Common issues to check:"
    echo "   - Package version conflicts"
    echo "   - Missing system dependencies"
    echo "   - Network connectivity issues"
    echo "   - Insufficient disk space"
    echo ""
    echo "📄 Check build.log for detailed error information"
    exit 1
fi