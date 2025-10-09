using System.ComponentModel;
using System.Text.Json;

namespace AgentService.Tools;

/// <summary>
/// Payroll-specific tools for the agent to interact with the Payroll API.
/// These tools enable the agent to retrieve employee payroll and PTO information.
/// </summary>
public class PayrollTools
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _configuration;
    private readonly ILogger<PayrollTools> _logger;
    private readonly string _payrollApiUrl;

    public PayrollTools(
        IHttpClientFactory httpClientFactory,
        IConfiguration configuration,
        ILogger<PayrollTools> logger)
    {
        _httpClientFactory = httpClientFactory;
        _configuration = configuration;
        _logger = logger;
        _payrollApiUrl = configuration["PayrollApi:Url"] ?? "http://localhost:5100";
    }

    /// <summary>
    /// Get user information from the payroll system.
    /// </summary>
    /// <param name="userToken">Optional authentication token for the user</param>
    /// <returns>JSON string containing user information including name, email, department, job title, manager, and hire date</returns>
    [Description("Get user information from the payroll system including name, email, department, job title, manager, and hire date")]
    public async Task<string> GetUserInfo(
        [Description("Optional authentication token for the user")] string? userToken = null)
    {
        try
        {
            var client = _httpClientFactory.CreateClient();

            // Add authorization header if token is provided
            if (!string.IsNullOrEmpty(userToken))
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {userToken}");
            }

            var response = await client.GetAsync($"{_payrollApiUrl}/payroll/user-info");

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Failed to get user info: {StatusCode} - {Error}",
                    response.StatusCode, errorContent);
                return JsonSerializer.Serialize(new {
                    error = $"Failed to retrieve user information: {response.StatusCode}",
                    details = errorContent
                });
            }

            var content = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Successfully retrieved user info");
            return content;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception while getting user info");
            return JsonSerializer.Serialize(new {
                error = "An error occurred while retrieving user information",
                exception = ex.Message
            });
        }
    }

    /// <summary>
    /// Get PTO (Paid Time Off) balance and upcoming time off for the user.
    /// </summary>
    /// <param name="userToken">Optional authentication token for the user</param>
    /// <returns>JSON string containing PTO balance information including current balance, accrued this year, used this year, pending requests, max carryover, and upcoming PTO</returns>
    [Description("Get PTO (Paid Time Off) balance and upcoming time off including current balance hours, accrued hours, used hours, pending requests, and upcoming scheduled PTO")]
    public async Task<string> GetUserPto(
        [Description("Optional authentication token for the user")] string? userToken = null)
    {
        try
        {
            var client = _httpClientFactory.CreateClient();

            // Add authorization header if token is provided
            if (!string.IsNullOrEmpty(userToken))
            {
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {userToken}");
            }

            var response = await client.GetAsync($"{_payrollApiUrl}/payroll/user-pto");

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError("Failed to get PTO info: {StatusCode} - {Error}",
                    response.StatusCode, errorContent);
                return JsonSerializer.Serialize(new {
                    error = $"Failed to retrieve PTO information: {response.StatusCode}",
                    details = errorContent
                });
            }

            var content = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Successfully retrieved PTO info");
            return content;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception while getting PTO info");
            return JsonSerializer.Serialize(new {
                error = "An error occurred while retrieving PTO information",
                exception = ex.Message
            });
        }
    }

    /// <summary>
    /// Calculate how many PTO days/hours are available for use.
    /// </summary>
    /// <param name="userToken">Optional authentication token for the user</param>
    /// <returns>JSON string with available PTO calculation (current balance minus pending requests)</returns>
    [Description("Calculate the available PTO (not including pending requests) that the user can actually use")]
    public async Task<string> CalculateAvailablePto(
        [Description("Optional authentication token for the user")] string? userToken = null)
    {
        try
        {
            var ptoJson = await GetUserPto(userToken);
            var ptoData = JsonSerializer.Deserialize<JsonElement>(ptoJson);

            if (ptoData.TryGetProperty("error", out _))
            {
                return ptoJson; // Return error as-is
            }

            var currentBalance = ptoData.GetProperty("currentBalanceHours").GetDouble();
            var pendingRequests = ptoData.GetProperty("pendingRequestsHours").GetDouble();
            var available = currentBalance - pendingRequests;

            var result = new
            {
                currentBalanceHours = currentBalance,
                pendingRequestsHours = pendingRequests,
                availableForUseHours = available,
                availableForUseDays = available / 8.0, // Assuming 8-hour workday
                message = $"You have {available} hours ({available / 8.0:F1} days) of PTO available for use"
            };

            return JsonSerializer.Serialize(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Exception while calculating available PTO");
            return JsonSerializer.Serialize(new {
                error = "An error occurred while calculating available PTO",
                exception = ex.Message
            });
        }
    }
}
