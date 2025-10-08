# Assistant-UI Frontend for Backend Agenting Framework POC

A Next.js frontend built with [assistant-ui](https://github.com/assistant-ui/assistant-ui) that integrates with a custom backend agenting framework using ExternalStoreRuntime for full control over backend integration and JWT authentication.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

The `.env.local` file is already configured with:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Update this URL to point to your backend agenting framework when ready.

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the chat interface.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main chat page
│   └── layout.tsx            # Root layout
├── components/
│   ├── chat/
│   │   └── ChatInterface.tsx # Custom chat component
│   └── assistant-ui/         # UI components from assistant-ui
├── lib/
│   ├── api-client.ts         # Backend API client with JWT
│   ├── runtime.ts            # Custom ExternalStoreRuntime
│   ├── auth.ts               # Token management utilities
│   └── utils.ts              # Helper functions
└── .env.local                # Environment variables
```

## 🔑 Key Features

- **Custom Backend Integration**: Uses ExternalStoreRuntime for full control over API calls
- **JWT Authentication**: Built-in token management via BackendApiClient
- **Streaming Support**: Parses SSE format responses from backend
- **TypeScript**: Full type safety throughout
- **Tailwind CSS**: Modern, responsive styling

## 🔧 Architecture

### Backend API Client (`lib/api-client.ts`)
- Handles HTTP requests to backend
- Injects JWT tokens automatically
- Configurable base URL

### Custom Runtime (`lib/runtime.ts`)
- Manages message state with React
- Handles streaming responses from backend
- Parses SSE format: `data: {"type": "content", "delta": "..."}`

### Chat Interface (`components/chat/ChatInterface.tsx`)
- Main chat UI component
- Integrates runtime with AssistantRuntimeProvider
- Accepts optional `initialToken` prop for JWT

## 🔌 Backend Integration

Your backend should expose an endpoint that:

1. **Accepts POST requests** to `/chat`:
   ```json
   {
     "messages": [
       { "role": "user", "content": "Hello" },
       { "role": "assistant", "content": "Hi!" }
     ]
   }
   ```

2. **Returns streaming responses** (SSE format):
   ```
   data: {"type": "content", "delta": "Hello"}
   data: {"type": "content", "delta": " world"}
   data: {"type": "done"}
   ```

3. **Validates JWT tokens** in Authorization header:
   ```
   Authorization: Bearer <jwt-token>
   ```

4. **Handles CORS** for development:
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   ```

## 🔐 Authentication

### Token Management

The `lib/auth.ts` provides utilities for JWT handling:

```typescript
import { getTokenFromCookie, setTokenCookie } from '@/lib/auth';

// Get token from cookie
const token = getTokenFromCookie();

// Set token in cookie
setTokenCookie('your-jwt-token');
```

### Using with ChatInterface

```typescript
import { ChatInterface } from '@/components/chat/ChatInterface';

export default function Page() {
  return <ChatInterface initialToken="your-jwt-token" />;
}
```

## 📚 Documentation

- **Full Implementation Plan**: See `IMPLEMENTATION_PLAN.md`
- **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md`
- **Assistant-UI Docs**: https://www.assistant-ui.com/docs
- **ExternalStoreRuntime**: https://www.assistant-ui.com/docs/runtimes/custom/external-store

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
- `thread.tsx` - Main chat thread
- `markdown-text.tsx` - Message rendering
- `attachment.tsx` - File attachments
- And more...

## 🚧 Current Status: Phase 1 Complete

✅ **Completed:**
- Project initialization with assistant-ui
- Custom runtime with streaming support
- Backend API client with JWT
- Chat interface component
- Token management utilities

🔜 **Next Steps (Phase 2):**
- Connect to real backend agenting framework
- Implement full JWT authentication flow
- Add error handling and retry logic
- Create API route proxy if needed

🎯 **Future (Phase 3):**
- Multi-thread support
- Message persistence
- Advanced agent visualizations
- Production deployment

## 🤝 Contributing

This is a POC project. Modify as needed for your backend integration requirements.

## 📄 License

MIT
