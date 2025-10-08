import { useSession, signIn, signOut } from "next-auth/react";

export function useAuth() {
  const { data: session, status } = useSession();

  const login = async () => {
    await signIn("azure-ad");
  };

  const logout = async () => {
    await signOut();
  };

  const getToken = async (): Promise<string | null> => {
    return session?.accessToken || null;
  };

  return {
    isAuthenticated: status === "authenticated",
    user: session?.user,
    login,
    logout,
    getToken,
    status,
  };
}
