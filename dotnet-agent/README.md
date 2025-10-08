# .NET Agent Implementation - Microsoft Agent Framework POC

## Overview

This .NET implementation demonstrates an ASP.NET Core Web API-based agent service using the Microsoft Agent Framework with JWT On-Behalf-Of (OBO) authentication flow.

## Technology Stack

- **.NET**: 8.0 (LTS)
- **Web Framework**: ASP.NET Core Web API
- **Agent Framework**: To be implemented with Azure OpenAI SDK
- **Authentication**:
  - `Microsoft.Identity.Web` (3.14.1) - Simplified MSAL.NET integration
  - `Microsoft.Identity.Client` (4.77.1) - MSAL.NET for OBO flow
  - `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.11) - JWT bearer token authentication
- **Azure SDK**: `Azure.Identity` (1.17.0)
- **API Documentation**: `Swashbuckle.AspNetCore` (6.5.0) - Swagger/OpenAPI
- **Configuration**: `Microsoft.Extensions.Configuration`

## Project Structure

```
dotnet-agent/
├── README.md                           # This file
├── AgentService.sln                    # Solution file
├── AgentService/
│   ├── AgentService.csproj            # Project file
│   ├── Program.cs                      # Application entry point & configuration
│   ├── appsettings.json               # Configuration (non-sensitive)
│   ├── appsettings.Development.json   # Development configuration
│   ├── Properties/
│   │   └── launchSettings.json        # Launch profiles
│   ├── Controllers/
│   │   └── AgentController.cs         # /agent endpoint
│   ├── Services/
│   │   ├── IAgentService.cs          # Agent service interface
│   │   ├── AgentService.cs           # Agent Framework integration
│   │   ├── IOboTokenService.cs       # OBO service interface
│   │   └── OboTokenService.cs        # JWT OBO flow implementation
│   ├── Models/
│   │   ├── AgentRequest.cs           # Request DTOs
│   │   └── AgentResponse.cs          # Response DTOs
│   └── Middleware/
│       └── ExceptionHandlingMiddleware.cs
└── AgentService.Tests/
    ├── AgentService.Tests.csproj
    ├── Controllers/
    │   └── AgentControllerTests.cs
    └── Services/
        └── OboTokenServiceTests.cs
```

## Getting Started

### Prerequisites

1. **.NET SDK 8.0+**:
   ```bash
   # macOS (via Homebrew)
   brew install dotnet

   # Or download from https://dotnet.microsoft.com/download

   # Verify installation
   dotnet --version
   ```

2. **Azure Resources** (for full OBO implementation):
   - Azure AD App Registration (for API)
   - Azure OpenAI Service instance
   - Configured API permissions and scopes

### Project Initialization

The project has already been initialized with the following structure and dependencies:

**Installed NuGet Packages:**
- `Microsoft.Identity.Web` (3.14.1) - Simplified MSAL.NET integration
- `Microsoft.Identity.Client` (4.77.1) - MSAL.NET for OBO flow
- `Azure.Identity` (1.17.0) - Azure credential management
- `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.11) - JWT authentication
- `Swashbuckle.AspNetCore` (6.5.0) - Swagger/OpenAPI support

**Note:** The `Azure.AI.Agents` package does not currently exist in NuGet. This will need to be replaced with the appropriate Azure OpenAI SDK when implementing Phase 2.

To build and run:

```bash
# Navigate to the dotnet-agent directory
cd dotnet-agent

# Restore dependencies (if needed)
dotnet restore

# Build project
dotnet build

# Run the application
dotnet run --project AgentService
```

### Configuration

Create `appsettings.Development.json` or use User Secrets:

```bash
# Initialize user secrets
dotnet user-secrets init

# Set secrets
dotnet user-secrets set "AzureAd:TenantId" "your-tenant-id"
dotnet user-secrets set "AzureAd:ClientId" "your-client-id"
dotnet user-secrets set "AzureAd:ClientSecret" "your-client-secret"
dotnet user-secrets set "AzureOpenAI:Endpoint" "https://your-openai.openai.azure.com"
dotnet user-secrets set "AzureOpenAI:DeploymentName" "gpt-4"
```

### Running the Service

```bash
# Run in development mode
dotnet run

# Run with specific profile
dotnet run --launch-profile https

# Watch mode (auto-reload on changes)
dotnet watch run

# Run tests
dotnet test

# Run with verbose output
dotnet run --verbosity detailed
```

### Testing

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true /p:CoverageReportFormat=opencover

# Run specific test
dotnet test --filter "FullyQualifiedName~AgentControllerTests"

# Test the /agent endpoint
curl http://localhost:5000/agent
# Expected response: {"message": "it's alive", "status": "healthy", "agentType": "dotnet-aspnet"}
```

## Implementation Details

### Phase 1: Basic API Endpoint (Current)

**File: `Program.cs`**
```csharp
using AgentService.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS for development
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", builder =>
    {
        builder.AllowAnyOrigin()
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

// Register application services
builder.Services.AddSingleton<IAgentService, Services.AgentService>();
builder.Services.AddSingleton<IOboTokenService, OboTokenService>();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowAll");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

**File: `Controllers/AgentController.cs`**
```csharp
using Microsoft.AspNetCore.Mvc;
using AgentService.Models;
using AgentService.Services;

namespace AgentService.Controllers;

[ApiController]
[Route("[controller]")]
public class AgentController : ControllerBase
{
    private readonly ILogger<AgentController> _logger;
    private readonly IAgentService _agentService;

    public AgentController(
        ILogger<AgentController> logger,
        IAgentService agentService)
    {
        _logger = logger;
        _agentService = agentService;
    }

    /// <summary>
    /// Main agent endpoint - receives chat requests and returns responses.
    /// Phase 1: Returns 'it's alive' message
    /// Phase 2+: Integrates with Agent Framework and OBO flow
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<AgentResponse>> Post([FromBody] AgentRequest request)
    {
        _logger.LogInformation("Agent endpoint called with message: {Message}", request.Message);

        return Ok(new AgentResponse
        {
            Message = "it's alive",
            Status = "healthy",
            AgentType = "dotnet-aspnet",
            ConversationId = request.ConversationId
        });
    }

    /// <summary>
    /// Simple GET endpoint for health checks
    /// </summary>
    [HttpGet]
    public ActionResult<object> Get()
    {
        return Ok(new
        {
            Message = "it's alive",
            Status = "healthy",
            AgentType = "dotnet-aspnet"
        });
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("/health")]
    public ActionResult<object> Health()
    {
        return Ok(new { Status = "healthy" });
    }
}
```

**File: `Models/AgentRequest.cs`**
```csharp
using System.ComponentModel.DataAnnotations;

namespace AgentService.Models;

public class AgentRequest
{
    /// <summary>
    /// User message/query
    /// </summary>
    [Required]
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Optional conversation ID for context
    /// </summary>
    public string? ConversationId { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
}
```

**File: `Models/AgentResponse.cs`**
```csharp
namespace AgentService.Models;

public class AgentResponse
{
    /// <summary>
    /// Response message from agent
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Status of the response
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// Type of agent that processed the request
    /// </summary>
    public string AgentType { get; set; } = string.Empty;

    /// <summary>
    /// Conversation ID
    /// </summary>
    public string? ConversationId { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
}
```

**File: `Services/IAgentService.cs`**
```csharp
namespace AgentService.Services;

public interface IAgentService
{
    Task<string> ProcessMessageAsync(string message, string? userToken = null);
    Task InitializeAsync();
}
```

### Phase 2: Agent Framework Integration

**Note:** This phase will require adding the Azure OpenAI SDK package when implemented:
```bash
dotnet add AgentService/AgentService.csproj package Azure.AI.OpenAI
```

**File: `Services/AgentService.cs`** (Conceptual - requires Azure OpenAI SDK)
```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.Configuration;

namespace AgentService.Services;

public class AgentService : IAgentService
{
    private readonly ILogger<AgentService> _logger;
    private readonly IConfiguration _configuration;
    private OpenAIClient? _client;

    public AgentService(
        ILogger<AgentService> logger,
        IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
    }

    public async Task InitializeAsync()
    {
        _logger.LogInformation("Initializing Azure OpenAI client");

        var endpoint = _configuration["AzureOpenAI:Endpoint"];
        var deploymentName = _configuration["AzureOpenAI:DeploymentName"];

        // Create credential
        var credential = GetAzureCredential();

        // Initialize Azure OpenAI client
        _client = new OpenAIClient(
            new Uri(endpoint!),
            credential
        );

        _logger.LogInformation("Azure OpenAI client initialized successfully");
    }

    public async Task<string> ProcessMessageAsync(string message, string? userToken = null)
    {
        if (_client == null)
        {
            await InitializeAsync();
        }

        _logger.LogInformation("Processing message through Azure OpenAI");

        // TODO: Implement actual Azure OpenAI chat completion call
        // This is a placeholder for Phase 2 implementation

        var response = "Agent processed response"; // Placeholder
        return response;
    }

    private TokenCredential GetAzureCredential()
    {
        var clientId = _configuration["AzureAd:ClientId"];
        var clientSecret = _configuration["AzureAd:ClientSecret"];
        var tenantId = _configuration["AzureAd:TenantId"];

        if (!string.IsNullOrEmpty(clientId) &&
            !string.IsNullOrEmpty(clientSecret) &&
            !string.IsNullOrEmpty(tenantId))
        {
            return new ClientSecretCredential(tenantId, clientId, clientSecret);
        }

        return new DefaultAzureCredential();
    }
}
```

### Phase 3: JWT Validation & OBO Flow

**File: `Services/IOboTokenService.cs`**
```csharp
namespace AgentService.Services;

public interface IOboTokenService
{
    Task<string> AcquireTokenOnBehalfOfAsync(string userToken, string[] scopes);
}
```

**File: `Services/OboTokenService.cs`**
```csharp
using Microsoft.Identity.Client;
using Microsoft.Extensions.Configuration;

namespace AgentService.Services;

public class OboTokenService : IOboTokenService
{
    private readonly ILogger<OboTokenService> _logger;
    private readonly IConfiguration _configuration;
    private readonly IConfidentialClientApplication _confidentialClient;

    public OboTokenService(
        ILogger<OboTokenService> logger,
        IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;

        var clientId = _configuration["AzureAd:ClientId"];
        var clientSecret = _configuration["AzureAd:ClientSecret"];
        var tenantId = _configuration["AzureAd:TenantId"];
        var authority = $"https://login.microsoftonline.com/{tenantId}";

        _confidentialClient = ConfidentialClientApplicationBuilder
            .Create(clientId)
            .WithClientSecret(clientSecret)
            .WithAuthority(new Uri(authority))
            .Build();
    }

    /// <summary>
    /// Acquires a token on behalf of the user using the OBO flow.
    /// This is the core implementation of JWT On-Behalf-Of authentication.
    /// </summary>
    /// <param name="userToken">The incoming user's JWT token</param>
    /// <param name="scopes">The scopes required for the downstream API</param>
    /// <returns>Access token for downstream API with user context</returns>
    public async Task<string> AcquireTokenOnBehalfOfAsync(
        string userToken,
        string[] scopes)
    {
        try
        {
            _logger.LogInformation("Acquiring OBO token for scopes: {Scopes}",
                string.Join(", ", scopes));

            // Create user assertion from the incoming token
            var userAssertion = new UserAssertion(userToken);

            // Acquire token on behalf of user
            var result = await _confidentialClient
                .AcquireTokenOnBehalfOf(scopes, userAssertion)
                .ExecuteAsync();

            _logger.LogInformation("OBO token acquired successfully");

            return result.AccessToken;
        }
        catch (MsalServiceException ex)
        {
            _logger.LogError(ex, "MSAL service exception during OBO flow");
            throw new InvalidOperationException(
                $"Failed to acquire OBO token: {ex.Message}", ex);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during OBO token acquisition");
            throw;
        }
    }
}
```

**Updated `Program.cs` with JWT Authentication**
```csharp
using AgentService.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add Microsoft Identity Web authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register application services
builder.Services.AddSingleton<IAgentService, Services.AgentService>();
builder.Services.AddSingleton<IOboTokenService, OboTokenService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### Phase 4: Full Integration

**Updated `Controllers/AgentController.cs` with Authentication**
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Identity.Web;
using AgentService.Models;
using AgentService.Services;
using System.Security.Claims;

namespace AgentService.Controllers;

[ApiController]
[Route("[controller]")]
[Authorize]  // Require authentication
public class AgentController : ControllerBase
{
    private readonly ILogger<AgentController> _logger;
    private readonly IAgentService _agentService;
    private readonly IOboTokenService _oboTokenService;

    public AgentController(
        ILogger<AgentController> logger,
        IAgentService agentService,
        IOboTokenService oboTokenService)
    {
        _logger = logger;
        _agentService = agentService;
        _oboTokenService = oboTokenService;
    }

    /// <summary>
    /// Authenticated agent endpoint with OBO flow.
    /// 1. Validates incoming JWT token (via [Authorize] attribute)
    /// 2. Acquires OBO token for downstream services
    /// 3. Processes message through Agent Framework
    /// 4. Returns response maintaining user context
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<AgentResponse>> Post(
        [FromBody] AgentRequest request)
    {
        // Extract user information from claims
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var userName = User.FindFirst(ClaimTypes.Name)?.Value;

        _logger.LogInformation(
            "Agent endpoint called by user {UserId} with message: {Message}",
            userId, request.Message);

        // Get the incoming user token
        var userToken = HttpContext.Request.Headers["Authorization"]
            .ToString().Replace("Bearer ", "");

        // Acquire OBO token for downstream API calls
        // (e.g., Microsoft Graph, custom APIs)
        var downstreamScopes = new[] { "api://your-api/.default" };
        var oboToken = await _oboTokenService.AcquireTokenOnBehalfOfAsync(
            userToken, downstreamScopes);

        // Process through agent with user context
        var responseMessage = await _agentService.ProcessMessageAsync(
            request.Message,
            oboToken);

        return Ok(new AgentResponse
        {
            Message = responseMessage,
            Status = "success",
            AgentType = "dotnet-aspnet",
            ConversationId = request.ConversationId,
            Metadata = new Dictionary<string, object>
            {
                { "userId", userId ?? "unknown" },
                { "userName", userName ?? "unknown" }
            }
        });
    }

    /// <summary>
    /// Simple GET endpoint for health checks (no auth required)
    /// </summary>
    [HttpGet]
    [AllowAnonymous]
    public ActionResult<object> Get()
    {
        return Ok(new
        {
            Message = "it's alive",
            Status = "healthy",
            AgentType = "dotnet-aspnet"
        });
    }
}
```

## Configuration Files

**File: `appsettings.json`**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "",
    "ClientId": "",
    "Audience": "api://your-api-id"
  },
  "AzureOpenAI": {
    "Endpoint": "",
    "DeploymentName": "",
    "ApiVersion": "2024-02-15-preview"
  }
}
```

**File: `appsettings.Development.json`**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.AspNetCore": "Information"
    }
  },
  "AzureAd": {
    "TenantId": "your-dev-tenant-id",
    "ClientId": "your-dev-client-id",
    "ClientSecret": "your-dev-client-secret"
  },
  "AzureOpenAI": {
    "Endpoint": "https://your-openai.openai.azure.com",
    "DeploymentName": "gpt-4"
  }
}
```

## Development Commands

```bash
# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run application
dotnet run --project AgentService

# Watch mode (auto-reload)
dotnet watch run --project AgentService

# Run tests
dotnet test

# Run specific test
dotnet test --filter "FullyQualifiedName~AgentControllerTests.Post_ReturnsSuccess"

# Clean build artifacts
dotnet clean

# Publish for deployment
dotnet publish -c Release -o ./publish

# Format code
dotnet format

# Check for outdated packages
dotnet list package --outdated

# Update package
dotnet add package Azure.AI.Agents --version 1.x.x
```

## API Endpoints

### `GET /health`
Health check endpoint (no authentication required).

**Response**:
```json
{
  "status": "healthy"
}
```

### `GET /agent`
Simple agent status check (Phase 1, no authentication).

**Response**:
```json
{
  "message": "it's alive",
  "status": "healthy",
  "agentType": "dotnet-aspnet"
}
```

### `POST /agent`
Main agent interaction endpoint (authenticated in Phase 4).

**Request**:
```json
{
  "message": "Hello, I need help with .NET",
  "conversationId": "optional-guid",
  "metadata": {}
}
```

**Response**:
```json
{
  "message": "it's alive",
  "status": "healthy",
  "agentType": "dotnet-aspnet",
  "conversationId": "optional-guid",
  "metadata": {}
}
```

**With Authentication (Phase 4)**:
```bash
curl -X POST https://localhost:5001/agent \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me with .NET"}'
```

## Security Notes

1. **Never commit** `appsettings.Development.json` with secrets to git
2. **Use User Secrets** for local development
3. **Use Azure Key Vault** for production secrets
4. **Validate all tokens** via `[Authorize]` attribute
5. **Use HTTPS** in production (enforced by default)
6. **Implement rate limiting** using ASP.NET Core middleware
7. **Enable CORS** appropriately for your frontend
8. **Log OBO exchanges** for audit trails (without exposing tokens)

## Next Steps

1. ✅ Phase 1: Basic `/agent` endpoint returning "it's alive"
2. ⏳ Phase 2: Integrate Microsoft Agent Framework
3. ⏳ Phase 3: Implement JWT validation and OBO flow
4. ⏳ Phase 4: Full multi-agent orchestration
5. ⏳ Phase 5: Production hardening and deployment

## Troubleshooting

### .NET SDK Issues
```bash
# List installed SDKs
dotnet --list-sdks

# List installed runtimes
dotnet --list-runtimes

# Clear NuGet cache
dotnet nuget locals all --clear
```

### Build Errors
```bash
# Clean and rebuild
dotnet clean
dotnet build --no-incremental

# Restore with force
dotnet restore --force
```

### Azure Authentication Issues
- Verify Azure AD app registration settings
- Check client secret hasn't expired
- Ensure correct tenant ID
- Verify API permissions are granted and admin consented
- Check `appsettings.json` configuration matches Azure AD

### Port Conflicts
```bash
# Change port in launchSettings.json or via command line
dotnet run --urls "https://localhost:5002;http://localhost:5001"
```

## References

- [.NET Documentation](https://learn.microsoft.com/en-us/dotnet/)
- [ASP.NET Core Documentation](https://learn.microsoft.com/en-us/aspnet/core/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Microsoft.Identity.Web](https://learn.microsoft.com/en-us/entra/msal/dotnet/microsoft-identity-web/)
- [MSAL.NET Documentation](https://learn.microsoft.com/en-us/entra/msal/dotnet/)
- [Azure.Identity NuGet](https://www.nuget.org/packages/Azure.Identity)
