"""Minimal role-based access control for the desktop application."""
import os
from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    ADMIN = "admin"


_PERMISSIONS = {
    "viewer": {"profile_read"},
    "operator": {"profile_read", "profile_write", "search_run"},
    "auditor": {"profile_read", "audit_read", "audit_export"},
    "admin": {"profile_read", "profile_write", "search_run", "audit_read", "audit_export"},
}


class AccessController:
    def __init__(self, role: str | None = None):
        raw = (role or os.getenv("PROFILEOSINT_ROLE", "admin")).lower()
        self.role = raw if raw in _PERMISSIONS else Role.VIEWER.value

    @property
    def user_id(self) -> str:
        return os.getenv("PROFILEOSINT_USER", "desktop-user")

    def can(self, permission: str) -> bool:
        return permission in _PERMISSIONS[self.role]

    def require(self, permission: str) -> None:
        if not self.can(permission):
            raise PermissionError(f"Role '{self.role}' lacks '{permission}' permission")
