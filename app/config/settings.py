"""Application configuration and global settings."""
import os
from pathlib import Path


class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "app" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # App settings
        self.app_name = "ProfileOSINT"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

        # Database paths
        self.audit_db_path = str(self.data_dir / "audit.db")
        self.profiles_dir = self.data_dir / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        # Security
        self.default_role = os.getenv("PROFILEOSINT_ROLE", "admin")
        self.default_user = os.getenv("PROFILEOSINT_USER", "desktop-user")

        # External integrations
        self.smtp_enabled = bool(os.getenv("PROFILEOSINT_SMTP_HOST"))
        self.sherlock_enabled = True  # Check at runtime
        self.web_search_enabled = True  # Check at runtime

    def get(self, key: str, default=None):
        """Get setting by key."""
        return getattr(self, key, default)

    def to_dict(self) -> dict:
        """Export non-sensitive settings."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "data_dir": str(self.data_dir),
            "default_role": self.default_role,
            "smtp_enabled": self.smtp_enabled,
        }


# Global settings instance
global_settings = Settings()
