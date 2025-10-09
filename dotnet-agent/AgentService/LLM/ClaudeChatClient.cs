using Microsoft.Extensions.AI;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;

namespace AgentService.LLM;

/// <summary>
/// Custom IChatClient implementation that wraps Claude Code CLI for local LLM usage.
/// This allows using Claude Code in headless mode as the underlying LLM for the agent framework.
/// </summary>
public sealed class ClaudeChatClient : IChatClient
{
    private readonly ILogger<ClaudeChatClient> _logger;
    private readonly Dictionary<string, string> _sessionCache = new();
    private readonly string _modelId;

    public ClaudeChatClient(ILogger<ClaudeChatClient> logger, string modelId = "claude-sonnet-4")
    {
        _logger = logger;
        _modelId = modelId;
        Metadata = new ChatClientMetadata("Claude", new Uri("https://claude.ai"), _modelId);
    }

    public ChatClientMetadata Metadata { get; }

    public async Task<ChatResponse> GetResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var messagesList = chatMessages.ToList();
            _logger.LogInformation("🔍 ClaudeChatClient: Processing request with {MessageCount} messages", messagesList.Count);

            // Extract tools from ChatOptions if available
            var toolDescriptions = ExtractToolDescriptions(options);

            if (toolDescriptions.Count > 0)
            {
                _logger.LogInformation("🔍 DEBUG: Found {Count} tools in ChatOptions", toolDescriptions.Count);
            }

            // Build the prompt from chat messages, injecting tool descriptions
            var prompt = BuildPromptFromMessages(messagesList, toolDescriptions);

            // 🔍 DEBUG: Log the full prompt being sent to Claude
            _logger.LogInformation("🔍 DEBUG: Prompt to be sent to Claude CLI:");
            _logger.LogInformation("🔍 ================================================");
            _logger.LogInformation("{Prompt}", prompt);
            _logger.LogInformation("🔍 ================================================");
            _logger.LogInformation("🔍 Prompt length: {Length} characters", prompt.Length);

            // Get conversation ID from options metadata if available
            string? conversationId = options?.AdditionalProperties?.TryGetValue("conversation_id", out var convId) == true
                ? convId?.ToString()
                : null;

            // Execute Claude CLI
            var (response, sessionId) = await ExecuteClaudeCLI(prompt, conversationId, cancellationToken);

            // Cache session ID for conversation continuity
            if (!string.IsNullOrEmpty(sessionId) && !string.IsNullOrEmpty(conversationId))
            {
                _sessionCache[conversationId] = sessionId;
            }

            _logger.LogInformation("🔍 ClaudeChatClient: Successfully received response ({Length} chars)", response.Length);

            // 🔍 DEBUG: Log the response from Claude
            _logger.LogInformation("🔍 DEBUG: Response from Claude CLI:");
            _logger.LogInformation("🔍 ================================================");
            _logger.LogInformation("{Response}", response);
            _logger.LogInformation("🔍 ================================================");

            // Return ChatResponse
            return new ChatResponse(
                new ChatMessage(ChatRole.Assistant, response))
            {
                ModelId = _modelId,
                FinishReason = ChatFinishReason.Stop
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "ClaudeChatClient: Error processing request");
            throw;
        }
    }

    public async IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        // Claude CLI doesn't support true streaming, so we simulate it
        // by getting the full response and yielding it in chunks
        _logger.LogInformation("ClaudeChatClient: Streaming mode (simulated)");

        var response = await GetResponseAsync(chatMessages, options, cancellationToken);

        // Get the text from the response
        var text = response.Text ?? string.Empty;

        // Split response into words for streaming simulation
        var words = text.Split(' ', StringSplitOptions.RemoveEmptyEntries);

        foreach (var word in words)
        {
            await Task.Delay(50, cancellationToken); // Simulate streaming delay
            yield return new ChatResponseUpdate(ChatRole.Assistant, word + " ");
        }
    }

    private List<string> ExtractToolDescriptions(ChatOptions? options)
    {
        var descriptions = new List<string>();

        if (options?.Tools == null || options.Tools.Count == 0)
        {
            _logger.LogInformation("🔍 DEBUG: No tools found in ChatOptions");
            return descriptions;
        }

        _logger.LogInformation("🔍 DEBUG: Extracting tool descriptions from {Count} tools", options.Tools.Count);

        foreach (var tool in options.Tools)
        {
            try
            {
                var toolName = tool.GetType().GetProperty("Name")?.GetValue(tool)?.ToString() ?? "UnknownTool";
                var toolDesc = tool.GetType().GetProperty("Description")?.GetValue(tool)?.ToString() ?? "No description";

                // Try to get parameters if available
                var parameters = new List<string>();
                var parametersProperty = tool.GetType().GetProperty("Parameters");
                if (parametersProperty != null)
                {
                    var paramValue = parametersProperty.GetValue(tool);
                    if (paramValue != null)
                    {
                        // Try to extract parameter information
                        var paramProps = paramValue.GetType().GetProperties();
                        foreach (var prop in paramProps)
                        {
                            parameters.Add($"  - {prop.Name}: {prop.PropertyType.Name}");
                        }
                    }
                }

                var toolDescription = new StringBuilder();
                toolDescription.AppendLine($"Tool: {toolName}");
                toolDescription.AppendLine($"Description: {toolDesc}");
                if (parameters.Count > 0)
                {
                    toolDescription.AppendLine("Parameters:");
                    foreach (var param in parameters)
                    {
                        toolDescription.AppendLine(param);
                    }
                }

                descriptions.Add(toolDescription.ToString());
                _logger.LogInformation("🔍   Tool extracted: {ToolName} - {Description}", toolName, toolDesc);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "🔍 Failed to extract tool description");
            }
        }

        return descriptions;
    }

    private string BuildPromptFromMessages(IList<ChatMessage> messages, List<string> toolDescriptions)
    {
        var sb = new StringBuilder();

        _logger.LogInformation("🔍 DEBUG: Building prompt from {Count} messages with {ToolCount} tools:",
            messages.Count, toolDescriptions.Count);

        for (int i = 0; i < messages.Count; i++)
        {
            var message = messages[i];
            var role = message.Role.Value;

            _logger.LogInformation("🔍 Message {Index}: Role={Role}, ContentLength={Length}",
                i + 1, role, message.Text?.Length ?? 0);

            if (role == "system")
            {
                sb.AppendLine($"System Instructions: {message.Text}");
                sb.AppendLine();

                // Inject tool descriptions into system message
                if (toolDescriptions.Count > 0)
                {
                    sb.AppendLine("Available Tools:");
                    sb.AppendLine("You have access to the following tools that you can call to help answer the user's questions:");
                    sb.AppendLine();
                    foreach (var toolDesc in toolDescriptions)
                    {
                        sb.AppendLine(toolDesc);
                        sb.AppendLine();
                    }
                    sb.AppendLine("To use a tool, respond with: TOOL_CALL: <tool_name> <parameters>");
                    sb.AppendLine();

                    _logger.LogInformation("🔍   Injected {Count} tool descriptions into system prompt", toolDescriptions.Count);
                }

                _logger.LogInformation("🔍   System: {Text}",
                    message.Text?.Length > 200 ? message.Text.Substring(0, 200) + "..." : message.Text);
            }
            else if (role == "user")
            {
                sb.AppendLine($"User: {message.Text}");
                _logger.LogInformation("🔍   User: {Text}", message.Text);
            }
            else if (role == "assistant")
            {
                sb.AppendLine($"Assistant: {message.Text}");
                _logger.LogInformation("🔍   Assistant: {Text}",
                    message.Text?.Length > 200 ? message.Text.Substring(0, 200) + "..." : message.Text);
            }
            else if (role == "tool")
            {
                // Handle tool results
                sb.AppendLine($"Tool Result: {message.Text}");
                _logger.LogInformation("🔍   Tool: {Text}", message.Text);
            }
        }

        return sb.ToString();
    }

    private async Task<(string response, string? sessionId)> ExecuteClaudeCLI(
        string prompt,
        string? conversationId,
        CancellationToken cancellationToken)
    {
        // Build command arguments for headless mode
        var args = new List<string> { "-p", "--output-format", "json" };

        // Resume session if we have one for this conversation
        if (!string.IsNullOrEmpty(conversationId) && _sessionCache.TryGetValue(conversationId, out var sessionId))
        {
            args.Add("--resume");
            args.Add(sessionId);
            _logger.LogInformation("🔍 ClaudeChatClient: Resuming session {SessionId}", sessionId);
        }

        _logger.LogInformation("🔍 DEBUG: Executing claude command");
        _logger.LogInformation("🔍 Args list: {Args}", string.Join(" ", args));
        _logger.LogInformation("🔍 Command: claude {Args}", string.Join(" ", args));

        var startInfo = new ProcessStartInfo
        {
            FileName = "claude",
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        // Add arguments
        foreach (var arg in args)
        {
            startInfo.ArgumentList.Add(arg);
        }

        using var process = new Process { StartInfo = startInfo };

        var outputBuilder = new StringBuilder();
        var errorBuilder = new StringBuilder();

        process.OutputDataReceived += (sender, e) =>
        {
            if (e.Data != null)
                outputBuilder.AppendLine(e.Data);
        };

        process.ErrorDataReceived += (sender, e) =>
        {
            if (e.Data != null)
                errorBuilder.AppendLine(e.Data);
        };

        try
        {
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            // Write prompt to stdin
            await process.StandardInput.WriteAsync(prompt);
            await process.StandardInput.FlushAsync();
            process.StandardInput.Close();

            // Wait for process to complete
            await process.WaitForExitAsync(cancellationToken);

            var stdout = outputBuilder.ToString();
            var stderr = errorBuilder.ToString();

            _logger.LogInformation("🔍 DEBUG: Return code: {ExitCode}", process.ExitCode);
            _logger.LogInformation("🔍 DEBUG: Stdout (first 500 chars): {Stdout}", stdout.Length > 500 ? stdout.Substring(0, 500) + "..." : stdout);
            _logger.LogInformation("🔍 DEBUG: Stderr (first 300 chars): {Stderr}", stderr.Length > 300 ? stderr.Substring(0, 300) + "..." : stderr);

            if (process.ExitCode != 0)
            {
                _logger.LogError("🔍 ClaudeChatClient: Claude CLI failed with exit code {ExitCode}. Error: {Error}",
                    process.ExitCode, stderr);
                throw new InvalidOperationException($"Claude CLI failed: {stderr}");
            }

            // Parse JSON output from Claude Code
            try
            {
                _logger.LogInformation("🔍 DEBUG: Attempting to parse JSON response from Claude CLI");
                var jsonDoc = JsonDocument.Parse(stdout);
                var root = jsonDoc.RootElement;

                // Extract result and session_id
                var result = root.TryGetProperty("result", out var resultProp)
                    ? resultProp.GetString() ?? string.Empty
                    : stdout;

                var newSessionId = root.TryGetProperty("session_id", out var sessionProp)
                    ? sessionProp.GetString()
                    : null;

                _logger.LogInformation("🔍 DEBUG: Parsed JSON response. Session: {SessionId}", newSessionId);
                _logger.LogInformation("🔍 DEBUG: Result length: {Length} characters", result.Length);

                return (result, newSessionId);
            }
            catch (JsonException ex)
            {
                _logger.LogWarning(ex, "🔍 ClaudeChatClient: Failed to parse JSON, using raw output");
                _logger.LogInformation("🔍 DEBUG: Raw stdout: {Stdout}", stdout);
                // If JSON parsing fails, return raw output
                return (stdout, null);
            }
        }
        catch (Exception ex) when (ex is not InvalidOperationException)
        {
            if (ex.Message.Contains("Cannot find") || ex.Message.Contains("not found"))
            {
                _logger.LogError("ClaudeChatClient: Claude CLI not found. Please install Claude Code.");
                throw new FileNotFoundException(
                    "Claude CLI not found. Please install Claude Code from https://claude.com/claude-code", ex);
            }

            _logger.LogError(ex, "ClaudeChatClient: Error executing Claude CLI");
            throw new InvalidOperationException($"Error executing Claude CLI: {ex.Message}", ex);
        }
    }

    public object? GetService(Type serviceType, object? serviceKey) =>
        serviceType == typeof(IChatClient) ? this : null;

    public TService? GetService<TService>(object? key = null) where TService : class =>
        this as TService;

    public void Dispose()
    {
        _sessionCache.Clear();
        _logger.LogInformation("ClaudeChatClient: Disposed");
    }
}
