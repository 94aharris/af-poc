"use client";

import { MsalProvider } from "@azure/msal-react";
import { msalInstance, initializeMsal } from "./msal-config";
import { useEffect, useState } from "react";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize MSAL using the singleton pattern
    // This ensures initialization happens only once, even with React Strict Mode
    initializeMsal()
      .then(() => {
        setIsInitialized(true);
      })
      .catch((error) => {
        console.error("MSAL initialization failed:", error);
      });
  }, []);

  if (!isInitialized) {
    return <div className="flex h-dvh w-full items-center justify-center">Loading authentication...</div>;
  }

  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
}
