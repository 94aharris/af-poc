# Azure AD Setup for JWT OBO Flow - Implementation Guide

This guide walks through the complete Azure AD configuration required to enable JWT On-Behalf-Of (OBO) authentication flow in the orchestrator POC.

## Overview

The OBO flow requires **3 Azure AD App Registrations**:

1. **Orchestrator API** - Receives user JWT, exchanges for OBO tokens
2. **Python Agent API** - Receives OBO token from orchestrator
3. **.NET Agent API** - Receives OBO token from orchestrator

## Architecture

```
User → Frontend (gets JWT for User)
         ↓ User JWT
      Orchestrator API (validates JWT)
         ↓ Exchange JWT for OBO token (calls Azure AD)
      Azure AD (validates orchestrator can act on behalf of user)
         ↓ Returns OBO token
      Orchestrator → Sub-Agent (Python or .NET)
         ↓ OBO token with user identity
      Sub-Agent validates and sees original user
```

## Prerequisites

- **Azure Subscription** with permission to create app registrations
- **Azure AD Tenant** (your organization's tenant)
- **Global Administrator** or **Application Administrator** role (for admin consent)

---

## Step 1: Register Orchestrator API

### 1.1 Create App Registration

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Enter details:
   - **Name**: `AgentFramework-Orchestrator-API`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave empty for now
4. Click **Register**

### 1.2 Configure App ID URI

1. In the orchestrator app, go to **Expose an API**
2. Click **Set** next to Application ID URI
3. Accept default: `api://{client-id}` or use custom: `api://agent-orchestrator`
4. Click **Save**

### 1.3 Add API Scopes

1. Still in **Expose an API**, click **Add a scope**
2. Enter scope details:
   - **Scope name**: `access_as_user`
   - **Who can consent**: `Admins and users`
   - **Admin consent display name**: `Access orchestrator on behalf of user`
   - **Admin consent description**: `Allow the application to access the orchestrator API on behalf of the signed-in user`
   - **User consent display name**: `Access orchestrator as you`
   - **User consent description**: `Allow the application to access the orchestrator API on your behalf`
   - **State**: `Enabled`
3. Click **Add scope**

### 1.4 Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Enter:
   - **Description**: `Orchestrator OBO Secret`
   - **Expires**: `24 months` (or your org policy)
4. Click **Add**
5. **COPY THE SECRET VALUE IMMEDIATELY** - you won't be able to see it again
6. Save this as `ORCHESTRATOR_CLIENT_SECRET`

### 1.5 Configure Authentication (Optional - for frontend)

If you'll have a frontend calling the orchestrator:

1. Go to **Authentication**
2. Click **Add a platform** → **Single-page application** (for React/Angular)
3. Add redirect URI: `http://localhost:3001` (for local testing)
4. Enable **Access tokens** and **ID tokens**
5. Click **Configure**

### 1.6 Record Values

Save these values:
```
ORCHESTRATOR_TENANT_ID=<your-tenant-id>
ORCHESTRATOR_CLIENT_ID=<orchestrator-app-client-id>
ORCHESTRATOR_CLIENT_SECRET=<secret-from-step-1.4>
ORCHESTRATOR_APP_ID_URI=api://<orchestrator-client-id>
```

---

## Step 2: Register Python Agent API

### 2.1 Create App Registration

1. **App registrations** → **New registration**
2. Enter:
   - **Name**: `AgentFramework-Python-Agent-API`
   - **Supported account types**: `Accounts in this organizational directory only`
3. Click **Register**

### 2.2 Configure App ID URI

1. **Expose an API** → **Set**
2. Use: `api://python-agent` or `api://{client-id}`
3. Click **Save**

### 2.3 Add API Scope

1. **Add a scope**:
   - **Scope name**: `access_as_user`
   - **Who can consent**: `Admins and users`
   - **Admin consent display name**: `Access Python agent on behalf of user`
   - **Admin consent description**: `Allow access to the Python agent API on behalf of the signed-in user`
   - **State**: `Enabled`
2. Click **Add scope**

### 2.4 Record Values

```
PYTHON_AGENT_CLIENT_ID=<python-agent-client-id>
PYTHON_AGENT_APP_ID_URI=api://python-agent
PYTHON_AGENT_SCOPE=api://python-agent/access_as_user
```

---

## Step 3: Register .NET Agent API

### 3.1 Create App Registration

1. **App registrations** → **New registration**
2. Enter:
   - **Name**: `AgentFramework-DotNet-Agent-API`
   - **Supported account types**: `Accounts in this organizational directory only`
3. Click **Register**

### 3.2 Configure App ID URI

1. **Expose an API** → **Set**
2. Use: `api://dotnet-agent` or `api://{client-id}`
3. Click **Save**

### 3.3 Add API Scope

1. **Add a scope**:
   - **Scope name**: `access_as_user`
   - **Who can consent**: `Admins and users`
   - **Admin consent display name**: `Access .NET agent on behalf of user`
   - **State**: `Enabled`
2. Click **Add scope**

### 3.4 Record Values

```
DOTNET_AGENT_CLIENT_ID=<dotnet-agent-client-id>
DOTNET_AGENT_APP_ID_URI=api://dotnet-agent
DOTNET_AGENT_SCOPE=api://dotnet-agent/access_as_user
```

---

## Step 4: Configure Orchestrator API Permissions (THE KEY STEP)

This is the **critical step** that enables OBO flow.

### 4.1 Add API Permissions for Python Agent

1. Go to **Orchestrator API** app registration
2. Click **API permissions**
3. Click **Add a permission**
4. Click **My APIs** tab
5. Select **AgentFramework-Python-Agent-API**
6. Check **access_as_user** permission
7. Click **Add permissions**

### 4.2 Add API Permissions for .NET Agent

1. Still in **API permissions**
2. Click **Add a permission**
3. **My APIs** → **AgentFramework-DotNet-Agent-API**
4. Check **access_as_user**
5. Click **Add permissions**

### 4.3 Grant Admin Consent

**CRITICAL**: Admin consent is required for OBO flow to work.

1. In **API permissions**, click **Grant admin consent for {tenant}**
2. Click **Yes** to confirm
3. Verify all permissions show green checkmarks under "Status"

Your permissions should look like:

| API / Permission name | Type | Admin consent required | Status |
|----------------------|------|------------------------|--------|
| AgentFramework-Python-Agent-API / access_as_user | Delegated | Yes | ✅ Granted for {tenant} |
| AgentFramework-DotNet-Agent-API / access_as_user | Delegated | Yes | ✅ Granted for {tenant} |

---

## Step 5: Configure Orchestrator Environment

Update `/orchestrator/.env`:

```bash
# Azure AD Configuration
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<orchestrator-client-id>
AZURE_CLIENT_SECRET=<orchestrator-client-secret>

# JWT Configuration
JWT_ALGORITHM=RS256
JWT_AUDIENCE=api://<orchestrator-client-id>
JWT_ISSUER=https://login.microsoftonline.com/<your-tenant-id>/v2.0

# Sub-Agent Endpoints
PYTHON_AGENT_URL=http://localhost:8000
DOTNET_AGENT_URL=http://localhost:5000

# OBO Scopes - MUST match the App ID URIs
PYTHON_AGENT_SCOPES=["api://python-agent/access_as_user"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent/access_as_user"]

# Enable Authentication
REQUIRE_AUTH=true
```

---

## Step 6: Testing the Configuration

### 6.1 Get a Test Token

You need a JWT token representing a user. Options:

**Option A: Use Postman**
1. Create a new request
2. Go to **Authorization** → **OAuth 2.0**
3. Configure:
   - **Grant Type**: `Authorization Code`
   - **Auth URL**: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize`
   - **Access Token URL**: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`
   - **Client ID**: `{orchestrator-client-id}`
   - **Scope**: `api://{orchestrator-client-id}/access_as_user`
4. Click **Get New Access Token**
5. Sign in with your Azure AD account
6. Copy the access token

**Option B: Use Azure CLI**
```bash
az login
az account get-access-token --resource api://<orchestrator-client-id>
```

**Option C: Use MSAL Python Script**
```python
import msal

tenant_id = "your-tenant-id"
client_id = "orchestrator-client-id"
scopes = ["api://orchestrator-client-id/access_as_user"]

app = msal.PublicClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

result = app.acquire_token_interactive(scopes=scopes)
print(result["access_token"])
```

### 6.2 Test JWT Validation

```bash
# Save token to variable
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Test orchestrator with token
curl -X POST http://localhost:3000/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test with real JWT"}'
```

### 6.3 Verify OBO Flow

Check orchestrator logs for:
```
INFO - Orchestrator received request from user: John Doe
INFO - Acquiring OBO token for scopes: ['api://python-agent/access_as_user']
INFO - OBO token acquired successfully
INFO - Calling python agent with OBO token
```

---

## Troubleshooting

### Error: "AADSTS65001: The user or administrator has not consented"

**Solution**: Go back to Step 4.3 and grant admin consent for orchestrator permissions.

### Error: "AADSTS50013: Assertion failed signature validation"

**Solution**:
- Verify `JWT_AUDIENCE` matches orchestrator's App ID URI exactly
- Verify `JWT_ISSUER` includes `/v2.0` at the end
- Check token was requested for the correct audience

### Error: "AADSTS70011: The provided value for the input parameter 'scope' is not valid"

**Solution**:
- Verify sub-agent App ID URIs match exactly in `.env`
- Ensure scopes include `/access_as_user` suffix
- Check for typos in scope names

### Error: "OBO token acquisition failed: unauthorized_client"

**Solution**:
- Verify orchestrator has API permissions for the sub-agent
- Ensure admin consent was granted (Step 4.3)
- Check client secret hasn't expired

### Token validation fails locally

**Solution**:
- Ensure `AZURE_TENANT_ID` is correct
- Verify `JWT_AUDIENCE` exactly matches the token's `aud` claim
- Check token hasn't expired (default 1 hour)

---

## Security Best Practices

1. **Never commit secrets** to git
   - Use environment variables or Azure Key Vault
   - Add `.env` to `.gitignore`

2. **Rotate secrets regularly**
   - Set expiration on client secrets
   - Update secrets before expiration

3. **Use least privilege**
   - Only grant necessary API permissions
   - Don't use `/.default` scope unless needed

4. **Enable logging**
   - Log all OBO token acquisitions (without exposing tokens)
   - Monitor for failed authentication attempts

5. **Use HTTPS in production**
   - Never send tokens over HTTP
   - Enforce HTTPS redirects

---

## Verification Checklist

Before proceeding, verify:

- [ ] 3 app registrations created (Orchestrator, Python Agent, .NET Agent)
- [ ] Each API has an App ID URI configured
- [ ] Each API exposes `access_as_user` scope
- [ ] Orchestrator has client secret created and saved
- [ ] Orchestrator has API permissions for both sub-agents
- [ ] Admin consent granted for all orchestrator permissions (green checkmarks)
- [ ] `.env` file updated with all values
- [ ] `REQUIRE_AUTH=true` in orchestrator `.env`
- [ ] Test token obtained successfully
- [ ] Token validation works in orchestrator

---

## What Happens Next

Once configured, the OBO flow works like this:

1. **User authenticates** to frontend → Gets JWT token for orchestrator
2. **Frontend calls orchestrator** with user's JWT in `Authorization` header
3. **Orchestrator validates JWT** using Azure AD's public keys
4. **Orchestrator extracts user identity** (oid, name, email from JWT claims)
5. **Orchestrator calls MSAL**: `acquire_token_on_behalf_of(user_jwt, sub_agent_scopes)`
6. **Azure AD validates**:
   - User's token is valid
   - Orchestrator has permission to act on behalf of user
   - Orchestrator has permission to access sub-agent
7. **Azure AD returns OBO token** with:
   - Same user identity (oid, name, etc.)
   - Audience = sub-agent API
   - Scopes = sub-agent permissions
8. **Orchestrator calls sub-agent** with OBO token
9. **Sub-agent validates OBO token** and sees original user's identity
10. **Sub-agent executes request** with user's permissions (RBAC enforced)

**Identity is preserved throughout the chain!** ✅

---

## Next Steps

After Azure AD is configured:

1. Test orchestrator JWT validation
2. Test OBO token acquisition
3. Add JWT validation to Python sub-agent
4. Add JWT validation to .NET sub-agent
5. Test end-to-end flow with real user tokens
6. Implement token caching (optional)
7. Add monitoring and logging

---

## Quick Reference

### Environment Variables Summary

```bash
# Orchestrator
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<orchestrator-client-id>
AZURE_CLIENT_SECRET=<orchestrator-secret>
JWT_AUDIENCE=api://<orchestrator-client-id>
JWT_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0
PYTHON_AGENT_SCOPES=["api://python-agent/access_as_user"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent/access_as_user"]
REQUIRE_AUTH=true
```

### Useful Azure CLI Commands

```bash
# List app registrations
az ad app list --display-name "AgentFramework"

# Get app details
az ad app show --id <app-id>

# List service principals
az ad sp list --display-name "AgentFramework"

# Check token
az account get-access-token --resource api://<app-id> | jq -r .accessToken | jwt decode -
```

### Token Decode (for debugging)

Visit https://jwt.ms and paste your token to see:
- `aud` (audience) - should match your API's App ID URI
- `iss` (issuer) - should be Azure AD
- `oid` (user object ID) - unique user identifier
- `scp` (scopes) - permissions granted
- `exp` (expiration) - when token expires
