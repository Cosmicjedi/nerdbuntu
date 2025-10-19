#!/usr/bin/env python3
"""
Nerdbuntu GUI Application  
Intelligent PDF to Markdown converter with semantic backlinking for RAG
Supports single file and bulk directory processing
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
from datetime import datetime
import threading
import time
import glob

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
    """Main application GUI with single file and bulk directory processing"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Nerdbuntu - Intelligent PDF to Markdown Converter")
        self.root.geometry("950x750")
        
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
        self.input_directory = None
        self.output_dir = Path.home() / "nerdbuntu" / "data" / "output"
        self.vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
        
        # Processing mode: 'file' or 'directory'
        self.processing_mode = tk.StringVar(value='file')
        
        # Bulk processing stats
        self.bulk_stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
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
        
        # Processing mode selection
        mode_frame = tk.LabelFrame(self.root, text="Processing Mode", padx=10, pady=10)
        mode_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Radiobutton(
            mode_frame,
            text="Single File - Process one PDF file",
            variable=self.processing_mode,
            value='file',
            command=self.update_mode_ui
        ).pack(anchor="w")
        
        tk.Radiobutton(
            mode_frame,
            text="Bulk Directory - Process all PDFs in a directory",
            variable=self.processing_mode,
            value='directory',
            command=self.update_mode_ui
        ).pack(anchor="w")
        
        # File selection frame
        self.file_frame = tk.LabelFrame(self.root, text="File Selection", padx=10, pady=10)
        self.file_frame.pack(fill="x", padx=20, pady=5)
        
        # Single file input (shown when mode='file')
        self.file_row = tk.Frame(self.file_frame)
        self.file_row.pack(fill="x")
        tk.Label(self.file_row, text="PDF File:").pack(side="left")
        self.input_entry = tk.Entry(self.file_row, width=55)
        self.input_entry.pack(side="left", padx=5)
        tk.Button(self.file_row, text="Browse File", command=self.browse_input_file).pack(side="left")
        
        # Directory input (shown when mode='directory')
        self.dir_row = tk.Frame(self.file_frame)
        tk.Label(self.dir_row, text="Input Directory:").pack(side="left")
        self.input_dir_entry = tk.Entry(self.dir_row, width=50)
        self.input_dir_entry.pack(side="left", padx=5)
        tk.Button(self.dir_row, text="Browse Directory", command=self.browse_input_directory).pack(side="left")
        
        # File pattern for directory mode
        self.pattern_row = tk.Frame(self.file_frame)
        tk.Label(self.pattern_row, text="File Pattern:").pack(side="left")
        self.pattern_entry = tk.Entry(self.pattern_row, width=20)
        self.pattern_entry.insert(0, "*.pdf")
        self.pattern_entry.pack(side="left", padx=5)
        tk.Label(
            self.pattern_row,
            text="(e.g., *.pdf, report_*.pdf)",
            font=("Arial", 9, "italic"),
            fg="gray"
        ).pack(side="left")
        
        # Output directory (always shown)
        output_row = tk.Frame(self.file_frame)
        output_row.pack(fill="x", pady=5)
        tk.Label(output_row, text="Output Directory:").pack(side="left")
        self.output_entry = tk.Entry(output_row, width=50)
        self.output_entry.insert(0, str(self.output_dir))
        self.output_entry.pack(side="left", padx=5)
        tk.Button(output_row, text="Browse", command=self.browse_output).pack(side="left")
        
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
        
        # Bulk processing options
        self.skip_existing = tk.BooleanVar(value=True)
        skip_checkbox = tk.Checkbutton(
            options_frame,
            text="Skip files that already have output (for bulk processing)",
            variable=self.skip_existing
        )
        skip_checkbox.pack(anchor="w")
        
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
            command=self.process,
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
        
        # Initialize UI mode
        self.update_mode_ui()
    
    def update_mode_ui(self):
        """Update UI based on selected processing mode"""
        mode = self.processing_mode.get()
        
        if mode == 'file':
            # Show file input, hide directory input
            self.file_row.pack(fill="x")
            self.dir_row.pack_forget()
            self.pattern_row.pack_forget()
            self.process_btn.config(text="Process PDF File")
        else:
            # Show directory input, hide file input
            self.file_row.pack_forget()
            self.dir_row.pack(fill="x")
            self.pattern_row.pack(fill="x", pady=5)
            self.process_btn.config(text="Process All PDFs in Directory")
    
    def browse_input_file(self):
        """Browse for input PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            self.input_file = filename
    
    def browse_input_directory(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(title="Select Input Directory with PDFs")
        if directory:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, directory)
            self.input_directory = directory
    
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
    
    def update_status(self, message):
        """Update status bar - thread-safe"""
        def _update():
            self.status_label.config(text=message)
            self.root.update_idletasks()
        
        self.root.after(0, _update)
    
    def process(self):
        """Main process dispatcher"""
        mode = self.processing_mode.get()
        
        if mode == 'file':
            self.process_single_file()
        else:
            self.process_directory()
    
    def process_single_file(self):
        """Process a single PDF file"""
        if not self.input_entry.get():
            messagebox.showerror("Error", "Please select a PDF file")
            return
        
        self.input_file = self.input_entry.get()
        self.output_dir = Path(self.output_entry.get())
        
        if not Path(self.input_file).exists():
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        # Run processing in a separate thread
        thread = threading.Thread(target=self._process_file_thread, args=(self.input_file,), daemon=True)
        thread.start()
    
    def process_directory(self):
        """Process all PDFs in a directory"""
        if not self.input_dir_entry.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
        
        self.input_directory = self.input_dir_entry.get()
        self.output_dir = Path(self.output_entry.get())
        
        if not Path(self.input_directory).exists():
            messagebox.showerror("Error", "Input directory does not exist")
            return
        
        # Get list of files
        pattern = self.pattern_entry.get() or "*.pdf"
        search_path = Path(self.input_directory) / pattern
        files = glob.glob(str(search_path))
        
        if not files:
            messagebox.showerror("Error", f"No files matching '{pattern}' found in directory")
            return
        
        # Confirm with user
        response = messagebox.askyesno(
            "Confirm Bulk Processing",
            f"Found {len(files)} file(s) matching '{pattern}'.\n\n"
            f"This will process all files and may take a while.\n\n"
            f"Continue?"
        )
        
        if not response:
            return
        
        # Run bulk processing in a separate thread
        thread = threading.Thread(target=self._process_directory_thread, args=(files,), daemon=True)
        thread.start()
    
    def _process_directory_thread(self, files):
        """Process multiple files in bulk"""
        try:
            # Disable UI
            self.root.after(0, lambda: self.process_btn.config(state="disabled"))
            self.root.after(0, lambda: self.progress.start())
            
            # Reset stats
            self.bulk_stats = {
                'total': len(files),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0
            }
            
            self.log("="*60)
            self.log(f"BULK PROCESSING MODE")
            self.log(f"Total files: {self.bulk_stats['total']}")
            self.log(f"Input directory: {self.input_directory}")
            self.log(f"Output directory: {self.output_dir}")
            self.log("="*60)
            
            # Process each file
            for idx, file_path in enumerate(files, 1):
                file_path = Path(file_path)
                
                self.log("")
                self.log(f"📄 File {idx}/{self.bulk_stats['total']}: {file_path.name}")
                self.update_status(f"Processing {idx}/{self.bulk_stats['total']}: {file_path.name}")
                
                # Check if output already exists
                output_filename = file_path.stem + ".md"
                output_path = self.output_dir / output_filename
                
                if self.skip_existing.get() and output_path.exists():
                    self.log(f"  ⏭️  Skipping (output already exists): {output_path.name}")
                    self.bulk_stats['skipped'] += 1
                    continue
                
                # Process the file
                try:
                    self._process_single_file_logic(str(file_path))
                    self.bulk_stats['successful'] += 1
                    self.log(f"  ✅ Success: {output_filename}")
                except Exception as e:
                    self.bulk_stats['failed'] += 1
                    self.log(f"  ❌ Failed: {e}")
                
                self.bulk_stats['processed'] += 1
            
            # Final summary
            self.log("")
            self.log("="*60)
            self.log("BULK PROCESSING COMPLETE")
            self.log(f"Total files: {self.bulk_stats['total']}")
            self.log(f"Processed: {self.bulk_stats['processed']}")
            self.log(f"Successful: {self.bulk_stats['successful']}")
            self.log(f"Failed: {self.bulk_stats['failed']}")
            self.log(f"Skipped: {self.bulk_stats['skipped']}")
            self.log("="*60)
            
            self.update_status(f"✓ Bulk processing complete: {self.bulk_stats['successful']}/{self.bulk_stats['total']} successful")
            
            # Show summary dialog
            def show_summary():
                messagebox.showinfo(
                    "Bulk Processing Complete",
                    f"Processing Summary:\n\n"
                    f"Total files: {self.bulk_stats['total']}\n"
                    f"Successful: {self.bulk_stats['successful']}\n"
                    f"Failed: {self.bulk_stats['failed']}\n"
                    f"Skipped: {self.bulk_stats['skipped']}\n\n"
                    f"Output directory: {self.output_dir}"
                )
            
            self.root.after(0, show_summary)
            
        except Exception as e:
            self.log(f"❌ Bulk processing error: {e}")
            self.update_status("✗ Bulk processing failed")
            
            def show_error():
                messagebox.showerror("Bulk Processing Error", f"An error occurred:\n\n{str(e)}")
            
            self.root.after(0, show_error)
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.process_btn.config(state="normal"))
    
    def _process_file_thread(self, file_path):
        """Process file in separate thread (wrapper for single file mode)"""
        try:
            # Disable UI
            self.root.after(0, lambda: self.process_btn.config(state="disabled"))
            self.root.after(0, lambda: self.progress.start())
            self.update_status("Processing...")
            
            self.log("="*60)
            self.log(f"Starting PDF processing pipeline")
            self.log(f"Input: {file_path}")
            self.log("="*60)
            
            # Process the file
            output_path = self._process_single_file_logic(file_path)
            
            # Success
            self.log("="*60)
            self.log("✓✓✓ ALL PROCESSING COMPLETE ✓✓✓")
            self.log(f"Output file: {output_path}")
            self.log("="*60)
            
            self.update_status("✓ Complete - All operations finished successfully")
            
            # Show success dialog
            def show_success():
                messagebox.showinfo(
                    "Processing Complete",
                    f"PDF successfully converted!\n\n"
                    f"Output: {output_path}\n"
                    f"Size: {output_path.stat().st_size:,} bytes\n\n"
                    f"All semantic processing and database operations completed."
                )
            
            self.root.after(0, show_success)
            
        except Exception as e:
            self.log("="*60)
            self.log(f"✗✗✗ ERROR OCCURRED ✗✗✗")
            self.log(f"Error: {str(e)}")
            self.log("="*60)
            self.update_status("✗ Error - Processing failed")
            
            def show_error():
                messagebox.showerror(
                    "Processing Failed", 
                    f"An error occurred:\n\n{str(e)}\n\n"
                    f"Check the log for details."
                )
            
            self.root.after(0, show_error)
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.process_btn.config(state="normal"))
    
    def _process_single_file_logic(self, file_path):
        """Core logic for processing a single file (used by both modes)"""
        # Step 1: Convert PDF to markdown
        self.log("Step 1: Converting PDF to Markdown...")
        result = self.markitdown.convert(file_path)
        markdown_text = result.text_content
        self.log(f"✓ PDF converted successfully ({len(markdown_text)} characters)")
        
        # Step 2: Apply semantic processing if enabled
        if self.enable_semantic.get() and self.azure_configured and self.semantic_linker:
            self.log("Step 2: Starting semantic processing...")
            self.log("⏳ This includes chunking, embedding generation, and AI analysis")
            
            try:
                markdown_text = self.semantic_linker.add_semantic_links(
                    markdown_text,
                    Path(file_path).name
                )
                self.log("✓ Semantic processing completed successfully")
                
            except Exception as e:
                self.log(f"✗ Semantic processing failed: {e}")
                self.log("⚠ Continuing with basic conversion...")
        else:
            self.log("Step 2: Skipping semantic processing (not enabled)")
        
        # Step 3: Save output file
        self.log("Step 3: Writing output file...")
        output_filename = Path(file_path).stem + ".md"
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        # Verify file was written
        if output_path.exists():
            file_size = output_path.stat().st_size
            self.log(f"✓ File written successfully: {output_path}")
            self.log(f"  File size: {file_size:,} bytes")
        else:
            raise Exception("File was not created on disk!")
        
        # Step 4: Verify everything is complete
        self.log("Step 4: Verifying completion...")
        
        # Ensure all file operations are flushed to disk
        os.sync()
        time.sleep(0.1)
        
        # Verify file still exists and is readable
        if not (output_path.exists() and output_path.is_file()):
            raise Exception("Output file verification failed!")
        
        self.log("✓ Output file verified on disk")
        
        # Check vector database if semantic was enabled
        if self.enable_semantic.get() and self.azure_configured and self.semantic_linker:
            if self.semantic_linker.collection:
                item_count = self.semantic_linker.collection.count()
                self.log(f"✓ Vector database populated with {item_count} chunks")
        
        return output_path


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = NerdbuntuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
