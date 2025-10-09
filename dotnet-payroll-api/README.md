# Payroll API - Secured User-Specific Data API

## Overview

The **Payroll API** is a secure .NET Web API that demonstrates JWT-based authentication and authorization in a microservices architecture. This API is designed to be called by agents (via OBO flow) to retrieve user-specific payroll information.

**Key Security Features:**
- ✅ JWT authentication required for all data endpoints
- ✅ Users can ONLY access their own data (oid claim validation)
- ✅ Real JWT signature validation via Microsoft.Identity.Web
- ✅ Audit logging for security events
- ✅ Returns proper HTTP status codes (401, 403, 404)

## Architecture Integration

```
User → Frontend (authenticates)
         ↓ User JWT
    Orchestrator (validates JWT)
         ↓ OBO Token Exchange
    .NET Agent (receives OBO token)
         ↓ Calls with OBO token
    Payroll API ⭐ (validates JWT, extracts user ID)
         ↓
    Returns user-specific data
```

## Project Structure

```
dotnet-payroll-api/
├── PayrollApi.sln
├── PayrollApi/
│   ├── PayrollApi.csproj
│   ├── Program.cs                      # JWT auth configuration
│   ├── appsettings.json                # Configuration (auth disabled by default)
│   ├── appsettings.Development.json    # Development config (gitignored - for personal data)
│   ├── appsettings.local.json          # Local config (gitignored)
│   │
│   ├── Configuration/
│   │   └── DeveloperUserConfiguration.cs  # Developer user config model
│   │
│   ├── Controllers/
│   │   └── PayrollController.cs        # /user-info & /user-pto endpoints
│   │
│   ├── Models/
│   │   ├── UserInfo.cs                 # User information model
│   │   ├── UserPto.cs                  # PTO balance model
│   │   └── ErrorResponse.cs            # Error response model
│   │
│   └── Services/
│       ├── IPayrollDataService.cs
│       └── PayrollDataService.cs       # In-memory data service with config support
│
└── README.md                            # This file
```

## Technology Stack

- **.NET**: 8.0 (LTS)
- **Web Framework**: ASP.NET Core Web API
- **Authentication**:
  - `Microsoft.Identity.Web` (3.2.1)
  - `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.11)
- **Ports**:
  - HTTP: 5100
  - HTTPS: 5101

## API Endpoints

### `GET /payroll/user-info`

Get user information for the authenticated user.

**Authentication**: Required
**Authorization**: User can only access their own data

**Response (200 OK):**
```json
{
  "userId": "00000000-0000-0000-0000-000000000001",
  "name": "Alice Johnson",
  "email": "alice.johnson@contoso.com",
  "department": "Engineering",
  "employeeId": "EMP001",
  "jobTitle": "Senior Software Engineer",
  "manager": "David Chen",
  "hireDate": "2020-03-15T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Attempting to access another user's data
- `404 Not Found`: User not found in payroll system

---

### `GET /payroll/user-pto`

Get PTO (Paid Time Off) balance and history for the authenticated user.

**Authentication**: Required
**Authorization**: User can only access their own data

**Response (200 OK):**
```json
{
  "userId": "00000000-0000-0000-0000-000000000001",
  "currentBalanceHours": 120.0,
  "accruedThisYearHours": 160.0,
  "usedThisYearHours": 40.0,
  "pendingRequestsHours": 16.0,
  "maxCarryoverHours": 80.0,
  "upcomingPto": [
    {
      "startDate": "2025-11-06T00:00:00Z",
      "endDate": "2025-11-08T00:00:00Z",
      "hours": 16.0,
      "status": "Approved",
      "type": "Vacation"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: Attempting to access another user's data
- `404 Not Found`: User PTO data not found

---

### `GET /health`

Health check endpoint (no authentication required).

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "payroll-api",
  "timestamp": "2025-10-07T12:00:00Z"
}
```

---

### `GET /`

Root endpoint with service information (no authentication required).

**Response (200 OK):**
```json
{
  "service": "Payroll API",
  "version": "1.0.0",
  "description": "Secure payroll API demonstrating JWT OBO flow",
  "endpoints": {
    "userInfo": "GET /payroll/user-info",
    "userPto": "GET /payroll/user-pto",
    "health": "GET /health"
  },
  "configuration": {
    "authenticationRequired": false,
    "httpPort": 5100,
    "httpsPort": 5101
  }
}
```

## Getting Started

### Prerequisites

- **.NET SDK 8.0+**
  ```bash
  # macOS (via Homebrew)
  brew install dotnet

  # Or download from https://dotnet.microsoft.com/download

  # Verify installation
  dotnet --version
  ```

### Installation

```bash
# Navigate to the payroll API directory
cd dotnet-payroll-api

# Restore dependencies
dotnet restore

# Build the project
dotnet build
```

### Configuration

The API has two modes:

#### 1. **Testing Mode** (Default - No Authentication)

For local development without Azure AD setup:

**appsettings.json:**
```json
{
  "Auth": {
    "RequireAuthentication": false
  }
}
```

In this mode:
- No JWT validation
- Uses mock user: `00000000-0000-0000-0000-000000000001` (Alice Johnson)
- Useful for testing API functionality

#### 2. **Production Mode** (With Azure AD Authentication & OBO Support)

For production or testing with real JWT tokens and OBO (On-Behalf-Of) flow:

##### Step 1: Run Azure Setup Script

The easiest way to set up Azure AD for the Payroll API is to use the automated setup script:

```bash
# From the project root
./setup-payroll-api-azure.sh
```

This script will:
1. Create the `af-poc-payroll-api` app registration in Azure AD
2. Expose the `access_as_user` API scope
3. Grant the orchestrator permission to call this API via OBO
4. Generate configuration files (.env and appsettings.local.json)

##### Step 2: Update Configuration

After running the setup script, create `appsettings.local.json`:

```bash
# Copy the example template
cp PayrollApi/appsettings.local.json.example PayrollApi/appsettings.local.json

# Edit with your Azure AD values (already generated by setup script)
```

**appsettings.local.json:**
```json
{
  "Auth": {
    "RequireAuthentication": true
  },
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "<your-tenant-id>",
    "ClientId": "<your-payroll-api-client-id>",
    "Audience": "api://<your-payroll-api-client-id>",
    "TokenValidation": {
      "ValidateIssuer": true,
      "ValidateAudience": true,
      "ValidateLifetime": true,
      "ValidateIssuerSigningKey": true,
      "AcceptBothV1AndV2Tokens": true
    }
  }
}
```

##### Step 3: Manual Azure AD Setup (Alternative)

If you prefer to set up Azure AD manually:

1. **Create App Registration**:
   ```bash
   az ad app create --display-name "af-poc-payroll-api"
   ```

2. **Get Client ID**:
   ```bash
   PAYROLL_API_APP_ID=$(az ad app list --display-name "af-poc-payroll-api" --query "[0].appId" -o tsv)
   ```

3. **Set Identifier URI**:
   ```bash
   az ad app update --id $PAYROLL_API_APP_ID --identifier-uris "api://$PAYROLL_API_APP_ID"
   ```

4. **Expose API Scope**:
   - Go to Azure Portal → App Registrations → af-poc-payroll-api
   - Select "Expose an API"
   - Add scope: `access_as_user` (delegated permission)

5. **Grant Orchestrator Permission**:
   - Go to orchestrator app registration
   - API Permissions → Add permission → My APIs → af-poc-payroll-api
   - Select `access_as_user` (delegated)
   - Grant admin consent

##### Step 4: Using User Secrets (Recommended for Development)

For local development, use .NET user secrets instead of appsettings:

```bash
cd PayrollApi

# Initialize user secrets
dotnet user-secrets init

# Set Azure AD configuration
dotnet user-secrets set "AzureAd:TenantId" "your-tenant-id"
dotnet user-secrets set "AzureAd:ClientId" "your-payroll-api-client-id"
dotnet user-secrets set "AzureAd:Audience" "api://your-payroll-api-client-id"
dotnet user-secrets set "Auth:RequireAuthentication" "true"
```

##### OBO Flow Configuration Notes

**Important**: For the OBO (On-Behalf-Of) flow to work properly:

1. **Token Version**: The API is configured to accept both v1.0 and v2.0 tokens
2. **Audience Validation**: The OBO token's `aud` claim must match one of:
   - The Payroll API's Client ID
   - `api://<payroll-api-client-id>`
3. **Issuer Validation**: Tokens are validated from both v1.0 and v2.0 endpoints:
   - `https://login.microsoftonline.com/{tenant}/v2.0`
   - `https://sts.windows.net/{tenant}/`
4. **User Identity Preservation**: The `oid` claim from the original user token is preserved in the OBO token

See [AUTH_PLAN.md](../AUTH_PLAN.md) for detailed OBO flow documentation.

### Running the API

```bash
# Development mode with auto-reload
dotnet run

# Or using dotnet watch
dotnet watch run

# Production mode
dotnet run --configuration Release
```

The API will be available at:
- **HTTP**: http://localhost:5100
- **HTTPS**: https://localhost:5101

## Test Data Configuration

### Example Users (Always Available)

The API includes hardcoded example data for 5 test users:

| User ID | Name | Department | Employee ID | PTO Balance |
|---------|------|------------|-------------|-------------|
| `00000000-0000-0000-0000-000000000001` | Alice Johnson | Engineering | EMP001 | 120 hours |
| `00000000-0000-0000-0000-000000000002` | Bob Smith | Marketing | EMP002 | 80 hours |
| `00000000-0000-0000-0000-000000000003` | Carol Williams | Sales | EMP003 | 100 hours |
| `00000000-0000-0000-0000-000000000004` | David Chen | Engineering | EMP004 | 200 hours |
| `00000000-0000-0000-0000-000000000005` | Emma Davis | Human Resources | EMP005 | 64 hours |

### Developer User Configuration (Your Personal Data)

To test with your own email address without committing personal information to the repository, use the `DeveloperUser` configuration in `appsettings.Development.json`:

**Step 1**: The `appsettings.json` contains example configuration (safe to commit):

```json
{
  "DeveloperUser": {
    "Enabled": false,
    "UserId": "dev-user-example",
    "Name": "Developer User",
    "Email": "developer@example.com",
    "Department": "Engineering",
    "EmployeeId": "DEV001",
    "JobTitle": "Software Engineer",
    "Manager": "Engineering Manager",
    "HireDate": "2024-01-01",
    "PtoBalance": {
      "CurrentBalanceHours": 240.0,
      "AccruedThisYearHours": 240.0,
      "UsedThisYearHours": 0.0,
      "PendingRequestsHours": 0.0,
      "MaxCarryoverHours": 80.0
    }
  }
}
```

**Step 2**: Override with your real information in `appsettings.Development.json` (gitignored):

```json
{
  "DeveloperUser": {
    "Enabled": true,
    "UserId": "your-user-id",
    "Name": "Your Name",
    "Email": "your.email@example.com",
    "Department": "Engineering",
    "EmployeeId": "EMP998",
    "JobTitle": "Senior Software Engineer",
    "Manager": "Engineering Manager",
    "HireDate": "2024-01-01",
    "PtoBalance": {
      "CurrentBalanceHours": 240.0,
      "AccruedThisYearHours": 240.0,
      "UsedThisYearHours": 0.0,
      "PendingRequestsHours": 0.0,
      "MaxCarryoverHours": 80.0
    }
  }
}
```

**Important Notes**:
- ✅ `appsettings.Development.json` is **gitignored** - your personal email is never committed
- ✅ Set `Enabled: true` to load your user data automatically on startup
- ✅ The email should match your Azure AD email for authentication testing
- ✅ The `UserId` should match the `oid` or `email` claim from your JWT token
- ✅ When enabled, your user is dynamically added to the in-memory data store at startup

## Testing

### Testing Without Authentication (Default)

```bash
# Start the API
dotnet run

# In another terminal:

# Get user info (returns Alice Johnson's data)
curl http://localhost:5100/payroll/user-info

# Get PTO balance
curl http://localhost:5100/payroll/user-pto

# Health check
curl http://localhost:5100/health

# Root endpoint
curl http://localhost:5100/
```

### Testing With Authentication

```bash
# Set authentication to required
# Edit appsettings.Development.json:
# "Auth": { "RequireAuthentication": true }

# Start the API
dotnet run

# Call with JWT token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5100/payroll/user-info

# Test unauthorized access (should return 401)
curl http://localhost:5100/payroll/user-info
```

### Testing Authorization (Cross-User Access Prevention)

When authentication is enabled, attempting to access another user's data should return 403:

```bash
# User A's token (oid: 00000000-0000-0000-0000-000000000001)
curl -H "Authorization: Bearer USER_A_TOKEN" \
  "http://localhost:5100/payroll/user-info?userId=00000000-0000-0000-0000-000000000002"

# Response: 403 Forbidden
# {
#   "error": "Access denied. You can only access your own information.",
#   "statusCode": 403
# }
```

## Security Implementation

### JWT Validation

The API validates JWT tokens using Microsoft.Identity.Web:

1. **Signature Validation**: Verifies token was signed by Azure AD
2. **Audience Validation**: Ensures token is intended for this API
3. **Issuer Validation**: Confirms token came from trusted Azure AD tenant
4. **Expiration Validation**: Checks token hasn't expired

**Location**: Program.cs:13-16

### User Authorization

**Critical Security Logic** (PayrollController.cs:46-59):

```csharp
// Extract user ID from JWT 'oid' claim
var currentUserId = GetCurrentUserId();

// Prevent cross-user access
if (userId != null && userId != currentUserId)
{
    _logger.LogWarning(
        "SECURITY: User {CurrentUserId} attempted to access {RequestedUserId}",
        currentUserId, userId);

    return StatusCode(403, new ErrorResponse
    {
        Error = "Access denied. You can only access your own information."
    });
}
```

### Audit Logging

All security events are logged:
- Successful data retrievals (Info level)
- Failed authentication attempts (Warning level)
- Cross-user access attempts (Warning level with SECURITY prefix)
- User not found errors (Warning level)

## Integration with Agent Flow

### Complete OBO Flow Example

**Scenario**: User asks .NET agent "How much PTO do I have?"

1. **User authenticates** → Frontend gets user JWT with `oid` claim
2. **Frontend calls Orchestrator** with user JWT
3. **Orchestrator validates JWT** and extracts user identity
4. **Orchestrator performs OBO exchange**:
   - User JWT → .NET agent scoped OBO token
   - OBO token still contains original user's `oid` claim
5. **Orchestrator calls .NET Agent** with OBO token
6. **.NET Agent processes request** and decides to call Payroll API
7. **.NET Agent calls Payroll API** with the same OBO token:
   ```http
   GET /payroll/user-pto
   Authorization: Bearer <OBO_TOKEN>
   ```
8. **Payroll API validates OBO token**:
   - Signature valid ✅
   - Audience matches ✅
   - Issuer matches ✅
   - Not expired ✅
9. **Payroll API extracts user ID** from `oid` claim
10. **Payroll API returns user-specific PTO data** (only for that user)
11. **.NET Agent formats response** and returns to Orchestrator
12. **Orchestrator returns to Frontend**

### Security Guarantees

✅ **Unauthenticated requests blocked**: `[Authorize]` attribute requires valid JWT
✅ **Users cannot access other users' data**: Authorization logic checks `oid` claim
✅ **JWT validation is real**: Microsoft.Identity.Web validates signature, audience, issuer, expiration
✅ **User identity preserved**: OBO flow maintains original user's `oid` claim throughout
✅ **Audit trail**: All access attempts logged with user ID and security warnings
✅ **No JWT bypass**: Even with correct endpoint, wrong user ID returns 403

## Development Commands

```bash
# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run application
dotnet run

# Watch mode (auto-reload)
dotnet watch run

# Run tests (when tests are added)
dotnet test

# Clean build artifacts
dotnet clean

# Publish for deployment
dotnet publish -c Release -o ./publish

# Check for outdated packages
dotnet list package --outdated
```

## Troubleshooting

### Port Already in Use

```bash
# macOS/Linux - Kill process on port 5100
lsof -ti:5100 | xargs kill

# Or change port in Program.cs
serverOptions.ListenLocalhost(5102); // Different port
```

### JWT Validation Fails

**Symptoms**: Always returns 401 Unauthorized

**Solutions**:
1. Verify `AzureAd:TenantId` matches your Azure AD tenant
2. Verify `AzureAd:ClientId` matches Payroll API app registration
3. Check token audience matches `AzureAd:Audience` setting
4. Ensure token hasn't expired
5. Check logs for detailed error messages

### User Not Found (404)

**Symptoms**: Returns 404 even with valid JWT

**Solution**: The email or `oid` claim in your JWT must match one of the available users. You have two options:

**Option 1: Use Developer User Configuration** (Recommended)
1. Edit `appsettings.Development.json`
2. Add your email and user information to the `DeveloperUser` section
3. Set `Enabled: true`
4. Restart the API - your user will be loaded automatically

**Option 2: Use Example Users**
Use one of the hardcoded example user IDs:
- `00000000-0000-0000-0000-000000000001` (alice.johnson@contoso.com)
- `00000000-0000-0000-0000-000000000002` (bob.smith@contoso.com)
- `00000000-0000-0000-0000-000000000003` (carol.williams@contoso.com)
- `00000000-0000-0000-0000-000000000004` (david.chen@contoso.com)
- `00000000-0000-0000-0000-000000000005` (emma.davis@contoso.com)

**Note**: The API now matches users by **email** from the JWT token (not just by `oid`).

### Developer User Not Loading

**Symptoms**: Your personal user from `appsettings.Development.json` is not available

**Checklist**:
1. ✅ Verify `DeveloperUser.Enabled` is set to `true`
2. ✅ Check that you're running in Development environment:
   ```bash
   # Set environment variable
   export ASPNETCORE_ENVIRONMENT=Development
   dotnet run
   ```
3. ✅ Verify the file is named exactly `appsettings.Development.json` (case-sensitive)
4. ✅ Restart the API after making changes to configuration
5. ✅ Check logs for "Adding developer user from configuration" message

**Verify Developer User is Loaded**:
```bash
# The API logs this on startup if developer user is enabled:
# "Adding developer user from configuration: your.email@example.com"
```

### Cross-User Access Returns 403

This is **expected behavior**! The API is working correctly by blocking unauthorized access.

## Next Steps

### Phase 1: Basic Testing ✅
- [x] API running on ports 5100/5101
- [x] Endpoints return data in testing mode
- [x] Health checks working

### Phase 2: Azure AD Integration
- [ ] Register Payroll API in Azure AD
- [ ] Configure API scopes (`api://payroll-api/access`)
- [ ] Update `appsettings.json` with real tenant/client IDs
- [ ] Test with real JWT tokens

### Phase 3: Agent Integration
- [ ] Update .NET Agent to call Payroll API
- [ ] Implement OBO token forwarding in .NET Agent
- [ ] Test complete flow: User → Orchestrator → .NET Agent → Payroll API
- [ ] Verify user identity preserved throughout

### Phase 4: Production Hardening
- [ ] Add rate limiting
- [ ] Implement caching for payroll data
- [ ] Add distributed tracing (OpenTelemetry)
- [ ] Configure health checks for monitoring
- [ ] Add comprehensive error handling

## References

- [Microsoft.Identity.Web Documentation](https://learn.microsoft.com/en-us/entra/msal/dotnet/microsoft-identity-web/)
- [ASP.NET Core Authentication](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/)
- [OAuth 2.0 On-Behalf-Of Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [JWT Claims](https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens#claims-in-access-tokens)

## License

This is a proof-of-concept project for demonstration purposes.
