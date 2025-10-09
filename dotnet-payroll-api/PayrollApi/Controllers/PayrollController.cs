using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using PayrollApi.Models;
using PayrollApi.Services;
using System.Security.Claims;

namespace PayrollApi.Controllers;

/// <summary>
/// Payroll API Controller
/// Provides secure access to user-specific payroll information
/// CRITICAL: Users can ONLY access their own data (enforced via JWT oid claim)
/// </summary>
[ApiController]
[Route("[controller]")]
public class PayrollController : ControllerBase
{
    private readonly ILogger<PayrollController> _logger;
    private readonly IPayrollDataService _payrollDataService;
    private readonly IConfiguration _configuration;

    public PayrollController(
        ILogger<PayrollController> logger,
        IPayrollDataService payrollDataService,
        IConfiguration configuration)
    {
        _logger = logger;
        _payrollDataService = payrollDataService;
        _configuration = configuration;
    }

    /// <summary>
    /// Get user information for the authenticated user
    /// </summary>
    /// <returns>User information from payroll system</returns>
    /// <response code="200">Successfully retrieved user information</response>
    /// <response code="401">Unauthorized - missing or invalid JWT token</response>
    /// <response code="403">Forbidden - attempting to access another user's data</response>
    /// <response code="404">User not found in payroll system</response>
    [HttpGet("user-info")]
    [Authorize]
    [ProducesResponseType(typeof(UserInfo), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status403Forbidden)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserInfo>> GetUserInfo([FromQuery] string? userId = null)
    {
        _logger.LogInformation("========================================");
        _logger.LogInformation("GET /payroll/user-info - Request received");

        var authHeader = Request.Headers["Authorization"].ToString();
        _logger.LogInformation("Auth header present: {HasAuth}", Request.Headers.ContainsKey("Authorization"));
        if (!string.IsNullOrEmpty(authHeader))
        {
            var tokenPreview = authHeader.Length > 50 ? authHeader.Substring(0, 50) + "..." : authHeader;
            _logger.LogInformation("Auth header value: {AuthHeader}", tokenPreview);
        }

        // Extract user email from JWT token
        var currentUserEmail = GetCurrentUserEmail();

        if (string.IsNullOrEmpty(currentUserEmail))
        {
            _logger.LogWarning("User email not found in JWT token");
            return Unauthorized(new ErrorResponse
            {
                Error = "User email not found in token",
                StatusCode = 401,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("Looking up user by email: {Email}", currentUserEmail);

        // Retrieve user information by email
        var userInfo = await _payrollDataService.GetUserInfoByEmailAsync(currentUserEmail);

        if (userInfo == null)
        {
            _logger.LogWarning("User not found in payroll system: {Email}", currentUserEmail);
            return NotFound(new ErrorResponse
            {
                Error = $"User not found in payroll system for email: {currentUserEmail}",
                StatusCode = 404,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("User info retrieved successfully for user: {Email}", currentUserEmail);
        return Ok(userInfo);
    }

    /// <summary>
    /// Get PTO (Paid Time Off) balance and history for the authenticated user
    /// </summary>
    /// <returns>User PTO data from payroll system</returns>
    /// <response code="200">Successfully retrieved PTO information</response>
    /// <response code="401">Unauthorized - missing or invalid JWT token</response>
    /// <response code="403">Forbidden - attempting to access another user's data</response>
    /// <response code="404">User not found in payroll system</response>
    [HttpGet("user-pto")]
    [Authorize]
    [ProducesResponseType(typeof(UserPto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status403Forbidden)]
    [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserPto>> GetUserPto([FromQuery] string? userId = null)
    {
        _logger.LogInformation("========================================");
        _logger.LogInformation("GET /payroll/user-pto - Request received");
        _logger.LogInformation("Auth header present: {HasAuth}", Request.Headers.ContainsKey("Authorization"));

        // Extract user email from JWT token
        var currentUserEmail = GetCurrentUserEmail();

        if (string.IsNullOrEmpty(currentUserEmail))
        {
            _logger.LogWarning("User email not found in JWT token");
            return Unauthorized(new ErrorResponse
            {
                Error = "User email not found in token",
                StatusCode = 401,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("Looking up PTO for user by email: {Email}", currentUserEmail);

        // Retrieve PTO data by email
        var userPto = await _payrollDataService.GetUserPtoByEmailAsync(currentUserEmail);

        if (userPto == null)
        {
            _logger.LogWarning("PTO data not found for user: {Email}", currentUserEmail);
            return NotFound(new ErrorResponse
            {
                Error = $"PTO data not found in payroll system for email: {currentUserEmail}",
                StatusCode = 404,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("PTO data retrieved successfully for user: {Email}", currentUserEmail);
        return Ok(userPto);
    }

    /// <summary>
    /// Health check endpoint (no authentication required)
    /// </summary>
    [HttpGet("/health")]
    [AllowAnonymous]
    public ActionResult<object> Health()
    {
        return Ok(new
        {
            Status = "healthy",
            Service = "payroll-api",
            Timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Root endpoint with service information (no authentication required)
    /// </summary>
    [HttpGet("/")]
    [AllowAnonymous]
    public ActionResult<object> Root()
    {
        var requireAuth = _configuration.GetValue<bool>("Auth:RequireAuthentication", true);

        return Ok(new
        {
            Service = "Payroll API",
            Version = "1.0.0",
            Description = "Secure payroll API demonstrating JWT OBO flow",
            Endpoints = new
            {
                UserInfo = "GET /payroll/user-info",
                UserPto = "GET /payroll/user-pto",
                Health = "GET /health"
            },
            Configuration = new
            {
                AuthenticationRequired = requireAuth,
                HttpPort = 5100,
                HttpsPort = 5101
            }
        });
    }

    /// <summary>
    /// Extract user email from JWT token claims
    /// Uses 'preferred_username' or 'email' claim to identify the user
    /// </summary>
    private string? GetCurrentUserEmail()
    {
        // For testing mode without authentication
        var requireAuth = _configuration.GetValue<bool>("Auth:RequireAuthentication", true);

        _logger.LogInformation("🔍 GetCurrentUserEmail called");
        _logger.LogInformation("  RequireAuth config value: {RequireAuth}", requireAuth);
        _logger.LogInformation("  User.Identity.IsAuthenticated: {IsAuth}", User?.Identity?.IsAuthenticated ?? false);
        _logger.LogInformation("  Claims count: {Count}", User?.Claims?.Count() ?? 0);

        if (!requireAuth)
        {
            // Return mock user for testing
            _logger.LogWarning("Running in TEST MODE - using mock user email");
            return "alice.johnson@contoso.com"; // Alice Johnson
        }

        // Log all claims for debugging
        _logger.LogInformation("=== JWT Token Claims ===");
        foreach (var claim in User.Claims)
        {
            _logger.LogInformation("  Claim: {Type} = {Value}", claim.Type, claim.Value);
        }
        _logger.LogInformation("========================");

        // Try to get 'preferred_username' claim first (commonly used for email in Azure AD)
        var preferredUsername = User.FindFirst("preferred_username")?.Value;
        if (!string.IsNullOrEmpty(preferredUsername))
        {
            _logger.LogInformation("✓ Found user email in 'preferred_username' claim: {Email}", preferredUsername);
            return preferredUsername;
        }
        else
        {
            _logger.LogWarning("⚠ 'preferred_username' claim not found in token");
        }

        // Fallback to 'email' claim
        var email = User.FindFirst("email")?.Value;
        if (!string.IsNullOrEmpty(email))
        {
            _logger.LogInformation("✓ Found user email in 'email' claim: {Email}", email);
            return email;
        }
        else
        {
            _logger.LogWarning("⚠ 'email' claim not found in token");
        }

        // Fallback to ClaimTypes.Email
        var claimsEmail = User.FindFirst(ClaimTypes.Email)?.Value;
        if (!string.IsNullOrEmpty(claimsEmail))
        {
            _logger.LogInformation("✓ Found user email in ClaimTypes.Email: {Email}", claimsEmail);
            return claimsEmail;
        }
        else
        {
            _logger.LogWarning("⚠ ClaimTypes.Email not found in token");
        }

        // Fallback to upn (User Principal Name)
        var upn = User.FindFirst("upn")?.Value;
        if (!string.IsNullOrEmpty(upn))
        {
            _logger.LogInformation("✓ Found user email in 'upn' claim: {Email}", upn);
            return upn;
        }
        else
        {
            _logger.LogWarning("⚠ 'upn' claim not found in token");
        }

        _logger.LogError("❌ No user email found in any claim (preferred_username, email, upn)");
        return null;
    }
}
