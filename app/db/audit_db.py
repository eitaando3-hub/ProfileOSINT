"""SQLite audit logging database"""
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class AuditDB:
    """Database wrapper for audit logs"""
    
    def __init__(self, db_path: str = "app/data/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    user_id TEXT,
                    ip_address TEXT,
                    status TEXT NOT NULL,
                    details TEXT,
                    error_message TEXT,
                    before_data TEXT,
                    after_data TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs (timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_logs (operation)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_resource_id ON audit_logs (resource_id)"
            )
            conn.commit()
        
        logger.info(f"Audit DB initialized: {self.db_path}")
    
    def log_event(
        self,
        operation: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None
    ) -> int:
        """Insert audit log event"""
        try:
            event_time = datetime.now().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO audit_logs (
                        timestamp, operation, resource_type, resource_id, user_id,
                        ip_address, status, details, error_message,
                        before_data, after_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_time,
                        operation,
                        resource_type,
                        resource_id,
                        user_id,
                        ip_address,
                        status,
                        json.dumps(details, ensure_ascii=False) if details is not None else None,
                        error_message,
                        json.dumps(before_data, ensure_ascii=False) if before_data is not None else None,
                        json.dumps(after_data, ensure_ascii=False) if after_data is not None else None,
                    )
                )
                conn.commit()
                return cursor.lastrowid
        
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return -1
    
    def get_logs(
        self,
        limit: int = 100,
        operation: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filters"""
        query = "SELECT * FROM audit_logs"
        conditions = []
        params = []
        
        if operation:
            conditions.append("operation = ?")
            params.append(operation)
        
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def clear_logs(self):
        """Clear all audit logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM audit_logs")
            conn.commit()


# Convenience functions
_audit_db = AuditDB()


def log_event(
    operation: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    before_data: Optional[Dict[str, Any]] = None,
    after_data: Optional[Dict[str, Any]] = None
) -> int:
    """Convenience function for logging"""
    return _audit_db.log_event(
        operation=operation,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        ip_address=ip_address,
        status=status,
        details=details,
        error_message=error_message,
        before_data=before_data,
        after_data=after_data,
    )
