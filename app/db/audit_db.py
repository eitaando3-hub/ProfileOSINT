"""SQLite audit log storage, filtering, and CSV export."""
import csv
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuditDB:
    def __init__(self, db_path: str = "app/data/audit.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()

    def _initialize_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS audit_logs (
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
                )"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_logs(operation)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_resource_id ON audit_logs(resource_id)")
            conn.commit()

    def log_event(self, operation: str, resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None, user_id: Optional[str] = None,
                  ip_address: Optional[str] = None, status: str = "success",
                  details: Optional[Dict[str, Any]] = None,
                  error_message: Optional[str] = None,
                  before_data: Optional[Dict[str, Any]] = None,
                  after_data: Optional[Dict[str, Any]] = None) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    """INSERT INTO audit_logs
                    (timestamp, operation, resource_type, resource_id, user_id,
                     ip_address, status, details, error_message, before_data, after_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.now(timezone.utc).isoformat(), operation, resource_type,
                        resource_id, user_id, ip_address, status,
                        json.dumps(details, ensure_ascii=False) if details is not None else None,
                        error_message,
                        json.dumps(before_data, ensure_ascii=False) if before_data is not None else None,
                        json.dumps(after_data, ensure_ascii=False) if after_data is not None else None,
                    ),
                )
                conn.commit()
                return int(cur.lastrowid)
        except Exception:
            logger.exception("Could not write audit event")
            return -1

    def get_logs(self, limit: int = 100, operation: Optional[str] = None,
                 resource_id: Optional[str] = None, status: Optional[str] = None,
                 text: Optional[str] = None) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 5000))
        conditions, params = [], []
        if operation:
            conditions.append("operation = ?")
            params.append(operation)
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if text:
            conditions.append("(operation LIKE ? OR details LIKE ? OR error_message LIKE ?)")
            pattern = f"%{text}%"
            params.extend([pattern, pattern, pattern])
        query = "SELECT * FROM audit_logs"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def export_to_csv(self, filepath: str, logs: Optional[List[Dict[str, Any]]] = None) -> bool:
        try:
            rows = logs if logs is not None else self.get_logs(limit=5000)
            if not rows:
                return False
            fields = ["id", "timestamp", "operation", "resource_type", "resource_id",
                      "user_id", "ip_address", "status", "details", "error_message",
                      "before_data", "after_data"]
            with open(filepath, "w", newline="", encoding="utf-8-sig") as output:
                writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
            return True
        except Exception:
            logger.exception("Could not export audit logs")
            return False


_audit_db = AuditDB()


def log_event(operation: str, resource_type: Optional[str] = None,
              resource_id: Optional[str] = None, user_id: Optional[str] = None,
              ip_address: Optional[str] = None, status: str = "success",
              details: Optional[Dict[str, Any]] = None,
              error_message: Optional[str] = None,
              before_data: Optional[Dict[str, Any]] = None,
              after_data: Optional[Dict[str, Any]] = None) -> int:
    return _audit_db.log_event(operation, resource_type, resource_id, user_id,
                               ip_address, status, details, error_message,
                               before_data, after_data)
