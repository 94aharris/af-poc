"""JWT validation and OBO token acquisition."""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import msal
import httpx
from typing import Optional, Dict
from src.config import settings

security = HTTPBearer(auto_error=False)


class JWTValidator:
    """Validates JWT tokens from Azure AD."""

    def __init__(self):
        self.jwks_cache = None

    async def get_signing_keys(self) -> Dict:
        """Fetch JWKS from Azure AD."""
        if self.jwks_cache:
            return self.jwks_cache

        if not settings.AZURE_TENANT_ID:
            raise HTTPException(
                status_code=500, detail="Azure AD not configured (AZURE_TENANT_ID missing)"
            )

        metadata_url = (
            f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/"
            f"v2.0/.well-known/openid-configuration"
        )

        async with httpx.AsyncClient() as client:
            metadata = await client.get(metadata_url)
            jwks_uri = metadata.json()["jwks_uri"]
            jwks_response = await client.get(jwks_uri)
            self.jwks_cache = jwks_response.json()

        return self.jwks_cache

    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims."""
        try:
            # Get signing keys
            jwks = await self.get_signing_keys()

            # Decode and validate token
            claims = jwt.decode(
                token,
                jwks,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"verify_signature": True},
            )

            return claims

        except JWTError as e:
            raise HTTPException(
                status_code=401, detail=f"Invalid authentication credentials: {str(e)}"
            )


class OBOTokenService:
    """Handles On-Behalf-Of token exchange.

    This is the CORE of the POC - demonstrating how the orchestrator
    exchanges the user's JWT for scoped tokens to call sub-agents.
    """

    def __init__(self):
        if settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET:
            self.msal_app = msal.ConfidentialClientApplication(
                client_id=settings.AZURE_CLIENT_ID,
                client_credential=settings.AZURE_CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}",
            )
        else:
            self.msal_app = None

    async def acquire_token_on_behalf_of(
        self, user_token: str, scopes: list[str]
    ) -> Optional[str]:
        """
        Exchange user token for a new token with different scopes.
        This is the CORE OBO FLOW IMPLEMENTATION.

        Flow:
        1. Orchestrator receives user's JWT token from frontend
        2. Orchestrator validates the token
        3. Orchestrator exchanges it for a new token with sub-agent scopes
        4. Sub-agent receives OBO token and can call APIs on behalf of user

        Args:
            user_token: The incoming JWT token from the user
            scopes: The scopes required for the downstream sub-agent API

        Returns:
            Access token for the downstream sub-agent with user context
        """
        if not self.msal_app:
            raise HTTPException(
                status_code=500,
                detail="OBO not configured. Set AZURE_CLIENT_ID and AZURE_CLIENT_SECRET.",
            )

        try:
            # Acquire token on behalf of the user
            result = self.msal_app.acquire_token_on_behalf_of(
                user_assertion=user_token, scopes=scopes
            )

            if "access_token" in result:
                return result["access_token"]
            else:
                error = result.get("error_description", "Unknown error")
                raise HTTPException(status_code=401, detail=f"Failed to acquire OBO token: {error}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OBO token acquisition failed: {str(e)}")


# Singleton instances
jwt_validator = JWTValidator()
obo_service = OBOTokenService()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[Dict]:
    """FastAPI dependency to validate JWT and extract user claims.

    If REQUIRE_AUTH is False, returns None (for testing without Azure AD).
    """
    if not settings.REQUIRE_AUTH:
        # Return mock user for testing without auth
        return {
            "oid": "test-user-id",
            "name": "Test User",
            "preferred_username": "test@example.com",
        }

    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")

    token = credentials.credentials
    claims = await jwt_validator.validate_token(token)
    return claims


async def get_obo_token(user_token: str, target_scopes: list[str]) -> str:
    """Helper to acquire OBO token."""
    return await obo_service.acquire_token_on_behalf_of(user_token, target_scopes)
