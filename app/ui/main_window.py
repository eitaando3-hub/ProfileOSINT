"""Main window UI"""
import logging
import threading
from typing import Optional
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.core.profile_manager import ProfileManager
from app.sources.sherlock_wrapper import SherlockWrapper
from app.sources.face_recognition import FaceRecognition
from app.config.settings import global_settings

logger = logging.getLogger(__name__)

class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ProfileOSINT")
        self.root.geometry("1200x700")
        
        self.profile_manager = ProfileManager()
        self.sherlock = SherlockWrapper()
        self.face_recognition = FaceRecognition()
        
        self.current_profile_id = None
        self.current_profile_data = None
        self.search_thread = None
        self.search_running = False
        
        self._setup_ui()
        self._load_profile_list()
    
    def _setup_ui(self):
        """Setup UI components"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Profile list
        left_panel = ttk.Frame(main_container, width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        ttk.Label(left_panel, text="Profiles", font=("Arial", 12, "bold")).pack()
        
        # Profile listbox
        self.profile_listbox = tk.Listbox(left_panel, height=20, width=25)
        self.profile_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.profile_listbox.bind('<<ListboxSelect>>', self._on_profile_select)
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="NEW", command=self._on_new_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self._on_delete_profile).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Tabs
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Profile tab
        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="Profile")
        self._setup_profile_tab()
        
        # Search tab
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search")
        self._setup_search_tab()
    
    def _setup_profile_tab(self):
        """Setup profile tab"""
        # Profile info frame
        info_frame = ttk.LabelFrame(self.profile_tab, text="Basic Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Profile ID
        ttk.Label(info_frame, text="Profile ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_id_label = ttk.Label(info_frame, text="-")
        self.profile_id_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Public Name
        ttk.Label(info_frame, text="公開名前:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(info_frame, width=40)
        self.name_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Public Username
        ttk.Label(info_frame, text="公開ユーザーネーム:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_entry = ttk.Entry(info_frame, width=40)
        self.username_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Job
        ttk.Label(info_frame, text="仕事:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.job_entry = ttk.Entry(info_frame, width=40)
        self.job_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Profile URL
        ttk.Label(info_frame, text="プロフィールURL:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_url_entry = ttk.Entry(info_frame, width=40)
        self.profile_url_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Memo
        ttk.Label(info_frame, text="メモ:").grid(row=5, column=0, sticky=tk.NW, padx=5, pady=5)
        self.memo_text = tk.Text(info_frame, height=4, width=40)
        self.memo_text.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Search button and progress
        search_frame = ttk.Frame(self.profile_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(search_frame, text="Sherlock検索", command=self._on_search).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(search_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = ttk.Label(search_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.profile_tab, text="検索結果")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results table
        columns = ("Platform", "Username", "Profile URL")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, height=10)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        self.results_tree.column("#0", width=0)
        self.results_tree.column("Platform", width=100)
        self.results_tree.column("Username", width=150)
        self.results_tree.column("Profile URL", width=400)
        
        self.results_tree.heading("#0", text="")
        self.results_tree.heading("Platform", text="Platform")
        self.results_tree.heading("Username", text="Username")
        self.results_tree.heading("Profile URL", text="Profile URL")
        
        # Face Recognition Results
        face_results_frame = ttk.LabelFrame(self.profile_tab, text="顔認識結果")
        face_results_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        columns = ("Face ID", "Age", "Gender", "Confidence", "Job")
        self.face_tree = ttk.Treeview(face_results_frame, columns=columns, height=5)
        self.face_tree.pack(fill=tk.BOTH, expand=True)
        
        self.face_tree.column("#0", width=0)
        self.face_tree.column("Face ID", width=60)
        self.face_tree.column("Age", width=60)
        self.face_tree.column("Gender", width=60)
        self.face_tree.column("Confidence", width=100)
        self.face_tree.column("Job", width=100)
        
        self.face_tree.heading("#0", text="")
        self.face_tree.heading("Face ID", text="Face ID")
        self.face_tree.heading("Age", text="Age")
        self.face_tree.heading("Gender", text="Gender")
        self.face_tree.heading("Confidence", text="Confidence")
        self.face_tree.heading("Job", text="Job")
        
        # Save button
        ttk.Button(self.profile_tab, text="Save Profile", command=self._on_save_profile).pack(pady=5)
    
    def _setup_search_tab(self):
        """Setup search tab"""
        ttk.Label(self.search_tab, text="Sherlock Search Results", font=("Arial", 12, "bold")).pack(pady=5)
        
        columns = ("Platform", "Username", "Profile URL", "Status")
        self.search_tree = ttk.Treeview(self.search_tab, columns=columns)
        self.search_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.search_tree.column("#0", width=0)
        self.search_tree.column("Platform", width=100)
        self.search_tree.column("Username", width=150)
        self.search_tree.column("Profile URL", width=400)
        self.search_tree.column("Status", width=80)
        
        self.search_tree.heading("#0", text="")
        self.search_tree.heading("Platform", text="Platform")
        self.search_tree.heading("Username", text="Username")
        self.search_tree.heading("Profile URL", text="Profile URL")
        self.search_tree.heading("Status", text="Status")
    
    def _load_profile_list(self):
        """Load profile list from disk"""
        self.profile_listbox.delete(0, tk.END)
        profiles = self.profile_manager.get_all_profiles()
        for profile_id in profiles:
            self.profile_listbox.insert(tk.END, profile_id)
    
    def _on_profile_select(self, event):
        """Handle profile selection"""
        selection = self.profile_listbox.curselection()
        if not selection:
            return
        
        profile_id = self.profile_listbox.get(selection[0])
        self.current_profile_id = profile_id
        self.current_profile_data = self.profile_manager.load_profile(profile_id)
        
        if self.current_profile_data:
            self._display_profile(self.current_profile_data)
    
    def _display_profile(self, profile_data: dict):
        """Display profile data in UI"""
        self.profile_id_label.config(text=profile_data.get("profile_id", "-"))
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.job_entry.delete(0, tk.END)
        self.profile_url_entry.delete(0, tk.END)
        self.memo_text.delete(1.0, tk.END)
        
        # Note: Names are hashed, so we can't display them
        # Just show placeholder
        self.name_entry.insert(0, "[Hashed]")
        self.username_entry.insert(0, "[Hashed]")
        self.job_entry.insert(0, profile_data.get("job", ""))
        self.profile_url_entry.insert(0, profile_data.get("profile_url", ""))
        self.memo_text.insert(1.0, profile_data.get("memo", ""))
        
        # Clear results tables
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for item in self.face_tree.get_children():
            self.face_tree.delete(item)
        
        # Load search results
        if "search_results" in profile_data:
            for search_result in profile_data["search_results"]:
                result = search_result.get("result", {})
                platform = result.get("name", "Unknown")
                username = result.get("username", "")
                url = result.get("url_main", "")
                
                self.results_tree.insert("", tk.END, values=(platform, username, url))
        
        # Load face recognition results
        if "face_recognition" in profile_data:
            for face_data in profile_data["face_recognition"]:
                face_id = face_data.get("face_id", "")
                age = face_data.get("age", "-")
                gender = face_data.get("gender", "-")
                confidence = f"{face_data.get('confidence', 0):.2f}"
                job = profile_data.get("job", "")
                
                self.face_tree.insert("", tk.END, values=(face_id, age, gender, confidence, job))
    
    def _on_new_profile(self):
        """Create new profile"""
        dialog = NewProfileDialog(self.root, self.profile_manager)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            profile_id = dialog.result
            self._load_profile_list()
            # Select new profile
            profiles = self.profile_manager.get_all_profiles()
            if profile_id in profiles:
                index = profiles.index(profile_id)
                self.profile_listbox.selection_clear(0, tk.END)
                self.profile_listbox.selection_set(index)
                self.profile_listbox.see(index)
                self._on_profile_select(None)
    
    def _on_delete_profile(self):
        """Delete selected profile"""
        if not self.current_profile_id:
            messagebox.showwarning("Warning", "Select a profile first")
            return
        
        if messagebox.askyesno("Confirm", f"Delete {self.current_profile_id}?"):
            self.profile_manager.delete_profile(self.current_profile_id)
            self.current_profile_id = None
            self.current_profile_data = None
            self._load_profile_list()
            messagebox.showinfo("Success", "Profile deleted")
    
    def _on_search(self):
        """Start Sherlock search"""
        if not self.current_profile_id:
            messagebox.showwarning("Warning", "Select a profile first")
            return
        
        username = self.current_profile_data.get("username_hash", "")
        if not username or username == "None":
            messagebox.showwarning("Warning", "Username not set")
            return
        
        # Get actual username from entry for search
        search_username = self.username_entry.get()
        if search_username == "[Hashed]":
            messagebox.showwarning("Warning", "Please enter username first")
            return
        
        # Run search in thread
        self.search_thread = threading.Thread(
            target=self._search_thread,
            args=(search_username,)
        )
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def _search_thread(self, username: str):
        """Background search thread"""
        self.search_running = True
        self.progress_var.set(0)
        self.progress_label.config(text="検索中...")
        
        try:
            # Simulate progress
            results = self.sherlock.search(username)
            
            # Update progress
            self.progress_var.set(100)
            self.progress_label.config(text="完了")
            
            # Display results
            self._display_search_results(results)
            
            # Save results to profile
            if results and self.current_profile_id:
                for result in results:
                    self.profile_manager.add_search_result(
                        self.current_profile_id,
                        "Sherlock",
                        result
                    )
                
                # Reload profile
                self.current_profile_data = self.profile_manager.load_profile(self.current_profile_id)
                self._display_profile(self.current_profile_data)
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.progress_label.config(text="エラー")
        
        finally:
            self.search_running = False
    
    def _display_search_results(self, results: list):
        """Display search results in tree"""
        # Clear search tab results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Add results
        for result in results:
            platform = result.get("name", "Unknown")
            username = result.get("username", "")
            url = result.get("url_main", "")
            status = "Found" if url else "Not Found"
            
            self.search_tree.insert("", tk.END, values=(platform, username, url, status))
    
    def _on_save_profile(self):
        """Save profile"""
        if not self.current_profile_id:
            messagebox.showwarning("Warning", "Select a profile first")
            return
        
        job = self.job_entry.get()
        profile_url = self.profile_url_entry.get()
        memo = self.memo_text.get(1.0, tk.END)
        
        self.current_profile_data["job"] = job
        self.current_profile_data["profile_url"] = profile_url
        self.current_profile_data["memo"] = memo
        
        if self.profile_manager.save_profile(self.current_profile_id, self.current_profile_data):
            messagebox.showinfo("Success", "Profile saved")
        else:
            messagebox.showerror("Error", "Failed to save profile")


class NewProfileDialog:
    """Dialog for creating new profile"""
    
    def __init__(self, parent, profile_manager: ProfileManager):
        self.window = tk.Toplevel(parent)
        self.window.title("New Profile")
        self.window.geometry("400x300")
        self.profile_manager = profile_manager
        self.result = None
        
        # Username
        ttk.Label(self.window, text="公開ユーザーネーム:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.username_entry = ttk.Entry(self.window, width=30)
        self.username_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Public Name
        ttk.Label(self.window, text="公開名前:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.window, width=30)
        self.name_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Job
        ttk.Label(self.window, text="仕事:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.job_entry = ttk.Entry(self.window, width=30)
        self.job_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Profile URL
        ttk.Label(self.window, text="プロフィールURL:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.url_entry = ttk.Entry(self.window, width=30)
        self.url_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Create", command=self._on_create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _on_create(self):
        """Create profile"""
        username = self.username_entry.get().strip()
        name = self.name_entry.get().strip()
        job = self.job_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Warning", "Enter username")
            return
        
        try:
            profile_id = self.profile_manager.create_profile(
                username=username,
                name=name,
                job=job,
                profile_url=url
            )
            self.result = profile_id
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create profile: {e}")
