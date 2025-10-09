using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Identity.Web;
using PayrollApi.Configuration;
using PayrollApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure JWT Authentication with Azure AD for OBO (On-Behalf-Of) Flow
// This validates incoming JWT tokens that have been obtained via OBO from the orchestrator
var requireAuth = builder.Configuration.GetValue<bool>("Auth:RequireAuthentication", false);

if (requireAuth)
{
    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddMicrosoftIdentityWebApi(options =>
        {
            builder.Configuration.Bind("AzureAd", options);

            // Configure token validation for OBO tokens
            options.TokenValidationParameters.ValidateIssuer = true;
            options.TokenValidationParameters.ValidateAudience = true;
            options.TokenValidationParameters.ValidateLifetime = true;
            options.TokenValidationParameters.ValidateIssuerSigningKey = true;

            // Add event handlers for detailed logging
            options.Events = new Microsoft.AspNetCore.Authentication.JwtBearer.JwtBearerEvents
            {
                OnTokenValidated = context =>
                {
                    var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();
                    logger.LogInformation("✓ JWT token validated successfully");
                    logger.LogInformation("  User: {User}", context.Principal?.Identity?.Name ?? "Unknown");
                    logger.LogInformation("  OID: {Oid}", context.Principal?.FindFirst("oid")?.Value ?? "Not found");
                    return Task.CompletedTask;
                },
                OnAuthenticationFailed = context =>
                {
                    var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();
                    logger.LogError("❌ JWT authentication failed: {Error}", context.Exception.Message);
                    logger.LogError("  Exception: {Exception}", context.Exception);
                    return Task.CompletedTask;
                },
                OnChallenge = context =>
                {
                    var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();
                    logger.LogWarning("⚠ JWT challenge issued: {Error}", context.Error ?? "No error");
                    logger.LogWarning("  Error Description: {Description}", context.ErrorDescription ?? "No description");
                    return Task.CompletedTask;
                }
            };

            // Accept both v1.0 and v2.0 tokens (important for OBO scenarios)
            options.TokenValidationParameters.ValidIssuers = new[]
            {
                $"https://login.microsoftonline.com/{builder.Configuration["AzureAd:TenantId"]}/v2.0",
                $"https://sts.windows.net/{builder.Configuration["AzureAd:TenantId"]}/"
            };

            // Ensure audience matches the API's client ID
            options.TokenValidationParameters.ValidAudiences = new[]
            {
                builder.Configuration["AzureAd:ClientId"],
                builder.Configuration["AzureAd:Audience"],
                $"api://{builder.Configuration["AzureAd:ClientId"]}"
            };

            // Map 'oid' claim to NameIdentifier for easy access
            options.TokenValidationParameters.NameClaimType = "preferred_username";
            options.TokenValidationParameters.RoleClaimType = "roles";

        }, options =>
        {
            builder.Configuration.Bind("AzureAd", options);
        });

    builder.Services.AddAuthorization();
}
else
{
    // Testing mode - authentication disabled
    // Still need to add authentication/authorization services but make them permissive
    builder.Services.AddAuthentication();
    builder.Services.AddAuthorization(options =>
    {
        options.FallbackPolicy = null;
        options.DefaultPolicy = new AuthorizationPolicyBuilder()
            .RequireAssertion(_ => true)
            .Build();
    });
}

// Add controllers
builder.Services.AddControllers();

// Configure CORS for development
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Configure options
builder.Services.Configure<DeveloperUserConfiguration>(
    builder.Configuration.GetSection("DeveloperUser"));

// Register application services
builder.Services.AddSingleton<IPayrollDataService, PayrollDataService>();

// Configure Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure Kestrel to use port 5100 (HTTP only for now)
builder.WebHost.ConfigureKestrel(serverOptions =>
{
    serverOptions.ListenLocalhost(5100); // HTTP
    // HTTPS disabled - requires dev certificate: dotnet dev-certs https --trust
    // serverOptions.ListenLocalhost(5101, listenOptions =>
    // {
    //     listenOptions.UseHttps(); // HTTPS
    // });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Log authentication configuration
var logger = app.Services.GetRequiredService<ILogger<Program>>();
logger.LogInformation("Payroll API starting. Authentication required: {RequireAuth}", requireAuth);

app.UseHttpsRedirection();
app.UseCors("AllowAll");

if (requireAuth)
{
    app.UseAuthentication();
}

app.UseAuthorization();

app.MapControllers();

logger.LogInformation("Payroll API listening on http://localhost:5100 and https://localhost:5101");

app.Run();
