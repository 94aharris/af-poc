// Simple proxy to orchestrator backend
export async function POST(req: Request) {
  const body = await req.json();
  const { messages } = body;

  // Get the last user message
  const lastMessage = messages[messages.length - 1];
  const userMessage = lastMessage?.content?.[0]?.text || lastMessage?.content || "";

  console.log(`[API Proxy] Forwarding message to orchestrator:`, userMessage.substring(0, 100));

  const orchestratorUrl = process.env.ORCHESTRATOR_URL || "http://localhost:3000";

  try {
    const response = await fetch(`${orchestratorUrl}/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userMessage,
        conversation_id: null,
        preferred_agent: "auto",
        metadata: {}
      }),
    });

    if (!response.ok) {
      throw new Error(`Orchestrator returned ${response.status}`);
    }

    const data = await response.json();

    console.log(`[API Proxy] Received response from orchestrator:`, data.selected_agent);

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
