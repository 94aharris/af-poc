"use client";

import { useState } from "react";
import { useExternalStoreRuntime } from "@assistant-ui/react";
import { BackendApiClient } from "./api-client";

export const useCustomRuntime = (apiClient: BackendApiClient) => {
  const [messages, setMessages] = useState<any[]>([]);

  return useExternalStoreRuntime({
    messages,
    onNew: async ({ message }) => {
      // Add user message to state
      setMessages((prev) => [...prev, message]);

      // Send to backend and handle streaming response
      const response = await apiClient.sendMessage([...messages, message]);
      const reader = response.body?.getReader();

      if (!reader) {
        throw new Error("No response body");
      }

      // Handle streaming response
      let assistantMessage = { role: "assistant", content: "" };
      setMessages((prev) => [...prev, assistantMessage]);

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Parse streaming data and update message
        const chunk = decoder.decode(value, { stream: true });

        // Parse SSE format: "data: {...}\n\n"
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "content" && data.delta) {
                assistantMessage.content += data.delta;
                setMessages((prev) => [
                  ...prev.slice(0, -1),
                  { ...assistantMessage },
                ]);
              } else if (data.type === "done") {
                // Stream complete
                break;
              }
            } catch (e) {
              // Skip invalid JSON
              console.warn("Failed to parse SSE data:", e);
            }
          }
        }
      }
    },
  });
};
