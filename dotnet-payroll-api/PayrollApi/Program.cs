using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Identity.Web;
using PayrollApi.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure JWT Authentication with Azure AD
// This validates incoming JWT tokens from users or agents
var requireAuth = builder.Configuration.GetValue<bool>("Auth:RequireAuthentication", false);

if (requireAuth)
{
    builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

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
