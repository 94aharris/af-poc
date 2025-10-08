using PayrollApi.Models;

namespace PayrollApi.Services;

/// <summary>
/// In-memory payroll data service with hardcoded test data
/// In a real application, this would query a database or external API
/// </summary>
public class PayrollDataService : IPayrollDataService
{
    private readonly ILogger<PayrollDataService> _logger;

    // Hardcoded user information data (simulates database)
    private static readonly Dictionary<string, UserInfo> _userInfoData = new()
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

    // Hardcoded PTO data (simulates database)
    private static readonly Dictionary<string, UserPto> _userPtoData = new()
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

    public PayrollDataService(ILogger<PayrollDataService> logger)
    {
        _logger = logger;
    }

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
}
