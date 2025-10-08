# Assistant-UI Frontend for Backend Agenting Framework POC

A Next.js frontend built with [assistant-ui](https://github.com/assistant-ui/assistant-ui) that integrates with a custom orchestrator backend using `useLocalRuntime` and a custom `ChatModelAdapter` for seamless communication.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create or update `.env.local`:

```bash
ORCHESTRATOR_URL=http://localhost:3001
```

This points to the orchestrator service (default port 3001).

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the chat interface.

> **Note**: Make sure the orchestrator service is running on port 3001 before testing.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main entry point (renders Assistant component)
│   ├── assistant.tsx         # Main chat UI with useLocalRuntime integration
│   ├── layout.tsx            # Root layout
│   └── api/
│       └── chat/
│           └── route.ts      # Next.js API route (proxy to orchestrator)
├── components/
│   ├── assistant-ui/         # UI components from assistant-ui library
│   │   ├── thread.tsx        # Main chat thread component
│   │   ├── markdown-text.tsx # Message rendering with markdown
│   │   └── ...               # Other UI components
│   └── ui/                   # shadcn/ui components
│       ├── sidebar.tsx
│       ├── breadcrumb.tsx
│       └── ...
└── .env.local                # Environment variables (ORCHESTRATOR_URL)
```

## 🔑 Key Features

- **useLocalRuntime Integration**: Uses assistant-ui's native runtime for custom backends
- **ChatModelAdapter Pattern**: Clean separation between UI and backend communication
- **Server-Side Proxy**: Next.js API route handles orchestrator communication
- **Simple JSON Responses**: No complex streaming protocols needed
- **TypeScript**: Full type safety throughout
- **Tailwind CSS + shadcn/ui**: Modern, accessible styling

## 🔧 Architecture

### How It Works

The frontend uses a three-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React Components)                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Assistant Component (app/assistant.tsx)              │  │
│  │  - useLocalRuntime(orchestratorAdapter)               │  │
│  │  - Manages chat state client-side                     │  │
│  │  - Renders Thread component                           │  │
│  └────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │ fetch("/api/chat", { messages })
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Next.js Server (Node.js)                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Route (app/api/chat/route.ts)                    │  │
│  │  - Extracts user message from messages array          │  │
│  │  - Proxies to orchestrator backend                    │  │
│  │  - Returns JSON: {content, metadata}                  │  │
│  └────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │ POST /agent
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator Service (Python FastAPI - Port 3001)          │
│  - Receives message                                          │
│  - Selects appropriate agent (Python/.NET)                  │
│  - Returns response with agent metadata                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. ChatModelAdapter (`app/assistant.tsx:22-58`)

The `orchestratorAdapter` implements the `ChatModelAdapter` interface:

```typescript
const orchestratorAdapter: ChatModelAdapter = {
  async run({ messages, abortSignal }) {
    // Calls /api/chat (Next.js route, not orchestrator directly)
    const response = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ messages }),
      signal: abortSignal,
    });

    const data = await response.json();

    // Returns assistant-ui compatible format
    return {
      content: [{ type: "text", text: data.content }]
    };
  }
};
```

**Key Points:**
- Implements `async run()` method that returns `ChatModelRunResult`
- Receives `messages` array containing conversation history
- Supports abort signals for cancellation
- Returns content as array of message parts (text, tool calls, etc.)

#### 2. useLocalRuntime Hook (`app/assistant.tsx:62`)

```typescript
const runtime = useLocalRuntime(orchestratorAdapter);
```

**What it does:**
- Manages conversation state (messages, loading states, etc.)
- Calls the adapter's `run()` method when user sends a message
- Handles optimistic updates and error states
- Provides React hooks for accessing chat state

**Why useLocalRuntime:**
- No dependency on Vercel AI SDK or specific LLM providers
- Full control over backend communication
- Works with any HTTP API that returns text
- Simpler than ExternalStoreRuntime for basic use cases

#### 3. Next.js API Route (`app/api/chat/route.ts`)

**Simple JSON proxy:**

```typescript
export async function POST(req: Request) {
  const { messages } = await req.json();
  const userMessage = messages[messages.length - 1]?.content;

  // Call orchestrator
  const response = await fetch(`${ORCHESTRATOR_URL}/agent`, {
    method: "POST",
    body: JSON.stringify({ message: userMessage })
  });

  const data = await response.json();

  // Return simple JSON response
  return Response.json({
    content: data.message,
    metadata: { agent: data.selected_agent, status: data.status }
  });
}
```

**Benefits of this pattern:**
- Server-side only - JWT tokens can be injected securely
- Request/response transformation without client changes
- Error handling and retry logic in one place
- CORS and network issues handled server-side

## 🔌 Backend Integration

### Expected API Contract

The `/api/chat` route expects the orchestrator to expose a `/agent` endpoint:

**Request:**
```bash
POST http://localhost:3001/agent
Content-Type: application/json

{
  "message": "What is the weather?",
  "conversation_id": null,
  "preferred_agent": "auto",
  "metadata": {}
}
```

**Response:**
```json
{
  "message": "The weather is sunny.",
  "selected_agent": "python",
  "status": "success",
  "conversation_id": "uuid-here"
}
```

### Message Flow

1. **User sends message** via assistant-ui Thread component
2. **useLocalRuntime** calls `orchestratorAdapter.run({ messages })`
3. **Adapter** sends POST to `/api/chat` with messages array
4. **API route** extracts last user message and forwards to orchestrator
5. **Orchestrator** processes and returns response
6. **API route** transforms to `{content, metadata}` format
7. **Adapter** returns to useLocalRuntime as `{content: [{type: "text", text: "..."}]}`
8. **assistant-ui** renders the message in the UI

## 🔐 Authentication (Future)

JWT authentication will be added in Phase 2. The architecture will support:

1. **Token acquisition** in browser via Azure AD/MSAL.js
2. **Token storage** in HTTP-only cookies (secure)
3. **Token injection** in `/api/chat` route before forwarding to orchestrator
4. **OBO flow** in orchestrator to call sub-agents

**Future implementation:**
```typescript
// In app/api/chat/route.ts
const token = cookies().get('auth_token')?.value;

const response = await fetch(`${orchestratorUrl}/agent`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: userMessage })
});
```

## 📚 Documentation

- **Assistant-UI Docs**: https://www.assistant-ui.com/docs
- **useLocalRuntime**: https://www.assistant-ui.com/docs/runtimes/custom/local
- **ChatModelAdapter**: Custom backend integration pattern
- **Next.js API Routes**: https://nextjs.org/docs/app/building-your-application/routing/route-handlers

## 🛠️ Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Run production server
npm run lint     # Run ESLint
```

### Customizing the UI

All assistant-ui components are in `components/assistant-ui/` and can be customized:
- `thread.tsx` - Main chat thread component
- `markdown-text.tsx` - Message rendering with markdown support
- `threadlist-sidebar.tsx` - Conversation history sidebar
- And more...

**Styling**: Uses Tailwind CSS with shadcn/ui components. Customize in `tailwind.config.ts`.

## 🚧 Current Status: Integrated with Orchestrator

✅ **Completed:**
- ✅ Next.js project with assistant-ui
- ✅ useLocalRuntime with ChatModelAdapter pattern
- ✅ Next.js API route proxy to orchestrator
- ✅ Simple JSON request/response handling
- ✅ Agent metadata display in messages
- ✅ Thread UI with markdown rendering

🔜 **Next Steps:**
- [ ] Add JWT authentication with Azure AD
- [ ] Token injection in API route
- [ ] Error handling and retry logic
- [ ] Streaming support for real-time responses
- [ ] Loading states and optimistic updates

🎯 **Future Enhancements:**
- [ ] Multi-thread support (conversation history)
- [ ] Message persistence (database)
- [ ] Tool calling UI (if agents use tools)
- [ ] Agent visualization (show which agent responded)
- [ ] Production deployment

## 🤝 Contributing

This is a POC project. Modify as needed for your backend integration requirements.

## 📄 License

MIT
