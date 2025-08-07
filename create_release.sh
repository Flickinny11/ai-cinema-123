#!/bin/bash

echo "🚀 Creating GitHub Release for RunPod Hub"
echo "=========================================="

# Get current version from git
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
NEW_VERSION="v1.0.0"

echo "Current version: $VERSION"
echo "New version: $NEW_VERSION"

# Create a new tag
echo ""
echo "📦 Creating new tag: $NEW_VERSION"
git tag -a $NEW_VERSION -m "🎬 Cinema AI Production Pipeline v1.0.0 - RunPod Hub Release"

# Push the tag
echo ""
echo "🔄 Pushing tag to GitHub..."
git push origin $NEW_VERSION

echo ""
echo "✅ Tag created and pushed!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://github.com/Flickinny11/ai-cinema-test-1/releases"
echo "2. Click 'Create a new release'"
echo "3. Select the tag: $NEW_VERSION"
echo "4. Title: 'Cinema AI Production Pipeline v1.0.0'"
echo "5. Description:"
echo "   🎬 Cinema AI Production Pipeline v1.0.0"
echo "   "
echo "   ## Features"
echo "   - HunyuanVideo (13B) - Cinema quality video generation"
echo "   - LTX-Video (13B) - Real-time generation (30x faster)"
echo "   - MusicGen-Large - Orchestral film scores"
echo "   - AudioGen-Medium - Professional sound effects"
echo "   - XTTS-v2 - Voice cloning from 6s samples"
echo "   - DeepSeek v3 - Script processing and development"
echo "   "
echo "   ## Performance"
echo "   - 5s video: 2-10 seconds generation"
echo "   - 30s video: 15-90 seconds generation"
echo "   - Supports 720p/1080p/4K resolution"
echo "   - H100/A100 80GB GPU optimized"
echo "   "
echo "   ## Usage"
echo "   - Health check: {\"type\": \"health_check\"}"
echo "   - Single scene: {\"type\": \"single_scene\", \"scene\": {...}}"
echo "   - Script to video: {\"type\": \"script_to_video\", \"script\": \"...\"}"
echo "   - Batch scenes: {\"type\": \"batch_scenes\", \"scenes\": [...]}"
echo "6. Click 'Publish release'"
echo ""
echo "🎉 Your RunPod hub will be updated automatically!"
