namespace PayrollApi.Models;

/// <summary>
/// User information from payroll system
/// </summary>
public class UserInfo
{
    /// <summary>
    /// Azure AD User Object ID (oid claim from JWT)
    /// </summary>
    public string UserId { get; set; } = string.Empty;

    /// <summary>
    /// Full name of the employee
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Email address
    /// </summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// Department
    /// </summary>
    public string Department { get; set; } = string.Empty;

    /// <summary>
    /// Employee ID
    /// </summary>
    public string EmployeeId { get; set; } = string.Empty;

    /// <summary>
    /// Job title
    /// </summary>
    public string JobTitle { get; set; } = string.Empty;

    /// <summary>
    /// Manager name
    /// </summary>
    public string? Manager { get; set; }

    /// <summary>
    /// Hire date
    /// </summary>
    public DateTime HireDate { get; set; }
}
