import { Configuration, PublicClientApplication, EventType } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID}`,
    redirectUri: process.env.NEXT_PUBLIC_REDIRECT_URI || "http://localhost:3000",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest = {
  scopes: [`api://${process.env.NEXT_PUBLIC_ORCHESTRATOR_CLIENT_ID}/access_as_user`],
};

export const msalInstance = new PublicClientApplication(msalConfig);

// Singleton promise to ensure initialization happens only once
let initializationPromise: Promise<void> | null = null;

/**
 * Initialize MSAL and handle redirect promise.
 * This MUST be called before rendering MsalProvider.
 * Uses a singleton pattern to ensure it only runs once, even with React Strict Mode.
 */
export const initializeMsal = async (): Promise<void> => {
  if (initializationPromise) {
    return initializationPromise;
  }

  initializationPromise = (async () => {
    await msalInstance.initialize();

    // Handle redirect promise - this processes the code= parameter from Azure AD
    // This can only be called once per page load
    const response = await msalInstance.handleRedirectPromise();

    if (response) {
      console.log("Login successful:", response.account);
      msalInstance.setActiveAccount(response.account);
    }

    // Set up event callback for future login events
    msalInstance.addEventCallback((event) => {
      if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
        const payload = event.payload as any;
        msalInstance.setActiveAccount(payload.account);
      }
    });
  })();

  return initializationPromise;
};
