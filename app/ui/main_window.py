"""ProfileOSINT Main Window with Audit Log support"""
import logging
import threading
from tkinter import ttk, messagebox, Tk
from app.core.profile_manager import ProfileManager
from app.sources.sherlock_wrapper import SherlockWrapper
from app.db.audit_db import AuditDB, log_event

logger = logging.getLogger(__name__)


class MainWindow:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("ProfileOSINT")
        self.root.geometry("1400x900")

        self.audit_db = AuditDB()
        self.profile_manager = ProfileManager()
        self.sherlock = SherlockWrapper()

        self.current_profile_id = None
        self.current_profile_data = None

        self._build_ui()
        self._load_profiles()
        log_event(
            operation="ui_open",
            resource_type="application",
            status="success",
            details={"window": "main"},
            user_id="system",
        )

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Profiles", font=("Arial", 12, "bold")).pack(anchor="w")
        self.profile_listbox = tk.Listbox(left, width=25, height=20)
        self.profile_listbox.pack(fill="y", pady=5)
        self.profile_listbox.bind("<<ListboxSelect>>", self._on_select_profile)

        btns = ttk.Frame(left)
        btns.pack(fill="x")
        ttk.Button(btns, text="NEW", command=self._on_new_profile).pack(side="left", padx=2)
        ttk.Button(btns, text="Delete", command=self._on_delete_profile).pack(side="left", padx=2)

        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)

        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="Profile")
        self._build_profile_tab()

        self.audit_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.audit_tab, text="Audit Log")
        self._build_audit_tab()

    def _build_profile_tab(self):
        fields = ttk.LabelFrame(self.profile_tab, text="Profile Details")
        fields.pack(fill="x", padx=10, pady=10)

        ttk.Label(fields, text="Profile ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.profile_id_var = tk.StringVar(value="-")
        ttk.Label(fields, textvariable=self.profile_id_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(fields, text="公開名前:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(fields, text="公開ユーザーネーム:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.username_var, width=40).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(fields, text="仕事:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.job_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.job_var, width=40).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(fields, text="プロフィールURL:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.url_var, width=60).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(fields, text="メモ:").grid(row=5, column=0, sticky="nw", padx=5, pady=5)
        self.memo_text = tk.Text(fields, width=60, height=5)
        self.memo_text.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        action = ttk.Frame(self.profile_tab)
        action.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action, text="Sherlock検索", command=self._run_search).pack(side="left", padx=5)
        ttk.Button(action, text="Save Profile", command=self._save_profile).pack(side="left", padx=5)

        self.progress = ttk.Progressbar(action, orient="horizontal", length=250, mode="determinate")
        self.progress.pack(side="left", padx=10)
        self.progress_label = ttk.Label(action, text="")
        self.progress_label.pack(side="left")

        results = ttk.LabelFrame(self.profile_tab, text="Search Results")
        results.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("Platform", "Username", "Profile URL", "Status")
        self.results_tree = ttk.Treeview(results, columns=columns, show="headings")
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=180)
        self.results_tree.pack(fill="both", expand=True)

    def _build_audit_tab(self):
        columns = ("Timestamp", "Operation", "Resource ID", "Status", "Details")
        self.audit_tree = ttk.Treeview(self.audit_tab, columns=columns, show="headings")
        for col in columns:
            self.audit_tree.heading(col, text=col)
            self.audit_tree.column(col, width=180)
        self.audit_tree.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(self.audit_tab, text="Refresh Audit Log", command=self._refresh_audit_log).pack(pady=(0, 10))
        self._refresh_audit_log()

    def _load_profiles(self):
        self.profile_listbox.delete(0, tk.END)
        profiles = self.profile_manager.get_all_profiles()
        for profile in profiles:
            self.profile_listbox.insert(tk.END, profile)

    def _on_select_profile(self, event):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
        self.current_profile_id = self.profile_listbox.get(selection[0])
        self.current_profile_data = self.profile_manager.load_profile(self.current_profile_id)
        if not self.current_profile_data:
            return

        self.profile_id_var.set(self.current_profile_data.get("profile_id", "-"))
        self.name_var.set("[Hashed]")
        self.username_var.set("[Hashed]")
        self.job_var.set(self.current_profile_data.get("job", ""))
        self.url_var.set(self.current_profile_data.get("profile_url", ""))
        self.memo_text.delete(1.0, tk.END)
        self.memo_text.insert(1.0, self.current_profile_data.get("memo", ""))

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for entry in self.current_profile_data.get("search_results", []):
            result = entry.get("result", {})
            platform = result.get("name", "Unknown")
            username = result.get("username", "")
            url = result.get("url_main", "")
            status = "Found" if url else "Not Found"
            self.results_tree.insert("", "end", values=(platform, username, url, status))

    def _on_new_profile(self):
        username = simpledialog.askstring("New Profile", "公開ユーザーネーム:")
        if not username:
            return
        name = simpledialog.askstring("New Profile", "公開名前:") or ""
        job = simpledialog.askstring("New Profile", "仕事:") or ""
        url = simpledialog.askstring("New Profile", "プロフィールURL:") or ""
        profile_id = self.profile_manager.create_profile(username=username, name=name, job=job, profile_url=url)
        self.current_profile_id = profile_id
        self._load_profiles()
        self._on_select_profile(None)
        log_event(
            operation="profile_create_ui",
            resource_type="profile",
            resource_id=profile_id,
            status="success",
            details={"username": username, "job": job},
            user_id="system",
        )

    def _on_delete_profile(self):
        if not self.current_profile_id:
            messagebox.showwarning("Warning", "Select a profile first")
            return
        if messagebox.askyesno("Delete", f"Delete {self.current_profile_id}?"):
            self.profile_manager.delete_profile(self.current_profile_id)
            self._load_profiles()
            self.current_profile_id = None
            self.current_profile_data = None
            log_event(
                operation="profile_delete_ui",
                resource_type="profile",
                resource_id=self.current_profile_id,
                status="success",
                user_id="system",
            )

    def _run_search(self):
        if not self.current_profile_id or not self.current_profile_data:
            messagebox.showwarning("Warning", "Select a profile first")
            return

        username = self.username_var.get()
        if username in ("", "[Hashed]"):
            messagebox.showwarning("Warning", "Please enter a username first")
            return

        self.progress_label.config(text="検索中...")
        self.progress['value'] = 0

        def worker():
            results = self.sherlock.search(username)
            self.root.after(0, lambda: self._finish_search(results))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_search(self, results):
        self.progress['value'] = 100
        self.progress_label.config(text="完了")
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for result in results:
            platform = result.get("name", "Unknown")
            username = result.get("username", "")
            url = result.get("url_main", "")
            status = "Found" if url else "Not Found"
            self.results_tree.insert("", "end", values=(platform, username, url, status))

        if self.current_profile_id:
            for result in results:
                self.profile_manager.add_search_result(self.current_profile_id, "Sherlock", result)
            self.current_profile_data = self.profile_manager.load_profile(self.current_profile_id)
            self._on_select_profile(None)

        log_event(
            operation="search_ui_complete",
            resource_type="profile",
            resource_id=self.current_profile_id,
            status="success",
            details={"result_count": len(results)},
            user_id="system",
        )

    def _save_profile(self):
        if not self.current_profile_id or not self.current_profile_data:
            messagebox.showwarning("Warning", "Select a profile first")
            return

        self.current_profile_data["job"] = self.job_var.get()
        self.current_profile_data["profile_url"] = self.url_var.get()
        self.current_profile_data["memo"] = self.memo_text.get(1.0, tk.END)
        self.profile_manager.save_profile(self.current_profile_id, self.current_profile_data)
        messagebox.showinfo("Save", "Profile saved")
        log_event(
            operation="profile_update_ui",
            resource_type="profile",
            resource_id=self.current_profile_id,
            status="success",
            details={"job": self.job_var.get()},
            user_id="system",
        )

    def _refresh_audit_log(self):
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        logs = self.audit_db.get_logs(limit=100)
        for log in logs:
            details = log.get("details") or ""
            self.audit_tree.insert(
                "",
                "end",
                values=(
                    str(log.get("timestamp", "")),
                    str(log.get("operation", "")),
                    str(log.get("resource_id", "")),
                    str(log.get("status", "")),
                    str(details)[:160],
                ),
            )


if __name__ == "__main__":
    import tkinter as tk
    import tkinter.simpledialog as simpledialog
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
