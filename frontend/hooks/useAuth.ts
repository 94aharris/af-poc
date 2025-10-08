import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/lib/msal-config";
import { AuthenticationResult } from "@azure/msal-browser";

export function useAuth() {
  const { instance, accounts, inProgress } = useMsal();

  const login = async () => {
    try {
      // Use redirect instead of popup to avoid nested popup issues
      await instance.loginRedirect(loginRequest);
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = () => {
    // Use redirect for logout as well
    instance.logoutRedirect();
  };

  const getToken = async (): Promise<string | null> => {
    if (accounts.length === 0) return null;

    try {
      const response: AuthenticationResult = await instance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });
      return response.accessToken;
    } catch (error) {
      // Token expired, redirect to login
      console.error("Token acquisition failed, redirecting to login:", error);
      await instance.loginRedirect(loginRequest);
      return null;
    }
  };

  return {
    isAuthenticated: accounts.length > 0,
    user: accounts[0],
    login,
    logout,
    getToken,
    inProgress,
  };
}
