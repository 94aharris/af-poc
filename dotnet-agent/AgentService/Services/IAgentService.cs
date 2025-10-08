namespace AgentService.Services;

public interface IAgentService
{
    Task<string> ProcessMessageAsync(string message, string? userToken = null);
    Task InitializeAsync();
}
