namespace AgentService.Models;

public class AgentResponse
{
    /// <summary>
    /// Response message from agent
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Status of the response
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// Type of agent that processed the request
    /// </summary>
    public string AgentType { get; set; } = string.Empty;

    /// <summary>
    /// Conversation ID
    /// </summary>
    public string? ConversationId { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
}
