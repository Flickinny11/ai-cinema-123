#!/bin/bash

# Simple RunPod Status Checker
echo "🔍 Checking RunPod Status for ai-cinema-123"
echo "============================================"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

API_KEY="${RUNPOD_API_KEY}"
REPO_URL="https://github.com/Flickinny11/ai-cinema-123"

echo "📋 Configuration:"
echo "   API Key: ${API_KEY:0:10}..."
echo "   Repository: $REPO_URL"
echo ""

# Check GitHub repository status
echo "1️⃣ Checking GitHub repository..."
GITHUB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/Flickinny11/ai-cinema-123")

if [ "$GITHUB_STATUS" = "200" ]; then
    echo "✅ GitHub repository is accessible"
    
    # Get latest release info
    LATEST_RELEASE=$(curl -s "https://api.github.com/repos/Flickinny11/ai-cinema-123/releases/latest" | jq -r '.tag_name // "none"')
    RELEASE_DATE=$(curl -s "https://api.github.com/repos/Flickinny11/ai-cinema-123/releases/latest" | jq -r '.published_at // "unknown"')
    
    echo "   Latest Release: $LATEST_RELEASE"
    echo "   Release Date: $RELEASE_DATE"
else
    echo "❌ GitHub repository not accessible (HTTP $GITHUB_STATUS)"
fi

echo ""

# Check RunPod API with simple REST call
echo "2️⃣ Checking RunPod API connection..."

# Try to get user info with REST API
RUNPOD_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/runpod_response.json \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    "https://api.runpod.io/graphql" \
    -d '{"query": "query { myself { username } }"}')

HTTP_CODE="${RUNPOD_RESPONSE: -3}"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ RunPod API is accessible"
    USERNAME=$(cat /tmp/runpod_response.json | jq -r '.data.myself.username // "unknown"')
    echo "   Username: $USERNAME"
else
    echo "❌ RunPod API failed (HTTP $HTTP_CODE)"
    echo "   Response: $(cat /tmp/runpod_response.json 2>/dev/null || echo 'No response')"
fi

echo ""

# Check RunPod Hub directly
echo "3️⃣ Checking RunPod Hub..."
HUB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://runpod.io/console/hub")

if [ "$HUB_STATUS" = "200" ]; then
    echo "✅ RunPod Hub is accessible"
else
    echo "❌ RunPod Hub not accessible (HTTP $HUB_STATUS)"
fi

echo ""

# Try to search for templates
echo "4️⃣ Searching for Cinema AI templates..."

# Search query
SEARCH_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/search_response.json \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    "https://api.runpod.io/graphql" \
    -d '{"query": "query { searchTemplates(input: \"cinema\") { id name author { username } githubUrl } }"}')

SEARCH_HTTP_CODE="${SEARCH_RESPONSE: -3}"

if [ "$SEARCH_HTTP_CODE" = "200" ]; then
    echo "✅ Template search successful"
    TEMPLATE_COUNT=$(cat /tmp/search_response.json | jq '.data.searchTemplates | length' 2>/dev/null || echo "0")
    echo "   Found $TEMPLATE_COUNT templates matching 'cinema'"
    
    # Show matching templates
    cat /tmp/search_response.json | jq -r '.data.searchTemplates[]? | "   📋 \(.name) by \(.author.username // "unknown")"' 2>/dev/null
else
    echo "❌ Template search failed (HTTP $SEARCH_HTTP_CODE)"
fi

echo ""

# Summary
echo "============================================"
echo "📊 SUMMARY"
echo "============================================"

if [ "$GITHUB_STATUS" = "200" ] && [ "$HTTP_CODE" = "200" ]; then
    echo "✅ All systems operational"
    echo "🎯 Next steps:"
    echo "   1. Check RunPod Console: https://runpod.io/console"
    echo "   2. Look for ai-cinema-123 in Hub: https://runpod.io/console/hub"
    echo "   3. Create template if not found"
elif [ "$GITHUB_STATUS" = "200" ]; then
    echo "⚠️  GitHub OK, RunPod API issues"
    echo "🎯 Check API key and try again"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "⚠️  RunPod OK, GitHub issues"
    echo "🎯 Check repository accessibility"
else
    echo "❌ Multiple issues detected"
    echo "🎯 Check network connectivity and credentials"
fi

# Cleanup
rm -f /tmp/runpod_response.json /tmp/search_response.json

echo ""
echo "🔗 Useful Links:"
echo "   Repository: $REPO_URL"
echo "   RunPod Console: https://runpod.io/console"
echo "   RunPod Hub: https://runpod.io/console/hub"