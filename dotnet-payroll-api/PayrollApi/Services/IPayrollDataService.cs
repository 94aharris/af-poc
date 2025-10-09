using PayrollApi.Models;

namespace PayrollApi.Services;

/// <summary>
/// Service interface for accessing payroll data
/// </summary>
public interface IPayrollDataService
{
    /// <summary>
    /// Get user information by user ID
    /// </summary>
    /// <param name="userId">Azure AD User Object ID (oid claim)</param>
    /// <returns>User information or null if not found</returns>
    Task<UserInfo?> GetUserInfoAsync(string userId);

    /// <summary>
    /// Get user PTO balance and history by user ID
    /// </summary>
    /// <param name="userId">Azure AD User Object ID (oid claim)</param>
    /// <returns>User PTO data or null if not found</returns>
    Task<UserPto?> GetUserPtoAsync(string userId);

    /// <summary>
    /// Get user information by email address
    /// </summary>
    /// <param name="email">User's email address (from preferred_username or email claim)</param>
    /// <returns>User information or null if not found</returns>
    Task<UserInfo?> GetUserInfoByEmailAsync(string email);

    /// <summary>
    /// Get user PTO balance and history by email address
    /// </summary>
    /// <param name="email">User's email address (from preferred_username or email claim)</param>
    /// <returns>User PTO data or null if not found</returns>
    Task<UserPto?> GetUserPtoByEmailAsync(string email);
}
