#!/bin/bash
# Setup Azure App Registration for Payroll API with OBO Support
# This script creates and configures the Azure AD app registration for the payroll API
# to accept OBO (On-Behalf-Of) tokens from the orchestrator

set -e  # Exit on any error

echo "==================================================================="
echo "  Azure AD Setup for Payroll API (OBO Support)"
echo "==================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}ERROR: Azure CLI is not installed${NC}"
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
echo "Checking Azure CLI login status..."
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Please log in now...${NC}"
    az login
fi

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)
echo -e "${GREEN}✓ Logged in to Azure${NC}"
echo "  Tenant ID: $TENANT_ID"
echo ""

# ============================================
# Step 1: Create Payroll API App Registration
# ============================================
echo "Step 1: Creating Payroll API app registration..."

# Check if app already exists
EXISTING_APP_ID=$(az ad app list --display-name "af-poc-payroll-api" --query "[0].appId" -o tsv 2>/dev/null)

if [ ! -z "$EXISTING_APP_ID" ]; then
    echo -e "${YELLOW}⚠ App registration 'af-poc-payroll-api' already exists${NC}"
    echo "  App ID: $EXISTING_APP_ID"
    read -p "Do you want to update the existing app? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping app creation. Using existing app ID: $EXISTING_APP_ID"
        PAYROLL_API_APP_ID=$EXISTING_APP_ID
    else
        echo "Updating existing app registration..."
        PAYROLL_API_APP_ID=$EXISTING_APP_ID
    fi
else
    # Create new app registration
    echo "Creating new app registration 'af-poc-payroll-api'..."
    az ad app create \
      --display-name "af-poc-payroll-api" \
      --sign-in-audience AzureADMyOrg \
      --output none

    # Get the app ID
    PAYROLL_API_APP_ID=$(az ad app list --display-name "af-poc-payroll-api" --query "[0].appId" -o tsv)
    echo -e "${GREEN}✓ Created Payroll API app registration${NC}"
    echo "  App ID: $PAYROLL_API_APP_ID"
fi

# ============================================
# Step 2: Set Identifier URI
# ============================================
echo ""
echo "Step 2: Setting identifier URI..."

az ad app update \
  --id $PAYROLL_API_APP_ID \
  --identifier-uris "api://$PAYROLL_API_APP_ID"

echo -e "${GREEN}✓ Set identifier URI: api://$PAYROLL_API_APP_ID${NC}"

# ============================================
# Step 3: Expose API Scope
# ============================================
echo ""
echo "Step 3: Exposing API scope 'access_as_user'..."

# Generate a unique ID for the scope (or reuse existing)
EXISTING_SCOPE_ID=$(az ad app show --id $PAYROLL_API_APP_ID --query "api.oauth2PermissionScopes[?value=='access_as_user'].id" -o tsv 2>/dev/null)

if [ -z "$EXISTING_SCOPE_ID" ]; then
    PAYROLL_SCOPE_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
    echo "  Generated new scope ID: $PAYROLL_SCOPE_ID"
else
    PAYROLL_SCOPE_ID=$EXISTING_SCOPE_ID
    echo "  Using existing scope ID: $PAYROLL_SCOPE_ID"
fi

# Expose the API scope
az ad app update \
  --id $PAYROLL_API_APP_ID \
  --set api="{\"oauth2PermissionScopes\":[{
    \"adminConsentDescription\": \"Allow the orchestrator to access the payroll API on behalf of the signed-in user\",
    \"adminConsentDisplayName\": \"Access Payroll API as user\",
    \"id\": \"$PAYROLL_SCOPE_ID\",
    \"isEnabled\": true,
    \"type\": \"User\",
    \"userConsentDescription\": \"Allow access to payroll API on your behalf\",
    \"userConsentDisplayName\": \"Access Payroll API\",
    \"value\": \"access_as_user\"
  }]}"

echo -e "${GREEN}✓ Exposed API scope: api://$PAYROLL_API_APP_ID/access_as_user${NC}"

# ============================================
# Step 4: Create Service Principal
# ============================================
echo ""
echo "Step 4: Creating service principal..."

# Create service principal (ignore if already exists)
az ad sp create --id $PAYROLL_API_APP_ID 2>/dev/null || echo "  Service principal already exists"

echo -e "${GREEN}✓ Service principal created/verified${NC}"

# ============================================
# Step 5: Update Orchestrator Permissions
# ============================================
echo ""
echo "Step 5: Granting orchestrator permission to call payroll API..."

# Get orchestrator app ID
ORCHESTRATOR_APP_ID=$(az ad app list --display-name "af-poc-orchestrator" --query "[0].appId" -o tsv 2>/dev/null)

if [ -z "$ORCHESTRATOR_APP_ID" ]; then
    echo -e "${YELLOW}⚠ Orchestrator app registration not found${NC}"
    echo "  Please run the main setup script first to create the orchestrator app"
    echo "  Or manually grant the orchestrator permission to call this API"
else
    echo "  Found orchestrator app: $ORCHESTRATOR_APP_ID"

    # Create service principal for orchestrator if needed
    az ad sp create --id $ORCHESTRATOR_APP_ID 2>/dev/null || echo "  Orchestrator SP already exists"

    # Check if permission already exists
    EXISTING_PERMISSION=$(az ad app permission list --id $ORCHESTRATOR_APP_ID --query "[?resourceAppId=='$PAYROLL_API_APP_ID']" -o tsv 2>/dev/null)

    if [ -z "$EXISTING_PERMISSION" ]; then
        # Add the required API permission to the orchestrator
        echo "  Adding API permission to orchestrator..."
        az ad app permission add \
          --id $ORCHESTRATOR_APP_ID \
          --api $PAYROLL_API_APP_ID \
          --api-permissions $PAYROLL_SCOPE_ID=Scope

        echo "  Granting admin consent..."
        az ad app permission grant \
          --id $ORCHESTRATOR_APP_ID \
          --api $PAYROLL_API_APP_ID \
          --scope "access_as_user" 2>/dev/null || echo "  Consent may need to be granted manually in portal"

        echo -e "${GREEN}✓ Granted orchestrator permission to call payroll API${NC}"
    else
        echo -e "${YELLOW}⚠ Permission already exists${NC}"
    fi
fi

# ============================================
# Step 6: Export Configuration
# ============================================
echo ""
echo "==================================================================="
echo "  Configuration Summary"
echo "==================================================================="
echo ""
echo -e "${GREEN}Payroll API Configuration:${NC}"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_CLIENT_ID=$PAYROLL_API_APP_ID"
echo "AUDIENCE=api://$PAYROLL_API_APP_ID"
echo ""

# Create/update .env file for payroll API
ENV_FILE="./dotnet-payroll-api/.env"
echo "Creating/updating $ENV_FILE..."

cat > $ENV_FILE <<EOF
# Azure AD Configuration for Payroll API (Generated by setup script)
AZURE_TENANT_ID=$TENANT_ID
AZURE_CLIENT_ID=$PAYROLL_API_APP_ID
REQUIRE_AUTHENTICATION=false

# API Configuration
HTTP_PORT=5100
HTTPS_PORT=5101
EOF

echo -e "${GREEN}✓ Created $ENV_FILE${NC}"

# Update orchestrator configuration if it exists
ORCHESTRATOR_ENV="./orchestrator/.env"
if [ -f "$ORCHESTRATOR_ENV" ]; then
    echo ""
    echo "Updating orchestrator configuration with payroll API scopes..."

    # Check if PAYROLL_API_SCOPES already exists
    if grep -q "PAYROLL_API_SCOPES" "$ORCHESTRATOR_ENV"; then
        # Update existing line
        sed -i.bak "s|PAYROLL_API_SCOPES=.*|PAYROLL_API_SCOPES=[\\\"api://$PAYROLL_API_APP_ID/access_as_user\\\"]|" "$ORCHESTRATOR_ENV"
        rm "$ORCHESTRATOR_ENV.bak" 2>/dev/null || true
        echo -e "${GREEN}✓ Updated PAYROLL_API_SCOPES in orchestrator .env${NC}"
    else
        # Append new line
        echo "PAYROLL_API_SCOPES=[\"api://$PAYROLL_API_APP_ID/access_as_user\"]" >> "$ORCHESTRATOR_ENV"
        echo "PAYROLL_API_URL=http://localhost:5100" >> "$ORCHESTRATOR_ENV"
        echo -e "${GREEN}✓ Added payroll API configuration to orchestrator .env${NC}"
    fi
fi

# ============================================
# Final Instructions
# ============================================
echo ""
echo "==================================================================="
echo "  ✅ Setup Complete!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "1. Update dotnet-payroll-api/PayrollApi/appsettings.local.json with:"
echo "   - TenantId: $TENANT_ID"
echo "   - ClientId: $PAYROLL_API_APP_ID"
echo "   - Audience: api://$PAYROLL_API_APP_ID"
echo ""
echo "2. To enable authentication, set in appsettings.local.json:"
echo "   \"Auth\": { \"RequireAuthentication\": true }"
echo ""
echo "3. Ensure the orchestrator has PAYROLL_API_SCOPES configured:"
echo "   PAYROLL_API_SCOPES=[\"api://$PAYROLL_API_APP_ID/access_as_user\"]"
echo ""
echo "4. Start the payroll API:"
echo "   cd dotnet-payroll-api"
echo "   dotnet run --project PayrollApi"
echo ""
echo "5. Test the OBO flow:"
echo "   - The orchestrator should be able to call the payroll API on behalf of users"
echo "   - User identity will be preserved through the 'oid' claim"
echo ""
echo "For troubleshooting, see: dotnet-payroll-api/README.md"
echo ""
