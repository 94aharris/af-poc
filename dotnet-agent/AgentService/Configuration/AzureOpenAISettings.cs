namespace AgentService.Configuration;

/// <summary>
/// Configuration settings for Azure OpenAI service.
/// These values should be set in appsettings.local.json (gitignored) or environment variables.
/// </summary>
public class AzureOpenAISettings
{
    /// <summary>
    /// Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)
    /// Can also be set via environment variable: AZURE_OPENAI_ENDPOINT
    /// </summary>
    public string? Endpoint { get; set; }

    /// <summary>
    /// Azure OpenAI deployment name (e.g., gpt-4o, gpt-4o-mini)
    /// Can also be set via environment variable: AZURE_OPENAI_DEPLOYMENT_NAME
    /// </summary>
    public string? DeploymentName { get; set; }

    /// <summary>
    /// Optional: Azure OpenAI API key (if not using Azure CLI credential)
    /// Can also be set via environment variable: AZURE_OPENAI_API_KEY
    /// </summary>
    public string? ApiKey { get; set; }

    /// <summary>
    /// Whether to use Azure CLI credential for authentication (default: true)
    /// Set to false if using API key authentication
    /// </summary>
    public bool UseAzureCliCredential { get; set; } = true;
}
