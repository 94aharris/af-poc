namespace PayrollApi.Configuration;

/// <summary>
/// Configuration for developer user that can be set in appsettings.Development.json
/// This allows developers to test with their own email without committing personal info
/// </summary>
public class DeveloperUserConfiguration
{
    /// <summary>
    /// Whether to add the developer user to the in-memory data store
    /// </summary>
    public bool Enabled { get; set; }

    /// <summary>
    /// User ID for the developer user
    /// </summary>
    public string UserId { get; set; } = string.Empty;

    /// <summary>
    /// Full name of the developer user
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Email address of the developer user (should match Azure AD token)
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// Department the developer user belongs to
    /// </summary>
    public string Department { get; set; } = string.Empty;

    /// <summary>
    /// Employee ID for the developer user
    /// </summary>
    public string EmployeeId { get; set; } = string.Empty;

    /// <summary>
    /// Job title of the developer user
    /// </summary>
    public string JobTitle { get; set; } = string.Empty;

    /// <summary>
    /// Manager name for the developer user
    /// </summary>
    public string Manager { get; set; } = string.Empty;

    /// <summary>
    /// Hire date for the developer user
    /// </summary>
    public string HireDate { get; set; } = DateTime.Now.ToString("yyyy-MM-dd");

    /// <summary>
    /// PTO balance configuration for the developer user
    /// </summary>
    public PtoBalanceConfiguration PtoBalance { get; set; } = new();
}

/// <summary>
/// Configuration for developer user's PTO balance
/// </summary>
public class PtoBalanceConfiguration
{
    public decimal CurrentBalanceHours { get; set; } = 240.0m;
    public decimal AccruedThisYearHours { get; set; } = 240.0m;
    public decimal UsedThisYearHours { get; set; } = 0.0m;
    public decimal PendingRequestsHours { get; set; } = 0.0m;
    public decimal MaxCarryoverHours { get; set; } = 80.0m;
}
