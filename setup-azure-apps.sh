#!/bin/bash

# Azure AD App Registration Setup Script
# This script creates all required Azure AD app registrations for the af-poc project
# Based on AUTH_PLAN.md

set -e

echo "================================"
echo "Azure AD App Registration Setup"
echo "================================"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   macOS: brew install azure-cli"
    echo "   Other: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
fi

echo "✅ Azure CLI detected and logged in"
echo ""

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "📋 Tenant ID: $TENANT_ID"
echo ""

echo "================================"
echo "Creating App Registrations"
echo "================================"
echo ""

# ===== FRONTEND APP =====
echo "🔨 Creating Frontend App (af-poc-frontend)..."
FRONTEND_APP_ID=$(az ad app list --display-name "af-poc-frontend" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$FRONTEND_APP_ID" ]; then
    echo "   ⚠️  Frontend app already exists: $FRONTEND_APP_ID"
else
    az ad app create --display-name "af-poc-frontend" --sign-in-audience AzureADMyOrg > /dev/null
    FRONTEND_APP_ID=$(az ad app list --display-name "af-poc-frontend" --query "[0].appId" -o tsv)
    echo "   ✅ Created: $FRONTEND_APP_ID"

    # Configure as SPA
    az ad app update --id $FRONTEND_APP_ID \
        --set spa="{\"redirectUris\":[\"http://localhost:3000\",\"http://localhost:3000/redirect\"]}" > /dev/null

    # Enable token issuance
    az ad app update --id $FRONTEND_APP_ID \
        --set web="{\"implicitGrantSettings\":{\"enableIdTokenIssuance\":true,\"enableAccessTokenIssuance\":true}}" > /dev/null

    echo "   ✅ Configured SPA redirect URIs"
fi
echo ""

# ===== ORCHESTRATOR APP =====
echo "🔨 Creating Orchestrator App (af-poc-orchestrator)..."
ORCHESTRATOR_APP_ID=$(az ad app list --display-name "af-poc-orchestrator" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$ORCHESTRATOR_APP_ID" ]; then
    echo "   ⚠️  Orchestrator app already exists: $ORCHESTRATOR_APP_ID"
else
    az ad app create --display-name "af-poc-orchestrator" --sign-in-audience AzureADMyOrg > /dev/null
    ORCHESTRATOR_APP_ID=$(az ad app list --display-name "af-poc-orchestrator" --query "[0].appId" -o tsv)
    echo "   ✅ Created: $ORCHESTRATOR_APP_ID"

    # Set identifier URI
    az ad app update --id $ORCHESTRATOR_APP_ID --identifier-uris "api://$ORCHESTRATOR_APP_ID" > /dev/null
    echo "   ✅ Set identifier URI: api://$ORCHESTRATOR_APP_ID"

    # Create client secret
    ORCHESTRATOR_SECRET=$(az ad app credential reset --id $ORCHESTRATOR_APP_ID --query password -o tsv)
    echo "   ✅ Created client secret: $ORCHESTRATOR_SECRET"
    echo "   ⚠️  SAVE THIS SECRET - you cannot retrieve it later!"

    # Generate scope ID
    ORCHESTRATOR_SCOPE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

    # Expose API scope
    az ad app update --id $ORCHESTRATOR_APP_ID \
        --set api="{\"oauth2PermissionScopes\":[{
            \"adminConsentDescription\": \"Allow the application to access the orchestrator on behalf of the signed-in user\",
            \"adminConsentDisplayName\": \"Access orchestrator as user\",
            \"id\": \"$ORCHESTRATOR_SCOPE_ID\",
            \"isEnabled\": true,
            \"type\": \"User\",
            \"userConsentDescription\": \"Allow the application to access the orchestrator on your behalf\",
            \"userConsentDisplayName\": \"Access orchestrator\",
            \"value\": \"access_as_user\"
        }]}" > /dev/null

    echo "   ✅ Exposed API scope: access_as_user"
fi
echo ""

# ===== PYTHON AGENT APP =====
echo "🔨 Creating Python Agent App (af-poc-python-agent)..."
PYTHON_AGENT_APP_ID=$(az ad app list --display-name "af-poc-python-agent" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$PYTHON_AGENT_APP_ID" ]; then
    echo "   ⚠️  Python agent app already exists: $PYTHON_AGENT_APP_ID"
else
    az ad app create --display-name "af-poc-python-agent" --sign-in-audience AzureADMyOrg > /dev/null
    PYTHON_AGENT_APP_ID=$(az ad app list --display-name "af-poc-python-agent" --query "[0].appId" -o tsv)
    echo "   ✅ Created: $PYTHON_AGENT_APP_ID"

    # Set identifier URI
    az ad app update --id $PYTHON_AGENT_APP_ID --identifier-uris "api://$PYTHON_AGENT_APP_ID" > /dev/null

    # Generate scope ID
    PYTHON_SCOPE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

    # Expose API scope
    az ad app update --id $PYTHON_AGENT_APP_ID \
        --set api="{\"oauth2PermissionScopes\":[{
            \"adminConsentDescription\": \"Allow the orchestrator to access the Python agent on behalf of the signed-in user\",
            \"adminConsentDisplayName\": \"Access Python agent as user\",
            \"id\": \"$PYTHON_SCOPE_ID\",
            \"isEnabled\": true,
            \"type\": \"User\",
            \"userConsentDescription\": \"Allow access to Python agent on your behalf\",
            \"userConsentDisplayName\": \"Access Python agent\",
            \"value\": \"access_as_user\"
        }]}" > /dev/null

    echo "   ✅ Exposed API scope: access_as_user"
fi
echo ""

# ===== .NET AGENT APP =====
echo "🔨 Creating .NET Agent App (af-poc-dotnet-agent)..."
DOTNET_AGENT_APP_ID=$(az ad app list --display-name "af-poc-dotnet-agent" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$DOTNET_AGENT_APP_ID" ]; then
    echo "   ⚠️  .NET agent app already exists: $DOTNET_AGENT_APP_ID"
else
    az ad app create --display-name "af-poc-dotnet-agent" --sign-in-audience AzureADMyOrg > /dev/null
    DOTNET_AGENT_APP_ID=$(az ad app list --display-name "af-poc-dotnet-agent" --query "[0].appId" -o tsv)
    echo "   ✅ Created: $DOTNET_AGENT_APP_ID"

    # Set identifier URI
    az ad app update --id $DOTNET_AGENT_APP_ID --identifier-uris "api://$DOTNET_AGENT_APP_ID" > /dev/null

    # Generate scope ID
    DOTNET_SCOPE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')

    # Expose API scope
    az ad app update --id $DOTNET_AGENT_APP_ID \
        --set api="{\"oauth2PermissionScopes\":[{
            \"adminConsentDescription\": \"Allow the orchestrator to access the .NET agent on behalf of the signed-in user\",
            \"adminConsentDisplayName\": \"Access .NET agent as user\",
            \"id\": \"$DOTNET_SCOPE_ID\",
            \"isEnabled\": true,
            \"type\": \"User\",
            \"userConsentDescription\": \"Allow access to .NET agent on your behalf\",
            \"userConsentDisplayName\": \"Access .NET agent\",
            \"value\": \"access_as_user\"
        }]}" > /dev/null

    echo "   ✅ Exposed API scope: access_as_user"
fi
echo ""

echo "================================"
echo "Configuring API Permissions"
echo "================================"
echo ""

# Create service principals
echo "🔨 Creating service principals..."
az ad sp create --id $FRONTEND_APP_ID 2>/dev/null || echo "   Frontend SP already exists"
az ad sp create --id $ORCHESTRATOR_APP_ID 2>/dev/null || echo "   Orchestrator SP already exists"
az ad sp create --id $PYTHON_AGENT_APP_ID 2>/dev/null || echo "   Python Agent SP already exists"
az ad sp create --id $DOTNET_AGENT_APP_ID 2>/dev/null || echo "   .NET Agent SP already exists"
echo "   ✅ Service principals ready"
echo ""

# Grant Frontend → Orchestrator permission
echo "🔨 Granting Frontend → Orchestrator permissions..."
ORCHESTRATOR_SCOPE_ID=$(az ad app show --id $ORCHESTRATOR_APP_ID --query "api.oauth2PermissionScopes[?value=='access_as_user'].id" -o tsv)

# Check if permission already exists
EXISTING_PERM=$(az ad app permission list --id $FRONTEND_APP_ID --query "[?resourceAppId=='$ORCHESTRATOR_APP_ID']" -o tsv 2>/dev/null || echo "")

if [ -z "$EXISTING_PERM" ]; then
    az ad app permission add --id $FRONTEND_APP_ID --api $ORCHESTRATOR_APP_ID --api-permissions $ORCHESTRATOR_SCOPE_ID=Scope > /dev/null
    echo "   ✅ Added API permission"
else
    echo "   ⚠️  Permission already exists"
fi
echo ""

# Grant Orchestrator → Python Agent permission
echo "🔨 Granting Orchestrator → Python Agent permissions..."
PYTHON_SCOPE_ID=$(az ad app show --id $PYTHON_AGENT_APP_ID --query "api.oauth2PermissionScopes[?value=='access_as_user'].id" -o tsv)

EXISTING_PERM=$(az ad app permission list --id $ORCHESTRATOR_APP_ID --query "[?resourceAppId=='$PYTHON_AGENT_APP_ID']" -o tsv 2>/dev/null || echo "")

if [ -z "$EXISTING_PERM" ]; then
    az ad app permission add --id $ORCHESTRATOR_APP_ID --api $PYTHON_AGENT_APP_ID --api-permissions $PYTHON_SCOPE_ID=Scope > /dev/null
    echo "   ✅ Added API permission"
else
    echo "   ⚠️  Permission already exists"
fi
echo ""

# Grant Orchestrator → .NET Agent permission
echo "🔨 Granting Orchestrator → .NET Agent permissions..."
DOTNET_SCOPE_ID=$(az ad app show --id $DOTNET_AGENT_APP_ID --query "api.oauth2PermissionScopes[?value=='access_as_user'].id" -o tsv)

EXISTING_PERM=$(az ad app permission list --id $ORCHESTRATOR_APP_ID --query "[?resourceAppId=='$DOTNET_AGENT_APP_ID']" -o tsv 2>/dev/null || echo "")

if [ -z "$EXISTING_PERM" ]; then
    az ad app permission add --id $ORCHESTRATOR_APP_ID --api $DOTNET_AGENT_APP_ID --api-permissions $DOTNET_SCOPE_ID=Scope > /dev/null
    echo "   ✅ Added API permission"
else
    echo "   ⚠️  Permission already exists"
fi
echo ""

echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Run the following command to get your configuration values:"
echo "   ./get-azure-config.sh"
echo ""
echo "2. Update your .env files with the values from step 1"
echo ""
echo "3. MANUAL STEPS (Azure Portal):"
echo "   a. Pre-authorize frontend app for orchestrator:"
echo "      - Go to af-poc-orchestrator → Expose an API"
echo "      - Add client application: $FRONTEND_APP_ID"
echo "      - Check 'access_as_user' scope"
echo ""
echo "   b. Configure token version (v2.0):"
echo "      - For each app, go to Manifest"
echo "      - Set 'accessTokenAcceptedVersion': 2"
echo ""
echo "   c. Grant admin consent:"
echo "      - af-poc-frontend → API permissions → Grant admin consent"
echo "      - af-poc-orchestrator → API permissions → Grant admin consent"
echo ""
echo "4. Start your services and test authentication!"
echo ""
