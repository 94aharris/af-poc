namespace PayrollApi.Models;

/// <summary>
/// User PTO (Paid Time Off) balance and history
/// </summary>
public class UserPto
{
    /// <summary>
    /// Azure AD User Object ID (oid claim from JWT)
    /// </summary>
    public string UserId { get; set; } = string.Empty;

    /// <summary>
    /// Current PTO balance in hours
    /// </summary>
    public decimal CurrentBalanceHours { get; set; }

    /// <summary>
    /// Total PTO accrued this year in hours
    /// </summary>
    public decimal AccruedThisYearHours { get; set; }

    /// <summary>
    /// Total PTO used this year in hours
    /// </summary>
    public decimal UsedThisYearHours { get; set; }

    /// <summary>
    /// Pending PTO requests in hours
    /// </summary>
    public decimal PendingRequestsHours { get; set; }

    /// <summary>
    /// Maximum PTO carryover allowed in hours
    /// </summary>
    public decimal MaxCarryoverHours { get; set; }

    /// <summary>
    /// List of upcoming PTO
    /// </summary>
    public List<PtoRequest>? UpcomingPto { get; set; }
}

/// <summary>
/// Individual PTO request details
/// </summary>
public class PtoRequest
{
    /// <summary>
    /// Start date of PTO
    /// </summary>
    public DateTime StartDate { get; set; }

    /// <summary>
    /// End date of PTO
    /// </summary>
    public DateTime EndDate { get; set; }

    /// <summary>
    /// Total hours requested
    /// </summary>
    public decimal Hours { get; set; }

    /// <summary>
    /// Status: Approved, Pending, Denied
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// PTO type: Vacation, Sick, Personal
    /// </summary>
    public string Type { get; set; } = string.Empty;
}
