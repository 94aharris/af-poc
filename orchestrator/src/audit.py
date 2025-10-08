"""Audit logging for security and compliance."""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from enum import Enum

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("orchestrator.audit")


class AuditEventType(str, Enum):
    """Types of auditable events."""
    JWT_VALIDATION_SUCCESS = "jwt_validation_success"
    JWT_VALIDATION_FAILURE = "jwt_validation_failure"
    OBO_TOKEN_ACQUIRED = "obo_token_acquired"
    OBO_TOKEN_FAILED = "obo_token_failed"
    AGENT_SELECTED = "agent_selected"
    AGENT_CALL_SUCCESS = "agent_call_success"
    AGENT_CALL_FAILURE = "agent_call_failure"
    AUTHORIZATION_DENIED = "authorization_denied"
    USER_ACTION = "user_action"


class AuditLogger:
    """Centralized audit logging service."""

    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        agent_type: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log an audit event with structured data."""

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "user_id": user_id or "anonymous",
            "user_name": user_name or "unknown",
            "user_email": user_email or "unknown",
            "agent_type": agent_type,
            "success": success,
            "details": details or {},
        }

        # Log as JSON for structured logging systems (e.g., ELK, Splunk)
        logger.info(json.dumps(event))

        # In production, you would also:
        # 1. Send to Azure Application Insights
        # 2. Write to database for audit trail
        # 3. Send to SIEM system

    def log_jwt_validation(self, user_claims: Dict, success: bool = True):
        """Log JWT validation event."""
        self.log_event(
            event_type=AuditEventType.JWT_VALIDATION_SUCCESS if success else AuditEventType.JWT_VALIDATION_FAILURE,
            user_id=user_claims.get("oid"),
            user_name=user_claims.get("name"),
            user_email=user_claims.get("preferred_username") or user_claims.get("email"),
            success=success,
            details={
                "roles": user_claims.get("roles", []),
                "token_issued_at": user_claims.get("iat"),
                "token_expires_at": user_claims.get("exp"),
            },
        )

    def log_obo_exchange(
        self,
        user_claims: Dict,
        agent_type: str,
        scopes: List[str],
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Log OBO token exchange."""
        self.log_event(
            event_type=AuditEventType.OBO_TOKEN_ACQUIRED if success else AuditEventType.OBO_TOKEN_FAILED,
            user_id=user_claims.get("oid"),
            user_name=user_claims.get("name"),
            user_email=user_claims.get("preferred_username") or user_claims.get("email"),
            agent_type=agent_type,
            success=success,
            details={
                "scopes": scopes,
                "error": error,
            },
        )

    def log_agent_selection(self, user_claims: Dict, agent_type: str, reason: str):
        """Log agent selection decision."""
        self.log_event(
            event_type=AuditEventType.AGENT_SELECTED,
            user_id=user_claims.get("oid"),
            user_name=user_claims.get("name"),
            user_email=user_claims.get("preferred_username") or user_claims.get("email"),
            agent_type=agent_type,
            details={"reason": reason},
        )

    def log_agent_call(
        self,
        user_claims: Dict,
        agent_type: str,
        success: bool = True,
        response_time_ms: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """Log sub-agent API call."""
        self.log_event(
            event_type=AuditEventType.AGENT_CALL_SUCCESS if success else AuditEventType.AGENT_CALL_FAILURE,
            user_id=user_claims.get("oid"),
            user_name=user_claims.get("name"),
            user_email=user_claims.get("preferred_username") or user_claims.get("email"),
            agent_type=agent_type,
            success=success,
            details={
                "response_time_ms": response_time_ms,
                "error": error,
            },
        )

    def log_authorization_denied(self, user_claims: Dict, resource: str, reason: str):
        """Log authorization denial."""
        self.log_event(
            event_type=AuditEventType.AUTHORIZATION_DENIED,
            user_id=user_claims.get("oid"),
            user_name=user_claims.get("name"),
            user_email=user_claims.get("preferred_username") or user_claims.get("email"),
            success=False,
            details={"resource": resource, "reason": reason},
        )


audit_logger = AuditLogger()
