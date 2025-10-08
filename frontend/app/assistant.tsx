"use client";

import { useEffect } from "react";
import { AssistantRuntimeProvider, useLocalRuntime, type ChatModelAdapter } from "@assistant-ui/react";
import { Thread } from "@/components/assistant-ui/thread";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThreadListSidebar } from "@/components/assistant-ui/threadlist-sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

export const Assistant = () => {
  const { isAuthenticated, user, login, logout, getToken, status } = useAuth();

  // Check for auth errors in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const error = params.get('error');
    if (error) {
      console.error('Auth error from URL:', error);
    }
  }, []);

  // Custom adapter for orchestrator backend with auth
  const orchestratorAdapter: ChatModelAdapter = {
    async run({ messages, abortSignal }) {
      const headers: HeadersInit = { "Content-Type": "application/json" };

      // Add Bearer token if authenticated
      if (isAuthenticated) {
        const token = await getToken();
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
      }

      const response = await fetch("/api/chat", {
        method: "POST",
        headers,
        body: JSON.stringify({ messages }),
        signal: abortSignal,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          content: [
            {
              type: "text" as const,
              text: data.content || data.error || "An error occurred",
            },
          ],
        };
      }

      // Build the response text with metadata
      const responseText = data.content;
      const metadataText = data.metadata
        ? `\n\n---\n**Agent:** ${data.metadata.agent}\n**Status:** ${data.metadata.status}`
        : "";

      return {
        content: [
          {
            type: "text" as const,
            text: responseText + metadataText,
          },
        ],
      };
    },
  };

  const runtime = useLocalRuntime(orchestratorAdapter);

  // Show loading screen while checking authentication
  if (status === "loading") {
    return (
      <div className="flex h-dvh w-full items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold">Loading...</h1>
          <p className="text-muted-foreground">Checking authentication status</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="flex h-dvh w-full items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold">Authentication Required</h1>
          <p className="text-muted-foreground">Please sign in to use the assistant</p>
          <Button onClick={login}>Sign In with Microsoft</Button>
        </div>
      </div>
    );
  }

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <SidebarProvider>
        <div className="flex h-dvh w-full pr-0.5">
          <ThreadListSidebar />
          <SidebarInset>
            <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
              <SidebarTrigger />
              <Separator orientation="vertical" className="mr-2 h-4" />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem className="hidden md:block">
                    <BreadcrumbLink
                      href="https://www.assistant-ui.com/docs/getting-started"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Build Your Own ChatGPT UX
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    <BreadcrumbPage>Orchestrator Agent</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <div className="ml-auto flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {user?.name || user?.email}
                </span>
                <Button variant="outline" size="sm" onClick={logout}>
                  Sign Out
                </Button>
              </div>
            </header>
            <div className="flex-1 overflow-hidden">
              <Thread />
            </div>
          </SidebarInset>
        </div>
      </SidebarProvider>
    </AssistantRuntimeProvider>
  );
};
