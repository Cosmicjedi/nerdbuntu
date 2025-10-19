#!/usr/bin/env python3
"""
ChromaDB to Qdrant Migration GUI
User-friendly interface for backing up ChromaDB and restoring to Qdrant
Supports both single-server and two-server migration scenarios
NOW SUPPORTS: ChromaDB Server URLs (http://host:port) and File Paths
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
    from chromadb.config import Settings
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
        self.root.title("ChromaDB to Qdrant Migration Tool - Server & File Support")
        self.root.geometry("950x750")
        
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
            'chromadb_path': 'http://localhost:8000',
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
    
    def is_url(self, path_or_url):
        """Check if string is a URL or file path"""
        return path_or_url.startswith('http://') or path_or_url.startswith('https://')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.create_export_tab()
        self.create_import_tab()
        self.create_config_tab()
        self.create_history_tab()
        
        self.status_var = tk.StringVar(value="Ready - Supports ChromaDB servers and file paths")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_export_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Export (ChromaDB)")
        
        title_frame = ttk.Frame(tab, relief=tk.RIDGE, borderwidth=2)
        title_frame.pack(pady=10, fill='x', padx=10)
        ttk.Label(title_frame, text="Export ChromaDB Data", font=('Arial', 14, 'bold')).pack(pady=5)
        
        info_frame = ttk.LabelFrame(tab, text="Connection Options", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        info_text = """SERVER URL: http://localhost:8000\nFILE PATH: /path/to/vector_db\n\nGUI auto-detects type!"""
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor='w')
        
        path_frame = ttk.LabelFrame(tab, text="ChromaDB Connection", padding=10)
        path_frame.pack(fill='x', padx=10, pady=5)
        
        self.chromadb_path_var = tk.StringVar(value=self.config['chromadb_path'])
        ttk.Label(path_frame, text="Server URL or File Path:").pack(anchor='w')
        path_entry = ttk.Frame(path_frame)
        path_entry.pack(fill='x', pady=5)
        ttk.Entry(path_entry, textvariable=self.chromadb_path_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(path_entry, text="Browse", command=self.browse_chromadb_path).pack(side='left', padx=5)
        ttk.Button(path_entry, text="Test", command=self.test_chromadb_connection).pack(side='left')
        
        export_frame = ttk.LabelFrame(tab, text="Export Destination", padding=10)
        export_frame.pack(fill='x', padx=10, pady=5)
        self.export_dir_var = tk.StringVar(value=self.config['export_dir'])
        ttk.Label(export_frame, text="Export Directory:").pack(anchor='w')
        export_entry = ttk.Frame(export_frame)
        export_entry.pack(fill='x', pady=5)
        ttk.Entry(export_entry, textvariable=self.export_dir_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(export_entry, text="Browse", command=self.browse_export_dir).pack(side='left', padx=5)
        
        options_frame = ttk.LabelFrame(tab, text="Export Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        self.export_json_var = tk.BooleanVar(value=True)
        self.export_pickle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Export as JSON", variable=self.export_json_var).pack(anchor='w')
        ttk.Checkbutton(options_frame, text="Export as Pickle", variable=self.export_pickle_var).pack(anchor='w')
        
        self.export_button = ttk.Button(tab, text="🚀 Start Export", command=self.start_export)
        self.export_button.pack(pady=10)
        
        self.export_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.export_progress.pack(fill='x', padx=10, pady=5)
        
        log_frame = ttk.LabelFrame(tab, text="Export Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.export_log = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.export_log.pack(fill='both', expand=True)
    
    def create_import_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Import (Qdrant)")
        
        title_frame = ttk.Frame(tab, relief=tk.RIDGE, borderwidth=2)
        title_frame.pack(pady=10, fill='x', padx=10)
        ttk.Label(title_frame, text="Import to Qdrant", font=('Arial', 14, 'bold')).pack(pady=5)
        
        file_frame = ttk.LabelFrame(tab, text="Export File", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        self.import_file_var = tk.StringVar()
        ttk.Label(file_frame, text="Select Export File:").pack(anchor='w')
        file_entry = ttk.Frame(file_frame)
        file_entry.pack(fill='x', pady=5)
        ttk.Entry(file_entry, textvariable=self.import_file_var, width=60).pack(side='left', fill='x', expand=True)
        ttk.Button(file_entry, text="Browse", command=self.browse_import_file).pack(side='left', padx=5)
        
        qdrant_frame = ttk.LabelFrame(tab, text="Qdrant Connection", padding=10)
        qdrant_frame.pack(fill='x', padx=10, pady=5)
        self.qdrant_url_var = tk.StringVar(value=self.config['qdrant_url'])
        ttk.Label(qdrant_frame, text="Qdrant URL:").pack(anchor='w')
        url_frame = ttk.Frame(qdrant_frame)
        url_frame.pack(fill='x', pady=2)
        ttk.Entry(url_frame, textvariable=self.qdrant_url_var).pack(side='left', fill='x', expand=True)
        ttk.Button(url_frame, text="Test", command=self.test_qdrant_connection).pack(side='left', padx=5)
        
        self.qdrant_api_key_var = tk.StringVar(value=self.config.get('qdrant_api_key', ''))
        ttk.Label(qdrant_frame, text="API Key (optional):").pack(anchor='w', pady=(10, 0))
        ttk.Entry(qdrant_frame, textvariable=self.qdrant_api_key_var, show='*').pack(fill='x', pady=2)
        
        import_options_frame = ttk.LabelFrame(tab, text="Import Options", padding=10)
        import_options_frame.pack(fill='x', padx=10, pady=5)
        
        self.collection_name_var = tk.StringVar()
        ttk.Label(import_options_frame, text="Collection Name (optional):").pack(anchor='w')
        ttk.Entry(import_options_frame, textvariable=self.collection_name_var).pack(fill='x', pady=2)
        
        self.batch_size_var = tk.IntVar(value=self.config['batch_size'])
        ttk.Label(import_options_frame, text="Batch Size:").pack(anchor='w', pady=(10, 0))
        ttk.Spinbox(import_options_frame, from_=100, to=2000, textvariable=self.batch_size_var, increment=100).pack(fill='x', pady=2)
        
        self.verify_import_var = tk.BooleanVar(value=True)
        self.test_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(import_options_frame, text="Verify import", variable=self.verify_import_var).pack(anchor='w', pady=2)
        ttk.Checkbutton(import_options_frame, text="Test search", variable=self.test_search_var).pack(anchor='w', pady=2)
        
        self.import_button = ttk.Button(tab, text="🚀 Start Import", command=self.start_import)
        self.import_button.pack(pady=10)
        
        self.import_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.import_progress.pack(fill='x', padx=10, pady=5)
        
        log_frame = ttk.LabelFrame(tab, text="Import Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.import_log = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.import_log.pack(fill='both', expand=True)
    
    def create_config_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Config")
        ttk.Label(tab, text="Migration Settings", font=('Arial', 14, 'bold')).pack(pady=10)
        
        info_frame = ttk.LabelFrame(tab, text="System Info", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        info_text = scrolledtext.ScrolledText(info_frame, height=15, wrap=tk.WORD)
        info_text.pack(fill='both', expand=True)
        info_text.insert('1.0', self.get_system_info())
        info_text.config(state='disabled')
    
    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📜 History")
        ttk.Label(tab, text="Migration History", font=('Arial', 14, 'bold')).pack(pady=10)
        
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('timestamp', 'operation', 'status', 'details')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.history_tree.heading(col, text=col.capitalize())
        self.history_tree.column('timestamp', width=150)
        self.history_tree.column('operation', width=150)
        self.history_tree.column('status', width=100)
        self.history_tree.column('details', width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        ttk.Button(tab, text="Refresh", command=self.refresh_history).pack(pady=5)
        self.refresh_history()
    
    def get_system_info(self):
        info = ["=== ChromaDB to Qdrant Migration Tool ===\n"]
        info.append(f"Python: {sys.version}\n")
        info.append("\n=== Connection Support ===\n")
        info.append("✅ ChromaDB Server URLs\n")
        info.append("✅ ChromaDB File Paths\n")
        try:
            import chromadb
            info.append(f"\n✅ ChromaDB: {chromadb.__version__}\n")
        except:
            info.append("\n❌ ChromaDB: Not installed\n")
        try:
            from qdrant_client import QdrantClient
            info.append("✅ Qdrant Client: Installed\n")
        except:
            info.append("❌ Qdrant Client: Not installed\n")
        return ''.join(info)
    
    def browse_chromadb_path(self):
        path = filedialog.askdirectory(title="Select ChromaDB Directory")
        if path:
            self.chromadb_path_var.set(path)
            self.config['chromadb_path'] = path
            self.save_config()
    
    def browse_export_dir(self):
        path = filedialog.askdirectory(title="Select Export Directory")
        if path:
            self.export_dir_var.set(path)
            self.config['export_dir'] = path
            self.save_config()
    
    def browse_import_file(self):
        path = filedialog.askopenfilename(title="Select Export File", filetypes=[("JSON", "*.json"), ("Pickle", "*.pkl"), ("All", "*.*")])
        if path:
            self.import_file_var.set(path)
    
    def log(self, message, log_widget=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put((f"[{timestamp}] {message}", log_widget))
    
    def process_log_queue(self):
        try:
            while True:
                message, log_widget = self.log_queue.get_nowait()
                if log_widget:
                    log_widget.insert(tk.END, message + '\n')
                    log_widget.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)
    
    def test_chromadb_connection(self):
        def test():
            try:
                location = self.chromadb_path_var.get()
                self.log("Testing ChromaDB...", self.export_log)
                
                if self.is_url(location):
                    self.log("  Type: Server URL", self.export_log)
                    url_clean = location.replace('http://', '').replace('https://', '')
                    parts = url_clean.split(':')
                    host = parts[0]
                    port = int(parts[1]) if len(parts) > 1 else 8000
                    client = chromadb.HttpClient(host=host, port=port)
                else:
                    self.log("  Type: File Path", self.export_log)
                    if not Path(location).exists():
                        raise ValueError(f"Path not found: {location}")
                    client = chromadb.PersistentClient(path=location)
                
                collections = client.list_collections()
                self.log(f"✅ Connected! {len(collections)} collections", self.export_log)
                for col in collections:
                    self.log(f"  - {col.name}", self.export_log)
                messagebox.showinfo("Success", f"Connected!\n{len(collections)} collections found")
            except Exception as e:
                self.log(f"❌ Failed: {e}", self.export_log)
                messagebox.showerror("Error", f"Connection failed:\n{e}")
        threading.Thread(target=test, daemon=True).start()
    
    def test_qdrant_connection(self):
        def test():
            try:
                self.log("Testing Qdrant...", self.import_log)
                url = self.qdrant_url_var.get()
                api_key = self.qdrant_api_key_var.get() or None
                client = QdrantClient(url=url, api_key=api_key) if api_key else QdrantClient(url=url)
                collections = client.get_collections()
                self.log(f"✅ Connected! {len(collections.collections)} collections", self.import_log)
                for col in collections.collections:
                    self.log(f"  - {col.name}", self.import_log)
                messagebox.showinfo("Success", f"Connected!\n{len(collections.collections)} collections")
            except Exception as e:
                self.log(f"❌ Failed: {e}", self.import_log)
                messagebox.showerror("Error", f"Connection failed:\n{e}")
        threading.Thread(target=test, daemon=True).start()
    
    def start_export(self):
        location = self.chromadb_path_var.get()
        if not self.is_url(location) and not Path(location).exists():
            messagebox.showerror("Error", f"Path not found: {location}")
            return
        if not self.export_json_var.get() and not self.export_pickle_var.get():
            messagebox.showerror("Error", "Select at least one format")
            return
        
        self.export_log.delete('1.0', tk.END)
        self.export_button.config(state='disabled')
        self.export_progress.start()
        self.status_var.set("Exporting...")
        
        def export_task():
            try:
                self.run_export()
                self.root.after(0, lambda: messagebox.showinfo("Success", "Export complete!"))
            except Exception as e:
                self.log(f"❌ Export failed: {e}", self.export_log)
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.export_button.config(state='normal'))
                self.root.after(0, self.export_progress.stop)
                self.root.after(0, lambda: self.status_var.set("Ready"))
        threading.Thread(target=export_task, daemon=True).start()
    
    def run_export(self):
        location = self.chromadb_path_var.get()
        export_base = Path(self.export_dir_var.get())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = export_base / timestamp
        export_dir.mkdir(parents=True, exist_ok=True)
        
        self.log("Connecting to ChromaDB...", self.export_log)
        
        if self.is_url(location):
            self.log("  Type: HTTP Server", self.export_log)
            url_clean = location.replace('http://', '').replace('https://', '')
            parts = url_clean.split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 8000
            client = chromadb.HttpClient(host=host, port=port)
        else:
            self.log("  Type: File-based", self.export_log)
            client = chromadb.PersistentClient(path=location)
        
        self.log("Loading embedding model...", self.export_log)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        collections = client.list_collections()
        self.log(f"Found {len(collections)} collections", self.export_log)
        
        for collection in collections:
            self.log(f"\nExporting: {collection.name}", self.export_log)
            col = client.get_collection(collection.name)
            all_data = col.get(include=['embeddings', 'documents', 'metadatas'])
            total = len(all_data['ids'])
            
            if total == 0:
                self.log("  Empty, skipping", self.export_log)
                continue
            
            export_data = {
                'collection_info': {
                    'name': collection.name,
                    'export_date': datetime.now().isoformat(),
                    'total_items': total,
                    'embedding_model': 'all-MiniLM-L6-v2',
                    'embedding_dimension': 384,
                    'distance_metric': 'cosine',
                    'source_type': 'server' if self.is_url(location) else 'file',
                    'source_location': location
                },
                'vectors': []
            }
            
            for i in range(total):
                export_data['vectors'].append({
                    'id': all_data['ids'][i],
                    'vector': all_data['embeddings'][i] if all_data['embeddings'] else None,
                    'payload': {
                        'document': all_data['documents'][i] if all_data['documents'] else '',
                        'metadata': all_data['metadatas'][i] if all_data['metadatas'] else {}
                    }
                })
            
            base = f"{collection.name}_export_{timestamp}"
            
            if self.export_json_var.get():
                json_file = export_dir / f"{base}.json"
                self.log("  Saving JSON...", self.export_log)
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            if self.export_pickle_var.get():
                pkl_file = export_dir / f"{base}.pkl"
                self.log("  Saving Pickle...", self.export_log)
                with open(pkl_file, 'wb') as f:
                    pickle.dump(export_data, f)
        
        self.log(f"\n✅ Export complete: {export_dir}", self.export_log)
        self.config['last_export'] = str(export_dir)
        self.save_config()
        self.add_history('Export', 'Success', str(export_dir))
    
    def start_import(self):
        import_file = self.import_file_var.get()
        if not import_file or not Path(import_file).exists():
            messagebox.showerror("Error", "Select a valid file")
            return
        
        self.import_log.delete('1.0', tk.END)
        self.import_button.config(state='disabled')
        self.import_progress.start()
        self.status_var.set("Importing...")
        
        def import_task():
            try:
                self.run_import()
                self.root.after(0, lambda: messagebox.showinfo("Success", "Import complete!"))
            except Exception as e:
                self.log(f"❌ Import failed: {e}", self.import_log)
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.root.after(0, lambda: self.import_button.config(state='normal'))
                self.root.after(0, self.import_progress.stop)
                self.root.after(0, lambda: self.status_var.set("Ready"))
        threading.Thread(target=import_task, daemon=True).start()
    
    def run_import(self):
        import_file = Path(self.import_file_var.get())
        url = self.qdrant_url_var.get()
        api_key = self.qdrant_api_key_var.get() or None
        
        self.log("Connecting to Qdrant...", self.import_log)
        client = QdrantClient(url=url, api_key=api_key) if api_key else QdrantClient(url=url)
        
        self.log("Loading export file...", self.import_log)
        if import_file.suffix == '.pkl':
            with open(import_file, 'rb') as f:
                data = pickle.load(f)
        else:
            with open(import_file, 'r') as f:
                data = json.load(f)
        
        info = data['collection_info']
        collection_name = self.collection_name_var.get() or info['name']
        
        self.log(f"Collection: {collection_name}", self.import_log)
        self.log(f"Vectors: {info['total_items']}", self.import_log)
        
        collections = client.get_collections()
        existing = [c.name for c in collections.collections]
        if collection_name not in existing:
            self.log("Creating collection...", self.import_log)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=info['embedding_dimension'], distance=Distance.COSINE)
            )
        
        batch_size = self.batch_size_var.get()
        vectors = data['vectors']
        total = len(vectors)
        
        self.log(f"Importing {total} vectors...", self.import_log)
        
        imported = 0
        for i in range(0, total, batch_size):
            batch = vectors[i:i + batch_size]
            points = [PointStruct(id=str(item['id']), vector=item['vector'], payload=item['payload']) 
                     for item in batch if item['vector']]
            if points:
                client.upsert(collection_name=collection_name, points=points)
                imported += len(points)
            self.log(f"  {min(i+batch_size, total)}/{total}", self.import_log)
        
        self.log(f"\n✅ Imported {imported} vectors", self.import_log)
        
        if self.verify_import_var.get():
            self.log("Verifying...", self.import_log)
            col_info = client.get_collection(collection_name)
            self.log(f"  Count: {col_info.vectors_count}", self.import_log)
        
        if self.test_search_var.get():
            self.log("Testing search...", self.import_log)
            scroll = client.scroll(collection_name=collection_name, limit=1)
            if scroll[0]:
                test_vec = scroll[0][0].vector
                results = client.search(collection_name=collection_name, query_vector=test_vec, limit=3)
                self.log(f"  ✅ Search works!", self.import_log)
        
        self.config['last_import'] = str(import_file)
        self.save_config()
        self.add_history('Import', 'Success', f"{imported} to {collection_name}")
    
    def add_history(self, operation, status, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_tree.insert('', 0, values=(timestamp, operation, status, details))
    
    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        if self.config.get('last_export'):
            self.history_tree.insert('', 0, values=("Last", "Export", "Done", self.config['last_export']))
        if self.config.get('last_import'):
            self.history_tree.insert('', 0, values=("Last", "Import", "Done", self.config['last_import']))


def main():
    root = tk.Tk()
    app = MigrationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
