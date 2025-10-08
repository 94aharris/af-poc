namespace PayrollApi.Models;

/// <summary>
/// Standard error response model
/// </summary>
public class ErrorResponse
{
    /// <summary>
    /// Error message
    /// </summary>
    public string Error { get; set; } = string.Empty;

    /// <summary>
    /// HTTP status code
    /// </summary>
    public int StatusCode { get; set; }

    /// <summary>
    /// Detailed error message (only in development)
    /// </summary>
    public string? Details { get; set; }

    /// <summary>
    /// Request ID for tracking
    /// </summary>
    public string? RequestId { get; set; }
}
