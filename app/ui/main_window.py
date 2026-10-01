"""ProfileOSINT desktop UI with audit history, RBAC, CSV export, and alerts."""
import json
import logging
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk

from app.core.profile_manager import ProfileManager
from app.db.audit_db import AuditDB, log_event
from app.notifications.notifier import NotificationService
from app.security.access_control import AccessController
from app.sources.sherlock_wrapper import SherlockWrapper

logger = logging.getLogger(__name__)


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ProfileOSINT")
        self.root.geometry("1400x900")
        self.access = AccessController()
        self.audit_db = AuditDB()
        self.notifications = NotificationService()
        self.profile_manager = ProfileManager()
        self.sherlock = SherlockWrapper()
        self.current_profile_id = None
        self.current_profile_data = None
        self._build_ui()
        self._load_profiles()
        self._record("ui_open", "application", details={"role": self.access.role})

    def _record(self, operation, resource_type=None, resource_id=None, status="success", details=None, error=None):
        log_event(operation, resource_type, resource_id, self.access.user_id, status=status,
                  details=details, error_message=error)
        if status in {"failure", "denied"} or operation in {"profile_delete", "audit_export_csv"}:
            self.notifications.notify_important(operation, status, details, error)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10); main.pack(fill="both", expand=True)
        left = ttk.Frame(main); left.pack(side="left", fill="y", padx=(0, 10))
        ttk.Label(left, text="Profiles", font=("Arial", 12, "bold")).pack(anchor="w")
        self.profile_listbox = tk.Listbox(left, width=25, height=20); self.profile_listbox.pack(fill="y", pady=5)
        self.profile_listbox.bind("<<ListboxSelect>>", self._on_select_profile)
        buttons = ttk.Frame(left); buttons.pack(fill="x")
        self.new_button = ttk.Button(buttons, text="NEW", command=self._on_new_profile); self.new_button.pack(side="left", padx=2)
        self.delete_button = ttk.Button(buttons, text="Delete", command=self._on_delete_profile); self.delete_button.pack(side="left", padx=2)
        right = ttk.Frame(main); right.pack(side="right", fill="both", expand=True)
        self.notebook = ttk.Notebook(right); self.notebook.pack(fill="both", expand=True)
        self.profile_tab = ttk.Frame(self.notebook); self.notebook.add(self.profile_tab, text="Profile"); self._build_profile_tab()
        self.audit_tab = ttk.Frame(self.notebook); self.notebook.add(self.audit_tab, text="Audit Log"); self._build_audit_tab()
        self.history_tab = ttk.Frame(self.notebook); self.notebook.add(self.history_tab, text="Search History"); self._build_history_tab()
        if not self.access.can("profile_write"):
            self.new_button.state(["disabled"]); self.delete_button.state(["disabled"])

    def _build_profile_tab(self):
        fields = ttk.LabelFrame(self.profile_tab, text="Profile Details"); fields.pack(fill="x", padx=10, pady=10)
        self.profile_id_var = tk.StringVar(value="-"); self.name_var = tk.StringVar(); self.username_var = tk.StringVar(); self.job_var = tk.StringVar(); self.url_var = tk.StringVar()
        for row, label, variable, width in [(0, "Profile ID:", self.profile_id_var, 40), (1, "公開名前:", self.name_var, 40), (2, "公開ユーザーネーム:", self.username_var, 40), (3, "仕事:", self.job_var, 40), (4, "プロフィールURL:", self.url_var, 60)]:
            ttk.Label(fields, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5); ttk.Entry(fields, textvariable=variable, width=width).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(fields, text="メモ:").grid(row=5, column=0, sticky="nw", padx=5, pady=5)
        self.memo_text = tk.Text(fields, width=60, height=5); self.memo_text.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        actions = ttk.Frame(self.profile_tab); actions.pack(fill="x", padx=10, pady=5)
        self.search_button = ttk.Button(actions, text="Sherlock検索", command=self._run_search); self.search_button.pack(side="left", padx=5)
        self.save_button = ttk.Button(actions, text="Save Profile", command=self._save_profile); self.save_button.pack(side="left", padx=5)
        self.progress = ttk.Progressbar(actions, length=250, mode="determinate"); self.progress.pack(side="left", padx=10)
        self.progress_label = ttk.Label(actions, text=""); self.progress_label.pack(side="left")
        results = ttk.LabelFrame(self.profile_tab, text="Search Results"); results.pack(fill="both", expand=True, padx=10, pady=5)
        self.results_tree = ttk.Treeview(results, columns=("Platform", "Username", "Profile URL", "Status"), show="headings")
        for col in self.results_tree["columns"]: self.results_tree.heading(col, text=col); self.results_tree.column(col, width=180)
        self.results_tree.pack(fill="both", expand=True)
        if not self.access.can("search_run"): self.search_button.state(["disabled"])
        if not self.access.can("profile_write"): self.save_button.state(["disabled"])

    def _build_audit_tab(self):
        filters = ttk.LabelFrame(self.audit_tab, text=f"Filters (role: {self.access.role})"); filters.pack(fill="x", padx=10, pady=10)
        self.operation_var = tk.StringVar(); self.status_var = tk.StringVar(); self.resource_var = tk.StringVar(); self.text_var = tk.StringVar()
        ttk.Label(filters, text="Operation").grid(row=0, column=0); ttk.Combobox(filters, textvariable=self.operation_var, values=["", "profile_create", "profile_update", "profile_delete", "search_sherlock", "search_ui_complete", "audit_export_csv"], width=22, state="readonly").grid(row=0, column=1)
        ttk.Label(filters, text="Status").grid(row=0, column=2); ttk.Combobox(filters, textvariable=self.status_var, values=["", "success", "failure", "denied", "started"], width=12, state="readonly").grid(row=0, column=3)
        ttk.Label(filters, text="Resource ID").grid(row=0, column=4); ttk.Entry(filters, textvariable=self.resource_var, width=18).grid(row=0, column=5)
        ttk.Label(filters, text="Text").grid(row=0, column=6); ttk.Entry(filters, textvariable=self.text_var, width=18).grid(row=0, column=7)
        ttk.Button(filters, text="Search", command=self._refresh_audit_log).grid(row=0, column=8); ttk.Button(filters, text="CSV Export", command=self._export_audit_csv).grid(row=0, column=9); ttk.Button(filters, text="Refresh", command=self._refresh_audit_log).grid(row=0, column=10)
        self.audit_tree = ttk.Treeview(self.audit_tab, columns=("Timestamp", "Operation", "Resource ID", "Status", "Details"), show="headings")
        for col in self.audit_tree["columns"]: self.audit_tree.heading(col, text=col); self.audit_tree.column(col, width=280 if col == "Details" else 160)
        self.audit_tree.tag_configure("failure", foreground="red"); self.audit_tree.tag_configure("denied", foreground="red"); self.audit_tree.tag_configure("success", foreground="green")
        self.audit_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self._refresh_audit_log()
        if not self.access.can("audit_read"):
            self.audit_tree.insert("", "end", values=("", "", "", "denied", "監査ログ閲覧権限がありません"), tags=("denied",))

    def _build_history_tab(self):
        ttk.Label(self.history_tab, text="Sherlock search history").pack(anchor="w", padx=10, pady=8)
        self.history_tree = ttk.Treeview(self.history_tab, columns=("Timestamp", "Profile", "Status", "Details"), show="headings")
        for col in self.history_tree["columns"]: self.history_tree.heading(col, text=col); self.history_tree.column(col, width=260 if col == "Details" else 180)
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)
        ttk.Button(self.history_tab, text="Refresh History", command=self._refresh_history).pack(pady=8)
        self._refresh_history()

    def _load_profiles(self):
        self.profile_listbox.delete(0, tk.END)
        for profile in self.profile_manager.get_all_profiles(): self.profile_listbox.insert(tk.END, profile)

    def _on_select_profile(self, _event=None):
        selection = self.profile_listbox.curselection()
        if not selection: return
        self.current_profile_id = self.profile_listbox.get(selection[0]); self.current_profile_data = self.profile_manager.load_profile(self.current_profile_id)
        if not self.current_profile_data: return
        self.profile_id_var.set(self.current_profile_data.get("profile_id", "-")); self.name_var.set("[Hashed]"); self.username_var.set("[Hashed]")
        self.job_var.set(self.current_profile_data.get("job", "")); self.url_var.set(self.current_profile_data.get("profile_url", "")); self.memo_text.delete("1.0", tk.END); self.memo_text.insert("1.0", self.current_profile_data.get("memo", ""))
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        for entry in self.current_profile_data.get("search_results", []):
            result = entry.get("result", {}); url = result.get("url_main", "")
            self.results_tree.insert("", "end", values=(result.get("name", "Unknown"), result.get("username", ""), url, "Found" if url else "Not Found"))

    def _on_new_profile(self):
        try: self.access.require("profile_write")
        except PermissionError as exc: self._record("profile_create", "profile", status="denied", error=str(exc)); messagebox.showerror("権限エラー", str(exc)); return
        username = simpledialog.askstring("New Profile", "公開ユーザーネーム:", parent=self.root)
        if not username: return
        name = simpledialog.askstring("New Profile", "公開名前:", parent=self.root) or ""; job = simpledialog.askstring("New Profile", "仕事:", parent=self.root) or ""; url = simpledialog.askstring("New Profile", "プロフィールURL:", parent=self.root) or ""
        profile_id = self.profile_manager.create_profile(username=username, name=name, job=job, profile_url=url); self._load_profiles(); self._record("profile_create_ui", "profile", profile_id, details={"job": job}); self._refresh_audit_log()

    def _on_delete_profile(self):
        if not self.current_profile_id: return
        if messagebox.askyesno("Delete", f"Delete {self.current_profile_id}?", parent=self.root):
            profile_id = self.current_profile_id; self.profile_manager.delete_profile(profile_id); self.current_profile_id = None; self.current_profile_data = None; self._load_profiles(); self._record("profile_delete_ui", "profile", profile_id); self._refresh_audit_log()

    def _run_search(self):
        try: self.access.require("search_run")
        except PermissionError as exc: self._record("search_sherlock", "profile", self.current_profile_id, status="denied", error=str(exc)); messagebox.showerror("権限エラー", str(exc)); return
        if not self.current_profile_id or not self.current_profile_data: messagebox.showwarning("Warning", "Select a profile first"); return
        username = self.username_var.get()
        if username in ("", "[Hashed]"): messagebox.showwarning("Warning", "Please enter a username first"); return
        self.progress["value"] = 0; self.progress_label.config(text="検索中...")
        threading.Thread(target=lambda: self.root.after(0, lambda: self._finish_search(self.sherlock.search(username))), daemon=True).start()

    def _finish_search(self, results):
        self.progress["value"] = 100; self.progress_label.config(text="完了")
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        for result in results: self.results_tree.insert("", "end", values=(result.get("name", "Unknown"), result.get("username", ""), result.get("url_main", ""), "Found" if result.get("url_main") else "Not Found"))
        for result in results: self.profile_manager.add_search_result(self.current_profile_id, "Sherlock", result)
        self.current_profile_data = self.profile_manager.load_profile(self.current_profile_id); self._on_select_profile(None)
        self._record("search_ui_complete", "profile", self.current_profile_id, details={"result_count": len(results)}); self._refresh_audit_log(); self._refresh_history()

    def _save_profile(self):
        if not self.current_profile_id or not self.current_profile_data: return
        before = dict(self.current_profile_data); self.current_profile_data["job"] = self.job_var.get(); self.current_profile_data["profile_url"] = self.url_var.get(); self.current_profile_data["memo"] = self.memo_text.get("1.0", tk.END)
        self.profile_manager.save_profile(self.current_profile_id, self.current_profile_data); self._record("profile_update_ui", "profile", self.current_profile_id, details={"before": before, "after": self.current_profile_data}); self._refresh_audit_log()

    def _refresh_audit_log(self):
        for item in self.audit_tree.get_children(): self.audit_tree.delete(item)
        if not self.access.can("audit_read"): return
        logs = self.audit_db.get_logs(500, self.operation_var.get() or None, self.resource_var.get() or None, self.status_var.get() or None, self.text_var.get() or None)
        for log in logs: self.audit_tree.insert("", "end", values=(log.get("timestamp", ""), log.get("operation", ""), log.get("resource_id", ""), log.get("status", ""), str(log.get("details") or log.get("error_message") or "")[:300]), tags=(log.get("status", ""),))

    def _refresh_history(self):
        for item in self.history_tree.get_children(): self.history_tree.delete(item)
        if not self.access.can("audit_read"): return
        for log in self.audit_db.get_logs(500, operation="search_sherlock"):
            self.history_tree.insert("", "end", values=(log.get("timestamp", ""), log.get("resource_id", ""), log.get("status", ""), str(log.get("details") or log.get("error_message") or "")[:300]))

    def _export_audit_csv(self):
        if not self.access.can("audit_export"):
            self._record("audit_export_csv", "audit", status="denied", error="Permission denied"); messagebox.showerror("権限エラー", "監査ログのエクスポート権限がありません"); return
        logs = self.audit_db.get_logs(5000, self.operation_var.get() or None, self.resource_var.get() or None, self.status_var.get() or None, self.text_var.get() or None)
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".csv", initialfile=f"audit_log_{datetime.now():%Y%m%d_%H%M%S}.csv", filetypes=[("CSV", "*.csv")])
        if path and self.audit_db.export_to_csv(path, logs): self._record("audit_export_csv", "audit", status="success", details={"filepath": path, "count": len(logs)}); messagebox.showinfo("完了", "CSVを出力しました")


if __name__ == "__main__":
    root = tk.Tk(); MainWindow(root); root.mainloop()
