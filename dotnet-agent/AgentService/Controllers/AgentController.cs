using Microsoft.AspNetCore.Mvc;
using AgentService.Models;
using AgentService.Services;

namespace AgentService.Controllers;

[ApiController]
[Route("[controller]")]
public class AgentController : ControllerBase
{
    private readonly ILogger<AgentController> _logger;
    private readonly IAgentService _agentService;

    public AgentController(
        ILogger<AgentController> logger,
        IAgentService agentService)
    {
        _logger = logger;
        _agentService = agentService;
    }

    /// <summary>
    /// Main agent endpoint - receives chat requests and returns responses.
    /// Phase 1: Returns 'it's alive' message
    /// Phase 2+: Integrates with Agent Framework and OBO flow
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<AgentResponse>> Post([FromBody] AgentRequest request)
    {
        _logger.LogInformation("Agent endpoint called with message: {Message}", request.Message);

        return Ok(new AgentResponse
        {
            Message = "it's alive",
            Status = "healthy",
            AgentType = "dotnet-aspnet",
            ConversationId = request.ConversationId,
            Metadata = request.Metadata
        });
    }

    /// <summary>
    /// Simple GET endpoint for health checks
    /// </summary>
    [HttpGet]
    public ActionResult<object> Get()
    {
        return Ok(new
        {
            Message = "it's alive",
            Status = "healthy",
            AgentType = "dotnet-aspnet"
        });
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("/health")]
    public ActionResult<object> Health()
    {
        return Ok(new { Status = "healthy" });
    }
}
