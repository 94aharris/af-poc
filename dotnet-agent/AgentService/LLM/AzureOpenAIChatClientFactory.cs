using AgentService.Configuration;
using Azure;
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.OpenAI;

namespace AgentService.LLM;

/// <summary>
/// Factory for creating Azure OpenAI response clients for use with Microsoft Agent Framework.
/// This is the recommended approach for production agents using Azure OpenAI.
/// </summary>
public class AzureOpenAIChatClientFactory
{
    private readonly ILogger<AzureOpenAIChatClientFactory> _logger;
    private readonly AzureOpenAISettings _settings;

    public AzureOpenAIChatClientFactory(
        ILogger<AzureOpenAIChatClientFactory> logger,
        AzureOpenAISettings settings)
    {
        _logger = logger;
        _settings = settings;
    }

    /// <summary>
    /// Creates an AzureOpenAIClient instance configured for Azure OpenAI.
    /// This is used with GetOpenAIResponseClient() to create AIAgent instances.
    /// </summary>
    /// <returns>Tuple of AzureOpenAIClient and deployment name</returns>
    /// <exception cref="InvalidOperationException">Thrown when required configuration is missing</exception>
    public (AzureOpenAIClient client, string deploymentName) CreateClient()
    {
        // Validate configuration
        var endpoint = _settings.Endpoint ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT");
        var deploymentName = _settings.DeploymentName ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME");
        var apiKey = _settings.ApiKey ?? Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY");

        if (string.IsNullOrEmpty(endpoint))
        {
            throw new InvalidOperationException(
                "Azure OpenAI endpoint is not configured. Set 'AzureOpenAI:Endpoint' in appsettings.local.json or AZURE_OPENAI_ENDPOINT environment variable.");
        }

        if (string.IsNullOrEmpty(deploymentName))
        {
            throw new InvalidOperationException(
                "Azure OpenAI deployment name is not configured. Set 'AzureOpenAI:DeploymentName' in appsettings.local.json or AZURE_OPENAI_DEPLOYMENT_NAME environment variable.");
        }

        _logger.LogInformation("Creating Azure OpenAI response client with endpoint: {Endpoint}, deployment: {DeploymentName}",
            endpoint, deploymentName);

        // Create Azure OpenAI client with appropriate credential
        AzureOpenAIClient azureClient;

        if (_settings.UseAzureCliCredential && string.IsNullOrEmpty(apiKey))
        {
            _logger.LogInformation("Using Azure CLI credential for authentication");
            azureClient = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential());
        }
        else if (!string.IsNullOrEmpty(apiKey))
        {
            _logger.LogInformation("Using API key authentication");
            azureClient = new AzureOpenAIClient(new Uri(endpoint), new AzureKeyCredential(apiKey));
        }
        else
        {
            _logger.LogInformation("Using default Azure credential for authentication");
            azureClient = new AzureOpenAIClient(new Uri(endpoint), new DefaultAzureCredential());
        }

        _logger.LogInformation("Azure OpenAI client created successfully");

        return (azureClient, deploymentName);
    }
}
