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
        // Extract user ID from JWT token (oid claim = Azure AD Object ID)
        var currentUserId = GetCurrentUserId();

        if (string.IsNullOrEmpty(currentUserId))
        {
            _logger.LogWarning("User identity not found in JWT token");
            return Unauthorized(new ErrorResponse
            {
                Error = "User identity not found in token",
                StatusCode = 401,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        // CRITICAL SECURITY CHECK: Prevent users from accessing other users' data
        // If userId query parameter is provided, it must match the authenticated user
        if (userId != null && userId != currentUserId)
        {
            _logger.LogWarning(
                "SECURITY: User {CurrentUserId} attempted to access user info for {RequestedUserId}",
                currentUserId, userId);

            return StatusCode(StatusCodes.Status403Forbidden, new ErrorResponse
            {
                Error = "Access denied. You can only access your own information.",
                StatusCode = 403,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        // Retrieve user information
        var userInfo = await _payrollDataService.GetUserInfoAsync(currentUserId);

        if (userInfo == null)
        {
            _logger.LogWarning("User not found in payroll system: {UserId}", currentUserId);
            return NotFound(new ErrorResponse
            {
                Error = "User not found in payroll system",
                StatusCode = 404,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("User info retrieved successfully for user: {UserId}", currentUserId);
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
        // Extract user ID from JWT token (oid claim = Azure AD Object ID)
        var currentUserId = GetCurrentUserId();

        if (string.IsNullOrEmpty(currentUserId))
        {
            _logger.LogWarning("User identity not found in JWT token");
            return Unauthorized(new ErrorResponse
            {
                Error = "User identity not found in token",
                StatusCode = 401,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        // CRITICAL SECURITY CHECK: Prevent users from accessing other users' data
        // If userId query parameter is provided, it must match the authenticated user
        if (userId != null && userId != currentUserId)
        {
            _logger.LogWarning(
                "SECURITY: User {CurrentUserId} attempted to access PTO data for {RequestedUserId}",
                currentUserId, userId);

            return StatusCode(StatusCodes.Status403Forbidden, new ErrorResponse
            {
                Error = "Access denied. You can only access your own PTO information.",
                StatusCode = 403,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        // Retrieve PTO data
        var userPto = await _payrollDataService.GetUserPtoAsync(currentUserId);

        if (userPto == null)
        {
            _logger.LogWarning("PTO data not found for user: {UserId}", currentUserId);
            return NotFound(new ErrorResponse
            {
                Error = "PTO data not found in payroll system",
                StatusCode = 404,
                RequestId = HttpContext.TraceIdentifier
            });
        }

        _logger.LogInformation("PTO data retrieved successfully for user: {UserId}", currentUserId);
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
    /// Extract user ID from JWT token claims
    /// Uses the 'oid' claim (Azure AD Object ID) or falls back to NameIdentifier
    /// </summary>
    private string? GetCurrentUserId()
    {
        // For testing mode without authentication
        var requireAuth = _configuration.GetValue<bool>("Auth:RequireAuthentication", true);
        if (!requireAuth)
        {
            // Return mock user for testing
            _logger.LogWarning("Running in TEST MODE - using mock user ID");
            return "00000000-0000-0000-0000-000000000001"; // Alice Johnson
        }

        // Try to get 'oid' claim first (Azure AD Object ID)
        var oid = User.FindFirst("oid")?.Value;
        if (!string.IsNullOrEmpty(oid))
        {
            return oid;
        }

        // Fallback to standard NameIdentifier claim
        var nameIdentifier = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!string.IsNullOrEmpty(nameIdentifier))
        {
            return nameIdentifier;
        }

        // Fallback to 'sub' claim (Subject)
        var sub = User.FindFirst("sub")?.Value;
        if (!string.IsNullOrEmpty(sub))
        {
            return sub;
        }

        return null;
    }
}
