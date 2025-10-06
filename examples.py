#!/usr/bin/env python3
"""
Example script demonstrating batch processing and advanced features
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from core.semantic_linker import SemanticLinker
from markitdown import MarkItDown

# Load environment
load_dotenv()

def batch_process_pdfs(input_dir, output_dir):
    """
    Process all PDFs in a directory
    """
    # Initialize
    md = MarkItDown()
    linker = SemanticLinker(
        os.getenv("AZURE_ENDPOINT"),
        os.getenv("AZURE_API_KEY")
    )
    
    vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
    linker.initialize_vector_db(str(vector_db_path))
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(input_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            # Convert to markdown
            result = md.convert(str(pdf_file))
            
            # Add semantic links
            enhanced = linker.add_semantic_links(
                result.text_content,
                pdf_file.name
            )
            
            # Save output
            output_file = output_path / f"{pdf_file.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(enhanced)
            
            print(f"  ✓ Saved to: {output_file}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Batch processing complete!")


def query_similar_content(query_text, n_results=5):
    """
    Query the vector database for similar content
    """
    linker = SemanticLinker(
        os.getenv("AZURE_ENDPOINT"),
        os.getenv("AZURE_API_KEY")
    )
    
    vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
    linker.initialize_vector_db(str(vector_db_path))
    
    print(f"Searching for: {query_text}\n")
    
    results = linker.find_similar_chunks(query_text, n_results=n_results)
    
    if results and results['documents']:
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
            similarity = 1 - distance
            print(f"Result {i} (Similarity: {similarity:.3f})")
            print("-" * 60)
            print(doc[:300] + "..." if len(doc) > 300 else doc)
            print()
    else:
        print("No results found.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Batch process: python examples.py batch <input_dir> <output_dir>")
        print("  Query: python examples.py query '<search text>'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "batch" and len(sys.argv) == 4:
        batch_process_pdfs(sys.argv[2], sys.argv[3])
    elif command == "query" and len(sys.argv) == 3:
        query_similar_content(sys.argv[2])
    else:
        print("Invalid command or arguments")
        sys.exit(1)
