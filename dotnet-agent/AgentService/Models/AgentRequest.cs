using System.ComponentModel.DataAnnotations;

namespace AgentService.Models;

public class AgentRequest
{
    /// <summary>
    /// User message/query
    /// </summary>
    [Required]
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Optional conversation ID for context
    /// </summary>
    public string? ConversationId { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, object>? Metadata { get; set; }
}
