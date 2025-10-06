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
    print("Or install dotenv specifically:")
    print("  pip install python-dotenv")
    sys.exit(1)

try:
    from core.semantic_linker import SemanticLinker
    from markitdown import MarkItDown
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please run setup.sh first to install dependencies")
    sys.exit(1)


class NerdbuntuApp:
    """Main application GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nerdbuntu - Intelligent PDF to Markdown Converter")
        self.root.geometry("900x700")
        
        # Check Azure configuration
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.azure_api_key = os.getenv("AZURE_API_KEY")
        
        if not self.azure_endpoint or not self.azure_api_key:
            messagebox.showerror(
                "Configuration Error",
                "Azure credentials not found. Please run setup.sh first."
            )
            sys.exit(1)
        
        # Initialize components
        self.markitdown = MarkItDown()
        self.semantic_linker = SemanticLinker(self.azure_endpoint, self.azure_api_key)
        
        # Default paths
        self.input_file = None
        self.output_dir = Path.home() / "nerdbuntu" / "data" / "output"
        self.vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector DB
        self.semantic_linker.initialize_vector_db(str(self.vector_db_path))
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Nerdbuntu - Intelligent PDF to Markdown",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
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
        
        self.enable_semantic = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Enable Semantic Backlinking (uses Azure AI)",
            variable=self.enable_semantic
        ).pack(anchor="w")
        
        self.extract_concepts = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Extract Key Concepts (uses Azure AI)",
            variable=self.extract_concepts
        ).pack(anchor="w")
        
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
        """Add message to log"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
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
        thread = threading.Thread(target=self._process_file_thread)
        thread.daemon = True
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
            
            # Apply semantic processing if enabled
            if self.enable_semantic.get():
                self.log("Applying semantic backlinking...")
                markdown_text = self.semantic_linker.add_semantic_links(
                    markdown_text,
                    Path(self.input_file).name
                )
                self.log("Semantic backlinking complete")
            
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
