# Quick Start: OBO Flow with Personal Azure Account

## TL;DR - Can I Do This?

**YES!** You can implement JWT On-Behalf-Of flow with a personal Microsoft account (outlook.com, gmail.com, etc.).

**Time**: ~1 hour
**Cost**: $0 (free tier)
**Difficulty**: Medium

---

## What You Need to Know

### Three Important Distinctions

1. **Your Personal Email** (e.g., john@outlook.com)
   - This is you, the account owner
   - Used to sign up for Azure

2. **Azure AD Tenant** (e.g., johndoe.onmicrosoft.com)
   - The directory where apps are registered
   - Automatically created when you sign up for Azure
   - You become the Global Administrator

3. **Azure Subscription**
   - Billing account (can be free)
   - Links your email to a tenant

### The Good News

✅ OBO flow works perfectly with personal Azure accounts
✅ Microsoft Entra ID Free is sufficient (included with subscription)
✅ You can stay within free tier ($0 cost)
✅ Your orchestrator code is already OBO-ready
✅ You're automatically admin (can grant all permissions yourself)

### The 2025 Update

⚠️ **Change**: Creating tenants now requires paid Azure subscription (not just free trial)

✅ **Workaround**: Your FIRST tenant is created automatically when you sign up
- This is all you need for the POC!

⚠️ **Change**: Microsoft 365 Developer Program restricted (no more free E5 tenants)

✅ **Workaround**: Standard Azure free account is sufficient

---

## Two Paths to Success

### Path 1: Test Without Azure AD (5 minutes) ⚡

**Best for**: Testing orchestration logic quickly

```bash
# In .env
REQUIRE_AUTH=false

# Test
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

**What works**: Agent selection, sub-agent calls, response aggregation
**What doesn't**: JWT validation, OBO tokens, real user identity

### Path 2: Full OBO Setup (1 hour) 🔐

**Best for**: Production-ready authentication

#### Step 1: Create Azure Account (10 min)

1. Go to https://azure.microsoft.com/free/
2. Click "Start free"
3. Sign in with personal email (or create Microsoft account)
4. Verify phone + add credit card (for ID verification only)
5. Complete signup

**You get:**
- ✅ Azure AD tenant (automatic)
- ✅ You're the Global Administrator
- ✅ $200 credit (30 days)
- ✅ Free services (12 months)
- ✅ Always-free tier (forever)

#### Step 2: Note Your Tenant Info (2 min)

1. Sign in to https://portal.azure.com
2. Go to "Microsoft Entra ID"
3. Note from Overview:
   ```
   Tenant ID: <copy-this-guid>
   Primary domain: <yoursomething>.onmicrosoft.com
   ```

#### Step 3: Create App Registrations (30 min)

Follow detailed guide: [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md)

**Quick summary:**
1. Create Orchestrator API app
2. Create Python Agent API app
3. Create .NET Agent API app
4. Configure App ID URIs and scopes
5. Add API permissions from Orchestrator → Agents
6. **Grant admin consent** (you can do this yourself!)

#### Step 4: Update Orchestrator Config (5 min)

Update `/orchestrator/.env`:

```bash
# Azure AD Configuration
AZURE_TENANT_ID=<your-tenant-guid>
AZURE_CLIENT_ID=<orchestrator-client-id>
AZURE_CLIENT_SECRET=<orchestrator-secret>

# JWT Configuration
JWT_ALGORITHM=RS256
JWT_AUDIENCE=api://<orchestrator-client-id>
JWT_ISSUER=https://login.microsoftonline.com/<your-tenant-id>/v2.0

# Sub-Agent Scopes
PYTHON_AGENT_SCOPES=["api://python-agent/access_as_user"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent/access_as_user"]

# Enable Authentication
REQUIRE_AUTH=true
```

#### Step 5: Get Test Token (10 min)

**Option A: Azure CLI (Easiest)**
```bash
az login
az account get-access-token --resource api://<orchestrator-client-id>
```

**Option B: MSAL Python**
```python
import msal

app = msal.PublicClientApplication(
    "<orchestrator-client-id>",
    authority="https://login.microsoftonline.com/<tenant-id>"
)

result = app.acquire_token_interactive(
    scopes=["api://<orchestrator-client-id>/access_as_user"]
)
print(result["access_token"])
```

#### Step 6: Test OBO Flow (5 min)

```bash
export TOKEN="<your-token>"

curl -X POST http://localhost:3000/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test OBO"}'
```

**Check logs for:**
```
INFO - Orchestrator received request from user: <Your Name>
INFO - Acquiring OBO token for scopes: ['api://python-agent/access_as_user']
INFO - OBO token acquired successfully
```

---

## Cost Breakdown

### What's Free Forever

| Item | Free Tier | Sufficient? |
|------|-----------|-------------|
| Microsoft Entra ID | Free tier included | ✅ YES |
| App Registrations | Unlimited | ✅ YES |
| Authentication | 50,000 MAU | ✅ YES for dev |
| OBO Token Exchange | Included | ✅ YES |

### What Costs Money

Only if you:
- Use paid Azure services (VMs, App Service premium, etc.)
- Exceed 50,000 monthly users
- Enable Premium P1/P2 features

**For OBO development: $0/month**

---

## Common Issues & Quick Fixes

### "Cannot create tenant" button disabled

✅ **Fix**: Use the tenant created automatically with your subscription (you only need one!)

### "AADSTS65001: User has not consented"

✅ **Fix**:
```
Azure Portal → Microsoft Entra ID → App registrations
→ Orchestrator → API permissions
→ "Grant admin consent for <tenant>" → Yes
```

### "Subscription not found"

✅ **Fix**: Sign up for Azure free account at https://azure.microsoft.com/free/

### OBO token acquisition fails

✅ **Fix**:
1. Verify orchestrator has API permissions for sub-agents
2. Check admin consent granted (green checkmarks)
3. Verify client secret is correct
4. Check scopes match App ID URIs exactly

---

## How to Check What You Have

### Do you have Azure subscription?

```bash
# Install Azure CLI
curl -L https://aka.ms/InstallAzureCli | bash

# Login
az login

# Check subscription
az account show
```

**Look for**:
- `"state": "Enabled"`
- `"tenantId": "<some-guid>"` (not 9188040d-6c67-4c5b-b112-36a304b66dad)

If tenant ID is `9188040d-6c67-4c5b-b112-36a304b66dad` → You have pure personal account, no subscription

### Can you access Azure Portal?

1. Go to https://portal.azure.com
2. Sign in
3. Navigate to "Microsoft Entra ID"

✅ If you see tenant info → You have a tenant
❌ If error or blocked → Need to create subscription

---

## Decision Tree

```
Do you have Azure subscription?
│
├─ YES → Go to Step 3 (Create app registrations)
│        Time: 30 min | Cost: $0
│
└─ NO → Do you want full OBO now?
    │
    ├─ YES → Create Azure free account
    │        → Then follow Step 3-6
    │        Time: 1 hour | Cost: $0
    │
    └─ NO → Use testing mode (REQUIRE_AUTH=false)
             → Implement OBO later
             Time: 5 min | Cost: $0
```

---

## What Makes Personal Azure Different from Enterprise?

### For OBO Flow: Almost Nothing!

| Feature | Personal | Enterprise | Winner |
|---------|----------|------------|--------|
| Can create apps? | ✅ Yes | ✅ Yes | Tie |
| OBO supported? | ✅ Yes | ✅ Yes | Tie |
| Can grant admin consent? | ✅ Yes (you're admin) | ⚠️ Need admin approval | Personal easier |
| Cost for OBO? | ✅ Free | ✅ Free | Tie |
| Control/flexibility? | ✅ Full control | ⚠️ IT policies | Personal better |
| Premium features? | ⚠️ Must buy | ✅ Often included | Enterprise better |

**For learning/POC: Personal account is actually BETTER**

---

## Next Steps

### Recommended Order

1. ✅ Read this Quick Start (you're here!)
2. ✅ Review [PERSONAL_AZURE_ACCOUNT_OBO_GUIDE.md](./PERSONAL_AZURE_ACCOUNT_OBO_GUIDE.md) for details
3. ✅ Choose your path:
   - **Quick test**: Keep REQUIRE_AUTH=false
   - **Full OBO**: Follow Path 2 above
4. ✅ Follow [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md) for step-by-step app registration
5. ✅ Test with real tokens
6. ✅ Celebrate working OBO flow! 🎉

### Resources

**Create Azure Account**: https://azure.microsoft.com/free/

**Azure Portal**: https://portal.azure.com

**Decode Tokens**: https://jwt.ms

**Your Guides**:
- [PERSONAL_AZURE_ACCOUNT_OBO_GUIDE.md](./PERSONAL_AZURE_ACCOUNT_OBO_GUIDE.md) - Complete reference
- [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md) - Step-by-step setup
- [JWT_OBO_IMPLEMENTATION_PLAN.md](./JWT_OBO_IMPLEMENTATION_PLAN.md) - Implementation details

---

## Summary

✅ **Yes**, you can use a personal Microsoft account
✅ **Yes**, it's free for development
✅ **Yes**, your code is ready
✅ **Yes**, it's production-capable

⏱️ **Time**: ~1 hour for full setup
💰 **Cost**: $0 if you stay in free tier
🎯 **Difficulty**: Medium (clear instructions provided)

**The only thing standing between you and working OBO flow is creating an Azure free account and following the setup guide.**

**Ready?** Go to https://azure.microsoft.com/free/ to start!
