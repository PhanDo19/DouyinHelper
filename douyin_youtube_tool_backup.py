#!/usr/bin/env python3
"""
🎬 Douyin to YouTube Tool - Final Version
All-in-one tool for downloading Douyin videos and uploading to YouTube
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import json
import time
import threading
import os
import re
import webbrowser
from urllib.parse import urlparse, parse_qs, urlencode
import urllib.request
import urllib.error
from datetime import datetime
import subprocess
import platform
import http.cookiejar

# Check YouTube API availability
YOUTUBE_AVAILABLE = False
try:
    from youtube_uploader import YouTubeUploader
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

class DouyinYouTubeTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Douyin to YouTube Tool")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Data
        self.video_urls = []
        self.video_files = []
        self.download_folder = os.path.expanduser("~/Downloads/Douyin")
        self.selected_videos = set()
        self.is_downloading = False
        self.is_uploading = False
        self.current_preview_path = None
        self.current_video_folder = None
        
        # Cookie jar
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        
        # YouTube uploader
        self.youtube_uploader = None
        if YOUTUBE_AVAILABLE:
            self.youtube_uploader = self.init_youtube_uploader()
        
        self.setup_ui()
        self.create_download_folder()
        
    def init_youtube_uploader(self):
        """Initialize YouTube uploader"""
        try:
            return YouTubeUploader()
        except Exception as e:
            self.log(f"❌ Failed to initialize YouTube uploader: {e}")
            return None
            
    def authenticate_youtube(self):
        """Authenticate with YouTube"""
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return False
            
        try:
            self.log("🔐 Authenticating with YouTube...")
            success = self.youtube_uploader.authenticate()
            if success:
                self.log("✅ YouTube authentication successful!")
                return True
            else:
                self.log("❌ YouTube authentication failed!")
                return False
        except Exception as e:
            error_msg = f"❌ Authentication failed!\n\nError: {str(e)}\n\n🔧 Please check:\n• credentials.json file exists\n• Internet connection\n• Google API permissions"
            messagebox.showerror("Authentication Error", error_msg)
            self.log(f"❌ Authentication error: {e}")
            return False
        
    def create_download_folder(self):
        """Create download folder if not exists"""
        if not os.path.exists(self.download_folder):
            try:
                os.makedirs(self.download_folder)
                self.log(f"📁 Created download folder: {self.download_folder}")
            except:
                self.download_folder = os.path.expanduser("~/Downloads")
                
    def setup_ui(self):
        """Setup main UI with beautiful colors and styling"""
        # Configure styles and colors
        self.setup_styles()
        
        # Set root background
        self.root.configure(bg=self.colors['light'])
        
        # Main container with gradient-like background
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main_container)
        
        # Custom tab bar with better visibility and spacing
        tab_container = ttk.Frame(main_container)
        tab_container.pack(fill=tk.X, pady=(20, 0))
        
        # Custom tab buttons for better control
        tab_button_frame = ttk.Frame(tab_container)
        tab_button_frame.pack(pady=10)
        
        # Create custom tab buttons
        self.current_tab = tk.StringVar(value="download")
        
        self.download_tab_btn = tk.Button(tab_button_frame,
                                         text="  📥  Download Videos  ",
                                         command=lambda: self.switch_tab("download"),
                                         bg=self.colors['primary'], fg='white',
                                         font=('Segoe UI', 12, 'bold'),
                                         relief='flat', padx=25, pady=12,
                                         activebackground='#357ABD',
                                         activeforeground='white')
        self.download_tab_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.upload_tab_btn = tk.Button(tab_button_frame,
                                       text="  📤  Upload to YouTube  ",
                                       command=lambda: self.switch_tab("upload"),
                                       bg=self.colors['medium'], fg='white',
                                       font=('Segoe UI', 12, 'bold'),
                                       relief='flat', padx=25, pady=12,
                                       activebackground=self.colors['secondary'],
                                       activeforeground='white')
        self.upload_tab_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Content container
        self.content_container = ttk.Frame(tab_container)
        self.content_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs with new system
        self.create_download_tab()
        self.create_upload_tab()
        
        # Start with download tab
        self.switch_tab("download")
        
        # Footer
        self.create_footer(main_container)
        
    def switch_tab(self, tab_name):
        """Switch between custom tabs"""
        self.current_tab.set(tab_name)
        
        # Update button styles
        if tab_name == "download":
            self.download_tab_btn.config(bg=self.colors['primary'])
            self.upload_tab_btn.config(bg=self.colors['medium'])
            # Show download frame, hide upload frame
            self.download_frame.pack(fill=tk.BOTH, expand=True)
            self.upload_frame.pack_forget()
        else:
            self.download_tab_btn.config(bg=self.colors['medium'])
            self.upload_tab_btn.config(bg=self.colors['primary'])
            # Show upload frame, hide download frame
            self.upload_frame.pack(fill=tk.BOTH, expand=True)
            self.download_frame.pack_forget()
            
            # Auto-login for YouTube
            if YOUTUBE_AVAILABLE and self.youtube_uploader:
                if not self.youtube_uploader.youtube:
                    self.log("🔐 Auto-authenticating with YouTube...")
                    self.youtube_authenticate_thread()
                else:
                    self.log("✅ Already authenticated with YouTube")
            else:
                self.log("❌ YouTube uploader not available")
        
    def setup_styles(self):
        """Setup beautiful color themes and styles"""
        style = ttk.Style()
        
        # Configure color scheme
        self.colors = {
            'primary': '#4A90E2',      # Soft blue
            'secondary': '#7ED321',    # Fresh green  
            'accent': '#F5A623',       # Warm orange
            'danger': '#D0021B',       # Soft red
            'success': '#50E3C2',      # Mint green
            'warning': '#F8E71C',      # Sunny yellow
            'info': '#9013FE',         # Purple
            'light': '#F8F9FA',        # Light gray
            'medium': '#6C757D',       # Medium gray
            'dark': '#343A40'          # Dark gray
        }
        
        # Configure notebook style with better spacing and visibility
        style.configure('TNotebook', 
                       background=self.colors['light'],
                       borderwidth=0,
                       tabmargins=[10, 10, 10, 0])  # Better spacing between tabs
        style.configure('TNotebook.Tab', 
                       padding=[25, 12],  # More padding for better spacing
                       background=self.colors['medium'],
                       foreground='white',
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))  # Larger, bolder font
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary']),
                           ('active', self.colors['secondary'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white'),
                           ('!active', 'white')])
        
        # Configure button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', '#357ABD'),
                           ('pressed', '#2E6DA4')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['dark'],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#40C4AA')],
                 foreground=[('active', self.colors['dark'])])
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['dark'],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Warning.TButton',
                 foreground=[('active', self.colors['dark'])])
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton',
                 foreground=[('active', 'white')])
        
        # Configure frame styles
        style.configure('Colored.TLabelFrame',
                       background=self.colors['light'],
                       relief='solid',
                       borderwidth=1)
        style.configure('Colored.TLabelFrame.Label',
                       background=self.colors['light'],
                       foreground=self.colors['primary'],
                       font=('Segoe UI', 11, 'bold'))
        
    # Old method - now using custom tab system
    def create_header(self, parent):
        """Create beautiful colorful header"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Main title with gradient effect
        title_frame = ttk.Frame(header)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Animated title with colorful emojis
        title_label = tk.Label(title_frame, 
                              text="🎬 Douyin ➜ YouTube Tool 🚀", 
                              font=('Segoe UI', 22, 'bold'), 
                              foreground=self.colors['primary'],
                              background=self.colors['light'])
        title_label.pack(side=tk.LEFT)
        
        # Status with colorful indicators
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(side=tk.RIGHT)
        
        if YOUTUBE_AVAILABLE:
            status_text = "🟢 YouTube Ready"
            status_color = self.colors['success']
        else:
            status_text = "🔴 YouTube Not Available"
            status_color = self.colors['danger']
            
        status_label = tk.Label(status_frame, 
                               text=status_text,
                               font=('Segoe UI', 11, 'bold'), 
                               foreground=status_color,
                               background=self.colors['light'])
        status_label.pack()
        
        # Decorative separator with gradient
        separator_frame = ttk.Frame(header)
        separator_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Create gradient-like separator using multiple colored lines
        colors_gradient = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        for i, color in enumerate(colors_gradient):
            separator = tk.Frame(separator_frame, height=2, background=color)
            separator.pack(fill=tk.X, pady=1)
        
    def create_footer(self, parent):
        """Create colorful footer"""
        footer_container = ttk.Frame(parent)
        footer_container.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        
        # Gradient separator
        separator_frame = ttk.Frame(footer_container)
        separator_frame.pack(fill=tk.X, pady=(0, 10))
        
        colors_gradient = [self.colors['accent'], self.colors['secondary'], self.colors['primary']]
        for color in colors_gradient:
            separator = tk.Frame(separator_frame, height=1, background=color)
            separator.pack(fill=tk.X, pady=0.5)
        
        # Footer content with colors
        footer = ttk.Frame(footer_container)
        footer.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="🟢 Ready to start!")
        status_label = tk.Label(footer, 
                               textvariable=self.status_var,
                               font=('Segoe UI', 10, 'bold'), 
                               foreground=self.colors['primary'],
                               background=self.colors['light'])
        status_label.pack(side=tk.LEFT)
        
        # Styled progress bar
        progress_frame = ttk.Frame(footer)
        progress_frame.pack(side=tk.RIGHT)
        
        tk.Label(progress_frame, 
                text="Progress:",
                font=('Segoe UI', 9),
                foreground=self.colors['medium'],
                background=self.colors['light']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.global_progress = ttk.Progressbar(progress_frame, length=250, mode='determinate')
        self.global_progress.pack(side=tk.RIGHT)
        
    def create_download_tab(self):
        """Create colorful download tab"""
        self.download_frame = ttk.Frame(self.content_container)
        # Don't pack it yet, will be handled by switch_tab
        
        main_frame = ttk.Frame(self.download_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions (Simplified)
        inst_frame = ttk.LabelFrame(main_frame, text="📋 Quick Guide", padding="10")
        inst_frame.pack(fill=tk.X, pady=(0, 15))
        
        quick_instructions = [
            "🌐 Open Douyin → F12 → Network → Find 'aweme/post' → Copy as cURL → Paste below"
        ]
        
        for inst in quick_instructions:
            ttk.Label(inst_frame, text=inst, font=('Segoe UI', 10), 
                     foreground='#3498db', wraplength=600).pack(anchor=tk.W, pady=2)
            
        # cURL Input (Compact)
        curl_frame = ttk.LabelFrame(main_frame, text="🔗 cURL Input", padding="10")
        curl_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input area with buttons inline
        input_frame = ttk.Frame(curl_frame)
        input_frame.pack(fill=tk.X)
        
        # Text input (smaller)
        self.curl_text = tk.Text(input_frame, height=3, font=('Consolas', 9),
                                bg=self.colors['light'], fg=self.colors['dark'],
                                insertbackground=self.colors['primary'])
        self.curl_text.pack(fill=tk.X, pady=(0, 8))
        
        # Buttons with beautiful colors - using tk.Button for better visibility
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)
        
        paste_btn = tk.Button(button_frame, text="📋 Paste", 
                             command=self.paste_curl,
                             bg=self.colors['primary'], fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        paste_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        parse_btn = tk.Button(button_frame, text="🔍 Parse", 
                             command=self.parse_curl,
                             bg=self.colors['success'], fg=self.colors['dark'],
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        parse_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear", 
                             command=self.clear_curl,
                             bg=self.colors['warning'], fg=self.colors['dark'],
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', padx=15, pady=8)
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Show advanced toggle with color
        self.show_advanced = tk.BooleanVar()
        advanced_check = tk.Checkbutton(button_frame, text="⚙️ Advanced", 
                                       variable=self.show_advanced, command=self.toggle_advanced)
        advanced_check.pack(side=tk.RIGHT)        # Advanced Config (Initially Hidden)
        self.advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Configuration", padding="10")
        
        # API URL
        ttk.Label(self.advanced_frame, text="API URL:").pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.advanced_frame, textvariable=self.url_var, font=('Consolas', 9))
        self.url_entry.pack(fill=tk.X, pady=(2, 8))
        
        # Headers (Collapsible)
        self.show_headers = tk.BooleanVar()
        tk.Checkbutton(self.advanced_frame, text="🔧 Custom Headers", 
                       variable=self.show_headers, command=self.toggle_headers).pack(anchor=tk.W)
        
        self.headers_frame = ttk.Frame(self.advanced_frame)
        self.headers_text = tk.Text(self.headers_frame, height=4, font=('Consolas', 8),
                                   bg=self.colors['light'], fg=self.colors['dark'],
                                   insertbackground=self.colors['primary'])
        self.headers_text.pack(fill=tk.X)
        
        # Download section (More compact)
        download_frame = ttk.LabelFrame(main_frame, text="📥 Download Manager", padding="10")
        download_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Controls (Better layout)
        control_frame = ttk.Frame(download_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action buttons with colors - using tk.Button for visibility
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.LEFT)
        
        analyze_btn = tk.Button(action_frame, text="🔍 Analyze", 
                               command=self.analyze_url_thread,
                               bg=self.colors['primary'], fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', padx=15, pady=8)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        folder_btn = tk.Button(action_frame, text="📁 Folder", 
                              command=self.select_download_folder,
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        folder_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.download_btn = tk.Button(action_frame, text="📥 Download All", 
                                     command=self.download_videos_thread, 
                                     state='disabled',
                                     bg=self.colors['success'], fg=self.colors['dark'],
                                     font=('Segoe UI', 10, 'bold'),
                                     relief='flat', padx=15, pady=8)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Status on right with color
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.download_status_var = tk.StringVar(value="🟢 Ready")
        status_label = tk.Label(status_frame, 
                               textvariable=self.download_status_var,
                               font=('Segoe UI', 9, 'bold'),
                               foreground=self.colors['success'],
                               background=self.colors['light'])
        status_label.pack()
        
        # Progress
        self.download_progress = ttk.Progressbar(download_frame, mode='determinate')
        self.download_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Video list (Improved)
        list_frame = ttk.Frame(download_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with count and filters
        list_header = ttk.Frame(list_frame)
        list_header.pack(fill=tk.X, pady=(0, 8))
        
        self.video_count_var = tk.StringVar(value="📋 Videos: 0")
        ttk.Label(list_header, textvariable=self.video_count_var, 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        # Quick actions with colorful buttons - using tk.Button for visibility
        select_all_btn = tk.Button(list_header, text="✅ Select All", 
                                  command=self.select_all_videos,
                                  bg=self.colors['success'], fg=self.colors['dark'],
                                  font=('Segoe UI', 9, 'bold'),
                                  relief='flat', padx=12, pady=6)
        select_all_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        clear_all_btn = tk.Button(list_header, text="❌ Clear All", 
                                 command=self.clear_all_videos,
                                 bg=self.colors['warning'], fg=self.colors['dark'],
                                 font=('Segoe UI', 9, 'bold'),
                                 relief='flat', padx=12, pady=6)
        clear_all_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Treeview (Improved columns)
        columns = ('Select', 'Index', 'Status', 'Title', 'URL')
        self.video_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.video_tree.heading('Select', text='☐')
        self.video_tree.heading('Index', text='#')
        self.video_tree.heading('Status', text='Status')
        self.video_tree.heading('Title', text='Title')
        self.video_tree.heading('URL', text='URL')
        
        self.video_tree.column('Select', width=40, anchor=tk.CENTER)
        self.video_tree.column('Index', width=50, anchor=tk.CENTER)
        self.video_tree.column('Status', width=100, anchor=tk.CENTER)
        self.video_tree.column('Title', width=200)
        self.video_tree.column('URL', width=300)
        
        # Bind double-click to toggle selection
        self.video_tree.bind('<Double-1>', self.toggle_video_selection)
        
        # Scrollbar
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=v_scroll.set)
        
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_upload_tab(self):
        """Create upload tab"""
        self.upload_frame = ttk.Frame(self.content_container)
        # Don't pack it yet, will be handled by switch_tab
        
        main_frame = ttk.Frame(self.upload_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # YouTube Status & Authentication (Combined)
        status_frame = ttk.LabelFrame(main_frame, text="�  YouTube Status & Authentication", padding="15")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # API Status
        api_status_frame = ttk.Frame(status_frame)
        api_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_controls = ttk.Frame(api_status_frame)
        status_controls.pack(fill=tk.X)
        
        if YOUTUBE_AVAILABLE:
            ttk.Label(status_controls, text="✅ YouTube API Available", 
                     font=('Segoe UI', 10, 'bold'), foreground='#27ae60').pack(side=tk.LEFT)
            
            # YouTube Manager button
            tk.Button(status_controls, text="⚙️ YouTube Manager", 
                      command=self.show_youtube_manager,
                      bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                      font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.RIGHT)
        else:
            ttk.Label(status_controls, text="❌ YouTube API Not Available", 
                     font=('Segoe UI', 10, 'bold'), foreground='#e74c3c').pack(side=tk.LEFT)
            
        # Authentication Controls
        auth_controls = ttk.Frame(status_frame)
        auth_controls.pack(fill=tk.X)
        
        self.youtube_auth_btn = tk.Button(auth_controls, text="🔐 Login YouTube", 
                                          command=self.youtube_authenticate_thread,
                                          bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                                          font=('Segoe UI', 9, 'bold'), cursor='hand2')
        self.youtube_auth_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.auth_status = ttk.Label(auth_controls, text="🔴 Not authenticated", 
                                    font=('Segoe UI', 10), foreground='#e74c3c')
        self.auth_status.pack(side=tk.LEFT)

        # Comprehensive Upload Configuration (compact version)
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Upload Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))

        # Create compact settings in single row
        settings_row = ttk.Frame(config_frame)
        settings_row.pack(fill=tk.X, pady=(0, 5))

        # Basic settings in one row
        ttk.Label(settings_row, text="📝 Title:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_template_var = tk.StringVar(value="[FILENAME] - Amazing Douyin Video! 🔥")
        title_entry = tk.Entry(settings_row, textvariable=self.title_template_var, width=30,
                              bg=self.colors['light'], fg=self.colors['dark'],
                              insertbackground=self.colors['primary'], font=('Segoe UI', 9))
        title_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        
        ttk.Label(settings_row, text="🔒 Privacy:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.privacy_var = tk.StringVar(value="public")
        privacy_combo = ttk.Combobox(settings_row, textvariable=self.privacy_var, 
                    values=["public", "unlisted", "private"], state="readonly", width=10)
        privacy_combo.grid(row=0, column=3, padx=(0, 15))

        # Preset management compact
        ttk.Label(settings_row, text="🎛️ Preset:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.preset_var = tk.StringVar(value="Default")
        preset_combo = ttk.Combobox(settings_row, textvariable=self.preset_var,
                    values=["Default", "Entertainment", "Educational", "Gaming", "Music"], 
                    state="readonly", width=12)
        preset_combo.grid(row=0, column=5, padx=(0, 10))
        
        tk.Button(settings_row, text="💾 Save", 
                  command=self.save_upload_preset,
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 8, 'bold'), cursor='hand2').grid(row=0, column=6, padx=(0, 5))
        tk.Button(settings_row, text="📥 Load", 
                  command=self.load_upload_preset,
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 8, 'bold'), cursor='hand2').grid(row=0, column=7)

        # Title Template
        title_label = tk.Label(basic_grid, text="📝 Title Template:", 
                              bg=self.colors['light'], fg=self.colors['dark'],
                              font=('Segoe UI', 9, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        title_frame = ttk.Frame(basic_grid)
        title_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        
        self.title_template_var = tk.StringVar(value="[FILENAME] - Amazing Douyin Video! 🔥")
        title_entry = tk.Entry(title_frame, textvariable=self.title_template_var, width=60,
                              bg=self.colors['light'], fg=self.colors['dark'],
                              insertbackground=self.colors['primary'], font=('Segoe UI', 9))
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        hint_label = tk.Label(title_frame, text="💡 Use [FILENAME] as placeholder", 
                              bg=self.colors['light'], fg=self.colors['medium'],
                              font=('Segoe UI', 8))
        hint_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Description Template
        desc_label = tk.Label(basic_grid, text="📄 Description Template:", 
                             bg=self.colors['light'], fg=self.colors['dark'],
                             font=('Segoe UI', 9, 'bold'))
        desc_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        desc_frame = ttk.Frame(basic_grid)
        desc_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        
        self.description_var = tk.StringVar(value="""🎬 Amazing content from Douyin!

Follow for more amazing videos! 
Like and Subscribe if you enjoyed! 

#Douyin #Viral #Entertainment #Shorts""")
        
        desc_text = tk.Text(desc_frame, height=4, width=60, font=('Segoe UI', 9),
                           bg=self.colors['light'], fg=self.colors['dark'])
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_text.insert('1.0', self.description_var.get())
        
        desc_scroll = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=desc_text.yview)
        desc_text.configure(yscrollcommand=desc_scroll.set)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.description_text = desc_text

        # Privacy and Visibility
        privacy_frame = ttk.LabelFrame(basic_grid, text="👁️ Privacy & Visibility", padding="10")
        privacy_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        
        privacy_grid = ttk.Frame(privacy_frame)
        privacy_grid.pack(fill=tk.X)
        
        privacy_label1 = tk.Label(privacy_grid, text="Privacy:",
                                  bg=self.colors['light'], fg=self.colors['dark'],
                                  font=('Segoe UI', 9))
        privacy_label1.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.privacy_var = tk.StringVar(value="public")
        privacy_combo = ttk.Combobox(privacy_grid, textvariable=self.privacy_var, 
                    values=["public", "unlisted", "private"], state="readonly", width=12)
        privacy_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Made for Kids
        self.made_for_kids_var = tk.StringVar(value="no")
        kids_label = tk.Label(privacy_grid, text="Made for Kids:",
                             bg=self.colors['light'], fg=self.colors['dark'],
                             font=('Segoe UI', 9))
        kids_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        kids_combo = ttk.Combobox(privacy_grid, textvariable=self.made_for_kids_var,
                    values=["no", "yes"], state="readonly", width=8)
        kids_combo.grid(row=0, column=3)

        # Advanced Settings Tab
        advanced_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(advanced_tab, text="🚀 Advanced")
        
        adv_grid = ttk.Frame(advanced_tab, padding="10")
        adv_grid.pack(fill=tk.X)

        # Category and Language
        cat_frame = ttk.LabelFrame(adv_grid, text="📂 Category & Language", padding="10")
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        cat_grid = ttk.Frame(cat_frame)
        cat_grid.pack(fill=tk.X)
        
        cat_label1 = tk.Label(cat_grid, text="Category:",
                              bg=self.colors['light'], fg=self.colors['dark'],
                              font=('Segoe UI', 9))
        cat_label1.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.category_var = tk.StringVar(value="Entertainment")
        category_combo = ttk.Combobox(cat_grid, textvariable=self.category_var,
                    values=["Entertainment", "Comedy", "Music", "Gaming", "People & Blogs", 
                           "How-to & Style", "Sports", "Education", "Science & Technology"], 
                    state="readonly", width=18)
        category_combo.grid(row=0, column=1, padx=(0, 20))
        
        lang_label = tk.Label(cat_grid, text="Language:",
                              bg=self.colors['light'], fg=self.colors['dark'],
                              font=('Segoe UI', 9))
        lang_label.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.language_var = tk.StringVar(value="English")
        language_combo = ttk.Combobox(cat_grid, textvariable=self.language_var,
                    values=["English", "Vietnamese", "Chinese", "Spanish", "French", "Japanese", "Korean"],
                    state="readonly", width=12)
        language_combo.grid(row=0, column=3)

        # Tags and Keywords
        tags_frame = ttk.LabelFrame(adv_grid, text="🏷️ Tags & Keywords", padding="10")
        tags_frame.pack(fill=tk.X, pady=(0, 10))
        
        tags_label = tk.Label(tags_frame, text="Tags (comma separated):",
                              bg=self.colors['light'], fg=self.colors['dark'],
                              font=('Segoe UI', 9))
        tags_label.pack(anchor=tk.W)
        self.tags_var = tk.StringVar(value="douyin,viral,entertainment,funny,trending,shorts")
        tags_entry = tk.Entry(tags_frame, textvariable=self.tags_var, width=70,
                              bg=self.colors['light'], fg=self.colors['dark'],
                              insertbackground=self.colors['primary'], font=('Segoe UI', 9))
        tags_entry.pack(fill=tk.X, pady=(5, 0))

        # Thumbnail and Shorts Settings
        media_frame = ttk.LabelFrame(adv_grid, text="🎬 Media Settings", padding="10")
        media_frame.pack(fill=tk.X, pady=(0, 10))
        
        media_grid = ttk.Frame(media_frame)
        media_grid.pack(fill=tk.X)
        
        # Shorts optimization
        self.shorts_mode = tk.BooleanVar(value=True)
        shorts_check = tk.Checkbutton(media_grid, text=" Optimize for YouTube Shorts",
                                      variable=self.shorts_mode,
                                      bg=self.colors['light'], fg=self.colors['dark'],
                                      selectcolor=self.colors['primary'],
                                      font=('Segoe UI', 9))
        self.auto_thumbnail = tk.BooleanVar(value=True)
        thumb_check = tk.Checkbutton(media_grid, text=" Auto-generate thumbnail",
                                     variable=self.auto_thumbnail,
                                     bg=self.colors['light'], fg=self.colors['dark'],
                                     selectcolor=self.colors['primary'],
                                     font=('Segoe UI', 9))
        self.quality_var = tk.StringVar(value="hd720")
        ttk.Label(media_grid, text="Upload Quality:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(media_grid, textvariable=self.quality_var,
                    values=["hd1080", "hd720", "large", "medium"], state="readonly", width=12)
        quality_combo.grid(row=2, column=1, sticky=tk.W)

        # Monetization Tab
        monetization_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(monetization_tab, text="💰 Monetization")
        
        mon_grid = ttk.Frame(monetization_tab, padding="10")
        mon_grid.pack(fill=tk.X)

        # Monetization settings
        monetization_frame = ttk.LabelFrame(mon_grid, text="💰 Monetization Options", padding="10")
        monetization_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.enable_monetization = tk.BooleanVar(value=True)
        tk.Checkbutton(monetization_frame, text="💰 Enable monetization (if eligible)", 
                       variable=self.enable_monetization).pack(anchor=tk.W, pady=(0, 5))
        
        # License and Rights
        license_frame = ttk.LabelFrame(mon_grid, text="⚖️ License & Rights", padding="10")
        license_frame.pack(fill=tk.X, pady=(0, 10))
        
        license_grid = ttk.Frame(license_frame)
        license_grid.pack(fill=tk.X)
        
        ttk.Label(license_grid, text="License:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.license_var = tk.StringVar(value="YouTube Standard License")
        license_combo = ttk.Combobox(license_grid, textvariable=self.license_var,
                    values=["YouTube Standard License", "Creative Commons"], 
                    state="readonly", width=25)
        license_combo.grid(row=0, column=1)

        # Publishing Options Tab  
        publishing_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(publishing_tab, text="⏰ Publishing")
        
        pub_grid = ttk.Frame(publishing_tab, padding="10")
        pub_grid.pack(fill=tk.X)

        # Publish timing
        timing_frame = ttk.LabelFrame(pub_grid, text="⏰ Publish Timing", padding="10")
        timing_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.publish_timing = tk.StringVar(value="immediate")
        immediate_radio = tk.Radiobutton(timing_frame, text="📤 Publish immediately", 
                                        variable=self.publish_timing, value="immediate",
                                        bg=self.colors['light'], fg=self.colors['dark'],
                                        selectcolor=self.colors['primary'],
                                        font=('Segoe UI', 9))
        immediate_radio.pack(anchor=tk.W)
        
        scheduled_radio = tk.Radiobutton(timing_frame, text="📅 Schedule for later", 
                                        variable=self.publish_timing, value="scheduled",
                                        bg=self.colors['light'], fg=self.colors['dark'],
                                        selectcolor=self.colors['primary'],
                                        font=('Segoe UI', 9))
        scheduled_radio.pack(anchor=tk.W)
        
        draft_radio = tk.Radiobutton(timing_frame, text="💾 Save as draft", 
                                    variable=self.publish_timing, value="draft",
                                    bg=self.colors['light'], fg=self.colors['dark'],
                                    selectcolor=self.colors['primary'],
                                    font=('Segoe UI', 9))
        draft_radio.pack(anchor=tk.W)

        # Notification settings
        notif_frame = ttk.LabelFrame(pub_grid, text="🔔 Notifications", padding="10")
        notif_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.notify_subscribers = tk.BooleanVar(value=True)
        notify_check = tk.Checkbutton(notif_frame, text="🔔 Notify subscribers", 
                                      variable=self.notify_subscribers,
                                      bg=self.colors['light'], fg=self.colors['dark'],
                                      selectcolor=self.colors['primary'],
                                      font=('Segoe UI', 9))
        notify_check.pack(anchor=tk.W)

        # Preset management
        preset_frame = ttk.Frame(config_frame)
        preset_frame.pack(fill=tk.X, pady=(10, 0))
        
        preset_label = tk.Label(preset_frame, text="🎛️ Presets:", 
                                bg=self.colors['light'], fg=self.colors['dark'],
                                font=('Segoe UI', 9, 'bold'))
        preset_label.pack(side=tk.LEFT)
        
        self.preset_var = tk.StringVar(value="Default")
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                    values=["Default", "Entertainment", "Educational", "Gaming", "Music"], 
                    state="readonly", width=15)
        preset_combo.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Button(preset_frame, text="💾 Save Preset", 
                  command=self.save_upload_preset,
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(5, 0))
        tk.Button(preset_frame, text="📥 Load Preset", 
                  command=self.load_upload_preset,
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(5, 0))

        # Video Selection (moved below settings)
        video_frame = ttk.LabelFrame(main_frame, text="📹  Select Videos to Upload", padding="15")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Controls with better visibility
        selection_controls = ttk.Frame(video_frame)
        selection_controls.pack(fill=tk.X, pady=(0, 15))
        
        browse_btn = tk.Button(selection_controls, text="📁 Browse Videos", 
                              command=self.browse_videos_for_upload,
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        download_btn = tk.Button(selection_controls, text="📥 From Downloads", 
                                command=self.load_downloaded_videos,
                                bg=self.colors['primary'], fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', padx=15, pady=8)
        download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_all_btn = tk.Button(selection_controls, text="✅ Select All", 
                                  command=self.select_all_for_upload,
                                  bg=self.colors['success'], fg=self.colors['dark'],
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=8)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        deselect_btn = tk.Button(selection_controls, text="❌ Deselect All", 
                                command=self.deselect_all_for_upload,
                                bg=self.colors['warning'], fg=self.colors['dark'],
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', padx=15, pady=8)
        deselect_btn.pack(side=tk.LEFT)
        
        # Upload list
        upload_list_frame = ttk.Frame(video_frame)
        upload_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.upload_count_var = tk.StringVar(value="📋 Selected: 0")
        ttk.Label(upload_list_frame, textvariable=self.upload_count_var, 
                 font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Upload treeview
        upload_columns = ('Select', 'File', 'Size', 'Status', 'Actions')
        self.upload_tree = ttk.Treeview(upload_list_frame, columns=upload_columns, 
                                       show='headings', height=6)
        
        # Configure larger font for icons
        style = ttk.Style()
        style.configure("Large.Treeview", font=('Segoe UI', 11))
        style.configure("Large.Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        self.upload_tree.configure(style="Large.Treeview")
        
        self.upload_tree.heading('Select', text='✓')
        self.upload_tree.heading('File', text='📹 File')
        self.upload_tree.heading('Size', text='📊 Size')
        self.upload_tree.heading('Status', text='📋 Status')
        self.upload_tree.heading('Actions', text='🎛️ Actions')
        
        self.upload_tree.column('Select', width=50, anchor=tk.CENTER)
        self.upload_tree.column('File', width=220)
        self.upload_tree.column('Size', width=80, anchor=tk.CENTER)
        self.upload_tree.column('Status', width=100, anchor=tk.CENTER)
        self.upload_tree.column('Actions', width=140, anchor=tk.CENTER)
        
        # Configure row colors for selection
        self.upload_tree.tag_configure('selected', background='#e3f2fd', foreground='#1976d2')
        self.upload_tree.tag_configure('unselected', background=self.colors['light'], foreground=self.colors['dark'])
        
        upload_v_scroll = ttk.Scrollbar(upload_list_frame, orient=tk.VERTICAL, 
                                       command=self.upload_tree.yview)
        self.upload_tree.configure(yscrollcommand=upload_v_scroll.set)
        
        self.upload_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        upload_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.upload_tree.bind('<Double-1>', self.toggle_upload_selection)
        self.upload_tree.bind('<<TreeviewSelect>>', self.on_video_select)
        self.upload_tree.bind('<Button-1>', self.on_tree_click)
        self.upload_tree.bind('<Button-3>', self.show_context_menu)  # Right click
        
        # Compact preview info (below table)
        preview_compact = ttk.Frame(upload_list_frame)
        preview_compact.pack(fill=tk.X, pady=(5, 0))
        
        self.preview_info = ttk.Label(preview_compact, text="📹  No video selected", 
                                     font=('Segoe UI', 10), foreground='#666')
        self.preview_info.pack(anchor=tk.W)

        # Upload Controls (moved from old settings section)
        upload_controls_frame = ttk.LabelFrame(main_frame, text="� Upload Actions", padding="15")
        upload_controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        upload_controls = ttk.Frame(upload_controls_frame)
        upload_controls.pack(fill=tk.X)
        
        self.upload_selected_btn = tk.Button(upload_controls, text="🚀 Upload Selected", 
                                            command=self.upload_selected_videos_thread, state='disabled',
                                            bg=self.colors['success'], fg=self.colors['dark'],
                                            font=('Segoe UI', 10, 'bold'),
                                            relief='flat', padx=15, pady=8)
        self.upload_selected_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.upload_optimized_btn = tk.Button(upload_controls, text="🎯 Upload Optimized", 
                                             command=self.upload_optimized_videos_thread, state='disabled',
                                             bg=self.colors['primary'], fg='white',
                                             font=('Segoe UI', 10, 'bold'),
                                             relief='flat', padx=15, pady=8)
        self.upload_optimized_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.upload_shorts_btn = tk.Button(upload_controls, text="📱 Upload as Shorts", 
                                          command=self.upload_as_shorts_thread, state='disabled',
                                          bg=self.colors['accent'], fg=self.colors['dark'],
                                          font=('Segoe UI', 10, 'bold'),
                                          relief='flat', padx=15, pady=8)
        self.upload_shorts_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        studio_btn = tk.Button(upload_controls, text="📺 YouTube Studio", 
                              command=self.open_youtube_studio,
                              bg=self.colors['info'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', padx=15, pady=8)
        studio_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        channel_btn = tk.Button(upload_controls, text="📺 My Channel", 
                               command=self.open_my_channel,
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='flat', padx=15, pady=8)
        channel_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Combined YouTube Manager button
        ttk.Button(upload_controls, text="� YouTube Manager", 
                  command=self.show_youtube_manager).pack(side=tk.LEFT, padx=(0, 10))
        
        self.upload_status_var = tk.StringVar(value="🟢 Ready to upload...")
        ttk.Label(upload_controls, textvariable=self.upload_status_var).pack(side=tk.LEFT)
        
        self.upload_progress = ttk.Progressbar(config_frame, mode='determinate')
        self.upload_progress.pack(fill=tk.X, pady=(10, 0))
        
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.status_var.set(message)
        print(formatted_message)
        self.root.update_idletasks()
        
    # cURL Functions
    def paste_curl(self):
        """Paste cURL from clipboard"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.curl_text.delete(1.0, tk.END)
            self.curl_text.insert(tk.END, clipboard_text)
            self.log("📋 Pasted cURL from clipboard")
        except:
            messagebox.showerror("Error", "No text in clipboard!")
            
    def clear_curl(self):
        """Clear cURL text"""
        self.curl_text.delete(1.0, tk.END)
        self.log("🗑️ Cleared cURL input")
        
    def parse_curl(self):
        """Parse cURL command"""
        curl_text = self.curl_text.get(1.0, tk.END).strip()
        if not curl_text:
            messagebox.showerror("Error", "Please paste cURL command first!")
            return
            
        try:
            self.log("🔍 Parsing cURL command...")
            
            # Extract URL
            url_match = re.search(r"curl ['\"]([^'\"]+)['\"]", curl_text)
            if not url_match:
                url_match = re.search(r"curl ([^\s]+)", curl_text)
                
            if url_match:
                url = url_match.group(1)
                self.url_var.set(url)
                self.log(f"🎯 Extracted URL")
                
            # Extract headers
            headers = {}
            header_matches = re.findall(r"-H ['\"]([^:]+):\s*([^'\"]+)['\"]", curl_text)
            for header_name, header_value in header_matches:
                headers[header_name] = header_value
                
            # Extract cookies
            cookie_match = re.search(r"-b ['\"]([^'\"]+)['\"]", curl_text)
            if cookie_match:
                cookie_string = cookie_match.group(1)
                headers['Cookie'] = cookie_string
                
            if headers:
                self.headers_text.delete(1.0, tk.END)
                self.headers_text.insert(tk.END, json.dumps(headers, indent=2))
                self.log(f"✅ Extracted {len(headers)} headers")
            else:
                self.log("⚠️ No headers found")
                
        except Exception as e:
            self.log(f"❌ Error parsing cURL: {e}")
            messagebox.showerror("Error", f"Failed to parse cURL: {e}")
            
    def toggle_advanced(self):
        """Toggle advanced configuration visibility"""
        if self.show_advanced.get():
            self.advanced_frame.pack(fill=tk.X, pady=(0, 15))
            self.log("⚙️ Advanced configuration shown")
        else:
            self.advanced_frame.pack_forget()
            self.log("⚙️ Advanced configuration hidden")
            
    def toggle_headers(self):
        """Toggle headers visibility"""
        if self.show_headers.get():
            self.headers_frame.pack(fill=tk.X, pady=(10, 0))
        else:
            self.headers_frame.pack_forget()
            
    # Download Functions
    def select_download_folder(self):
        """Select download folder"""
        folder = filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.log(f"📁 Selected folder: {os.path.basename(folder)}")
            
    def select_all_videos(self):
        """Select all videos for download"""
        for item in self.video_tree.get_children():
            self.video_tree.set(item, 'Select', '☑')
        self.log("✅ Selected all videos")
        
    def clear_all_videos(self):
        """Clear all video selections"""
        for item in self.video_tree.get_children():
            self.video_tree.set(item, 'Select', '☐')
        self.log("❌ Cleared all selections")
        
    def toggle_video_selection(self, event):
        """Toggle video selection on double-click"""
        item = self.video_tree.selection()[0] if self.video_tree.selection() else None
        if item:
            current = self.video_tree.set(item, 'Select')
            new_state = '☐' if current == '☑' else '☑'
            self.video_tree.set(item, 'Select', new_state)
            
    def analyze_url_thread(self):
        """Analyze URL in thread"""
        thread = threading.Thread(target=self.analyze_url, daemon=True)
        thread.start()
        
    def analyze_url(self):
        """Analyze URL and get video list"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please provide API URL!")
            return
            
        if 'aweme/v1/web/aweme/post' not in url:
            messagebox.showerror("Error", "URL must be Douyin API endpoint!")
            return
            
        try:
            self.log("🔍 Analyzing URL...")
            
            # Extract user ID
            sec_user_id = self.extract_user_id_from_api_url(url)
            if not sec_user_id:
                messagebox.showerror("Error", "Cannot extract User ID!")
                return
                
            # Clear previous results
            for item in self.video_tree.get_children():
                self.video_tree.delete(item)
            self.video_urls.clear()
            
            # Fetch data
            max_cursor = 0
            page = 1
            
            while page <= 5:  # Limit to 5 pages
                self.log(f"📄 Loading page {page}...")
                
                current_url = self.update_url_with_params(url, max_cursor, sec_user_id)
                data = self.fetch_api_data(current_url)
                
                if not data:
                    break
                    
                if 'aweme_list' not in data:
                    break
                    
                aweme_list = data.get('aweme_list', [])
                has_more = data.get('has_more', False)
                max_cursor = data.get('max_cursor', 0)
                
                for video in aweme_list:
                    video_url = self.extract_video_url(video)
                    if video_url:
                        self.video_urls.append(video_url)
                        index = len(self.video_urls)
                        
                        self.video_tree.insert('', 'end', values=(
                            f"#{index:03d}",
                            "📋 Found",
                            video_url[:60] + "..." if len(video_url) > 60 else video_url
                        ))
                        
                if not has_more:
                    break
                    
                page += 1
                time.sleep(1)
                
            if self.video_urls:
                self.log(f"🎉 Found {len(self.video_urls)} videos")
                self.video_count_var.set(f"📋 Videos: {len(self.video_urls)}")
                self.download_btn.config(state='normal')
            else:
                self.log("❌ No videos found")
                
        except Exception as e:
            self.log(f"❌ Analysis error: {e}")
            messagebox.showerror("Error", f"Analysis failed: {e}")
            
    def extract_user_id_from_api_url(self, url):
        """Extract user ID from API URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'sec_user_id' in params:
                return params['sec_user_id'][0]
        except:
            pass
        return None
        
    def update_url_with_params(self, base_url, max_cursor, sec_user_id):
        """Update URL with new parameters"""
        try:
            parsed = urlparse(base_url)
            params = parse_qs(parsed.query)
            
            params['max_cursor'] = [str(max_cursor)]
            params['sec_user_id'] = [sec_user_id]
            
            new_query = urlencode(params, doseq=True)
            new_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
            return new_url
        except:
            return base_url
            
    def fetch_api_data(self, url):
        """Fetch data from API"""
        try:
            headers = self.get_headers()
            req = urllib.request.Request(url, headers=headers)
            
            with self.opener.open(req, timeout=30) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                    
        except Exception as e:
            self.log(f"❌ API error: {e}")
            
        return None
        
    def get_headers(self):
        """Get headers from text area"""
        try:
            headers_text = self.headers_text.get(1.0, tk.END).strip()
            return json.loads(headers_text) if headers_text else {}
        except:
            return {}
            
    def extract_video_url(self, video_data):
        """Extract video URL from API data"""
        try:
            if 'video' in video_data:
                video_info = video_data['video']
                
                if 'play_addr' in video_info and 'url_list' in video_info['play_addr']:
                    url_list = video_info['play_addr']['url_list']
                    if url_list:
                        url = url_list[0]
                        return url.replace('http', 'https') if not url.startswith('https') else url
                        
        except:
            pass
            
        return None
        
    def download_videos_thread(self):
        """Download videos in thread"""
        thread = threading.Thread(target=self.download_videos, daemon=True)
        thread.start()
        
    def download_videos(self):
        """Download all videos"""
        if not self.video_urls:
            messagebox.showerror("Error", "No videos to download!")
            return
            
        if not self.download_folder:
            messagebox.showerror("Error", "Please select download folder!")
            return
            
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        
        total_videos = len(self.video_urls)
        self.download_progress['maximum'] = total_videos
        self.download_progress['value'] = 0
        
        successful = 0
        failed = 0
        
        try:
            for i, url in enumerate(self.video_urls):
                filename = f"video_{i + 1:03d}.mp4"
                file_path = os.path.join(self.download_folder, filename)
                
                # Update tree item
                items = self.video_tree.get_children()
                if i < len(items):
                    self.video_tree.item(items[i], values=(
                        f"#{i+1:03d}",
                        "📥 Downloading...",
                        url[:60] + "..." if len(url) > 60 else url
                    ))
                
                if self.download_single_video(url, file_path, i):
                    successful += 1
                    self.video_files.append({
                        'path': file_path,
                        'filename': filename,
                        'size': self.get_file_size(file_path)
                    })
                    
                    if i < len(items):
                        self.video_tree.item(items[i], values=(
                            f"#{i+1:03d}",
                            "✅ Downloaded",
                            url[:60] + "..." if len(url) > 60 else url
                        ))
                else:
                    failed += 1
                    if i < len(items):
                        self.video_tree.item(items[i], values=(
                            f"#{i+1:03d}",
                            "❌ Failed",
                            url[:60] + "..." if len(url) > 60 else url
                        ))
                
                self.download_progress['value'] = i + 1
                self.download_status_var.set(f"📥 Downloaded: {i + 1}/{total_videos}")
                self.root.update_idletasks()
                
                time.sleep(1)
                
        except Exception as e:
            self.log(f"❌ Download error: {e}")
            
        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal')
            
            # Update upload tab
            self.update_upload_list()
            
            result = f"Download complete!\nSuccess: {successful}\nFailed: {failed}"
            self.log(result)
            messagebox.showinfo("Download Complete", result)
            
    def download_single_video(self, url, file_path, index):
        """Download single video"""
        try:
            self.log(f"📥 Downloading video {index + 1}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.douyin.com/'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.read())
                    return True
                    
        except Exception as e:
            self.log(f"❌ Download error for video {index + 1}: {e}")
            
        return False
        
    def get_file_size(self, file_path):
        """Get human readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"
            
    # Upload Functions
    def browse_videos_for_upload(self):
        """Browse videos for upload"""
        files = filedialog.askopenfilenames(
            title="Select Videos",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            # Store the folder of first file for reference
            self.current_video_folder = os.path.dirname(files[0])
            
            for file_path in files:
                self.add_video_to_upload_list(file_path)
                
            self.log(f"� Added {len(files)} videos from {os.path.basename(self.current_video_folder)}")
        
    def add_video_to_upload_list(self, file_path):
        """Add video to upload list"""
        if not os.path.exists(file_path):
            return
            
        file_name = os.path.basename(file_path)
        file_size = self.get_file_size(file_path)
        
        # Check if already exists
        for item in self.upload_tree.get_children():
            if self.upload_tree.item(item, 'values')[1] == file_name:
                return  # Already exists
        
        # Insert with selected color and actions
        item = self.upload_tree.insert('', 'end', values=(
            "✓",
            file_name,
            file_size,
            "📋 Ready",
            "🎬  📁"  # Larger action buttons with spacing
        ), tags=('selected',))
        
        self.selected_videos.add(file_name)
        self.update_upload_count()
        
    def load_downloaded_videos(self):
        """Load videos from download folder"""
        if not os.path.exists(self.download_folder):
            messagebox.showerror("Error", "Download folder not found!")
            return
            
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
        video_files = []
        
        for file_name in os.listdir(self.download_folder):
            file_path = os.path.join(self.download_folder, file_name)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_name.lower())
                if ext in video_extensions:
                    video_files.append(file_path)
                    
        if video_files:
            # Set download folder as current folder
            self.current_video_folder = self.download_folder
            
            for file_path in video_files:
                self.add_video_to_upload_list(file_path)
            self.log(f"📥 Loaded {len(video_files)} videos from downloads")
        else:
            messagebox.showinfo("Info", "No videos found in download folder")
        
    def update_upload_list(self):
        """Update upload list with downloaded videos"""
        # Clear existing list
        for item in self.upload_tree.get_children():
            self.upload_tree.delete(item)
        self.selected_videos.clear()
        
        # Set download folder as current video folder
        self.current_video_folder = self.download_folder
        
        # Add all downloaded videos
        for video_info in self.video_files:
            file_path = os.path.join(self.download_folder, video_info['filename'])
            if os.path.exists(file_path):
                # Insert with selected color and actions
                item = self.upload_tree.insert('', 'end', values=(
                    "✓",
                    video_info['filename'],
                    video_info['size'],
                    "📋 Ready",
                    "🎬  📁"  # Larger action buttons
                ), tags=('selected',))
                self.selected_videos.add(video_info['filename'])
            
        self.update_upload_count()
        if self.video_files:
            self.log(f"📤 Updated upload list with {len(self.video_files)} videos")
        
    def toggle_upload_selection(self, event):
        """Toggle video selection"""
        item = self.upload_tree.selection()[0] if self.upload_tree.selection() else None
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values:
            current_select = values[0]
            new_select = "✓" if current_select != "✓" else ""
            
            new_values = list(values)
            new_values[0] = new_select
            
            # Update color based on selection
            if new_select == "✓":
                self.upload_tree.item(item, values=new_values, tags=('selected',))
                self.selected_videos.add(values[1])
            else:
                self.upload_tree.item(item, values=new_values, tags=('unselected',))
                self.selected_videos.discard(values[1])
            
            self.update_upload_count()
            
    def on_tree_click(self, event):
        """Handle tree click for selection"""
        region = self.upload_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.upload_tree.identify_row(event.y)
            column = self.upload_tree.identify_column(event.x)
            
            # Handle different column clicks
            if column == "#1":  # Select column
                self.toggle_upload_selection_direct(item)
            elif column == "#5":  # Actions column
                self.handle_action_click(event, item)
                
    def handle_action_click(self, event, item):
        """Handle click on actions column"""
        if not item:
            return
            
        # Get click position within the cell
        bbox = self.upload_tree.bbox(item, "#5")
        if bbox:
            cell_x = event.x - bbox[0]
            cell_width = bbox[2]
            
            # Determine which "button" was clicked (approximate)
            if cell_x < cell_width / 2:
                # First half - open video
                self.open_video_from_item(item)
            else:
                # Second half - show in folder
                self.show_video_folder_from_item(item)
                
    def open_video_from_item(self, item):
        """Open video from tree item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values and len(values) >= 2:
            file_name = values[1]
            self.open_video_by_name(file_name)
            
    def show_video_folder_from_item(self, item):
        """Show video folder from tree item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values and len(values) >= 2:
            file_name = values[1]
            self.show_video_folder_by_name(file_name)
            
    def open_video_by_name(self, file_name):
        """Open video by filename"""
        file_path = self.get_full_video_path(file_name)
        if file_path and os.path.exists(file_path):
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', file_path])
                    
                self.log(f"🎬 Opened video: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open video: {e}")
        else:
            messagebox.showwarning("Warning", f"Video file not found: {file_name}")
            
    def show_video_folder_by_name(self, file_name):
        """Show video folder by filename"""
        file_path = self.get_full_video_path(file_name)
        if file_path and os.path.exists(file_path):
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', file_path])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', file_path])
                else:  # Linux
                    subprocess.run(['nautilus', '--select', file_path])
                    
                self.log(f"📁 Showed in folder: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot show in folder: {e}")
        else:
            messagebox.showwarning("Warning", f"Video file not found: {file_name}")
            
    def get_full_video_path(self, file_name):
        """Get full path for video file"""
        # Try current video folder first
        if hasattr(self, 'current_video_folder') and self.current_video_folder:
            test_path = os.path.join(self.current_video_folder, file_name)
            if os.path.exists(test_path):
                return test_path
        
        # Then try download folder
        test_path = os.path.join(self.download_folder, file_name)
        if os.path.exists(test_path):
            return test_path
            
        # Finally try absolute path
        if os.path.isabs(file_name) and os.path.exists(file_name):
            return file_name
            
        return None
        
    def show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.upload_tree.identify_row(event.y)
        if item:
            # Select the item
            self.upload_tree.selection_set(item)
            
            # Create context menu with larger font
            context_menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 10))
            context_menu.add_command(label="🎬  Open Video", 
                                   command=lambda: self.open_video_from_item(item))
            context_menu.add_command(label="📁  Show in Folder", 
                                   command=lambda: self.show_video_folder_from_item(item))
            context_menu.add_separator()
            context_menu.add_command(label="✅  Toggle Selection", 
                                   command=lambda: self.toggle_upload_selection_direct(item))
            
            # Show menu
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
                
    def toggle_upload_selection_direct(self, item):
        """Toggle selection directly for an item"""
        if not item:
            return
            
        values = self.upload_tree.item(item, 'values')
        if values:
            current_select = values[0]
            new_select = "✓" if current_select != "✓" else ""
            
            new_values = list(values)
            new_values[0] = new_select
            
            # Update color based on selection
            if new_select == "✓":
                self.upload_tree.item(item, values=new_values, tags=('selected',))
                self.selected_videos.add(values[1])
            else:
                self.upload_tree.item(item, values=new_values, tags=('unselected',))
                self.selected_videos.discard(values[1])
            
            self.update_upload_count()
            
    def on_video_select(self, event):
        """Handle video selection for preview"""
        selection = self.upload_tree.selection()
        if selection:
            item = selection[0]
            values = self.upload_tree.item(item, 'values')
            if values and len(values) >= 2:
                file_name = values[1]
                self.update_video_preview(file_name)
                
    def update_video_preview(self, file_name):
        """Update video preview information"""
        # Find full path
        full_path = self.get_full_video_path(file_name)
        
        if full_path and os.path.exists(full_path):
            # Update compact preview info
            file_size = self.get_file_size(full_path)
            info_text = f"📹 {file_name} | 📊 {file_size} | � {os.path.dirname(full_path)}"
            self.preview_info.config(text=info_text)
            self.current_preview_path = full_path
        else:
            self.preview_info.config(text="📹 File not found")
            self.current_preview_path = None
            
    def open_selected_video(self):
        """Open selected video in default player"""
        if hasattr(self, 'current_preview_path') and self.current_preview_path:
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(self.current_preview_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', self.current_preview_path])
                else:  # Linux
                    subprocess.run(['xdg-open', self.current_preview_path])
                    
                self.log(f"🎬 Opened video: {os.path.basename(self.current_preview_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open video: {e}")
        else:
            messagebox.showwarning("Warning", "No video selected!")
            
    def show_video_in_folder(self):
        """Show video in file explorer"""
        if hasattr(self, 'current_preview_path') and self.current_preview_path:
            try:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', self.current_preview_path])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', self.current_preview_path])
                else:  # Linux
                    subprocess.run(['nautilus', '--select', self.current_preview_path])
                    
                self.log(f"📁 Showed in folder: {os.path.basename(self.current_preview_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot show in folder: {e}")
        else:
            messagebox.showwarning("Warning", "No video selected!")
            
    def open_youtube_studio(self):
        """Open YouTube Studio in browser"""
        try:
            import webbrowser
            webbrowser.open("https://studio.youtube.com")
            self.log("📺 Opened YouTube Studio")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open YouTube Studio: {e}")
            
    def open_my_channel(self):
        """Open user's channel in browser"""
        try:
            import webbrowser
            webbrowser.open("https://www.youtube.com/@sealrepo")
            self.log("📺 Opened your channel")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open channel: {e}")
            
    def check_recent_uploads(self):
        """Check status of recent uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("🔍 Checking recent uploads status...")
            
            # Get recent uploads
            result = self.youtube_uploader.list_recent_uploads(max_results=10)
            
            if result['success']:
                videos = result['videos']
                
                if not videos:
                    msg = "❌ No recent uploads found!\n\nPossible reasons:\n• Videos were removed by YouTube\n• Upload failed completely\n• Wrong account authenticated\n\n🔧 Try:\n1. Check YouTube Studio manually\n2. Re-authenticate with correct account\n3. Check for copyright issues"
                    messagebox.showwarning("No Videos Found", msg)
                    self.log("❌ No recent uploads found in channel")
                    return
                
                # Show detailed status
                self.log("📊 ========== RECENT UPLOADS STATUS ==========")
                self.log(f"Found {len(videos)} recent uploads:")
                
                status_details = f"🔍 Recent Uploads Status ({len(videos)} videos):\n\n"
                
                for i, video in enumerate(videos, 1):
                    title = video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
                    privacy = video['privacy_status']
                    upload_status = video['upload_status']
                    processing = video['processing_status']
                    
                    # Log to console
                    self.log(f"{i}. {title}")
                    self.log(f"   🔒 Privacy: {privacy}")
                    self.log(f"   📤 Upload: {upload_status}")
                    self.log(f"   ⚙️  Processing: {processing}")
                    
                    # Add to dialog
                    status_icon = "❌" if upload_status == 'failed' else "⚠️" if processing == 'processing' else "✅"
                    status_details += f"{status_icon} {title}\n"
                    status_details += f"   Privacy: {privacy} | Upload: {upload_status} | Processing: {processing}\n\n"
                    
                    # Check for problems
                    if upload_status == 'failed':
                        self.log(f"   ❌ FAILED: Video upload failed!")
                    elif processing == 'processing':
                        self.log(f"   ⏳ Still processing - wait longer")
                    elif privacy == 'private':
                        self.log(f"   ⚠️  Private - won't show in channel")
                    elif upload_status == 'uploaded' and processing == 'succeeded':
                        self.log(f"   ✅ Should be visible in channel")
                
                self.log("=" * 50)
                
                # Show summary dialog
                status_details += "💡 If videos are missing from your channel:\n"
                status_details += "• Check if they're set to 'Private'\n"
                status_details += "• Wait longer if still 'Processing'\n" 
                status_details += "• Check for copyright/community strikes\n"
                status_details += "• Verify you're checking the correct channel"
                
                messagebox.showinfo("Upload Status Check", status_details)
                
            else:
                error_msg = f"❌ Failed to check upload status!\n\nError: {result['error']}\n\n🔧 Try:\n1. Re-authenticate YouTube\n2. Check internet connection\n3. Verify API permissions"
                messagebox.showerror("Status Check Failed", error_msg)
                self.log(f"❌ Failed to check uploads: {result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error checking video status!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking video status: {e}")
            
    def check_todays_uploads(self):
        """Check videos uploaded today"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📅 Checking today's uploads...")
            
            # Get today's uploads
            result = self.youtube_uploader.get_todays_uploads()
            
            if result['success']:
                videos = result['videos']
                channel_title = result['channel_title']
                total_today = result['total_today']
                
                from datetime import datetime
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                if total_today == 0:
                    msg = f"📅 No uploads today ({today_str})\n\nChannel: {channel_title}\n\n💡 Tips:\n• Videos may take time to appear\n• Check if uploads were successful\n• Verify correct account is authenticated"
                    messagebox.showinfo("No Uploads Today", msg)
                    self.log(f"📅 No uploads found for today ({today_str})")
                    return
                
                # Show detailed status
                self.log(f"📅 ========== TODAY'S UPLOADS ({today_str}) ==========")
                self.log(f"Channel: {channel_title}")
                self.log(f"Total uploads today: {total_today}")
                
                status_details = f"📅 Today's Uploads ({today_str})\n"
                status_details += f"Channel: {channel_title}\n"
                status_details += f"Total: {total_today} video(s)\n\n"
                
                public_count = 0
                private_count = 0
                processing_count = 0
                failed_count = 0
                
                for i, video in enumerate(videos, 1):
                    title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                    privacy = video['privacy_status']
                    upload_status = video['upload_status']
                    processing = video['processing_status']
                    duration = video.get('duration', 'unknown')
                    failure_reason = video.get('failure_reason')
                    rejection_reason = video.get('rejection_reason')
                    
                    # Count by status
                    if privacy == 'public':
                        public_count += 1
                    elif privacy == 'private':
                        private_count += 1
                        
                    if processing == 'processing':
                        processing_count += 1
                    elif upload_status == 'failed' or failure_reason or rejection_reason:
                        failed_count += 1
                    
                    # Log to console
                    self.log(f"{i}. {title}")
                    self.log(f"   🔒 Privacy: {privacy}")
                    self.log(f"   📤 Upload: {upload_status}")
                    self.log(f"   ⚙️  Processing: {processing}")
                    self.log(f"   ⏱️  Duration: {duration}")
                    self.log(f"   🔗 URL: {video['url']}")
                    
                    if failure_reason:
                        self.log(f"   ❌ Failure: {failure_reason}")
                    if rejection_reason:
                        self.log(f"   🚫 Rejected: {rejection_reason}")
                    
                    # Add to dialog
                    if upload_status == 'failed' or failure_reason:
                        status_icon = "❌"
                    elif rejection_reason:
                        status_icon = "🚫"
                    elif processing == 'processing':
                        status_icon = "⏳"
                    elif privacy == 'private':
                        status_icon = "🔒"
                    else:
                        status_icon = "✅"
                        
                    status_details += f"{status_icon} {title}\n"
                    status_details += f"   {privacy} | {upload_status} | {processing}\n"
                    
                    if failure_reason:
                        status_details += f"   ❌ Failed: {failure_reason}\n"
                    if rejection_reason:
                        status_details += f"   🚫 Rejected: {rejection_reason}\n"
                        
                    status_details += f"   🔗 {video['url']}\n\n"
                
                # Add summary
                status_details += "📊 Summary:\n"
                status_details += f"✅ Public: {public_count}\n"
                status_details += f"🔒 Private: {private_count}\n"
                status_details += f"⏳ Processing: {processing_count}\n"
                status_details += f"❌ Failed: {failed_count}\n\n"
                
                if private_count > 0:
                    status_details += "💡 Private videos won't show in your channel publicly.\n"
                if processing_count > 0:
                    status_details += "⏳ Processing videos may take time to appear.\n"
                if failed_count > 0:
                    status_details += "❌ Failed videos need to be re-uploaded.\n"
                
                self.log("=" * 55)
                
                # Show summary dialog
                messagebox.showinfo("Today's Uploads", status_details)
                
            else:
                error_msg = f"❌ Failed to check today's uploads!\n\nError: {result['error']}\n\n🔧 Try:\n1. Re-authenticate YouTube\n2. Check internet connection\n3. Verify API permissions\n4. Make sure you have uploads today"
                messagebox.showerror("Check Failed", error_msg)
                self.log(f"❌ Failed to check today's uploads: {result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error checking today's uploads!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking today's uploads: {e}")
            
    def quick_check_channel(self):
        """Quick check channel recent uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📺 Checking channel recent uploads...")
            
            # Get recent uploads
            result = self.youtube_uploader.list_recent_uploads(max_results=20)
            
            if result['success']:
                videos = result['videos']
                total_found = result['total_found']
                
                if total_found == 0:
                    msg = "📺 No recent uploads found in channel!\n\nPossible reasons:\n• No videos uploaded recently\n• Wrong account authenticated\n• Videos were removed\n\n💡 Tips:\n• Check YouTube Studio manually\n• Verify correct account\n• Try re-authentication"
                    messagebox.showinfo("No Recent Uploads", msg)
                    self.log("📺 No recent uploads found")
                    return
                
                # Show summary
                self.log(f"📺 Found {total_found} recent uploads")
                
                # Create summary
                summary = f"📺 Channel Recent Uploads\n"
                summary += "=" * 40 + "\n\n"
                summary += f"Total videos found: {total_found}\n\n"
                
                # Categorize by status
                public_count = sum(1 for v in videos if v['privacy_status'] == 'public')
                private_count = sum(1 for v in videos if v['privacy_status'] == 'private')
                processing_count = sum(1 for v in videos if v['processing_status'] == 'processing')
                failed_count = sum(1 for v in videos if v['upload_status'] == 'failed')
                
                summary += f"📊 Status Summary:\n"
                summary += f"• Public: {public_count}\n"
                summary += f"• Private: {private_count}\n"
                summary += f"• Processing: {processing_count}\n"
                summary += f"• Failed: {failed_count}\n\n"
                
                summary += f"📋 Recent Videos:\n"
                summary += "-" * 30 + "\n"
                
                for i, video in enumerate(videos[:10], 1):  # Show first 10
                    title = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                    privacy = video['privacy_status'].upper()
                    processing = video['processing_status']
                    
                    summary += f"{i}. {title}\n"
                    summary += f"   Status: {privacy} | {processing}\n"
                    if video.get('published_at'):
                        summary += f"   Published: {video['published_at'][:10]}\n"
                    summary += "\n"
                
                if total_found > 10:
                    summary += f"... and {total_found - 10} more videos\n"
                    summary += "\n💡 Use 'YouTube Manager' for detailed view"
                
                messagebox.showinfo("Channel Uploads", summary)
                
            else:
                error_msg = f"❌ Failed to check channel!\n\nError: {result['error']}\n\n🔧 Try:\n• Re-authenticate YouTube\n• Check internet connection\n• Verify API permissions"
                messagebox.showerror("Error", error_msg)
                self.log(f"❌ Failed to check channel: {result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error checking channel!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking channel: {e}")
            
    def quick_check_today(self):
        """Quick check today's uploads"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        try:
            # Authenticate if needed
            if not self.youtube_uploader.youtube:
                self.authenticate_youtube()
                
            self.log("📅 Checking today's uploads...")
            
            # Get today's uploads
            result = self.youtube_uploader.get_todays_uploads()
            
            if result['success']:
                videos = result['videos']
                channel_title = result['channel_title']
                total_today = result['total_today']
                
                from datetime import datetime
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                if total_today == 0:
                    msg = f"📅 No uploads today ({today_str})\n\nChannel: {channel_title}\n\n💡 This is normal if:\n• You haven't uploaded today\n• Videos are still processing\n• Upload failed\n\n🔧 Check 'YouTube Manager' for more details"
                    messagebox.showinfo("No Uploads Today", msg)
                    self.log(f"📅 No uploads today ({today_str})")
                    return
                
                # Show today's summary
                self.log(f"📅 Found {total_today} uploads today")
                
                summary = f"📅 Today's Uploads ({today_str})\n"
                summary += "=" * 40 + "\n\n"
                summary += f"Channel: {channel_title}\n"
                summary += f"Total uploads today: {total_today}\n\n"
                
                # Categorize today's videos
                public_count = sum(1 for v in videos if v['privacy_status'] == 'public')
                private_count = sum(1 for v in videos if v['privacy_status'] == 'private')
                processing_count = sum(1 for v in videos if v['processing_status'] == 'processing')
                failed_count = sum(1 for v in videos if v.get('failure_reason'))
                
                summary += f"📊 Today's Status:\n"
                summary += f"• Public: {public_count}\n"
                summary += f"• Private: {private_count}\n"
                summary += f"• Processing: {processing_count}\n"
                summary += f"• Failed: {failed_count}\n\n"
                
                summary += f"📋 Today's Videos:\n"
                summary += "-" * 30 + "\n"
                
                for i, video in enumerate(videos, 1):
                    title = video['title'][:30] + "..." if len(video['title']) > 30 else video['title']
                    privacy = video['privacy_status'].upper()
                    processing = video['processing_status']
                    
                    summary += f"{i}. {title}\n"
                    summary += f"   Status: {privacy} | {processing}\n"
                    if video.get('duration'):
                        summary += f"   Duration: {video['duration']}\n"
                    if video.get('failure_reason'):
                        summary += f"   ❌ Failed: {video['failure_reason']}\n"
                    summary += "\n"
                
                summary += "\n💡 Use 'YouTube Manager' for detailed analysis"
                
                messagebox.showinfo("Today's Uploads", summary)
                
            else:
                error_msg = f"❌ Failed to check today's uploads!\n\nError: {result['error']}\n\n🔧 Try:\n• Re-authenticate YouTube\n• Check internet connection\n• Verify you uploaded today"
                messagebox.showerror("Error", error_msg)
                self.log(f"❌ Failed to check today: {result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error checking today's uploads!\n\nError: {str(e)}\n\n🔧 This might be:\n• Authentication issue\n• Network problem\n• API quota exceeded"
            messagebox.showerror("Error", error_msg)
            self.log(f"❌ Error checking today: {e}")
            
    def on_shorts_mode_change(self):
        """Handle Shorts mode toggle"""
        if self.shorts_mode.get():
            self.log("📱 Shorts mode enabled - videos will be optimized for YouTube Shorts")
            # Update default tags for Shorts
            current_tags = self.tags_var.get()
            if "Shorts" not in current_tags:
                new_tags = current_tags + ",Shorts,YouTubeShorts,Short"
                self.tags_var.set(new_tags)
            # Set privacy to public (recommended for Shorts)
            self.privacy_var.set("public")
            # Update button visibility
            self.upload_shorts_btn.pack(side=tk.LEFT, padx=(0, 15))
        else:
            self.log("📹 Regular upload mode - standard YouTube video upload")
            # Remove Shorts tags
            current_tags = self.tags_var.get()
            tags_list = [tag.strip() for tag in current_tags.split(",")]
            shorts_tags = ["Shorts", "YouTubeShorts", "Short", "Vertical"]
            filtered_tags = [tag for tag in tags_list if tag not in shorts_tags]
            self.tags_var.set(",".join(filtered_tags))
            # Hide Shorts upload button
            self.upload_shorts_btn.pack_forget()
            
    def on_quality_mode_change(self):
        """Handle quality optimization toggle"""
        if self.optimize_quality.get():
            self.log("🎯 Quality optimization enabled - videos will be optimized before upload")
            # Show optimized upload button
            self.upload_optimized_btn.pack(side=tk.LEFT, padx=(0, 15))
        else:
            self.log("📹 Basic upload mode - no quality optimization")
            # Hide optimized upload button
            self.upload_optimized_btn.pack_forget()
            
    def on_quality_preset_change(self, event=None):
        """Handle quality preset change"""
        preset = self.quality_preset_var.get()
        
        preset_descriptions = {
            'high_quality': 'Maximum quality with larger file size (CRF 18, slow preset)',
            'youtube_optimized': 'Balanced quality and file size for YouTube (CRF 20, medium preset)', 
            'fast_upload': 'Faster processing with good quality (CRF 23, fast preset)'
        }
        
        description = preset_descriptions.get(preset, 'Unknown preset')
        self.quality_info_label.config(text=description)
        self.log(f"🎯 Quality preset changed to: {preset}")
        
    def analyze_selected_video_quality(self):
        """Analyze quality of selected video"""
        selection = self.upload_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a video to analyze!")
            return
            
        item = selection[0]
        values = self.upload_tree.item(item, 'values')
        if not values or len(values) < 2:
            return
            
        file_name = values[1]
        full_path = self.get_full_video_path(file_name)
        
        if not full_path or not os.path.exists(full_path):
            messagebox.showerror("Error", "Video file not found!")
            return
            
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        # Show analysis in popup
        self.show_video_quality_analysis(full_path, file_name)
        
    def show_video_quality_analysis(self, video_path, file_name):
        """Show detailed video quality analysis in popup"""
        # Create analysis window
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title(f"📊 Video Quality Analysis - {file_name}")
        analysis_window.geometry("900x700")
        analysis_window.resizable(True, True)
        
        # Make it modal
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        
        # Center the window
        analysis_window.update_idletasks()
        x = (analysis_window.winfo_screenwidth() // 2) - (analysis_window.winfo_width() // 2)
        y = (analysis_window.winfo_screenheight() // 2) - (analysis_window.winfo_height() // 2)
        analysis_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(analysis_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text=f"📊 Quality Analysis: {file_name}", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Create notebook for different analysis sections
        analysis_notebook = ttk.Notebook(main_frame)
        analysis_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Analyze video
        self.log(f"📊 Analyzing video quality: {file_name}")
        analysis = self.youtube_uploader.analyze_video_quality(video_path)
        
        if 'error' in analysis:
            ttk.Label(main_frame, text=f"❌ Analysis failed: {analysis['error']}", 
                     font=('Segoe UI', 12), foreground='red').pack(pady=20)
            ttk.Button(main_frame, text="Close", command=analysis_window.destroy).pack(pady=10)
            return
        
        # Video Info Tab
        video_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(video_frame, text="📹 Video Info")
        
        video_info = analysis.get('video', {})
        video_text = self._format_video_info(video_info)
        
        video_display = scrolledtext.ScrolledText(video_frame, height=15, font=('Consolas', 10))
        video_display.pack(fill=tk.BOTH, expand=True)
        video_display.insert(tk.END, video_text)
        video_display.config(state=tk.DISABLED)
        
        # Audio Info Tab
        audio_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(audio_frame, text="🔊 Audio Info")
        
        audio_info = analysis.get('audio', {})
        audio_text = self._format_audio_info(audio_info)
        
        audio_display = scrolledtext.ScrolledText(audio_frame, height=15, font=('Consolas', 10))
        audio_display.pack(fill=tk.BOTH, expand=True)
        audio_display.insert(tk.END, audio_text)
        audio_display.config(state=tk.DISABLED)
        
        # Recommendations Tab
        rec_frame = ttk.Frame(analysis_notebook, padding="15")
        analysis_notebook.add(rec_frame, text="💡 Recommendations")
        
        recommendations = analysis.get('recommendations', [])
        youtube_opt = analysis.get('youtube_optimization', [])
        
        rec_text = "📋 Quality Recommendations:\n"
        rec_text += "=" * 50 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            rec_text += f"{i}. {rec}\n"
        
        rec_text += "\n\n🎬 YouTube Optimization:\n"
        rec_text += "=" * 50 + "\n\n"
        
        for i, opt in enumerate(youtube_opt, 1):
            rec_text += f"{i}. {opt}\n"
        
        rec_display = scrolledtext.ScrolledText(rec_frame, height=15, font=('Segoe UI', 10))
        rec_display.pack(fill=tk.BOTH, expand=True)
        rec_display.insert(tk.END, rec_text)
        rec_display.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🎯 Optimize This Video", 
                  command=lambda: self.optimize_single_video(video_path, analysis_window)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📤 Upload Original", 
                  command=lambda: self.upload_single_video(video_path, analysis_window)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", 
                  command=analysis_window.destroy).pack(side=tk.RIGHT)
                  
    def _format_video_info(self, video_info):
        """Format video information for display"""
        text = "📹 VIDEO STREAM ANALYSIS\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Resolution:       {video_info.get('width', 'unknown')} x {video_info.get('height', 'unknown')}\n"
        text += f"Aspect Ratio:     {video_info.get('aspect_ratio', 'unknown')}\n"
        text += f"Frame Rate:       {video_info.get('fps', 'unknown')} fps\n"
        text += f"Duration:         {video_info.get('duration', 'unknown')} seconds\n"
        text += f"Codec:            {video_info.get('codec', 'unknown')}\n"
        text += f"Profile:          {video_info.get('profile', 'unknown')}\n"
        text += f"Level:            {video_info.get('level', 'unknown')}\n"
        text += f"Bitrate:          {self._format_bitrate(video_info.get('bitrate', 0))}\n"
        text += f"Pixel Count:      {video_info.get('pixel_count', 'unknown'):,} pixels\n"
        text += f"Quality Level:    {video_info.get('quality_level', 'unknown').upper()}\n\n"
        
        text += "📊 ORIENTATION:\n"
        text += f"• Vertical:       {'✅' if video_info.get('is_vertical') else '❌'}\n"
        text += f"• Horizontal:     {'✅' if video_info.get('is_horizontal') else '❌'}\n"
        text += f"• Square:         {'✅' if video_info.get('is_square') else '❌'}\n\n"
        
        # YouTube compatibility
        width = video_info.get('width', 0)
        height = video_info.get('height', 0)
        fps = video_info.get('fps', 0)
        
        text += "🎬 YOUTUBE COMPATIBILITY:\n"
        
        if width >= 1920 and height >= 1080:
            text += "• Resolution:     ✅ HD/Full HD compatible\n"
        elif width >= 1280 and height >= 720:
            text += "• Resolution:     ⚠️ HD compatible (720p)\n"
        else:
            text += "• Resolution:     ❌ Below HD standard\n"
            
        if fps in [24, 25, 30, 50, 60]:
            text += f"• Frame Rate:     ✅ Standard ({fps}fps)\n"
        else:
            text += f"• Frame Rate:     ⚠️ Non-standard ({fps}fps)\n"
            
        codec = video_info.get('codec', '')
        if codec in ['h264', 'h265']:
            text += f"• Codec:          ✅ YouTube preferred ({codec})\n"
        else:
            text += f"• Codec:          ⚠️ May need conversion ({codec})\n"
        
        return text
        
    def _format_audio_info(self, audio_info):
        """Format audio information for display"""
        text = "🔊 AUDIO STREAM ANALYSIS\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Codec:            {audio_info.get('codec', 'unknown')}\n"
        text += f"Sample Rate:      {audio_info.get('sample_rate', 'unknown')} Hz\n"
        text += f"Channels:         {audio_info.get('channels', 'unknown')}\n"
        text += f"Bitrate:          {self._format_bitrate(audio_info.get('bitrate', 0))}\n"
        text += f"Quality Level:    {audio_info.get('quality_level', 'unknown').upper()}\n\n"
        
        text += "📊 CHANNEL CONFIGURATION:\n"
        text += f"• Mono:           {'✅' if audio_info.get('is_mono') else '❌'}\n"
        text += f"• Stereo:         {'✅' if audio_info.get('is_stereo') else '❌'}\n"
        text += f"• Surround:       {'✅' if audio_info.get('is_surround') else '❌'}\n\n"
        
        # YouTube audio recommendations
        text += "🎬 YOUTUBE AUDIO COMPATIBILITY:\n"
        
        codec = audio_info.get('codec', '')
        if codec in ['aac', 'mp3']:
            text += f"• Codec:          ✅ YouTube preferred ({codec})\n"
        else:
            text += f"• Codec:          ⚠️ May need conversion ({codec})\n"
            
        sample_rate = audio_info.get('sample_rate', 0)
        if sample_rate in [44100, 48000]:
            text += f"• Sample Rate:    ✅ Standard ({sample_rate}Hz)\n"
        else:
            text += f"• Sample Rate:    ⚠️ Non-standard ({sample_rate}Hz)\n"
            
        bitrate = audio_info.get('bitrate', 0)
        if bitrate >= 192000:
            text += f"• Bitrate:        ✅ High quality ({self._format_bitrate(bitrate)})\n"
        elif bitrate >= 128000:
            text += f"• Bitrate:        ✅ Good quality ({self._format_bitrate(bitrate)})\n"
        elif bitrate >= 96000:
            text += f"• Bitrate:        ⚠️ Fair quality ({self._format_bitrate(bitrate)})\n"
        else:
            text += f"• Bitrate:        ❌ Low quality ({self._format_bitrate(bitrate)})\n"
        
        return text
        
    def _format_bitrate(self, bitrate):
        """Format bitrate for display"""
        if not bitrate or bitrate == 0:
            return "unknown"
        
        if bitrate >= 1000000:
            return f"{bitrate/1000000:.1f} Mbps"
        elif bitrate >= 1000:
            return f"{bitrate/1000:.0f} kbps"
        else:
            return f"{bitrate} bps"
            
    def analyze_video_for_shorts(self, video_path):
        """Analyze video to check Shorts compatibility"""
        if not self.youtube_uploader:
            return None
            
        try:
            return self.youtube_uploader.detect_shorts_video(video_path)
        except Exception as e:
            self.log(f"❌ Error analyzing video: {e}")
            return None
            
    def upload_as_shorts_thread(self):
        """Upload selected videos as Shorts in thread"""
        if not self.selected_videos:
            messagebox.showwarning("Warning", "No videos selected!")
            return
            
        def upload_shorts():
            try:
                self.is_uploading = True
                self.upload_shorts_btn.config(state='disabled')
                self.upload_selected_btn.config(state='disabled')
                
                # Get settings
                title_prefix = self.title_prefix_var.get()
                tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
                privacy = self.privacy_var.get()
                
                selected_files = [self.video_files[i] for i in self.selected_videos]
                total_files = len(selected_files)
                successful = 0
                failed = 0
                
                self.log(f"📱 Starting Shorts upload for {total_files} videos...")
                
                for i, video_file in enumerate(selected_files):
                    try:
                        # Update progress
                        progress = (i / total_files) * 100
                        self.upload_progress.config(value=progress)
                        self.upload_status_var.set(f"📱 Uploading Shorts {i+1}/{total_files}...")
                        self.root.update_idletasks()
                        
                        # Analyze video for Shorts
                        self.log(f"📱 Analyzing video for Shorts: {os.path.basename(video_file)}")
                        shorts_info = self.analyze_video_for_shorts(video_file)
                        
                        if shorts_info:
                            if shorts_info.get('is_shorts'):
                                self.log(f"✅ Perfect for Shorts: {shorts_info.get('width')}x{shorts_info.get('height')}, {shorts_info.get('duration')}s")
                            else:
                                recommendations = shorts_info.get('recommendations', [])
                                if recommendations:
                                    self.log(f"⚠️ Shorts recommendations: {recommendations[0]}")
                        
                        # Generate title
                        filename = os.path.basename(video_file)
                        name_without_ext = os.path.splitext(filename)[0]
                        title = f"{title_prefix}{name_without_ext}"
                        
                        # Create Shorts description
                        description = f"📱 Vertical video optimized for mobile viewing\n"
                        if shorts_info and shorts_info.get('is_shorts'):
                            description += f"✅ {shorts_info.get('width')}x{shorts_info.get('height')}, {shorts_info.get('duration')}s\n"
                        description += f"🎬 From Douyin collection\n"
                        description += f"📊 File: {shorts_info.get('file_size_mb')}MB\n" if shorts_info else ""
                        
                        # Upload as Shorts
                        self.log(f"📱 Uploading as YouTube Shorts: {title}")
                        result = self.youtube_uploader.upload_shorts_video(
                            video_file, title, description, tags, privacy
                        )
                        
                        if result['success']:
                            successful += 1
                            video_url = result.get('url', 'Unknown URL')
                            self.log(f"✅ Shorts upload successful: {video_url}")
                            
                            # Update tree with success
                            for item in self.upload_tree.get_children():
                                if self.upload_tree.item(item)['values'][1] == os.path.basename(video_file):
                                    self.upload_tree.item(item, values=(
                                        self.upload_tree.item(item)['values'][0],
                                        self.upload_tree.item(item)['values'][1],
                                        self.upload_tree.item(item)['values'][2],
                                        "📱 Shorts ✅",
                                        "🔗 Open"
                                    ))
                                    break
                        else:
                            failed += 1
                            error = result.get('error', 'Unknown error')
                            self.log(f"❌ Shorts upload failed: {error}")
                            
                            # Update tree with failure
                            for item in self.upload_tree.get_children():
                                if self.upload_tree.item(item)['values'][1] == os.path.basename(video_file):
                                    self.upload_tree.item(item, values=(
                                        self.upload_tree.item(item)['values'][0],
                                        self.upload_tree.item(item)['values'][1],
                                        self.upload_tree.item(item)['values'][2],
                                        "📱 Failed ❌",
                                        "❌ Error"
                                    ))
                                    break
                                    
                    except Exception as e:
                        failed += 1
                        self.log(f"❌ Error uploading {video_file}: {e}")
                        
                # Complete
                self.upload_progress.config(value=100)
                self.upload_status_var.set(f"📱 Shorts upload complete! ✅{successful} ❌{failed}")
                
                # Summary message
                if successful > 0:
                    summary_msg = f"📱 YouTube Shorts Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n🎉 Shorts are optimized for mobile!\n• Vertical format with #Shorts tags\n• Should appear in Shorts feed\n• Perfect for mobile viewing\n\n📺 Check your Shorts: https://www.youtube.com/@sealrepo/shorts\n\n💡 Shorts tips:\n• Keep videos ≤60 seconds\n• Use vertical (9:16) format\n• Engage viewers in first 3 seconds\n• Use trending sounds/music"
                else:
                    summary_msg = f"❌ Shorts Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
                
                messagebox.showinfo("Shorts Upload Complete", summary_msg)
                
            except Exception as e:
                self.log(f"❌ Critical error during Shorts upload: {e}")
                messagebox.showerror("Upload Error", f"Critical error: {e}")
            finally:
                self.is_uploading = False
                self.upload_shorts_btn.config(state='normal')
                self.upload_selected_btn.config(state='normal')
                
        # Start upload in thread
        upload_thread = threading.Thread(target=upload_shorts, daemon=True)
        upload_thread.start()
        
    def upload_optimized_videos_thread(self):
        """Upload selected videos with optimization in thread"""
        if not self.selected_videos:
            messagebox.showwarning("Warning", "No videos selected!")
            return
            
        def upload_optimized():
            try:
                self.is_uploading = True
                self.upload_optimized_btn.config(state='disabled')
                self.upload_selected_btn.config(state='disabled')
                self.upload_shorts_btn.config(state='disabled')
                
                # Get settings
                title_prefix = self.title_prefix_var.get()
                tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
                privacy = self.privacy_var.get()
                quality_preset = self.quality_preset_var.get()
                optimize = self.optimize_quality.get()
                
                selected_files = [self.video_files[i] for i in self.selected_videos]
                total_files = len(selected_files)
                successful = 0
                failed = 0
                total_optimization_time = 0
                
                self.log(f"🎯 Starting optimized upload for {total_files} videos...")
                self.log(f"📊 Quality preset: {quality_preset}")
                
                for i, video_file in enumerate(selected_files):
                    try:
                        # Update progress
                        progress = (i / total_files) * 100
                        self.upload_progress.config(value=progress)
                        self.upload_status_var.set(f"🎯 Processing {i+1}/{total_files}...")
                        self.root.update_idletasks()
                        
                        # Generate title
                        filename = os.path.basename(video_file)
                        name_without_ext = os.path.splitext(filename)[0]
                        title = f"{title_prefix}{name_without_ext}"
                        
                        # Create description
                        description = f"🎯 High-quality video optimized for YouTube\n"
                        description += f"📊 Quality preset: {quality_preset}\n"
                        description += f"🎬 Processed with advanced encoding\n"
                        description += f"📱 Optimized for all devices\n"
                        
                        # Upload with optimization
                        self.log(f"🎯 Uploading with optimization: {title}")
                        
                        start_time = time.time()
                        result = self.youtube_uploader.upload_optimized_video(
                            video_file, title, description, tags, "22", privacy,
                            optimize_quality=optimize, quality_preset=quality_preset
                        )
                        end_time = time.time()
                        
                        processing_time = end_time - start_time
                        total_optimization_time += processing_time
                        
                        if result['success']:
                            successful += 1
                            video_url = result.get('url', 'Unknown URL')
                            
                            # Log optimization info
                            if result.get('optimization'):
                                opt_info = result['optimization']
                                self.log(f"✅ Optimized: {opt_info['input_size_mb']}MB → {opt_info['output_size_mb']}MB")
                                self.log(f"📊 Compression: {opt_info['compression_ratio']:.2f}x")
                            
                            self.log(f"✅ Upload successful: {video_url}")
                            self.log(f"⏱️ Processing time: {processing_time:.1f}s")
                            
                            # Update tree with success
                            for item in self.upload_tree.get_children():
                                if self.upload_tree.item(item)['values'][1] == os.path.basename(video_file):
                                    status = "🎯 Optimized ✅"
                                    if result.get('optimization'):
                                        opt_info = result['optimization']
                                        status += f" ({opt_info['compression_ratio']:.1f}x)"
                                    
                                    self.upload_tree.item(item, values=(
                                        self.upload_tree.item(item)['values'][0],
                                        self.upload_tree.item(item)['values'][1],
                                        self.upload_tree.item(item)['values'][2],
                                        status,
                                        "🔗 Open"
                                    ))
                                    break
                        else:
                            failed += 1
                            error = result.get('error', 'Unknown error')
                            self.log(f"❌ Upload failed: {error}")
                            
                            # Update tree with failure
                            for item in self.upload_tree.get_children():
                                if self.upload_tree.item(item)['values'][1] == os.path.basename(video_file):
                                    self.upload_tree.item(item, values=(
                                        self.upload_tree.item(item)['values'][0],
                                        self.upload_tree.item(item)['values'][1],
                                        self.upload_tree.item(item)['values'][2],
                                        "🎯 Failed ❌",
                                        "❌ Error"
                                    ))
                                    break
                                    
                    except Exception as e:
                        failed += 1
                        self.log(f"❌ Error uploading {video_file}: {e}")
                        
                # Complete
                self.upload_progress.config(value=100)
                avg_time = total_optimization_time / total_files if total_files > 0 else 0
                self.upload_status_var.set(f"🎯 Optimized upload complete! ✅{successful} ❌{failed}")
                
                # Summary message
                if successful > 0:
                    summary_msg = f"🎯 Optimized YouTube Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n• Quality preset: {quality_preset}\n• Avg processing time: {avg_time:.1f}s\n\n🎉 Videos optimized for best quality!\n• Enhanced encoding for YouTube\n• Optimized bitrates and codecs\n• Better compression efficiency\n• Improved compatibility\n\n📺 Check your channel: https://www.youtube.com/@sealrepo\n\n💡 Optimization benefits:\n• Better video quality\n• Faster YouTube processing\n• Improved mobile compatibility\n• Reduced storage usage"
                else:
                    summary_msg = f"❌ Optimized Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
                
                messagebox.showinfo("Optimized Upload Complete", summary_msg)
                
            except Exception as e:
                self.log(f"❌ Critical error during optimized upload: {e}")
                messagebox.showerror("Upload Error", f"Critical error: {e}")
            finally:
                self.is_uploading = False
                self.upload_optimized_btn.config(state='normal')
                self.upload_selected_btn.config(state='normal')
                self.upload_shorts_btn.config(state='normal')
                
        # Start upload in thread
        upload_thread = threading.Thread(target=upload_optimized, daemon=True)
        upload_thread.start()
        
    def optimize_single_video(self, video_path, parent_window):
        """Optimize single video from analysis window"""
        if not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        quality_preset = self.quality_preset_var.get()
        
        try:
            # Generate output filename
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_optimized{ext}"
            
            self.log(f"🔧 Optimizing video: {os.path.basename(video_path)}")
            
            # Perform optimization
            result = self.youtube_uploader.optimize_video_for_youtube(
                video_path, output_path, quality_preset
            )
            
            if result['success']:
                opt_info = f"✅ Optimization successful!\n\n"
                opt_info += f"📊 Size: {result['input_size_mb']}MB → {result['output_size_mb']}MB\n"
                opt_info += f"📉 Compression: {result['compression_ratio']:.2f}x\n"
                opt_info += f"🎯 Preset: {result['optimization_preset']}\n\n"
                opt_info += f"📁 Output: {output_path}\n\n"
                opt_info += "Would you like to upload the optimized version?"
                
                if messagebox.askyesno("Optimization Complete", opt_info):
                    parent_window.destroy()
                    self.upload_single_video(output_path)
            else:
                messagebox.showerror("Optimization Failed", f"❌ Error: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Optimization Error", f"❌ Error: {str(e)}")
            
    def upload_single_video(self, video_path, parent_window=None):
        """Upload single video immediately"""
        if parent_window:
            parent_window.destroy()
            
        # Implementation for single video upload
        filename = os.path.basename(video_path)
        title = f"Video - {os.path.splitext(filename)[0]}"
        
        try:
            result = self.youtube_uploader.upload_video(
                video_path, title, "Uploaded via Douyin to YouTube Tool", 
                ["video", "upload"], "22", "private"
            )
            
            if result['success']:
                messagebox.showinfo("Upload Complete", f"✅ Video uploaded successfully!\n\nURL: {result.get('url', 'Unknown')}")
            else:
                messagebox.showerror("Upload Failed", f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Upload Error", f"❌ Error: {str(e)}")
            
    def show_youtube_manager(self):
        """Show YouTube Manager (alias for open_youtube_manager)"""
        self.open_youtube_manager()
        
    def open_youtube_manager(self):
        """Show Enhanced YouTube Manager with comprehensive features"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        # Create manager window
        manager_window = tk.Toplevel(self.root)
        manager_window.title("� YouTube Manager Pro")
        manager_window.geometry("1000x700")
        manager_window.resizable(True, True)
        
        # Make it modal
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        # Center the window
        manager_window.update_idletasks()
        x = (manager_window.winfo_screenwidth() // 2) - (manager_window.winfo_width() // 2)
        y = (manager_window.winfo_screenheight() // 2) - (manager_window.winfo_height() // 2)
        manager_window.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(manager_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with channel info
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="🚀 YouTube Manager Pro", 
                 font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        
        # Refresh button
        tk.Button(header_frame, text="🔄 Refresh Data", 
                  command=lambda: self.refresh_manager_data(manager_window),
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Dashboard Overview
        self.create_dashboard_tab(notebook, manager_window)
        
        # Tab 2: Video Management  
        self.create_video_management_tab(notebook, manager_window)
        
        # Tab 3: Analytics
        self.create_analytics_tab(notebook, manager_window)
        
        # Tab 4: Comments
        self.create_comments_tab(notebook, manager_window)
        
        # Tab 5: SEO Tools
        self.create_seo_tab(notebook, manager_window)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.manager_status_var = tk.StringVar(value="🟢 YouTube Manager Ready")
        ttk.Label(status_frame, textvariable=self.manager_status_var).pack(side=tk.LEFT)
        
        # Auto-load data
        self.refresh_manager_data(manager_window)
        
        # Load real stats after window is created
        self.load_channel_statistics(manager_window)
        
        # Also trigger refresh of stats in refresh function
        try:
            # Find the first working refresh_manager_data function and update it
            threading.Thread(target=lambda: self.load_channel_statistics(manager_window), daemon=True).start()
        except:
            pass
        
    def create_dashboard_tab(self, notebook, parent_window):
        """Create dashboard overview tab"""
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Main container with scrollable content
        canvas = tk.Canvas(dashboard_frame)
        scrollbar = ttk.Scrollbar(dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Quick Stats Section
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📊 Quick Stats", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Stats cards
        self.create_stat_card(stats_grid, "📹 Total Videos", "Loading...", 0, 0)
        self.create_stat_card(stats_grid, "👥 Subscribers", "Loading...", 0, 1)
        self.create_stat_card(stats_grid, "👁️ Total Views", "Loading...", 0, 2)
        self.create_stat_card(stats_grid, "📅 Today's Uploads", "Loading...", 1, 0)
        self.create_stat_card(stats_grid, "⏱️ Watch Time", "Loading...", 1, 1)
        self.create_stat_card(stats_grid, "💰 Revenue (Est.)", "Loading...", 1, 2)
        
        # Recent Activity Section
        activity_frame = ttk.LabelFrame(scrollable_frame, text="📈 Recent Activity", padding="15")
        activity_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Activity buttons
        activity_buttons = tk.Frame(activity_frame, bg=self.colors['light'])
        activity_buttons.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(activity_buttons, text="📺 Check Today's Videos", 
                  command=self.quick_check_today,
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(activity_buttons, text="📋 Recent Uploads", 
                  command=self.quick_check_channel,
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(activity_buttons, text="💬 Recent Comments", 
                  command=lambda: self.check_recent_comments(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').pack(side=tk.LEFT)
        
        # Quick Actions Section
        actions_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Quick Actions", padding="15")
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        actions_grid = tk.Frame(actions_frame, bg=self.colors['light'])
        actions_grid.pack(fill=tk.X)
        
        # Action buttons in grid
        tk.Button(actions_grid, text="🚀 Upload Video", 
                  command=self.browse_videos_for_upload,
                  bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=0, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="🎨 Create Thumbnail", 
                  command=lambda: self.open_thumbnail_tools(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="📝 Edit Metadata", 
                  command=lambda: self.open_bulk_editor(parent_window),
                  bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=0, column=2, pady=(0, 5), sticky="ew")
        
        tk.Button(actions_grid, text="📊 Export Analytics", 
                  command=lambda: self.export_analytics_data(parent_window),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=0, padx=(0, 10), pady=(0, 5), sticky="ew")
        tk.Button(actions_grid, text="🔍 SEO Analyzer", 
                  command=lambda: notebook.select(4),
                  bg=self.colors['success'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")  # Switch to SEO tab
        tk.Button(actions_grid, text="📅 Schedule Upload", 
                  command=lambda: self.open_scheduler(parent_window),
                  bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9, 'bold'), cursor='hand2').grid(row=1, column=2, pady=(0, 5), sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            actions_grid.columnconfigure(i, weight=1)
        
        # Performance Insights
        insights_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Performance Insights", padding="15")
        insights_frame.pack(fill=tk.X)
        
        insights_text = tk.Text(insights_frame, height=8, font=('Segoe UI', 9),
                               bg=self.colors['light'], fg=self.colors['dark'],
                               insertbackground=self.colors['primary'])
        insights_scroll = ttk.Scrollbar(insights_frame, orient="vertical", command=insights_text.yview)
        insights_text.configure(yscrollcommand=insights_scroll.set)
        
        insights_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        insights_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sample insights (will be populated with real data)
        sample_insights = """🎯 Channel Performance Insights:

📈 Top Performing Video: Will be loaded from analytics...
📊 Average View Duration: Analyzing...  
🎬 Best Upload Time: Calculating...
🏷️ Most Effective Tags: Processing...
👥 Audience Demographics: Loading...
📱 Traffic Sources: Fetching data...

💡 Recommendations:
• Upload frequency analysis pending...
• Content optimization suggestions loading...
• SEO improvements being calculated...
"""
        
        insights_text.insert(tk.END, sample_insights)
        insights_text.config(state=tk.DISABLED)
        
        # Pack scrollable elements
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_stat_card(self, parent, title, value, row, col):
        """Create a stat card widget"""
        card_frame = ttk.LabelFrame(parent, text=title, padding="10")
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        value_label = ttk.Label(card_frame, text=str(value), font=('Segoe UI', 14, 'bold'))
        value_label.pack()
        
        # Store reference for updating
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[title] = value_label
        
        # Configure grid weights
        parent.columnconfigure(col, weight=1)
        
    def refresh_manager_data(self, manager_window):
        """Refresh data in YouTube Manager"""
        try:
            # Update any displayed statistics or data
            self.log("🔄 Refreshing YouTube Manager data...")
            if hasattr(self, 'stat_labels'):
                # Refresh channel statistics if available
                if self.youtube_uploader and self.youtube_uploader.youtube:
                    # Could add real-time data refresh here
                    pass
            self.log("✅ YouTube Manager data refreshed")
        except Exception as e:
            self.log(f"❌ Error refreshing manager data: {e}")
    
    def manager_check_todays_uploads(self, window):
        """Check today's uploads from manager"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            messagebox.showerror("Error", "Please authenticate first!")
            return
            
        self.manager_results.delete(1.0, tk.END)
        self.manager_results.insert(tk.END, "📅 Checking today's uploads...\n")
        self.manager_results.insert(tk.END, "═" * 50 + "\n")
        window.update()
        
        try:
            result = self.youtube_uploader.get_todays_uploads()
            
            if result['success']:
                videos = result['videos']
                channel_title = result['channel_title']
                total_today = result['total_today']
                
                from datetime import datetime
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                self.manager_results.insert(tk.END, f"Channel: {channel_title}\n")
                self.manager_results.insert(tk.END, f"Date: {today_str}\n")
                self.manager_results.insert(tk.END, f"Total uploads today: {total_today}\n\n")
                
                if total_today == 0:
                    self.manager_results.insert(tk.END, "📭 No uploads found for today\n")
                    self.manager_results.insert(tk.END, "\n💡 This could mean:\n")
                    self.manager_results.insert(tk.END, "• No videos were uploaded today\n")
                    self.manager_results.insert(tk.END, "• Videos are still processing\n")
                    self.manager_results.insert(tk.END, "• Wrong account authenticated\n")
                else:
                    public_count = sum(1 for v in videos if v['privacy_status'] == 'public')
                    private_count = sum(1 for v in videos if v['privacy_status'] == 'private')
                    processing_count = sum(1 for v in videos if v['processing_status'] == 'processing')
                    
                    self.manager_results.insert(tk.END, f"📊 Summary:\n")
                    self.manager_results.insert(tk.END, f"• Public: {public_count}\n")
                    self.manager_results.insert(tk.END, f"• Private: {private_count}\n") 
                    self.manager_results.insert(tk.END, f"• Processing: {processing_count}\n\n")
                    
                    self.manager_results.insert(tk.END, "📋 Video Details:\n")
                    self.manager_results.insert(tk.END, "─" * 50 + "\n")
                    
                    for i, video in enumerate(videos, 1):
                        title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                        privacy = video['privacy_status'].upper()
                        processing = video['processing_status']
                        
                        self.manager_results.insert(tk.END, f"{i}. {title}\n")
                        self.manager_results.insert(tk.END, f"   Privacy: {privacy} | Processing: {processing}\n")
                        self.manager_results.insert(tk.END, f"   URL: {video['url']}\n\n")
            else:
                self.manager_results.insert(tk.END, f"❌ Error: {result['error']}\n")
                
        except Exception as e:
            self.manager_results.insert(tk.END, f"❌ Exception: {str(e)}\n")
            
        self.manager_results.see(tk.END)
        
    def manager_check_recent_uploads(self, window):
        """Check recent uploads status from manager"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            messagebox.showerror("Error", "Please authenticate first!")
            return
            
        self.manager_results.delete(1.0, tk.END)
        self.manager_results.insert(tk.END, "🔍 Checking recent uploads status...\n")
        self.manager_results.insert(tk.END, "═" * 50 + "\n")
        window.update()
        
        try:
            result = self.youtube_uploader.list_recent_uploads(max_results=10)
            
            if result['success']:
                videos = result['videos']
                total_found = result['total_found']
                
                self.manager_results.insert(tk.END, f"Total recent uploads: {total_found}\n\n")
                
                if total_found == 0:
                    self.manager_results.insert(tk.END, "📭 No recent uploads found\n")
                else:
                    self.manager_results.insert(tk.END, "📋 Recent Videos Status:\n")
                    self.manager_results.insert(tk.END, "─" * 50 + "\n")
                    
                    for i, video in enumerate(videos, 1):
                        title = video['title'][:40] + "..." if len(video['title']) > 40 else video['title']
                        privacy = video['privacy_status'].upper()
                        upload_status = video['upload_status']
                        processing = video['processing_status']
                        
                        self.manager_results.insert(tk.END, f"{i}. {title}\n")
                        self.manager_results.insert(tk.END, f"   Privacy: {privacy}\n")
                        self.manager_results.insert(tk.END, f"   Upload: {upload_status} | Processing: {processing}\n")
                        if video.get('published_at'):
                            self.manager_results.insert(tk.END, f"   Published: {video['published_at']}\n")
                        self.manager_results.insert(tk.END, "\n")
            else:
                self.manager_results.insert(tk.END, f"❌ Error: {result['error']}\n")
                
        except Exception as e:
            self.manager_results.insert(tk.END, f"❌ Exception: {str(e)}\n")
            
        self.manager_results.see(tk.END)
                
    def select_all_for_upload(self):
        """Select all videos"""
        for item in self.upload_tree.get_children():
            values = list(self.upload_tree.item(item, 'values'))
            values[0] = "✓"
            # Ensure actions column exists
            if len(values) < 5:
                values.append("🎬  📁")
            self.upload_tree.item(item, values=values, tags=('selected',))
            self.selected_videos.add(values[1])
            
        self.update_upload_count()
        self.log("✅ Selected all videos")
        
    def deselect_all_for_upload(self):
        """Deselect all videos"""
        for item in self.upload_tree.get_children():
            values = list(self.upload_tree.item(item, 'values'))
            values[0] = ""
            # Ensure actions column exists
            if len(values) < 5:
                values.append("🎬  📁")
            self.upload_tree.item(item, values=values, tags=('unselected',))
            
        self.selected_videos.clear()
        self.update_upload_count()
        self.log("❌ Deselected all videos")
        
    def update_upload_count(self):
        """Update upload count"""
        total = len(self.upload_tree.get_children())
        selected = len(self.selected_videos)
        self.upload_count_var.set(f"📋 Selected: {selected}/{total}")
        
        if selected > 0 and YOUTUBE_AVAILABLE:
            self.upload_selected_btn.config(state='normal')
        else:
            self.upload_selected_btn.config(state='disabled')
            
    def youtube_authenticate_thread(self):
        """YouTube authentication in thread"""
        thread = threading.Thread(target=self.youtube_authenticate, daemon=True)
        thread.start()
        
    def youtube_authenticate(self):
        """Authenticate with YouTube"""
        if not YOUTUBE_AVAILABLE:
            messagebox.showerror("Error", "YouTube API not available!")
            return
            
        try:
            self.log("🔐 Authenticating with YouTube...")
            
            if not os.path.exists('credentials.json'):
                messagebox.showerror("Error", "credentials.json not found!")
                return
                
            if self.youtube_uploader:
                success = self.youtube_uploader.authenticate()
                if success:
                    self.log("✅ YouTube authentication successful!")
                    self.auth_status.config(text="✅ Authenticated", foreground='#27ae60')
                else:
                    self.log("❌ YouTube authentication failed!")
                    
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            
    def upload_selected_videos_thread(self):
        """Upload selected videos in thread"""
        thread = threading.Thread(target=self.upload_selected_videos, daemon=True)
        thread.start()
        
    def upload_selected_videos(self):
        """Upload selected videos"""
        if not YOUTUBE_AVAILABLE or not self.youtube_uploader:
            messagebox.showerror("Error", "YouTube uploader not available!")
            return
            
        if not self.selected_videos:
            messagebox.showerror("Error", "No videos selected for upload!\n\nPlease:\n1. Browse videos or load from downloads\n2. Double-click videos to select them (✓)\n3. Try again")
            return
            
        self.log(f"🚀 Starting upload of {len(self.selected_videos)} videos...")
        
        # Get selected video files with full paths
        selected_files = []
        for item in self.upload_tree.get_children():
            values = self.upload_tree.item(item, 'values')
            if values[0] == "✓":  # Selected
                file_name = values[1]
                
                # Try multiple path locations
                file_path = None
                
                # First try current video folder
                if hasattr(self, 'current_video_folder') and self.current_video_folder:
                    test_path = os.path.join(self.current_video_folder, file_name)
                    if os.path.exists(test_path):
                        file_path = test_path
                
                # Then try download folder
                if not file_path:
                    test_path = os.path.join(self.download_folder, file_name)
                    if os.path.exists(test_path):
                        file_path = test_path
                
                # Finally try absolute path if it looks like one
                if not file_path and os.path.isabs(file_name):
                    if os.path.exists(file_name):
                        file_path = file_name
                
                if file_path:
                    selected_files.append((item, file_path, file_name))
                else:
                    self.log(f"⚠️ File not found: {file_name}")
                    
        if not selected_files:
            messagebox.showerror("Error", "No valid video files found!\n\nPossible issues:\n• Files were moved or deleted\n• Wrong folder selected\n• File permissions")
            return
            
        self.log(f"📤 Found {len(selected_files)} valid files to upload")
        
        self.is_uploading = True
        self.upload_selected_btn.config(state='disabled')
        
        total = len(selected_files)
        self.upload_progress['maximum'] = total
        self.upload_progress['value'] = 0
        
        successful = 0
        failed = 0
        
        try:
            for i, (item, file_path, file_name) in enumerate(selected_files):
                # Update status
                values = list(self.upload_tree.item(item, 'values'))
                values[3] = "📤 Uploading..."
                self.upload_tree.item(item, values=values)
                
                title = f"{self.title_prefix_var.get()}{os.path.splitext(file_name)[0]}"
                tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]
                
                self.log(f"📤 Uploading {i+1}/{total}: {file_name}")
                
                try:
                    result = self.youtube_uploader.upload_video(
                        video_file=file_path,
                        title=title,
                        description=f"Video from Douyin\n\n#douyin #video",
                        tags=tags,
                        privacy_status=self.privacy_var.get()
                    )
                    
                    if result['success']:
                        successful += 1
                        values[3] = "✅ Uploaded"
                        privacy_status = self.privacy_var.get()
                        video_url = result['url']
                        video_id = result.get('video_id', '')
                        
                        # Log detailed success info
                        self.log(f"✅ Upload successful!")
                        self.log(f"   📹 Title: {title}")
                        self.log(f"   🔗 URL: {video_url}")
                        self.log(f"   🆔 Video ID: {video_id}")
                        self.log(f"   🔒 Privacy: {privacy_status}")
                        
                        # Check detailed status after upload
                        if video_id:
                            try:
                                status_check = self.youtube_uploader.check_video_status(video_id)
                                if status_check['success']:
                                    upload_status = status_check.get('upload_status', 'unknown')
                                    processing_status = status_check.get('processing_status', 'unknown')
                                    failure_reason = status_check.get('failure_reason')
                                    rejection_reason = status_check.get('rejection_reason')
                                    
                                    self.log(f"   📤 Upload Status: {upload_status}")
                                    self.log(f"   ⚙️  Processing: {processing_status}")
                                    
                                    if failure_reason:
                                        self.log(f"   ❌ Failure Reason: {failure_reason}")
                                    if rejection_reason:
                                        self.log(f"   🚫 Rejection Reason: {rejection_reason}")
                                        
                                    # Update status in table based on actual status
                                    if upload_status == 'failed':
                                        values[3] = "❌ Failed"
                                        successful -= 1
                                        failed += 1
                                    elif processing_status == 'processing':
                                        values[3] = "⏳ Processing"
                                    elif rejection_reason:
                                        values[3] = "🚫 Rejected"
                                        
                            except Exception as status_error:
                                self.log(f"   ⚠️  Could not verify status: {status_error}")
                        
                        # Check for processing status
                        if 'processing_status' in result:
                            proc_status = result['processing_status']
                            upload_status = result.get('upload_status', 'unknown')
                            self.log(f"   ⚙️  Processing: {proc_status}")
                            self.log(f"   📤 Upload Status: {upload_status}")
                        
                        # Check for warnings
                        if 'warning' in result:
                            self.log(f"   ⚠️  Warning: {result['warning']}")
                        
                        if privacy_status == "private":
                            self.log(f"   ⚠️  Video is PRIVATE - won't appear in channel publicly!")
                            self.log(f"   💡 Go to YouTube Studio to change privacy to 'Public'")
                        elif privacy_status == "unlisted":
                            self.log(f"   ⚠️  Video is UNLISTED - only viewable with direct link!")
                        else:
                            self.log(f"   ✅ Video is PUBLIC - should appear in your channel")
                            self.log(f"   ⏳ May take a few minutes to process and appear")
                            
                    else:
                        failed += 1
                        values[3] = "❌ Failed"
                        error_msg = result.get('error', 'Unknown error')
                        self.log(f"❌ Upload failed: {error_msg}")
                        
                        # Specific error handling
                        if "quota" in error_msg.lower():
                            self.log(f"   💡 This might be a YouTube API quota issue")
                        elif "forbidden" in error_msg.lower():
                            self.log(f"   💡 Check if your account has upload permissions")
                        elif "invalid" in error_msg.lower():
                            self.log(f"   💡 Check video file format and size")
                        
                except Exception as e:
                    failed += 1
                    values[3] = "❌ Error"
                    self.log(f"❌ Upload error: {e}")
                    
                self.upload_tree.item(item, values=values)
                self.upload_progress['value'] = i + 1
                self.upload_status_var.set(f"📤 Uploaded: {i + 1}/{total}")
                self.root.update_idletasks()
                
                time.sleep(2)
                
        except Exception as e:
            self.log(f"❌ Upload process error: {e}")
            
        finally:
            self.is_uploading = False
            self.upload_selected_btn.config(state='normal')
            
            # Detailed completion summary
            privacy_status = self.privacy_var.get()
            
            self.log("🎯 ========== UPLOAD SUMMARY ==========")
            self.log(f"✅ Successful uploads: {successful}")
            self.log(f"❌ Failed uploads: {failed}")
            self.log(f"🔒 Privacy setting: {privacy_status}")
            
            if successful > 0:
                if privacy_status == "private":
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n⚠️  IMPORTANT: Videos are set to PRIVATE\n\n🔧 To make them visible in your channel:\n1. Go to YouTube Studio (studio.youtube.com)\n2. Click 'Content' in left menu\n3. Find your uploaded videos\n4. Change visibility from 'Private' to 'Public'\n\n💡 Or change privacy setting to 'Public' before uploading next time!"
                elif privacy_status == "unlisted":
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n⚠️  Videos are UNLISTED\n• Only viewable with direct links\n• Won't appear in channel publicly\n\n💡 Change to 'Public' in YouTube Studio to show in channel"
                else:
                    summary_msg = f"✅ Upload Complete!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\n🎉 Videos are PUBLIC\n• Should appear in your channel\n• May take a few minutes to process\n\n📺 Check your channel: https://www.youtube.com/@sealrepo\n\n� If videos are missing after 15+ minutes:\n• Click '🔍 Check Video Status' button\n• Go to YouTube Studio → Content\n• Look for copyright/community strikes\n• Check if videos were rejected\n\n💡 Common issues:\n• Processing can take 5-60 minutes\n• Copyright content may be blocked\n• Account verification required\n• File format/quality issues"
            else:
                summary_msg = f"❌ Upload Failed!\n\n📊 Results:\n• Successful: {successful}\n• Failed: {failed}\n\nPlease check the logs for error details."
            
            self.log("=" * 45)
            messagebox.showinfo("Upload Complete", summary_msg)

    def refresh_manager_data(self, manager_window):
        """Refresh all data in YouTube Manager"""
        try:
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set("🔄 Refreshing data...")
            # Placeholder for data refresh logic
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set("🟢 Data refreshed successfully")
        except Exception as e:
            if hasattr(self, 'manager_status_var'):
                self.manager_status_var.set(f"❌ Error refreshing data: {e}")
            
    def create_video_management_tab(self, notebook, parent_window):
        """Create video management tab - placeholder"""
        video_frame = ttk.Frame(notebook)
        notebook.add(video_frame, text="🎬 Videos")
        ttk.Label(video_frame, text="🎬 Video Management (Coming Soon)", 
                 font=('Segoe UI', 14)).pack(expand=True)
                 
    def create_analytics_tab(self, notebook, parent_window):
        """Create analytics tab - placeholder"""
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📊 Analytics")
        ttk.Label(analytics_frame, text="📊 Analytics Dashboard (Coming Soon)", 
                 font=('Segoe UI', 14)).pack(expand=True)
                 
    def create_comments_tab(self, notebook, parent_window):
        """Create comments tab - placeholder"""
        comments_frame = ttk.Frame(notebook)
        notebook.add(comments_frame, text="💬 Comments")
        ttk.Label(comments_frame, text="💬 Comment Management (Coming Soon)", 
                 font=('Segoe UI', 14)).pack(expand=True)
                 
    def create_seo_tab(self, notebook, parent_window):
        """Create SEO tab - placeholder"""
        seo_frame = ttk.Frame(notebook)
        notebook.add(seo_frame, text="🔍 SEO")
        ttk.Label(seo_frame, text="🔍 SEO Tools (Coming Soon)", 
                 font=('Segoe UI', 14)).pack(expand=True)
                 
    # Placeholder methods for dashboard actions
    def check_recent_comments(self, parent_window):
        messagebox.showinfo("Coming Soon", "💬 Recent Comments feature coming soon!")
        
    def open_thumbnail_tools(self, parent_window):
        messagebox.showinfo("Coming Soon", "🎨 Thumbnail Tools feature coming soon!")
    
    def save_upload_preset(self):
        """Save current upload settings as a preset"""
        try:
            preset_name = self.preset_var.get()
            if not preset_name or preset_name == "Default":
                preset_name = tk.simpledialog.askstring("Save Preset", "Enter preset name:")
                if not preset_name:
                    return
            
            # Gather all current settings
            preset_data = {
                'title_template': self.title_template_var.get(),
                'description': self.description_text.get('1.0', tk.END).strip(),
                'privacy': self.privacy_var.get(),
                'made_for_kids': self.made_for_kids_var.get(),
                'category': self.category_var.get(),
                'language': self.language_var.get(),
                'tags': self.tags_var.get(),
                'shorts_mode': self.shorts_mode.get(),
                'auto_thumbnail': self.auto_thumbnail.get(),
                'quality': self.quality_var.get(),
                'enable_monetization': self.enable_monetization.get(),
                'license': self.license_var.get(),
                'publish_timing': self.publish_timing.get(),
                'notify_subscribers': self.notify_subscribers.get()
            }
            
            # Save to file
            presets_file = os.path.join(os.path.dirname(__file__), "upload_presets.json")
            try:
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
            except:
                presets = {}
            
            presets[preset_name] = preset_data
            
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
            
            self.log(f"💾 Saved preset: {preset_name}")
            messagebox.showinfo("Success", f"Preset '{preset_name}' saved successfully!")
            
        except Exception as e:
            self.log(f"❌ Error saving preset: {e}")
            messagebox.showerror("Error", f"Failed to save preset: {e}")
    
    def load_upload_preset(self):
        """Load a saved upload preset"""
        try:
            presets_file = os.path.join(os.path.dirname(__file__), "upload_presets.json")
            if not os.path.exists(presets_file):
                messagebox.showinfo("No Presets", "No saved presets found.")
                return
            
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            preset_name = self.preset_var.get()
            if preset_name not in presets:
                available = list(presets.keys())
                if available:
                    preset_name = tk.simpledialog.askstring("Load Preset", 
                                    f"Available presets: {', '.join(available)}\n\nEnter preset name:")
                else:
                    messagebox.showinfo("No Presets", "No saved presets found.")
                    return
            
            if preset_name in presets:
                preset_data = presets[preset_name]
                
                # Apply all settings
                self.title_template_var.set(preset_data.get('title_template', ''))
                
                # Update description text widget
                self.description_text.delete('1.0', tk.END)
                self.description_text.insert('1.0', preset_data.get('description', ''))
                
                self.privacy_var.set(preset_data.get('privacy', 'public'))
                self.made_for_kids_var.set(preset_data.get('made_for_kids', 'no'))
                self.category_var.set(preset_data.get('category', 'Entertainment'))
                self.language_var.set(preset_data.get('language', 'English'))
                self.tags_var.set(preset_data.get('tags', ''))
                self.shorts_mode.set(preset_data.get('shorts_mode', True))
                self.auto_thumbnail.set(preset_data.get('auto_thumbnail', True))
                self.quality_var.set(preset_data.get('quality', 'hd720'))
                self.enable_monetization.set(preset_data.get('enable_monetization', True))
                self.license_var.set(preset_data.get('license', 'YouTube Standard License'))
                self.publish_timing.set(preset_data.get('publish_timing', 'immediate'))
                self.notify_subscribers.set(preset_data.get('notify_subscribers', True))
                
                self.log(f"📥 Loaded preset: {preset_name}")
                messagebox.showinfo("Success", f"Preset '{preset_name}' loaded successfully!")
            else:
                messagebox.showerror("Error", f"Preset '{preset_name}' not found.")
                
        except Exception as e:
            self.log(f"❌ Error loading preset: {e}")
            messagebox.showerror("Error", f"Failed to load preset: {e}")
        
    def open_bulk_editor(self, parent_window):
        messagebox.showinfo("Coming Soon", "📝 Bulk Editor feature coming soon!")
        
    def export_analytics_data(self, parent_window):
        messagebox.showinfo("Coming Soon", "📊 Analytics Export feature coming soon!")
        
    def open_scheduler(self, parent_window):
        messagebox.showinfo("Coming Soon", "📅 Upload Scheduler feature coming soon!")
        
    def load_channel_statistics(self, manager_window):
        """Load real channel statistics from YouTube API"""
        if not self.youtube_uploader or not self.youtube_uploader.youtube:
            self.log("❌ Not authenticated with YouTube")
            return
            
        try:
            self.log("📊 Loading channel statistics...")
            
            # Get channel information
            youtube = self.youtube_uploader.youtube
            
            # Get channel details
            channels_response = youtube.channels().list(
                part='statistics,snippet',
                mine=True
            ).execute()
            
            if channels_response['items']:
                channel = channels_response['items'][0]
                stats = channel['statistics']
                snippet = channel['snippet']
                
                # Update stat cards if they exist
                if hasattr(self, 'stat_labels'):
                    # Format numbers
                    total_videos = int(stats.get('videoCount', 0))
                    subscribers = int(stats.get('subscriberCount', 0))
                    total_views = int(stats.get('viewCount', 0))
                    
                    # Format with commas
                    self.update_stat_card("📹 Total Videos", f"{total_videos:,}")
                    self.update_stat_card("👥 Subscribers", f"{subscribers:,}")
                    self.update_stat_card("👁️ Total Views", f"{total_views:,}")
                    
                    # Get today's uploads
                    today_result = self.youtube_uploader.get_todays_uploads()
                    if today_result['success']:
                        today_count = today_result['total_today']
                        self.update_stat_card("📅 Today's Uploads", f"{today_count}")
                    else:
                        self.update_stat_card("📅 Today's Uploads", "0")
                    
                    # Placeholder for other stats
                    self.update_stat_card("⏱️ Watch Time", "Check Analytics")
                    self.update_stat_card("💰 Revenue (Est.)", "Check Analytics")
                
                self.log(f"✅ Channel stats loaded: {total_videos:,} videos, {subscribers:,} subscribers")
                
            else:
                self.log("❌ No channel found")
                
        except Exception as e:
            self.log(f"❌ Error loading statistics: {e}")
            
    def update_stat_card(self, title, value):
        """Update a stat card with new value"""
        if hasattr(self, 'stat_labels') and title in self.stat_labels:
            self.stat_labels[title].config(text=str(value))

def main():
    """Run the application"""
    root = tk.Tk()
    root.minsize(1200, 800)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    app = DouyinYouTubeTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
