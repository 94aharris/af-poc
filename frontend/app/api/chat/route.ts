// Simple proxy to orchestrator backend with authentication support
export async function POST(req: Request) {
  const body = await req.json();
  const { messages } = body;

  // Generate unique request ID for tracing
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Get the last user message
  const lastMessage = messages[messages.length - 1];
  const userMessage = lastMessage?.content?.[0]?.text || lastMessage?.content || "";

  console.log(`[${requestId}] [FRONTEND→ORCHESTRATOR] User message:`, userMessage.substring(0, 100));

  const orchestratorUrl = process.env.ORCHESTRATOR_URL || "http://localhost:3000";

  // Extract Bearer token from incoming request (if present)
  const authHeader = req.headers.get("Authorization");

  try {
    const startTime = Date.now();

    const headers: HeadersInit = { "Content-Type": "application/json" };

    // Forward the Bearer token to orchestrator if present
    if (authHeader) {
      headers["Authorization"] = authHeader;
    }

    const response = await fetch(`${orchestratorUrl}/agent`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        message: userMessage,
        conversation_id: null,
        preferred_agent: "auto",
        metadata: { request_id: requestId }
      }),
    });

    if (!response.ok) {
      throw new Error(`Orchestrator returned ${response.status}`);
    }

    const data = await response.json();

    const elapsedTime = Date.now() - startTime;
    console.log(`[${requestId}] [ORCHESTRATOR→FRONTEND] Response received from ${data.selected_agent} in ${elapsedTime}ms`);

    return Response.json({
      content: data.message,
      metadata: {
        agent: data.selected_agent,
        status: data.status
      }
    });
  } catch (error) {
    console.error("[API Proxy] Error:", error);
    return Response.json(
      {
        error: error instanceof Error ? error.message : 'Unknown error',
        content: `Failed to connect to orchestrator: ${error instanceof Error ? error.message : 'Unknown error'}`
      },
      { status: 500 }
    );
  }
}
