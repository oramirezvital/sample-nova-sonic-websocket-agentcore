#!/bin/bash
# Build frontend with AgentCore Runtime ARN and Cognito config
# macOS/Linux version - auto-generated from build-frontend.ps1

set -e  # Exit on error

USER_POOL_ID="$1"
USER_POOL_CLIENT_ID="$2"
IDENTITY_POOL_ID="$3"
AGENT_RUNTIME_ARN="$4"
REGION="$5"
WS_DEBUG="${6:-false}"

if [ -z "$USER_POOL_ID" ] || [ -z "$USER_POOL_CLIENT_ID" ] || [ -z "$IDENTITY_POOL_ID" ] || [ -z "$AGENT_RUNTIME_ARN" ] || [ -z "$REGION" ]; then
    echo "Usage: $0 <USER_POOL_ID> <USER_POOL_CLIENT_ID> <IDENTITY_POOL_ID> <AGENT_RUNTIME_ARN> <REGION> [debug]"
    exit 1
fi

echo "Building frontend with:"
echo "  User Pool ID: $USER_POOL_ID"
echo "  User Pool Client ID: $USER_POOL_CLIENT_ID"
echo "  Identity Pool ID: $IDENTITY_POOL_ID"
echo "  Agent Runtime ARN: $AGENT_RUNTIME_ARN"
echo "  Region: $REGION"

# Create production environment file (overrides .env.local)
pushd frontend > /dev/null

# Remove local development environment file if it exists
if [ -f ".env.local" ]; then
    echo "Removing local development environment file..."
    rm .env.local
fi

# Create production environment file
cat > .env.production.local << EOF
VITE_USER_POOL_ID=$USER_POOL_ID
VITE_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
VITE_IDENTITY_POOL_ID=$IDENTITY_POOL_ID
VITE_AGENT_RUNTIME_ARN=$AGENT_RUNTIME_ARN
VITE_REGION=$REGION
VITE_LOCAL_DEV=false
VITE_WS_DEBUG=$WS_DEBUG
EOF

echo "Created production environment configuration"

# Build frontend
npm run build

popd > /dev/null

echo "Frontend build complete"
