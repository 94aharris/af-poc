export function getTokenFromCookie(): string | null {
  if (typeof window === "undefined") return null;
  const cookies = document.cookie.split(";");
  const tokenCookie = cookies.find((c) => c.trim().startsWith("auth_token="));
  return tokenCookie ? tokenCookie.split("=")[1] : null;
}

export function setTokenCookie(token: string) {
  document.cookie = `auth_token=${token}; path=/; secure; samesite=strict`;
}
