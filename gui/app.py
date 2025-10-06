#!/usr/bin/env python3
"""
Nerdbuntu GUI Application  
Intelligent PDF to Markdown converter with semantic backlinking for RAG
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
from datetime import datetime
import threading

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Error: python-dotenv package is not installed.")
    print("Please install required packages by running:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Import core modules
try:
    from core.semantic_linker import SemanticLinker
except ImportError as e:
    print(f"Error importing SemanticLinker: {e}")
    print("Please ensure the core module is properly set up")
    sys.exit(1)

# Import markitdown
try:
    from markitdown import MarkItDown
except ImportError as e:
    print(f"Error importing MarkItDown: {e}")
    print("\nMarkItDown is not installed. Please install it:")
    print("  pip install markitdown[all]")
    sys.exit(1)

# Import Azure and other dependencies
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install all dependencies: pip install -r requirements.txt")
    sys.exit(1)


class NerdbuntuApp:
    """Main application GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nerdbuntu - Intelligent PDF to Markdown Converter")
        self.root.geometry("900x700")
        
        # Set up cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Check Azure configuration
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_API_KEY")
        
        if not self.azure_endpoint or not self.azure_api_key:
            self.azure_configured = False
        else:
            self.azure_configured = True
        
        # Initialize components
        try:
            self.markitdown = MarkItDown()
        except Exception as e:
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize MarkItDown: {e}\n\n"
                "Please ensure all dependencies are installed."
            )
            sys.exit(1)
        
        # Initialize semantic linker only if Azure is configured
        if self.azure_configured:
            try:
                self.semantic_linker = SemanticLinker(self.azure_endpoint, self.azure_api_key)
                # Set progress callback
                self.semantic_linker.set_progress_callback(self.log)
            except Exception as e:
                self.azure_configured = False
                self.semantic_linker = None
        else:
            self.semantic_linker = None
        
        # Default paths
        self.input_file = None
        self.output_dir = Path.home() / "nerdbuntu" / "data" / "output"
        self.vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector DB only if Azure is configured
        if self.azure_configured and self.semantic_linker:
            try:
                self.semantic_linker.initialize_vector_db(str(self.vector_db_path))
            except Exception as e:
                self.azure_configured = False
        
        self.setup_ui()
    
    def on_closing(self):
        """Handle window close event"""
        # Forcefully exit to kill all background threads
        self.root.destroy()
        os._exit(0)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Nerdbuntu - Intelligent PDF to Markdown",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Configuration status
        status_text = "Azure AI: " + ("✓ Configured" if self.azure_configured else "✗ Not Configured (Basic Mode)")
        status_color = "green" if self.azure_configured else "orange"
        config_label = tk.Label(
            self.root,
            text=status_text,
            font=("Arial", 10),
            fg=status_color
        )
        config_label.pack()
        
        # File selection frame
        file_frame = tk.LabelFrame(self.root, text="File Selection", padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=5)
        
        # Input file
        tk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w")
        self.input_entry = tk.Entry(file_frame, width=60)
        self.input_entry.grid(row=0, column=1, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output directory
        tk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=5)
        self.output_entry = tk.Entry(file_frame, width=60)
        self.output_entry.insert(0, str(self.output_dir))
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # Options frame
        options_frame = tk.LabelFrame(self.root, text="Processing Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=5)
        
        self.enable_semantic = tk.BooleanVar(value=self.azure_configured)
        semantic_checkbox = tk.Checkbutton(
            options_frame,
            text="Enable Semantic Backlinking (uses Azure AI - slower but adds AI features)",
            variable=self.enable_semantic,
            state="normal" if self.azure_configured else "disabled"
        )
        semantic_checkbox.pack(anchor="w")
        
        self.extract_concepts = tk.BooleanVar(value=self.azure_configured)
        concepts_checkbox = tk.Checkbutton(
            options_frame,
            text="Extract Key Concepts (uses Azure AI)",
            variable=self.extract_concepts,
            state="normal" if self.azure_configured else "disabled"
        )
        concepts_checkbox.pack(anchor="w")
        
        if not self.azure_configured:
            tk.Label(
                options_frame,
                text="⚠ Azure features disabled - run ./configure_azure.sh to enable",
                fg="orange",
                font=("Arial", 9, "italic")
            ).pack(anchor="w", pady=5)
        
        # Process button
        self.process_btn = tk.Button(
            self.root,
            text="Process PDF",
            command=self.process_file,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        self.process_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill="x", padx=20, pady=5)
        
        # Log output
        log_frame = tk.LabelFrame(self.root, text="Process Log", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor="w"
        )
        self.status_label.pack(fill="x", side="bottom")
    
    def browse_input(self):
        """Browse for input PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            self.input_file = filename
    
    def browse_output(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            self.output_dir = Path(directory)
    
    def log(self, message):
        """Add message to log - thread-safe"""
        def _log():
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        
        # Schedule the update in the main thread
        self.root.after(0, _log)
    
    def process_file(self):
        """Process the PDF file"""
        if not self.input_entry.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
        
        self.input_file = self.input_entry.get()
        self.output_dir = Path(self.output_entry.get())
        
        if not Path(self.input_file).exists():
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        # Run processing in a separate thread
        thread = threading.Thread(target=self._process_file_thread, daemon=True)
        thread.start()
    
    def _process_file_thread(self):
        """Process file in separate thread"""
        try:
            self.process_btn.config(state="disabled")
            self.progress.start()
            self.status_label.config(text="Processing...")
            
            self.log(f"Processing file: {self.input_file}")
            
            # Convert PDF to markdown
            self.log("Converting PDF to Markdown...")
            result = self.markitdown.convert(self.input_file)
            markdown_text = result.text_content
            
            self.log(f"Conversion complete. Length: {len(markdown_text)} characters")
            
            # Apply semantic processing if enabled and available
            if self.enable_semantic.get() and self.azure_configured and self.semantic_linker:
                self.log("⏳ Starting semantic processing (this may take a minute)...")
                try:
                    markdown_text = self.semantic_linker.add_semantic_links(
                        markdown_text,
                        Path(self.input_file).name
                    )
                except Exception as e:
                    self.log(f"⚠ Semantic processing failed: {e}")
                    self.log("Continuing with basic conversion...")
            
            # Save output
            output_filename = Path(self.input_file).stem + ".md"
            output_path = self.output_dir / output_filename
            
            self.log(f"Saving to: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            self.log("✓ Processing complete!")
            self.status_label.config(text="Complete")
            
            messagebox.showinfo(
                "Success",
                f"PDF successfully converted!\n\nOutput: {output_path}"
            )
            
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            self.status_label.config(text="Error")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        
        finally:
            self.progress.stop()
            self.process_btn.config(state="normal")


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = NerdbuntuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
