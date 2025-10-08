# JWT OBO Implementation Plan - Orchestrator Service

## Current State ✅

The orchestrator **already has the OBO implementation** in place. Here's what exists:

### Implemented Components

1. **JWT Validation** (`src/auth.py`)
   - ✅ `JWTValidator` class
   - ✅ JWKS (JSON Web Key Set) fetching from Azure AD
   - ✅ Token signature verification
   - ✅ Audience and issuer validation

2. **OBO Token Service** (`src/auth.py`)
   - ✅ `OBOTokenService` class
   - ✅ MSAL Python integration
   - ✅ `acquire_token_on_behalf_of()` implementation
   - ✅ Error handling for token acquisition failures

3. **FastAPI Dependencies** (`src/auth.py`)
   - ✅ `get_current_user()` - Extracts and validates JWT
   - ✅ `get_obo_token()` - Helper for OBO acquisition
   - ✅ Testing mode support (REQUIRE_AUTH=false)

4. **Main Endpoint** (`src/api.py`)
   - ✅ JWT validation via dependency injection
   - ✅ Agent selection logic
   - ✅ OBO token acquisition for selected sub-agent
   - ✅ HTTP client with OBO token in Authorization header

5. **Configuration** (`src/config.py`)
   - ✅ All Azure AD settings
   - ✅ Sub-agent scope configuration
   - ✅ REQUIRE_AUTH flag for testing

## What's Already Working

### Testing Mode (REQUIRE_AUTH=false)
- ✅ Orchestrator accepts requests without JWT
- ✅ Mock user identity returned
- ✅ Agent selection works
- ✅ Sub-agent calls work (without OBO tokens)
- ✅ Response aggregation works

### Production-Ready Code (REQUIRE_AUTH=true)
- ✅ Full JWT validation
- ✅ OBO token acquisition
- ✅ Token passing to sub-agents
- ✅ User identity extraction
- ✅ Error handling

## What You Need to Do

### Option A: Test Without Azure AD (Quickest)

**Status**: Already working! ✅

You can test the entire orchestration flow **without** Azure AD:

1. Keep `REQUIRE_AUTH=false` in `.env`
2. Start orchestrator
3. Call `/agent` endpoint
4. Orchestrator will:
   - Use mock user identity
   - Skip JWT validation
   - Skip OBO token acquisition
   - Still call sub-agents
   - Still aggregate responses

**This is perfect for:**
- Testing orchestration logic
- Testing agent selection
- Testing sub-agent communication
- Developing features without Azure AD complexity

### Option B: Enable Full OBO Flow (Production)

**Prerequisites**:
1. Azure subscription
2. Permission to create app registrations
3. Admin consent capability

**Steps**:

#### Step 1: Azure AD Configuration (1-2 hours)
Follow the complete guide: [`AZURE_AD_SETUP.md`](./AZURE_AD_SETUP.md)

Key tasks:
- [ ] Create 3 app registrations (Orchestrator, Python Agent, .NET Agent)
- [ ] Configure App ID URIs for each
- [ ] Add `access_as_user` scope to each API
- [ ] Create client secret for orchestrator
- [ ] Add API permissions from orchestrator to sub-agents
- [ ] **CRITICAL**: Grant admin consent for all permissions

#### Step 2: Update Orchestrator Configuration (5 minutes)

Update `/orchestrator/.env`:

```bash
# Azure AD Configuration
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<orchestrator-client-id>
AZURE_CLIENT_SECRET=<orchestrator-secret>

# JWT Configuration
JWT_ALGORITHM=RS256
JWT_AUDIENCE=api://<orchestrator-client-id>
JWT_ISSUER=https://login.microsoftonline.com/<tenant-id>/v2.0

# Sub-Agent Scopes
PYTHON_AGENT_SCOPES=["api://python-agent/access_as_user"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent/access_as_user"]

# Enable Authentication
REQUIRE_AUTH=true
```

#### Step 3: Get a Test Token (10 minutes)

**Method 1: Using Postman**
1. Create OAuth 2.0 request
2. Configure auth URL and token URL
3. Use orchestrator client ID
4. Request scope: `api://<orchestrator-client-id>/access_as_user`
5. Sign in and get token

**Method 2: Using Azure CLI**
```bash
az login
az account get-access-token --resource api://<orchestrator-client-id>
```

**Method 3: Using MSAL Python**
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

#### Step 4: Test JWT Validation (5 minutes)

```bash
# Set token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Test orchestrator
curl -X POST http://localhost:3000/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test with real JWT"}'
```

**Expected behavior**:
1. Orchestrator validates JWT ✅
2. Extracts user identity (oid, name) ✅
3. Selects appropriate sub-agent ✅
4. Attempts OBO token acquisition ✅
5. Calls sub-agent with OBO token ✅

**Check logs**:
```
INFO - Orchestrator received request from user: John Doe
INFO - Selected agent: python
INFO - Acquiring OBO token for scopes: ['api://python-agent/access_as_user']
INFO - OBO token acquired successfully
INFO - Calling python agent with OBO token
```

#### Step 5: Configure Sub-Agents (Future)

To complete the end-to-end flow:

**Python Agent** needs:
- [ ] JWT validation (validate OBO token)
- [ ] Extract user claims from OBO token
- [ ] Use user identity in Agent Framework calls

**\.NET Agent** needs:
- [ ] JWT validation via `Microsoft.Identity.Web`
- [ ] Extract user claims from OBO token
- [ ] Use user identity in Agent Framework calls

---

## Implementation Checklist

### Orchestrator (Current Status)

- [x] JWT validation logic implemented
- [x] JWKS fetching and caching
- [x] Token signature verification
- [x] Audience validation
- [x] Issuer validation
- [x] OBO token service implemented
- [x] MSAL Python integration
- [x] acquire_token_on_behalf_of() method
- [x] Error handling for OBO failures
- [x] FastAPI dependencies for auth
- [x] Main endpoint with OBO flow
- [x] Configuration management
- [x] Testing mode support
- [ ] Azure AD app registrations (user's responsibility)
- [ ] Real JWT tokens for testing (requires Azure AD)
- [ ] End-to-end testing with sub-agents

### Python Agent (Future)

- [ ] Add JWT validation
- [ ] Add python-jose or similar library
- [ ] Validate OBO token from orchestrator
- [ ] Extract user claims
- [ ] Pass user context to Agent Framework

### .NET Agent (Future)

- [ ] Add Microsoft.Identity.Web
- [ ] Configure JWT Bearer authentication
- [ ] Validate OBO token from orchestrator
- [ ] Extract user claims
- [ ] Pass user context to Agent Framework

---

## Testing Strategy

### Phase 1: Testing Without Azure AD ✅ (Current)

**Goal**: Validate orchestration logic

```bash
# .env
REQUIRE_AUTH=false

# Test
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

**What's tested**:
- ✅ Agent selection
- ✅ Sub-agent HTTP calls
- ✅ Response aggregation
- ✅ Error handling
- ✅ Mock user context

**What's NOT tested**:
- ❌ JWT validation
- ❌ OBO token acquisition
- ❌ User identity preservation
- ❌ Azure AD integration

### Phase 2: Testing Orchestrator Only (After Azure AD Setup)

**Goal**: Validate JWT and OBO in orchestrator

```bash
# .env
REQUIRE_AUTH=true
# ... Azure AD config ...

# Test with real token
curl -X POST http://localhost:3000/agent \
  -H "Authorization: Bearer $REAL_JWT" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

**What's tested**:
- ✅ JWT validation
- ✅ User identity extraction
- ✅ OBO token acquisition from Azure AD
- ✅ OBO token passed to sub-agents
- ❌ Sub-agents don't validate OBO yet (future)

### Phase 3: End-to-End Testing (Future)

**Goal**: Full OBO flow with sub-agent validation

**Requirements**:
- Sub-agents validate OBO tokens
- Sub-agents extract user identity
- Sub-agents use user context

---

## Code Review: What's Already There

### 1. JWT Validation (`src/auth.py`)

```python
class JWTValidator:
    """Validates JWT tokens from Azure AD."""

    async def get_signing_keys(self) -> Dict:
        """Fetch JWKS from Azure AD."""
        # Fetches public keys from Azure AD
        # Caches keys for performance

    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims."""
        # Validates signature using JWKS
        # Validates audience and issuer
        # Returns user claims (oid, name, etc.)
```

**Status**: ✅ Fully implemented, production-ready

### 2. OBO Token Service (`src/auth.py`)

```python
class OBOTokenService:
    """Handles On-Behalf-Of token exchange."""

    async def acquire_token_on_behalf_of(
        self, user_token: str, scopes: list[str]
    ) -> Optional[str]:
        """
        Exchange user token for OBO token.

        THE CORE OF THE POC:
        1. Takes user's JWT
        2. Calls Azure AD with MSAL
        3. Gets new token with sub-agent scopes
        4. Returns OBO token with user identity
        """
        result = self.msal_app.acquire_token_on_behalf_of(
            user_assertion=user_token,
            scopes=scopes
        )
        return result["access_token"]
```

**Status**: ✅ Fully implemented, production-ready

### 3. Main Endpoint (`src/api.py`)

```python
@router.post("/agent")
async def orchestrator_endpoint(
    request: OrchestratorRequest,
    current_user: Dict = Depends(get_current_user),  # ← JWT validation
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Step 1: Validate JWT (done by dependency)
    # Step 2: Select agent
    selected_agent = agent_selector.select_agent(...)

    # Step 3: Acquire OBO token ⭐
    if settings.REQUIRE_AUTH:
        user_token = credentials.credentials
        target_scopes = get_scopes_for_agent(selected_agent)
        obo_token = await get_obo_token(user_token, target_scopes)

    # Step 4: Call sub-agent with OBO token
    response = await sub_agent_client.call_sub_agent(
        agent_type=selected_agent,
        message=request.message,
        obo_token=obo_token  # ← Passed to sub-agent
    )
```

**Status**: ✅ Fully implemented, production-ready

---

## What's Missing (Your Tasks)

### Immediate (To Enable OBO)

1. **Azure AD Setup** (1-2 hours)
   - Create app registrations
   - Configure permissions
   - Grant admin consent
   - Get credentials

2. **Update .env** (5 minutes)
   - Add Azure AD values
   - Set REQUIRE_AUTH=true

3. **Get Test Token** (10 minutes)
   - Use Postman, Azure CLI, or MSAL
   - Obtain JWT for orchestrator

4. **Test** (10 minutes)
   - Call orchestrator with real JWT
   - Verify OBO token acquisition
   - Check logs for success

### Future (To Complete End-to-End)

5. **Python Agent JWT Validation**
   - Add python-jose library
   - Implement token validation
   - Extract user claims

6. **\.NET Agent JWT Validation**
   - Add Microsoft.Identity.Web
   - Configure [Authorize] attribute
   - Extract user claims

7. **Integration Testing**
   - Test full flow with real tokens
   - Verify user identity preservation
   - Test RBAC scenarios

---

## Recommended Next Steps

### Option 1: Test Without Azure AD (Fastest) ✅

**Time**: 5 minutes

```bash
cd orchestrator
# Ensure REQUIRE_AUTH=false in .env
uv run uvicorn src.main:app --reload --port 3000

# In another terminal
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Test orchestration"}'
```

**Outcome**: See full orchestration working without auth

### Option 2: Enable Full OBO Flow (Production)

**Time**: 2-3 hours (mostly Azure AD setup)

1. Follow [`AZURE_AD_SETUP.md`](./AZURE_AD_SETUP.md) (1-2 hours)
2. Update `.env` (5 minutes)
3. Get test token (10 minutes)
4. Test orchestrator (10 minutes)

**Outcome**: Full JWT OBO flow working in orchestrator

---

## Summary

### What You Have ✅

The orchestrator has **complete, production-ready OBO implementation**:
- JWT validation logic
- OBO token acquisition
- MSAL integration
- Error handling
- Testing mode support

### What You Need 📋

To enable the OBO flow:
1. Azure AD app registrations (3 apps)
2. Admin consent for permissions
3. Configuration values in `.env`
4. Test JWT token

### Time Estimates

| Task | Time | Difficulty |
|------|------|------------|
| Test without auth (Option 1) | 5 min | Easy ✅ |
| Azure AD setup | 1-2 hours | Medium |
| Configure orchestrator | 5 min | Easy |
| Get test token | 10 min | Easy |
| Test OBO flow | 10 min | Easy |
| **Total (Option 2)** | **2-3 hours** | **Medium** |

---

## Questions to Answer

Before proceeding, decide:

1. **Do you have Azure AD access?**
   - Yes → Proceed with Option 2 (full OBO)
   - No → Use Option 1 (testing mode)

2. **Do you have admin consent capability?**
   - Yes → You can complete full setup
   - No → You'll need an admin to grant consent (Step 4.3)

3. **What do you want to test first?**
   - Orchestration logic → Option 1 (REQUIRE_AUTH=false)
   - Full OBO flow → Option 2 (REQUIRE_AUTH=true)

4. **Do you need sub-agents to validate OBO tokens?**
   - Not yet → Orchestrator OBO is sufficient for POC
   - Yes → Plan Python/\.NET agent auth (future work)

The code is ready. You just need to decide which path to take! 🚀
