# Complete Guide: JWT On-Behalf-Of Flow with Personal Azure Accounts

## Executive Summary

**Can you implement OBO flow with a personal Microsoft account?**

**YES - with important caveats**. You CAN implement JWT On-Behalf-Of flow with a personal Microsoft account, but you need to understand the distinction between:
1. **Personal Microsoft Account (MSA)** - your outlook.com, hotmail.com, live.com email
2. **Azure AD Tenant** - the directory where you register applications
3. **Azure Subscription** - the billing account (can be free)

**The Good News**:
- OBO flow now supports personal Microsoft accounts (MSA) as users
- You can create an Azure AD tenant with a personal email
- Azure offers free tiers for development/testing
- Your existing orchestrator code is ready for OBO

**The Challenge**:
- As of 2025, creating new Azure AD tenants requires a paid subscription (not just free trial)
- Microsoft 365 Developer Program (previously free) now requires Visual Studio Enterprise or partner status
- You'll need to sign up for a pay-as-you-go Azure account (but stay within free tier limits)

---

## Understanding Account Types

### 1. Personal Microsoft Account (MSA)

**What it is:**
- Email addresses like: `user@outlook.com`, `user@hotmail.com`, `user@live.com`
- Created by you for consumer Microsoft services (Xbox, OneDrive, Skype, etc.)
- Stored in Microsoft's consumer identity system
- Tenant ID is ALWAYS: `9188040d-6c67-4c5b-b112-36a304b66dad`

**What you CAN do with it:**
- Sign up for Azure services
- Create Azure subscriptions
- Become owner of an Azure AD tenant
- Use it as an identity in apps that support "Personal Microsoft accounts"

**What you CANNOT do with it:**
- Directly register apps without first creating a tenant
- Get free developer tenants (Microsoft 365 Dev Program changed in 2024)

### 2. Azure AD / Microsoft Entra ID Tenant

**What it is:**
- A dedicated directory instance
- Manages users, groups, and application registrations
- Has its own unique tenant ID (GUID)
- Required for app registrations

**How you get one:**
- Automatically created when you sign up for Azure subscription
- Can create additional tenants (requires paid subscription as of 2025)
- Each tenant has a default domain: `yourname.onmicrosoft.com`

**Free features included:**
- Microsoft Entra ID Free tier (no cost)
- App registrations (unlimited for free tier)
- User authentication
- API permissions and consent
- Everything needed for OBO flow

### 3. Azure Subscription

**What it is:**
- Billing account for Azure services
- Linked to an Azure AD tenant
- Can be owned by a personal Microsoft account

**Types:**
- **Free Account**: $200 credit for 30 days + always-free services
- **Pay-as-you-go**: Only pay for what you use (can stay free)
- **Student**: Free credit if you're a student
- **Visual Studio Subscription**: Includes monthly credits

---

## Can You Use OBO Flow with Personal Accounts?

### Answer: YES (with clarification)

The On-Behalf-Of flow works in two scenarios:

#### Scenario A: Personal Account as the App Owner (YOU)

```
YOU (personal email: john@outlook.com)
  ↓ Create Azure subscription (free or paid)
  ↓ Get Azure AD Tenant automatically
  ↓ Register 3 apps (Orchestrator, Python Agent, .NET Agent)
  ↓ Configure OBO flow
  ↓ Test with organizational users OR personal users
```

**This works!** Your personal email is just the owner/admin of the tenant.

#### Scenario B: Personal Account as the End User

```
End User (personal email: jane@gmail.com)
  ↓ Signs into your app
  ↓ Gets JWT token
  ↓ Your orchestrator receives JWT
  ↓ OBO flow exchanges token
```

**This works!** You just need to configure your app registration to support "Personal Microsoft accounts" in the "Supported account types" setting.

### What the Documentation Says

From Microsoft's OAuth 2.0 OBO flow documentation:
- "OBO flow now supports personal Microsoft accounts (MSA)"
- Previously, OBO didn't work for MSA - this was a limitation that has been lifted
- The flow works for both work/school accounts AND personal accounts

---

## Current Limitations (2025 Update)

### 1. Tenant Creation Requires Paid Subscription

**The Change:**
As of 2025, Microsoft disallows creating new Entra ID tenants with free trial accounts. You need a paid subscription.

**Workarounds:**
- Sign up for pay-as-you-go (free tier available, no charges if you stay within limits)
- Use your first tenant created automatically when you sign up for Azure
- External tenant 30-day trial (doesn't require subscription)

### 2. Microsoft 365 Developer Program Restricted

**The Change:**
After security incidents in early 2024, Microsoft restricted free developer tenants to:
- Visual Studio Enterprise subscribers
- Microsoft AI Cloud Partner Program members

**Impact:**
You can no longer get a free tenant with 25 E5 licenses using just a personal account.

### 3. Admin Consent Required

**The Requirement:**
OBO flow requires admin consent for delegated permissions.

**Who can grant it:**
- You (as Global Administrator of your own tenant)
- An admin in organizational tenants

**This is fine for personal Azure accounts** because you're automatically the Global Administrator of your own tenant.

---

## How to Check What You Have

### Step 1: Determine Your Account Type

**Method 1: Check Tenant ID**
```bash
# If you have Azure CLI installed
az login
az account show --query "homeTenantId" -o tsv
```

If the tenant ID is `9188040d-6c67-4c5b-b112-36a304b66dad`, you're using a pure personal account with no tenant.

**Method 2: Try to Access Azure Portal**
1. Go to https://portal.azure.com
2. Sign in with your email
3. Navigate to "Microsoft Entra ID" (or "Azure Active Directory")
4. Look at "Overview" → "Tenant information"

**What you'll see:**
- **If you have a subscription**: You'll see a tenant with a name like `yourname.onmicrosoft.com`
- **If you don't**: You'll see an error or limited access

### Step 2: Check for Active Azure Subscription

**In Azure Portal:**
1. Go to "Subscriptions" in the portal
2. Look for active subscriptions

**Using Azure CLI:**
```bash
az account list --output table
```

**What you might have:**
- "Azure subscription 1" (default name)
- "Free Trial"
- "Pay-As-You-Go"
- "Visual Studio Enterprise"

### Step 3: Check Tenant Creation Ability

1. Go to Microsoft Entra ID
2. Click "Overview" → "Manage tenants" → "Create"
3. If button is disabled: You need a paid subscription
4. If enabled: You can create additional tenants

---

## Step-by-Step: Getting Set Up from Scratch

### Path 1: You Have NO Azure Account (Starting Fresh)

**Total Time**: 30 minutes
**Cost**: $0 (if you stay within free tier)

#### Step 1: Create Azure Free Account

1. Go to https://azure.microsoft.com/free/
2. Click "Start free"
3. Sign in with your personal Microsoft account (or create one)
4. Provide:
   - Phone number (for verification)
   - Credit card (for identity verification - won't be charged)
   - Identity verification
5. Complete sign-up

**What you get:**
- ✅ $200 credit for 30 days
- ✅ Free services for 12 months
- ✅ Always-free services (including Entra ID Free)
- ✅ Automatic Azure AD tenant created
- ✅ You're the Global Administrator

#### Step 2: Verify Your Tenant

1. Sign in to https://portal.azure.com
2. Navigate to "Microsoft Entra ID"
3. Note your tenant information:
   ```
   Tenant name: Default Directory (or custom name)
   Tenant ID: <unique-guid>
   Primary domain: yourname.onmicrosoft.com
   ```

**Save these values - you'll need them later!**

#### Step 3: Create App Registrations

Follow the existing guide: [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md)

You'll create 3 apps:
1. AgentFramework-Orchestrator-API
2. AgentFramework-Python-Agent-API
3. AgentFramework-DotNet-Agent-API

**Time**: 20-30 minutes
**Cost**: FREE (app registrations are free)

---

### Path 2: You Have Azure Account But No Subscription

If you have a Microsoft account but never created an Azure subscription:

#### Option A: Upgrade to Pay-As-You-Go (Recommended)

1. Go to https://portal.azure.com
2. Navigate to "Subscriptions"
3. Click "Add" → "Pay-As-You-Go"
4. Complete setup (requires credit card)

**Cost**: $0 if you stay within free tier
- Microsoft Entra ID: FREE
- App Registrations: FREE
- Authentication requests: FREE up to 50,000 MAU

#### Option B: External Tenant Trial (Limited)

1. Go to Microsoft Entra admin center
2. Create "External Tenant" (for customer identity)
3. Select "30-day free trial" (no subscription required)

**Limitations:**
- Only lasts 30 days
- Designed for CIAM (Customer Identity) scenarios
- May have feature differences from standard tenant

---

### Path 3: You Have Azure Subscription (Easiest)

**You're already set!** You have everything needed.

1. Verify tenant exists: Azure Portal → Microsoft Entra ID
2. Note tenant ID and domain
3. Proceed to app registration (see AZURE_AD_SETUP.md)

---

## Cost Breakdown (Personal Azure Account)

### What's FREE Forever

| Service | Free Tier | Sufficient for OBO? |
|---------|-----------|---------------------|
| **Microsoft Entra ID Free** | Included with subscription | ✅ YES |
| **App Registrations** | Unlimited | ✅ YES |
| **Authentication Requests** | 50,000 MAU (Monthly Active Users) | ✅ YES for dev/testing |
| **Token Validation** | No limit | ✅ YES |
| **OBO Token Exchange** | Counted in authentication requests | ✅ YES |

### What Costs Money

| Service | When Charged | Typical Dev Cost |
|---------|--------------|------------------|
| **Premium P1/P2 Features** | Only if you enable them | N/A (not needed for OBO) |
| **Azure App Service** | If you host on Azure | $0 if using Free tier |
| **Virtual Machines** | If you create VMs | $0 if not created |

**Bottom Line for OBO Development**: $0/month

The only cost is if you:
- Deploy to paid Azure services (App Service, VMs, etc.)
- Exceed 50,000 monthly active users
- Enable Premium features (Conditional Access, PIM, etc.)

For local development and testing: **100% FREE**

---

## Recommended Approach for Personal Azure Accounts

### Recommended: Use Your Personal Azure Subscription

**Why this works best:**
1. ✅ You control everything (no enterprise policies)
2. ✅ You're automatically Global Administrator (can grant admin consent)
3. ✅ Free for OBO development
4. ✅ Can test with any account type (personal or organizational)
5. ✅ Same production features as enterprise

**Steps:**

#### 1. Create/Verify Azure Subscription (if needed)
- Sign up at https://azure.microsoft.com/free/
- Use your personal email (outlook.com, hotmail.com, gmail.com, etc.)

#### 2. Create App Registrations (3 apps)
- Follow [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md) exactly
- Takes 20-30 minutes

#### 3. Configure for Personal AND/OR Organizational Users

When creating app registrations, choose "Supported account types":

**Option A: Organizational accounts only (recommended for most)**
```
"Accounts in this organizational directory only (Default Directory only - Single tenant)"
```
- Use for: Testing within your own tenant
- Users: Only accounts you create in your tenant

**Option B: Personal + Organizational**
```
"Accounts in any organizational directory and personal Microsoft accounts"
```
- Use for: Public apps that support MSA
- Users: Anyone with Microsoft account

#### 4. Grant Admin Consent
- You can grant this yourself (you're Global Admin)
- No approval needed from anyone else

#### 5. Test with Real Tokens
- Create test users in your tenant
- Or use your own personal account (if you selected Option B)

---

## Configuration Example for Personal Azure Account

### Your Environment Variables

```bash
# Your Tenant (automatically created with subscription)
AZURE_TENANT_ID=<your-unique-tenant-guid>

# Orchestrator App Registration
AZURE_CLIENT_ID=<orchestrator-app-client-id>
AZURE_CLIENT_SECRET=<orchestrator-secret>

# JWT Settings
JWT_ALGORITHM=RS256
JWT_AUDIENCE=api://<orchestrator-client-id>
JWT_ISSUER=https://login.microsoftonline.com/<your-tenant-id>/v2.0

# Sub-Agent Scopes
PYTHON_AGENT_SCOPES=["api://python-agent/access_as_user"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent/access_as_user"]

# Enable Authentication
REQUIRE_AUTH=true
```

### Finding Your Values

**Tenant ID:**
```bash
# Azure Portal
Microsoft Entra ID → Overview → Tenant ID

# Azure CLI
az account show --query "homeTenantId" -o tsv
```

**Client IDs:**
```bash
# Azure Portal
Microsoft Entra ID → App registrations → (Your App) → Overview → Application (client) ID
```

**Client Secret:**
```bash
# Azure Portal
Microsoft Entra ID → App registrations → Orchestrator → Certificates & secrets
# Generate new secret, copy immediately (can't view again)
```

---

## Testing Your Setup

### Phase 1: Verify Tenant Access

```bash
# Install Azure CLI if needed
curl -L https://aka.ms/InstallAzureCli | bash

# Login with personal account
az login

# Verify tenant
az account show

# Expected output:
{
  "environmentName": "AzureCloud",
  "homeTenantId": "<your-tenant-guid>",
  "id": "<subscription-id>",
  "isDefault": true,
  "name": "Azure subscription 1",
  "state": "Enabled",
  "tenantId": "<your-tenant-guid>",
  "user": {
    "name": "you@outlook.com",
    "type": "user"
  }
}
```

### Phase 2: Verify App Registrations

```bash
# List your app registrations
az ad app list --display-name "AgentFramework" --output table

# Expected: 3 apps listed
DisplayName                          AppId
-----------------------------------  ------------------------------------
AgentFramework-Orchestrator-API      <guid>
AgentFramework-Python-Agent-API      <guid>
AgentFramework-DotNet-Agent-API      <guid>
```

### Phase 3: Get Test Token

**Option A: Using Azure CLI (Easiest)**

```bash
# Get token for orchestrator
az account get-access-token \
  --resource api://<orchestrator-client-id> \
  --query "accessToken" \
  --output tsv
```

**Option B: Using MSAL Python**

```python
import msal

tenant_id = "your-tenant-id"
client_id = "orchestrator-client-id"
scopes = [f"api://{client_id}/access_as_user"]

# Public client (no secret needed for user auth)
app = msal.PublicClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

# Interactive login
result = app.acquire_token_interactive(scopes=scopes)

if "access_token" in result:
    print("Token acquired!")
    print(result["access_token"])
else:
    print(f"Error: {result.get('error')}")
    print(f"Description: {result.get('error_description')}")
```

**Option C: Using Postman**

1. Create new request: `POST http://localhost:3000/agent`
2. Go to "Authorization" tab
3. Select "OAuth 2.0"
4. Click "Get New Access Token"
5. Configure:
   ```
   Grant Type: Authorization Code
   Auth URL: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize
   Access Token URL: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token
   Client ID: <orchestrator-client-id>
   Scope: api://<orchestrator-client-id>/access_as_user
   ```
6. Click "Request Token"
7. Sign in with your account
8. Copy token

### Phase 4: Test Orchestrator with Token

```bash
# Set your token
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Test endpoint
curl -X POST http://localhost:3000/agent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test OBO flow",
    "context": {}
  }'
```

**Expected Response:**
```json
{
  "response": "...",
  "agent_used": "python",
  "user": "Your Name",
  "user_id": "<user-object-id>"
}
```

**Check Orchestrator Logs:**
```
INFO - Orchestrator received request from user: Your Name
INFO - User ID: <oid>
INFO - Selected agent: python
INFO - Acquiring OBO token for scopes: ['api://python-agent/access_as_user']
INFO - OBO token acquired successfully
INFO - Calling python agent with OBO token
```

---

## Troubleshooting Personal Azure Accounts

### Issue 1: "Cannot create tenant" - Button Disabled

**Cause**: Free trial accounts cannot create additional tenants (2025 policy)

**Solution**:
1. Use the default tenant created with your subscription
2. OR upgrade to pay-as-you-go (free tier available)
3. OR use External Tenant trial (30 days)

**You only need ONE tenant for this POC!**

### Issue 2: "AADSTS50020: User account from identity provider does not exist in tenant"

**Cause**: You're trying to sign in with an account that doesn't exist in your tenant

**Solution**:
```bash
# Check which tenant you're signing into
# Token issuer should match your tenant

# Create user in your tenant:
az ad user create \
  --display-name "Test User" \
  --password "SecureP@ssw0rd!" \
  --user-principal-name testuser@<your-domain>.onmicrosoft.com

# OR configure app to support personal accounts:
# App registrations → (Your App) → Authentication
# Supported account types → "Personal Microsoft accounts"
```

### Issue 3: "AADSTS65001: The user or administrator has not consented"

**Cause**: Admin consent not granted for API permissions

**Solution**:
```bash
# Azure Portal
Microsoft Entra ID → App registrations → Orchestrator
→ API permissions → "Grant admin consent for <tenant>"
→ Click Yes
```

**As owner of personal Azure account, you ARE the admin** - you can grant this yourself!

### Issue 4: "Subscription not found"

**Cause**: No active Azure subscription associated with account

**Solution**:
1. Sign up for Azure free account: https://azure.microsoft.com/free/
2. Or activate existing subscription
3. Or create pay-as-you-go subscription

### Issue 5: Token Works but OBO Fails

**Cause**: Orchestrator doesn't have permission to call sub-agent API

**Solution**:
1. Verify API permissions in orchestrator app registration
2. Ensure admin consent granted (green checkmarks)
3. Check client secret is valid and correct
4. Verify scopes exactly match App ID URIs

**Debug steps:**
```bash
# Check orchestrator permissions
az ad app permission list --id <orchestrator-app-id>

# Should show delegated permissions for both sub-agent APIs
```

---

## Alternative: Testing Without Azure AD (Fastest)

If you want to test the orchestration logic WITHOUT dealing with Azure AD:

### Keep Testing Mode Enabled

```bash
# In .env
REQUIRE_AUTH=false
```

**What works:**
- ✅ Full orchestration flow
- ✅ Agent selection
- ✅ Sub-agent calls
- ✅ Response aggregation
- ✅ Mock user context

**What doesn't work:**
- ❌ JWT validation
- ❌ OBO token exchange
- ❌ Real user identity

**Perfect for:**
- Testing orchestration logic
- Developing features
- Demo without auth complexity

**Test command:**
```bash
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Test without auth"}'
```

---

## Summary & Next Steps

### What You Learned

1. **Personal Microsoft accounts CAN be used** for OBO flow development
2. **You need an Azure AD tenant**, which comes automatically with Azure subscription
3. **Azure subscription can be free** for development (stay within free tier)
4. **OBO flow supports both** organizational and personal accounts as end users
5. **As of 2025**, creating tenants requires paid subscription (but first tenant is automatic)
6. **You're the admin** of your own tenant (can grant all consents)

### Recommended Path

**For Most Personal Account Users:**

1. ✅ Sign up for Azure free account (https://azure.microsoft.com/free/)
   - Time: 10 minutes
   - Cost: $0
   - Gets you: Tenant + subscription + $200 credit

2. ✅ Create 3 app registrations (follow AZURE_AD_SETUP.md)
   - Time: 20-30 minutes
   - Cost: $0
   - Gets you: OBO-ready configuration

3. ✅ Configure orchestrator with Azure values
   - Time: 5 minutes
   - Cost: $0
   - Gets you: Production-ready auth

4. ✅ Test with real tokens
   - Time: 10 minutes
   - Cost: $0
   - Gets you: Working OBO flow

**Total Time**: ~1 hour
**Total Cost**: $0

### What About Enterprise vs Personal?

| Feature | Personal Azure | Enterprise Azure | Impact on OBO |
|---------|---------------|------------------|---------------|
| App Registrations | ✅ Unlimited | ✅ Unlimited | ✅ No difference |
| OBO Flow | ✅ Fully supported | ✅ Fully supported | ✅ No difference |
| Admin Consent | ✅ You can grant | ✅ Admin grants | ✅ Easier with personal (you are admin) |
| Cost for OBO | ✅ Free | ✅ Free | ✅ No difference |
| Tenant Control | ✅ Full control | ⚠️ IT policies may apply | ✅ Better with personal |
| Premium Features | ⚠️ Must purchase | ✅ Often included | N/A for OBO |
| Support | ⚠️ Community | ✅ Enterprise support | N/A for OBO |

**For OBO flow development: Personal Azure account is PERFECT!**

### Your Next Action

**Choose your path:**

**Path A**: Test without Azure AD first
```bash
# Keep REQUIRE_AUTH=false
# Test orchestration logic
# Come back to Azure AD later
```

**Path B**: Set up Azure AD now
1. Go to https://azure.microsoft.com/free/
2. Create free account with personal email
3. Follow AZURE_AD_SETUP.md
4. Test with real tokens

**Path C**: Use existing Azure subscription (if you have one)
1. Verify tenant exists
2. Follow AZURE_AD_SETUP.md
3. Test with real tokens

### Resources

**Official Microsoft Documentation:**
- [Create Azure Free Account](https://azure.microsoft.com/free/)
- [Create Entra ID Tenant](https://learn.microsoft.com/entra/fundamentals/create-new-tenant)
- [OAuth 2.0 OBO Flow](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [App Registration Quickstart](https://learn.microsoft.com/entra/identity-platform/quickstart-register-app)

**Your Project Guides:**
- [AZURE_AD_SETUP.md](./AZURE_AD_SETUP.md) - Complete setup instructions
- [JWT_OBO_IMPLEMENTATION_PLAN.md](./JWT_OBO_IMPLEMENTATION_PLAN.md) - Implementation details
- [README.md](./README.md) - Project overview

**Tools:**
- [Azure Portal](https://portal.azure.com)
- [JWT.ms](https://jwt.ms) - Decode and inspect tokens
- [Azure CLI](https://learn.microsoft.com/cli/azure/) - Command line tools

---

## Frequently Asked Questions

### Q: Do I need a company email to use Azure AD?

**A: No.** You can use any email (outlook.com, gmail.com, etc.) to create an Azure subscription and get an Azure AD tenant.

### Q: Will I be charged for using OBO flow?

**A: No.** Microsoft Entra ID Free includes authentication for up to 50,000 monthly active users. OBO token exchanges count toward this limit, but for development/testing you'll never hit it.

### Q: Can my app's end users use personal accounts (gmail, yahoo, etc.)?

**A: Yes**, if you configure your app registration to support "Personal Microsoft accounts". Users can sign in with outlook.com, hotmail.com, live.com accounts.

**Note**: Gmail/Yahoo users would need to create a Microsoft account first, or you'd need to use Azure AD B2C for social identity providers (additional setup).

### Q: What's the difference between my personal account and the tenant?

**A: Think of it this way:**
- Your personal account (john@outlook.com) = The owner/administrator
- The tenant (johndoe.onmicrosoft.com) = The directory/organization
- App registrations live in the tenant, not in your personal account

### Q: Can I transfer my apps to a company tenant later?

**A: No**, app registrations cannot be moved between tenants. However, you can:
- Export configuration and recreate in new tenant
- Use multi-tenant apps to work across tenants
- Keep dev/test in personal tenant, production in company tenant

### Q: Do I lose anything by using a personal Azure account vs enterprise?

**For OBO flow: No.** The features are identical. You might miss:
- Premium P1/P2 features (Conditional Access, PIM, etc.) - can purchase if needed
- Enterprise support - community support available
- Integration with corporate systems - not relevant for POC

### Q: What happens after my $200 credit expires?

**A: Free tier continues forever.**
- Microsoft Entra ID Free: Still free
- App registrations: Still free
- Authentication: Still free (up to 50k MAU)
- You only pay if you use paid Azure services (VMs, App Service premium tiers, etc.)

### Q: Can I delete my tenant if I want to start over?

**A: Yes**, but:
- Must delete all resources first
- Must not be your default tenant
- Cannot delete if subscription is associated
- Easier to just create new app registrations

### Q: Should I use my personal Azure account or ask my company for access?

**Personal is better for learning/POC because:**
- ✅ You control everything
- ✅ No approval needed
- ✅ No corporate policies blocking you
- ✅ Can test anytime
- ✅ Free for development

**Use company account when:**
- Ready for production
- Need to integrate with company systems
- Need enterprise support
- Building for company use case

---

## Conclusion

You absolutely CAN implement JWT On-Behalf-Of flow with a personal Azure account. The key is understanding that:

1. Your personal email is just the owner - you'll create a tenant
2. Azure offers free tiers sufficient for OBO development
3. As of 2025, you need to sign up for a free Azure account (which creates a tenant automatically)
4. Your existing orchestrator code is ready - you just need Azure configuration

**The fastest path to success:**
1. Create Azure free account (10 minutes)
2. Follow AZURE_AD_SETUP.md (30 minutes)
3. Test with real tokens (10 minutes)

**Total: ~1 hour to working OBO flow, $0 cost.**

You're in a great position - you already have the code implemented and ready to go. The Azure setup is straightforward, and using a personal account actually makes it easier because you have full control without needing corporate approvals.

**Ready to start?** Go to https://azure.microsoft.com/free/ and create your free account!
