#!/usr/bin/env python3
"""
ChromaDB to Qdrant Migration GUI
User-friendly interface for backing up ChromaDB and restoring to Qdrant
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import pickle
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    pass


class MigrationGUI:
    """Main GUI application for ChromaDB to Qdrant migration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ChromaDB to Qdrant Migration Tool")
        self.root.geometry("900x700")
        
        # Queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Configuration
        self.config = self.load_config()
        
        # Create UI
        self.create_widgets()
        
        # Start log update timer
        self.root.after(100, self.process_log_queue)
    
    def load_config(self):
        """Load or create configuration"""
        config_file = Path.home() / ".nerdbuntu_migration_config.json"
        
        default_config = {
            'chromadb_path': str(Path.home() / "nerdbuntu" / "data" / "vector_db"),
            'export_dir': str(Path.home() / "nerdbuntu" / "exports" / "qdrant"),
            'qdrant_url': 'http://localhost:6333',
            'qdrant_api_key': '',
            'batch_size': 500,
            'last_export': None,
            'last_import': None
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration"""
        config_file = Path.home() / ".nerdbuntu_migration_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log(f"Warning: Could not save config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_export_tab()
        self.create_import_tab()
        self.create_config_tab()
        self.create_history_tab()
        
        # Status bar at bottom
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_export_tab(self):
        """Create export (backup) tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Backup from ChromaDB")
        
        # Title
        title = ttk.Label(tab, text="Export ChromaDB to Qdrant Format", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # ChromaDB path section
        path_frame = ttk.LabelFrame(tab, text="ChromaDB Location", padding=10)
        path_frame.pack(fill='x', padx=10, pady=5)
        
        self.chromadb_path_var = tk.StringVar(value=self.config['chromadb_path'])
        ttk.Label(path_frame, text="ChromaDB Path:").pack(anchor='w')
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill='x', pady=5)
        ttk.Entry(path_entry_frame, textvariable=self.chromadb_path_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(path_entry_frame, text="Browse", command=self.browse_chromadb_path).pack(side='left', padx=5)
        
        # Export directory section
        export_frame = ttk.LabelFrame(tab, text="Export Destination", padding=10)
        export_frame.pack(fill='x', padx=10, pady=5)
        
        self.export_dir_var = tk.StringVar(value=self.config['export_dir'])
        ttk.Label(export_frame, text="Export Directory:").pack(anchor='w')
        export_entry_frame = ttk.Frame(export_frame)
        export_entry_frame.pack(fill='x', pady=5)
        ttk.Entry(export_entry_frame, textvariable=self.export_dir_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(export_entry_frame, text="Browse", command=self.browse_export_dir).pack(side='left', padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(tab, text="Export Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        self.export_json_var = tk.BooleanVar(value=True)
        self.export_pickle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Export as JSON (human-readable)", variable=self.export_json_var).pack(anchor='w')
        ttk.Checkbutton(options_frame, text="Export as Pickle (faster, compact)", variable=self.export_pickle_var).pack(anchor='w')
        
        # Export button
        self.export_button = ttk.Button(tab, text="🚀 Start Export", command=self.start_export, style='Accent.TButton')
        self.export_button.pack(pady=10)
        
        # Progress
        self.export_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.export_progress.pack(fill='x', padx=10, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Export Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.export_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.export_log.pack(fill='both', expand=True)
    
    def create_import_tab(self):
        """Create import (restore) tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Restore to Qdrant")
        
        # Title
        title = ttk.Label(tab, text="Import to Qdrant Database", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Import file section
        file_frame = ttk.LabelFrame(tab, text="Export File", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.import_file_var = tk.StringVar()
        ttk.Label(file_frame, text="Select Export File:").pack(anchor='w')
        file_entry_frame = ttk.Frame(file_frame)
        file_entry_frame.pack(fill='x', pady=5)
        ttk.Entry(file_entry_frame, textvariable=self.import_file_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(file_entry_frame, text="Browse", command=self.browse_import_file).pack(side='left', padx=5)
        
        # Qdrant connection section
        qdrant_frame = ttk.LabelFrame(tab, text="Qdrant Connection", padding=10)
        qdrant_frame.pack(fill='x', padx=10, pady=5)
        
        self.qdrant_url_var = tk.StringVar(value=self.config['qdrant_url'])
        ttk.Label(qdrant_frame, text="Qdrant URL:").pack(anchor='w')
        ttk.Entry(qdrant_frame, textvariable=self.qdrant_url_var).pack(fill='x', pady=2)
        
        self.qdrant_api_key_var = tk.StringVar(value=self.config.get('qdrant_api_key', ''))
        ttk.Label(qdrant_frame, text="API Key (optional, for Qdrant Cloud):").pack(anchor='w', pady=(10, 0))
        ttk.Entry(qdrant_frame, textvariable=self.qdrant_api_key_var, show='*').pack(fill='x', pady=2)
        
        ttk.Button(qdrant_frame, text="Test Connection", command=self.test_qdrant_connection).pack(pady=5)
        
        # Import options
        import_options_frame = ttk.LabelFrame(tab, text="Import Options", padding=10)
        import_options_frame.pack(fill='x', padx=10, pady=5)
        
        self.collection_name_var = tk.StringVar()
        ttk.Label(import_options_frame, text="Collection Name (leave empty to use default):").pack(anchor='w')
        ttk.Entry(import_options_frame, textvariable=self.collection_name_var).pack(fill='x', pady=2)
        
        self.batch_size_var = tk.IntVar(value=self.config['batch_size'])
        ttk.Label(import_options_frame, text="Batch Size:").pack(anchor='w', pady=(10, 0))
        ttk.Spinbox(import_options_frame, from_=100, to=2000, textvariable=self.batch_size_var, increment=100).pack(fill='x', pady=2)
        
        self.verify_import_var = tk.BooleanVar(value=True)
        self.test_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(import_options_frame, text="Verify import after completion", variable=self.verify_import_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_options_frame, text="Run test search", variable=self.test_search_var).pack(anchor='w', pady=2)
        
        # Import button
        self.import_button = ttk.Button(tab, text="🚀 Start Import", command=self.start_import, style='Accent.TButton')
        self.import_button.pack(pady=10)
        
        # Progress
        self.import_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.import_progress.pack(fill='x', padx=10, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(tab, text="Import Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.import_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.import_log.pack(fill='both', expand=True)
    
    def create_config_tab(self):
        """Create configuration tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Configuration")
        
        # Title
        title = ttk.Label(tab, text="Migration Settings", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(tab, text="Default Paths", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Add path configuration here
        ttk.Label(settings_frame, text="These settings are saved automatically").pack(pady=10)
        
        # System info
        info_frame = ttk.LabelFrame(tab, text="System Information", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        info_text = scrolledtext.ScrolledText(info_frame, height=15, wrap=tk.WORD)
        info_text.pack(fill='both', expand=True)
        
        # Populate system info
        info = self.get_system_info()
        info_text.insert('1.0', info)
        info_text.config(state='disabled')
    
    def create_history_tab(self):
        """Create history tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📜 History")
        
        # Title
        title = ttk.Label(tab, text="Migration History", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # History tree
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('timestamp', 'operation', 'status', 'details')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.history_tree.heading('timestamp', text='Timestamp')
        self.history_tree.heading('operation', text='Operation')
        self.history_tree.heading('status', text='Status')
        self.history_tree.heading('details', text='Details')
        
        self.history_tree.column('timestamp', width=150)
        self.history_tree.column('operation', width=150)
        self.history_tree.column('status', width=100)
        self.history_tree.column('details', width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Refresh button
        ttk.Button(tab, text="Refresh History", command=self.refresh_history).pack(pady=5)
        
        # Load initial history
        self.refresh_history()
    
    def get_system_info(self):
        """Get system information"""
        info = []
        info.append("=== ChromaDB to Qdrant Migration Tool ===\n")
        info.append(f"Python Version: {sys.version}\n")
        info.append(f"Platform: {sys.platform}\n\n")
        
        info.append("=== Installed Packages ===\n")
        
        try:
            import chromadb
            info.append(f"✅ ChromaDB: {chromadb.__version__}\n")
        except:
            info.append("❌ ChromaDB: Not installed\n")
        
        try:
            from qdrant_client import QdrantClient
            info.append(f"✅ Qdrant Client: Installed\n")
        except:
            info.append("❌ Qdrant Client: Not installed\n")
        
        try:
            from sentence_transformers import SentenceTransformer
            info.append(f"✅ Sentence Transformers: Installed\n")
        except:
            info.append("❌ Sentence Transformers: Not installed\n")
        
        info.append("\n=== Configuration ===\n")
        info.append(f"ChromaDB Path: {self.config['chromadb_path']}\n")
        info.append(f"Export Directory: {self.config['export_dir']}\n")
        info.append(f"Qdrant URL: {self.config['qdrant_url']}\n")
        
        return ''.join(info)
    
    def browse_chromadb_path(self):
        """Browse for ChromaDB path"""
        path = filedialog.askdirectory(title="Select ChromaDB Directory")
        if path:
            self.chromadb_path_var.set(path)
            self.config['chromadb_path'] = path
            self.save_config()
    
    def browse_export_dir(self):
        """Browse for export directory"""
        path = filedialog.askdirectory(title="Select Export Directory")
        if path:
            self.export_dir_var.set(path)
            self.config['export_dir'] = path
            self.save_config()
    
    def browse_import_file(self):
        """Browse for import file"""
        filetypes = [
            ("JSON files", "*.json"),
            ("Pickle files", "*.pkl"),
            ("All files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Export File", filetypes=filetypes)
        if path:
            self.import_file_var.set(path)
    
    def log(self, message, log_widget=None):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put((f"[{timestamp}] {message}", log_widget))
    
    def process_log_queue(self):
        """Process log queue and update UI"""
        try:
            while True:
                message, log_widget = self.log_queue.get_nowait()
                if log_widget:
                    log_widget.insert(tk.END, message + '\n')
                    log_widget.see(tk.END)
                else:
                    # Log to both
                    self.export_log.insert(tk.END, message + '\n')
                    self.export_log.see(tk.END)
                    self.import_log.insert(tk.END, message + '\n')
                    self.import_log.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_log_queue)
    
    def test_qdrant_connection(self):
        """Test connection to Qdrant"""
        def test():
            try:
                self.log("Testing Qdrant connection...", self.import_log)
                
                url = self.qdrant_url_var.get()
                api_key = self.qdrant_api_key_var.get() or None
                
                if api_key:
                    client = QdrantClient(url=url, api_key=api_key)
                else:
                    client = QdrantClient(url=url)
                
                collections = client.get_collections()
                self.log(f"✅ Connected successfully! Found {len(collections.collections)} collection(s)", self.import_log)
                
                for col in collections.collections:
                    self.log(f"  - {col.name}", self.import_log)
                
                messagebox.showinfo("Success", f"Connected to Qdrant successfully!\nFound {len(collections.collections)} collections.")
                
            except Exception as e:
                self.log(f"❌ Connection failed: {e}", self.import_log)
                messagebox.showerror("Connection Error", f"Failed to connect to Qdrant:\n{e}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def start_export(self):
        """Start export process in background thread"""
        # Validate inputs
        chromadb_path = Path(self.chromadb_path_var.get())
        if not chromadb_path.exists():
            messagebox.showerror("Error", f"ChromaDB path does not exist:\n{chromadb_path}")
            return
        
        if not self.export_json_var.get() and not self.export_pickle_var.get():
            messagebox.showerror("Error", "Please select at least one export format")
            return
        
        # Clear log
        self.export_log.delete('1.0', tk.END)
        
        # Disable button and start progress
        self.export_button.config(state='disabled')
        self.export_progress.start()
        self.status_var.set("Exporting...")
        
        def export_task():
            try:
                self.run_export()
                self.root.after(0, lambda: messagebox.showinfo("Success", "Export completed successfully!"))
            except Exception as e:
                self.log(f"❌ Export failed: {e}", self.export_log)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Export failed:\n{e}"))
            finally:
                self.root.after(0, lambda: self.export_button.config(state='normal'))
                self.root.after(0, lambda: self.export_progress.stop())
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=export_task, daemon=True).start()
    
    def run_export(self):
        """Run the actual export"""
        chromadb_path = Path(self.chromadb_path_var.get())
        export_base = Path(self.export_dir_var.get())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = export_base / timestamp
        export_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"📂 Connecting to ChromaDB at: {chromadb_path}", self.export_log)
        client = chromadb.PersistentClient(path=str(chromadb_path))
        
        self.log("🔧 Loading embedding model: all-MiniLM-L6-v2", self.export_log)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # List collections
        collections = client.list_collections()
        self.log(f"📋 Found {len(collections)} collection(s)", self.export_log)
        
        for col in collections:
            self.log(f"  - {col.name}", self.export_log)
        
        # Export each collection
        export_stats = []
        for collection in collections:
            self.log(f"\n🔄 Exporting collection: {collection.name}", self.export_log)
            
            col = client.get_collection(collection.name)
            all_data = col.get(include=['embeddings', 'documents', 'metadatas'])
            
            total_items = len(all_data['ids'])
            self.log(f"  Found {total_items} items", self.export_log)
            
            if total_items == 0:
                continue
            
            # Prepare export data
            export_data = {
                'collection_info': {
                    'name': collection.name,
                    'export_date': datetime.now().isoformat(),
                    'total_items': total_items,
                    'embedding_model': 'all-MiniLM-L6-v2',
                    'embedding_dimension': 384,
                    'distance_metric': 'cosine'
                },
                'vectors': []
            }
            
            for i in range(total_items):
                vector_data = {
                    'id': all_data['ids'][i],
                    'vector': all_data['embeddings'][i] if all_data['embeddings'] else None,
                    'payload': {
                        'document': all_data['documents'][i] if all_data['documents'] else '',
                        'metadata': all_data['metadatas'][i] if all_data['metadatas'] else {}
                    }
                }
                export_data['vectors'].append(vector_data)
            
            # Save files
            base_filename = f"{collection.name}_export_{timestamp}"
            
            if self.export_json_var.get():
                json_file = export_dir / f"{base_filename}.json"
                self.log(f"  💾 Saving JSON: {json_file.name}", self.export_log)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                json_size = json_file.stat().st_size / 1024 / 1024
                self.log(f"     Size: {json_size:.2f} MB", self.export_log)
            
            if self.export_pickle_var.get():
                pkl_file = export_dir / f"{base_filename}.pkl"
                self.log(f"  💾 Saving Pickle: {pkl_file.name}", self.export_log)
                with open(pkl_file, 'wb') as f:
                    pickle.dump(export_data, f)
                pkl_size = pkl_file.stat().st_size / 1024 / 1024
                self.log(f"     Size: {pkl_size:.2f} MB", self.export_log)
            
            export_stats.append({
                'collection': collection.name,
                'vectors': total_items,
                'timestamp': timestamp
            })
        
        self.log(f"\n✅ Export completed to: {export_dir}", self.export_log)
        self.config['last_export'] = str(export_dir)
        self.save_config()
        
        # Add to history
        self.add_history('Export', 'Success', f"{len(export_stats)} collection(s) exported to {export_dir}")
    
    def start_import(self):
        """Start import process in background thread"""
        # Validate inputs
        import_file = self.import_file_var.get()
        if not import_file or not Path(import_file).exists():
            messagebox.showerror("Error", "Please select a valid export file")
            return
        
        # Clear log
        self.import_log.delete('1.0', tk.END)
        
        # Disable button and start progress
        self.import_button.config(state='disabled')
        self.import_progress.start()
        self.status_var.set("Importing...")
        
        def import_task():
            try:
                self.run_import()
                self.root.after(0, lambda: messagebox.showinfo("Success", "Import completed successfully!"))
            except Exception as e:
                self.log(f"❌ Import failed: {e}", self.import_log)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Import failed:\n{e}"))
            finally:
                self.root.after(0, lambda: self.import_button.config(state='normal'))
                self.root.after(0, lambda: self.import_progress.stop())
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=import_task, daemon=True).start()
    
    def run_import(self):
        """Run the actual import"""
        import_file = Path(self.import_file_var.get())
        url = self.qdrant_url_var.get()
        api_key = self.qdrant_api_key_var.get() or None
        
        self.log(f"🔗 Connecting to Qdrant at: {url}", self.import_log)
        
        if api_key:
            client = QdrantClient(url=url, api_key=api_key)
        else:
            client = QdrantClient(url=url)
        
        # Test connection
        collections = client.get_collections()
        self.log(f"✅ Connected! Found {len(collections.collections)} existing collection(s)", self.import_log)
        
        # Load export file
        self.log(f"\n📂 Loading: {import_file.name}", self.import_log)
        
        if import_file.suffix == '.pkl':
            with open(import_file, 'rb') as f:
                data = pickle.load(f)
            self.log("✅ Loaded pickle file", self.import_log)
        else:
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.log("✅ Loaded JSON file", self.import_log)
        
        # Get collection info
        info = data['collection_info']
        collection_name = self.collection_name_var.get() or info['name']
        
        self.log(f"\n📊 Import Info:", self.import_log)
        self.log(f"  Collection: {collection_name}", self.import_log)
        self.log(f"  Total Vectors: {info['total_items']}", self.import_log)
        self.log(f"  Dimension: {info['embedding_dimension']}", self.import_log)
        
        # Create collection
        self.log(f"\n🔧 Creating collection: {collection_name}", self.import_log)
        
        existing = [c.name for c in collections.collections]
        if collection_name in existing:
            self.log(f"⚠️  Collection '{collection_name}' already exists", self.import_log)
            # In GUI, we'll just proceed (user should have deleted it beforehand)
        else:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=info['embedding_dimension'],
                    distance=Distance.COSINE
                )
            )
            self.log(f"✅ Collection created", self.import_log)
        
        # Import vectors
        batch_size = self.batch_size_var.get()
        vectors = data['vectors']
        total = len(vectors)
        
        self.log(f"\n📤 Importing {total} vectors (batch size: {batch_size})", self.import_log)
        
        imported = 0
        for i in range(0, total, batch_size):
            batch = vectors[i:i + batch_size]
            points = []
            
            for item in batch:
                if item['vector'] is None:
                    continue
                
                point = PointStruct(
                    id=str(item['id']),
                    vector=item['vector'],
                    payload=item['payload']
                )
                points.append(point)
            
            if points:
                client.upsert(collection_name=collection_name, points=points)
                imported += len(points)
            
            progress = min(i + batch_size, total)
            self.log(f"  Progress: {progress}/{total} ({progress/total*100:.1f}%)", self.import_log)
        
        self.log(f"\n✅ Import complete! Imported {imported} vectors", self.import_log)
        
        # Verify
        if self.verify_import_var.get():
            self.log(f"\n🔍 Verifying import...", self.import_log)
            col_info = client.get_collection(collection_name)
            actual = col_info.vectors_count
            self.log(f"  Expected: {total}, Actual: {actual}", self.import_log)
            if actual == total:
                self.log(f"  ✅ Verification successful!", self.import_log)
            else:
                self.log(f"  ⚠️  Count mismatch!", self.import_log)
        
        # Test search
        if self.test_search_var.get():
            self.log(f"\n🔎 Running test search...", self.import_log)
            scroll_result = client.scroll(collection_name=collection_name, limit=1)
            if scroll_result[0]:
                test_vector = scroll_result[0][0].vector
                results = client.search(
                    collection_name=collection_name,
                    query_vector=test_vector,
                    limit=3
                )
                self.log(f"  ✅ Search successful! Found {len(results)} results", self.import_log)
        
        self.config['last_import'] = str(import_file)
        self.save_config()
        
        # Add to history
        self.add_history('Import', 'Success', f"{imported} vectors imported to {collection_name}")
    
    def add_history(self, operation, status, details):
        """Add entry to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_tree.insert('', 0, values=(timestamp, operation, status, details))
    
    def refresh_history(self):
        """Refresh history view"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add current session info
        if self.config.get('last_export'):
            self.history_tree.insert('', 0, values=(
                "Last Session",
                "Export",
                "Completed",
                self.config['last_export']
            ))
        
        if self.config.get('last_import'):
            self.history_tree.insert('', 0, values=(
                "Last Session",
                "Import",
                "Completed",
                self.config['last_import']
            ))


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MigrationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
