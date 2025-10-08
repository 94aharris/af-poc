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
│   ├── Program.cs                  # JWT auth configuration
│   ├── appsettings.json           # Configuration (auth disabled by default)
│   ├── appsettings.Development.json
│   │
│   ├── Controllers/
│   │   └── PayrollController.cs   # /user-info & /user-pto endpoints
│   │
│   ├── Models/
│   │   ├── UserInfo.cs           # User information model
│   │   ├── UserPto.cs            # PTO balance model
│   │   └── ErrorResponse.cs      # Error response model
│   │
│   └── Services/
│       ├── IPayrollDataService.cs
│       └── PayrollDataService.cs  # Hardcoded test data
│
└── README.md                       # This file
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

#### 2. **Production Mode** (With Azure AD Authentication)

For production or testing with real JWT tokens:

**appsettings.json:**
```json
{
  "Auth": {
    "RequireAuthentication": true
  },
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-payroll-api-client-id",
    "Audience": "api://payroll-api"
  }
}
```

**Using User Secrets (Recommended for Development):**
```bash
dotnet user-secrets init
dotnet user-secrets set "AzureAd:TenantId" "your-tenant-id"
dotnet user-secrets set "AzureAd:ClientId" "your-client-id"
dotnet user-secrets set "Auth:RequireAuthentication" "true"
```

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

## Hardcoded Test Data

The API includes hardcoded data for 5 test users:

| User ID | Name | Department | Employee ID | PTO Balance |
|---------|------|------------|-------------|-------------|
| `00000000-0000-0000-0000-000000000001` | Alice Johnson | Engineering | EMP001 | 120 hours |
| `00000000-0000-0000-0000-000000000002` | Bob Smith | Marketing | EMP002 | 80 hours |
| `00000000-0000-0000-0000-000000000003` | Carol Williams | Sales | EMP003 | 100 hours |
| `00000000-0000-0000-0000-000000000004` | David Chen | Engineering | EMP004 | 200 hours |
| `00000000-0000-0000-0000-000000000005` | Emma Davis | Human Resources | EMP005 | 64 hours |

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

**Solution**: The `oid` claim in your JWT must match one of the hardcoded user IDs:
- `00000000-0000-0000-0000-000000000001`
- `00000000-0000-0000-0000-000000000002`
- `00000000-0000-0000-0000-000000000003`
- `00000000-0000-0000-0000-000000000004`
- `00000000-0000-0000-0000-000000000005`

For testing, you can update the hardcoded data in `Services/PayrollDataService.cs` to match your test user's `oid`.

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
