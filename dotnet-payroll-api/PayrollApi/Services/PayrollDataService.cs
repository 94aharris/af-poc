using Microsoft.Extensions.Options;
using PayrollApi.Configuration;
using PayrollApi.Models;

namespace PayrollApi.Services;

/// <summary>
/// In-memory payroll data service with hardcoded test data
/// In a real application, this would query a database or external API
/// </summary>
public class PayrollDataService : IPayrollDataService
{
    private readonly ILogger<PayrollDataService> _logger;
    private readonly Dictionary<string, UserInfo> _userInfoData;
    private readonly Dictionary<string, UserPto> _userPtoData;

    public PayrollDataService(
        ILogger<PayrollDataService> logger,
        IOptions<DeveloperUserConfiguration> developerUserConfig)
    {
        _logger = logger;

        // Initialize with example data
        _userInfoData = GetExampleUserInfoData();
        _userPtoData = GetExampleUserPtoData();

        // Add developer user if configured
        var devConfig = developerUserConfig.Value;
        if (devConfig.Enabled && !string.IsNullOrWhiteSpace(devConfig.Email))
        {
            _logger.LogInformation("Adding developer user from configuration: {Email}", devConfig.Email);

            var devUserInfo = new UserInfo
            {
                UserId = devConfig.UserId,
                Name = devConfig.Name,
                Email = devConfig.Email,
                Department = devConfig.Department,
                EmployeeId = devConfig.EmployeeId,
                JobTitle = devConfig.JobTitle,
                Manager = devConfig.Manager,
                HireDate = DateTime.TryParse(devConfig.HireDate, out var hireDate)
                    ? hireDate
                    : DateTime.Now
            };

            var devUserPto = new UserPto
            {
                UserId = devConfig.UserId,
                CurrentBalanceHours = devConfig.PtoBalance.CurrentBalanceHours,
                AccruedThisYearHours = devConfig.PtoBalance.AccruedThisYearHours,
                UsedThisYearHours = devConfig.PtoBalance.UsedThisYearHours,
                PendingRequestsHours = devConfig.PtoBalance.PendingRequestsHours,
                MaxCarryoverHours = devConfig.PtoBalance.MaxCarryoverHours,
                UpcomingPto = new List<PtoRequest>
                {
                    new PtoRequest
                    {
                        StartDate = DateTime.Now.AddDays(14),
                        EndDate = DateTime.Now.AddDays(16),
                        Hours = 24.0m,
                        Status = "Pending",
                        Type = "Vacation"
                    }
                }
            };

            _userInfoData[devConfig.UserId] = devUserInfo;
            _userPtoData[devConfig.UserId] = devUserPto;
        }
    }

    // Hardcoded example user information data (simulates database)
    // For testing with your own email, add it to appsettings.Development.json under DeveloperUser section
    private static Dictionary<string, UserInfo> GetExampleUserInfoData() => new()
    {
        ["00000000-0000-0000-0000-000000000001"] = new UserInfo
        {
            UserId = "00000000-0000-0000-0000-000000000001",
            Name = "Alice Johnson",
            Email = "alice.johnson@contoso.com",
            Department = "Engineering",
            EmployeeId = "EMP001",
            JobTitle = "Senior Software Engineer",
            Manager = "David Chen",
            HireDate = new DateTime(2020, 3, 15)
        },
        ["00000000-0000-0000-0000-000000000002"] = new UserInfo
        {
            UserId = "00000000-0000-0000-0000-000000000002",
            Name = "Bob Smith",
            Email = "bob.smith@contoso.com",
            Department = "Marketing",
            EmployeeId = "EMP002",
            JobTitle = "Marketing Manager",
            Manager = "Sarah Williams",
            HireDate = new DateTime(2019, 7, 1)
        },
        ["00000000-0000-0000-0000-000000000003"] = new UserInfo
        {
            UserId = "00000000-0000-0000-0000-000000000003",
            Name = "Carol Williams",
            Email = "carol.williams@contoso.com",
            Department = "Sales",
            EmployeeId = "EMP003",
            JobTitle = "Sales Director",
            Manager = "Michael Brown",
            HireDate = new DateTime(2018, 1, 10)
        },
        ["00000000-0000-0000-0000-000000000004"] = new UserInfo
        {
            UserId = "00000000-0000-0000-0000-000000000004",
            Name = "David Chen",
            Email = "david.chen@contoso.com",
            Department = "Engineering",
            EmployeeId = "EMP004",
            JobTitle = "VP of Engineering",
            Manager = "CEO",
            HireDate = new DateTime(2017, 5, 20)
        },
        ["00000000-0000-0000-0000-000000000005"] = new UserInfo
        {
            UserId = "00000000-0000-0000-0000-000000000005",
            Name = "Emma Davis",
            Email = "emma.davis@contoso.com",
            Department = "Human Resources",
            EmployeeId = "EMP005",
            JobTitle = "HR Business Partner",
            Manager = "Sarah Williams",
            HireDate = new DateTime(2021, 9, 1)
        }
    };

    // Hardcoded example PTO data (simulates database)
    // NOTE: Keys must match the UserInfo dictionary keys
    // For testing with your own email, add it to appsettings.Development.json under DeveloperUser section
    private static Dictionary<string, UserPto> GetExampleUserPtoData() => new()
    {
        ["00000000-0000-0000-0000-000000000001"] = new UserPto
        {
            UserId = "00000000-0000-0000-0000-000000000001",
            CurrentBalanceHours = 120.0m,
            AccruedThisYearHours = 160.0m,
            UsedThisYearHours = 40.0m,
            PendingRequestsHours = 16.0m,
            MaxCarryoverHours = 80.0m,
            UpcomingPto = new List<PtoRequest>
            {
                new PtoRequest
                {
                    StartDate = DateTime.Now.AddDays(30),
                    EndDate = DateTime.Now.AddDays(32),
                    Hours = 16.0m,
                    Status = "Approved",
                    Type = "Vacation"
                }
            }
        },
        ["00000000-0000-0000-0000-000000000002"] = new UserPto
        {
            UserId = "00000000-0000-0000-0000-000000000002",
            CurrentBalanceHours = 80.0m,
            AccruedThisYearHours = 120.0m,
            UsedThisYearHours = 40.0m,
            PendingRequestsHours = 8.0m,
            MaxCarryoverHours = 80.0m,
            UpcomingPto = new List<PtoRequest>
            {
                new PtoRequest
                {
                    StartDate = DateTime.Now.AddDays(15),
                    EndDate = DateTime.Now.AddDays(15),
                    Hours = 8.0m,
                    Status = "Pending",
                    Type = "Personal"
                }
            }
        },
        ["00000000-0000-0000-0000-000000000003"] = new UserPto
        {
            UserId = "00000000-0000-0000-0000-000000000003",
            CurrentBalanceHours = 100.0m,
            AccruedThisYearHours = 160.0m,
            UsedThisYearHours = 60.0m,
            PendingRequestsHours = 0.0m,
            MaxCarryoverHours = 80.0m,
            UpcomingPto = new List<PtoRequest>
            {
                new PtoRequest
                {
                    StartDate = DateTime.Now.AddDays(45),
                    EndDate = DateTime.Now.AddDays(49),
                    Hours = 32.0m,
                    Status = "Approved",
                    Type = "Vacation"
                }
            }
        },
        ["00000000-0000-0000-0000-000000000004"] = new UserPto
        {
            UserId = "00000000-0000-0000-0000-000000000004",
            CurrentBalanceHours = 200.0m,
            AccruedThisYearHours = 240.0m,
            UsedThisYearHours = 40.0m,
            PendingRequestsHours = 0.0m,
            MaxCarryoverHours = 160.0m,
            UpcomingPto = new List<PtoRequest>()
        },
        ["00000000-0000-0000-0000-000000000005"] = new UserPto
        {
            UserId = "00000000-0000-0000-0000-000000000005",
            CurrentBalanceHours = 64.0m,
            AccruedThisYearHours = 80.0m,
            UsedThisYearHours = 16.0m,
            PendingRequestsHours = 0.0m,
            MaxCarryoverHours = 40.0m,
            UpcomingPto = new List<PtoRequest>
            {
                new PtoRequest
                {
                    StartDate = DateTime.Now.AddDays(7),
                    EndDate = DateTime.Now.AddDays(7),
                    Hours = 8.0m,
                    Status = "Approved",
                    Type = "Sick"
                }
            }
        }
    };

    /// <summary>
    /// Get user information by user ID
    /// </summary>
    public Task<UserInfo?> GetUserInfoAsync(string userId)
    {
        _logger.LogInformation("Retrieving user info for user ID: {UserId}", userId);

        if (_userInfoData.TryGetValue(userId, out var userInfo))
        {
            _logger.LogInformation("User info found for user ID: {UserId}", userId);
            return Task.FromResult<UserInfo?>(userInfo);
        }

        _logger.LogWarning("User info not found for user ID: {UserId}", userId);
        return Task.FromResult<UserInfo?>(null);
    }

    /// <summary>
    /// Get user PTO balance and history by user ID
    /// </summary>
    public Task<UserPto?> GetUserPtoAsync(string userId)
    {
        _logger.LogInformation("Retrieving PTO data for user ID: {UserId}", userId);

        if (_userPtoData.TryGetValue(userId, out var userPto))
        {
            _logger.LogInformation("PTO data found for user ID: {UserId}", userId);
            return Task.FromResult<UserPto?>(userPto);
        }

        _logger.LogWarning("PTO data not found for user ID: {UserId}", userId);
        return Task.FromResult<UserPto?>(null);
    }

    /// <summary>
    /// Get user information by email address
    /// </summary>
    public Task<UserInfo?> GetUserInfoByEmailAsync(string email)
    {
        _logger.LogInformation("Retrieving user info for email: {Email}", email);

        var userInfo = _userInfoData.Values.FirstOrDefault(u =>
            u.Email.Equals(email, StringComparison.OrdinalIgnoreCase));

        if (userInfo != null)
        {
            _logger.LogInformation("User info found for email: {Email}", email);
            return Task.FromResult<UserInfo?>(userInfo);
        }

        _logger.LogWarning("User info not found for email: {Email}", email);
        return Task.FromResult<UserInfo?>(null);
    }

    /// <summary>
    /// Get user PTO balance and history by email address
    /// </summary>
    public Task<UserPto?> GetUserPtoByEmailAsync(string email)
    {
        _logger.LogInformation("Retrieving PTO data for email: {Email}", email);

        // First find the user by email to get their userId
        var userInfo = _userInfoData.Values.FirstOrDefault(u =>
            u.Email.Equals(email, StringComparison.OrdinalIgnoreCase));

        if (userInfo == null)
        {
            _logger.LogWarning("User not found for email: {Email}", email);
            return Task.FromResult<UserPto?>(null);
        }

        // Then get their PTO data using userId
        if (_userPtoData.TryGetValue(userInfo.UserId, out var userPto))
        {
            _logger.LogInformation("PTO data found for email: {Email}", email);
            return Task.FromResult<UserPto?>(userPto);
        }

        _logger.LogWarning("PTO data not found for email: {Email}", email);
        return Task.FromResult<UserPto?>(null);
    }
}
