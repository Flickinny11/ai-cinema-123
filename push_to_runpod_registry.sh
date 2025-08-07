#!/bin/bash

# Push to RunPod Container Registry
echo "🐳 Pushing Cinema AI to RunPod Container Registry"
echo "=================================================="

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# RunPod Registry Configuration
REGISTRY="registry.runpod.io"
REGISTRY_ID="${RUNPOD_REGISTRY_ID:-your_registry_id_here}"
USERNAME="${RUNPOD_USERNAME:-your_username_here}"
PASSWORD="${RUNPOD_PASSWORD:-your_password_here}"
IMAGE_NAME="cinema-ai-pipeline"
TAG="v1.0.7"

echo "📋 Configuration:"
echo "   Registry: $REGISTRY"
echo "   Registry ID: $REGISTRY_ID"
echo "   Image: $IMAGE_NAME:$TAG"
echo ""

# Login to RunPod registry
echo "🔐 Logging into RunPod registry..."
echo "$PASSWORD" | docker login $REGISTRY -u $USERNAME --password-stdin

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to RunPod registry"
    exit 1
fi

echo "✅ Successfully logged into RunPod registry"

# Build the image
echo ""
echo "🏗️  Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker build successful"

# Tag for RunPod registry
echo ""
echo "🏷️  Tagging image for RunPod registry..."
FULL_IMAGE_NAME="$REGISTRY/$REGISTRY_ID/$IMAGE_NAME:$TAG"
docker tag $IMAGE_NAME:$TAG $FULL_IMAGE_NAME

echo "✅ Image tagged as: $FULL_IMAGE_NAME"

# Push to registry
echo ""
echo "📤 Pushing to RunPod registry..."
docker push $FULL_IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Failed to push to RunPod registry"
    exit 1
fi

echo "✅ Successfully pushed to RunPod registry!"

# Also tag and push as latest
echo ""
echo "🏷️  Tagging and pushing as latest..."
LATEST_IMAGE_NAME="$REGISTRY/$REGISTRY_ID/$IMAGE_NAME:latest"
docker tag $IMAGE_NAME:$TAG $LATEST_IMAGE_NAME
docker push $LATEST_IMAGE_NAME

echo ""
echo "🎉 Deployment to RunPod registry complete!"
echo ""
echo "📊 Summary:"
echo "   Image: $FULL_IMAGE_NAME"
echo "   Latest: $LATEST_IMAGE_NAME"
echo "   Status: Ready for RunPod deployment"
echo ""
echo "🚀 Next steps:"
echo "   1. Go to RunPod Console: https://runpod.io/console"
echo "   2. Create new template using: $FULL_IMAGE_NAME"
echo "   3. Deploy serverless endpoint"
echo ""
echo "🔗 Registry URL: $REGISTRY/$REGISTRY_ID/$IMAGE_NAME"