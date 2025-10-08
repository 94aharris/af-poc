"""Authorization logic for the orchestrator."""

from typing import List, Dict
from fastapi import HTTPException
from src.models import AgentType
import logging

logger = logging.getLogger(__name__)


class AuthorizationService:
    """Handles authorization checks for agent access and features."""

    # Define role-based access control
    ROLE_PERMISSIONS = {
        "admin": {
            "agents": [AgentType.PYTHON, AgentType.DOTNET],
            "can_access_audit_logs": True,
            "can_manage_agents": True,
        },
        "analyst": {
            "agents": [AgentType.PYTHON],
            "can_access_audit_logs": False,
            "can_manage_agents": False,
        },
        "user": {
            "agents": [AgentType.DOTNET],
            "can_access_audit_logs": False,
            "can_manage_agents": False,
        },
        "viewer": {
            "agents": [],
            "can_access_audit_logs": False,
            "can_manage_agents": False,
        },
    }

    # Allow all authenticated users by default (even without specific roles)
    ALLOW_ANY_AUTHENTICATED_USER = True

    def check_agent_access(self, user_claims: Dict, agent_type: AgentType) -> bool:
        """Check if user has permission to access the specified agent."""
        roles = user_claims.get("roles", [])

        # Admin has access to everything
        if "admin" in roles:
            return True

        # Check specific role permissions
        for role in roles:
            permissions = self.ROLE_PERMISSIONS.get(role, {})
            allowed_agents = permissions.get("agents", [])
            if agent_type in allowed_agents:
                return True

        # If no specific role matched but we allow any authenticated user, grant access
        if self.ALLOW_ANY_AUTHENTICATED_USER:
            logger.warning(
                f"User {user_claims.get('name', 'unknown')} has no specific role but is authenticated. "
                f"Granting access to {agent_type.value} agent (ALLOW_ANY_AUTHENTICATED_USER=True)"
            )
            return True

        return False

    def require_agent_access(self, user_claims: Dict, agent_type: AgentType):
        """Raise exception if user doesn't have access."""
        if not self.check_agent_access(user_claims, agent_type):
            user_roles = user_claims.get("roles", [])
            raise HTTPException(
                status_code=403,
                detail=f"User with roles {user_roles} does not have permission to access {agent_type.value} agent"
            )

    def has_special_role(self, user_claims: Dict) -> bool:
        """Check if user has any special role defined in ROLE_PERMISSIONS."""
        roles = user_claims.get("roles", [])
        return any(role in self.ROLE_PERMISSIONS for role in roles)

    def get_user_role_level(self, user_claims: Dict) -> str:
        """
        Get user's role level for logging/tracking purposes.
        Returns the highest privilege role if user has multiple.
        """
        roles = user_claims.get("roles", [])

        # Priority order: admin > analyst > user > viewer
        if "admin" in roles:
            return "admin"
        elif "analyst" in roles:
            return "analyst"
        elif "user" in roles:
            return "user"
        elif "viewer" in roles:
            return "viewer"
        else:
            return "authenticated_no_role"

    def get_allowed_agents(self, user_claims: Dict) -> List[AgentType]:
        """Get list of agents the user can access."""
        roles = user_claims.get("roles", [])
        allowed_agents = set()

        for role in roles:
            permissions = self.ROLE_PERMISSIONS.get(role, {})
            allowed_agents.update(permissions.get("agents", []))

        return list(allowed_agents)


authorization_service = AuthorizationService()
