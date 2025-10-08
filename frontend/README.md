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
# Azure AD Configuration
AUTH_AZURE_AD_TENANT_ID=your-tenant-id
AUTH_AZURE_AD_ID=your-frontend-client-id
AUTH_AZURE_AD_SECRET=your-frontend-client-secret
ORCHESTRATOR_CLIENT_ID=your-orchestrator-client-id

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
AUTH_SECRET=generate-with-openssl-rand-base64-32

# Orchestrator URL
ORCHESTRATOR_URL=http://localhost:8001
```

Get Azure AD credentials from the root `.env` file or Azure Portal.

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

## 🔐 Authentication with Auth.js (NextAuth v5)

The frontend uses **Auth.js** (NextAuth.js v5) for Azure AD authentication. This provides a seamless OAuth flow with automatic token management and session handling.

### Authentication Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  1. User clicks "Sign In" button                                 │
│     ↓                                                             │
│  2. Auth.js redirects to Azure AD login                          │
│     ↓                                                             │
│  3. User authenticates with Microsoft credentials                │
│     ↓                                                             │
│  4. Azure AD redirects back with authorization code              │
│     ↓                                                             │
│  5. Auth.js exchanges code for access token                      │
│     ↓                                                             │
│  6. Token stored in encrypted session cookie                     │
│     ↓                                                             │
│  7. Frontend adapter extracts token and sends to orchestrator    │
│     ↓                                                             │
│  8. Orchestrator validates token & performs OBO exchange         │
│     ↓                                                             │
│  9. Sub-agents receive OBO token with user context               │
└──────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Auth Configuration (`auth.ts`)

```typescript
import NextAuth from "next-auth"
import AzureADProvider from "next-auth/providers/azure-ad"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    AzureADProvider({
      tenantId: process.env.AUTH_AZURE_AD_TENANT_ID,
      issuer: `https://login.microsoftonline.com/${process.env.AUTH_AZURE_AD_TENANT_ID}/v2.0`,
      authorization: {
        params: {
          scope: "openid profile email offline_access",
        },
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      // Store access token in JWT
      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },
    async session({ session, token }) {
      // Make access token available to client
      session.accessToken = token.accessToken
      return session
    },
  },
})
```

#### 2. Auth Provider (`lib/auth-provider.tsx`)

```typescript
import { SessionProvider } from "next-auth/react"

export function AuthProvider({ children }) {
  return <SessionProvider>{children}</SessionProvider>
}
```

#### 3. useAuth Hook (`hooks/useAuth.ts`)

Custom hook that wraps NextAuth's `useSession`:

```typescript
import { useSession, signIn, signOut } from "next-auth/react"

export function useAuth() {
  const { data: session, status } = useSession()

  return {
    isAuthenticated: status === "authenticated",
    user: session?.user,
    login: () => signIn("azure-ad"),
    logout: () => signOut(),
    getToken: async () => session?.accessToken || null,
    status,
  }
}
```

#### 4. Token Forwarding in ChatModelAdapter

The adapter extracts the token and forwards it to the orchestrator:

```typescript
const orchestratorAdapter: ChatModelAdapter = {
  async run({ messages, abortSignal }) {
    const headers: HeadersInit = { "Content-Type": "application/json" }

    // Add Bearer token if authenticated
    if (isAuthenticated) {
      const token = await getToken()
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }
    }

    const response = await fetch("/api/chat", {
      method: "POST",
      headers,
      body: JSON.stringify({ messages }),
      signal: abortSignal,
    })
    // ...
  }
}
```

### Why Auth.js Instead of MSAL?

We switched from **@azure/msal-react** to **Auth.js** for several reasons:

| Feature | MSAL React | Auth.js |
|---------|------------|---------|
| **Setup Complexity** | High - manual initialization, redirect handling, token refresh | Low - convention-based configuration |
| **Next.js Integration** | Manual - requires careful handling of SSR/CSR | Native - built for Next.js App Router |
| **Session Management** | Manual - state in React context | Automatic - encrypted server-side sessions |
| **Token Refresh** | Manual - acquireTokenSilent logic | Automatic - built-in refresh flow |
| **Redirect Handling** | Bug-prone - double-click issues with Strict Mode | Robust - PKCE flow with proper state management |
| **TypeScript Support** | Good | Excellent |
| **Bundle Size** | ~100KB | ~50KB |

### Authentication Flow Details

1. **Initial Load**: Auth.js checks for existing session cookie
2. **Sign In Click**: Redirects to Azure AD with PKCE challenge
3. **Azure AD Login**: User authenticates with Microsoft
4. **Callback**: Auth.js receives auth code at `/api/auth/callback/azure-ad`
5. **Token Exchange**: Auth.js exchanges code for access token
6. **Session Creation**: Token encrypted and stored in HTTP-only cookie
7. **Client Access**: `useSession()` hook provides session data to React components

### Token Lifecycle

- **Access Token**: Stored in encrypted session cookie (HTTP-only, secure)
- **Refresh Token**: Automatically handled by Auth.js
- **Token Expiry**: Auth.js refreshes tokens before expiry
- **Logout**: Clears session cookie and redirects to Azure AD logout

### Security Benefits

1. **No Client-Side Token Storage**: Tokens never exposed to JavaScript
2. **HTTP-Only Cookies**: Prevents XSS attacks
3. **PKCE Flow**: Protects against authorization code interception
4. **Encrypted Sessions**: Session data encrypted with `AUTH_SECRET`
5. **CSRF Protection**: Built-in CSRF tokens for all auth operations

### Azure AD Configuration Required

In your Azure AD app registration for the frontend app:

1. **Redirect URIs**: Add `http://localhost:3000/api/auth/callback/azure-ad`
2. **Logout URLs**: Add `http://localhost:3000` (optional)
3. **API Permissions**:
   - `openid`, `profile`, `email`, `offline_access` (Microsoft Graph)
   - `api://{orchestrator-client-id}/access_as_user` (custom scope)
4. **Grant Admin Consent**: Required for organizational accounts

### Debugging Authentication

Enable debug mode in `auth.ts`:

```typescript
export const { handlers, signIn, signOut, auth } = NextAuth({
  debug: true, // Logs all auth events to terminal
  // ...
})
```

Check terminal output for:
- `[auth][debug]: authorization url is ready` - OAuth flow started
- `JWT callback triggered` - Token received from Azure AD
- `Session callback` - Session created successfully

### Common Issues

1. **OAuthCallbackError**: Check redirect URI matches Azure AD exactly
2. **Invalid audience**: Verify `AUTH_AZURE_AD_TENANT_ID` is correct
3. **Scope rejection**: Ensure admin consent granted for custom API scopes
4. **Session not persisting**: Check `AUTH_SECRET` is set and consistent

## 📚 Documentation

- **Assistant-UI Docs**: https://www.assistant-ui.com/docs
- **useLocalRuntime**: https://www.assistant-ui.com/docs/runtimes/custom/local
- **ChatModelAdapter**: Custom backend integration pattern
- **Next.js API Routes**: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- **Auth.js (NextAuth v5)**: https://authjs.dev/getting-started/installation
- **Azure AD Provider**: https://authjs.dev/getting-started/providers/azure-ad

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

## 🚧 Current Status: Integrated with Orchestrator + Authentication

✅ **Completed:**
- ✅ Next.js project with assistant-ui
- ✅ useLocalRuntime with ChatModelAdapter pattern
- ✅ Next.js API route proxy to orchestrator
- ✅ Simple JSON request/response handling
- ✅ Agent metadata display in messages
- ✅ Thread UI with markdown rendering
- ✅ Auth.js (NextAuth v5) with Azure AD integration
- ✅ JWT token forwarding to orchestrator
- ✅ Secure session management with HTTP-only cookies
- ✅ Automatic token refresh

🔜 **Next Steps:**
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
