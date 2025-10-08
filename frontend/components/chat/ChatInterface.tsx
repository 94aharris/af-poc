"use client";

import { useState } from "react";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { Thread } from "@/components/assistant-ui/thread";
import { useCustomRuntime } from "@/lib/runtime";
import { BackendApiClient } from "@/lib/api-client";

export function ChatInterface({ initialToken }: { initialToken?: string }) {
  const [token, setToken] = useState(initialToken);

  const apiClient = new BackendApiClient(
    process.env.NEXT_PUBLIC_BACKEND_URL!,
    () => token || null
  );

  const runtime = useCustomRuntime(apiClient);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="h-screen">
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
}
