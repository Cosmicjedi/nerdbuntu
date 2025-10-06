#!/usr/bin/env python3
"""
Multi-Document Processing Demo
Shows how to process multiple PDFs and query across them
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from core.semantic_linker import SemanticLinker
from markitdown import MarkItDown


def process_multiple_pdfs(input_files, output_dir, enable_semantic=True):
    """
    Process multiple PDF files and add them all to the same vector database
    
    Args:
        input_files: List of PDF file paths
        output_dir: Directory to save markdown files
        enable_semantic: Whether to use semantic processing
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    markitdown = MarkItDown()
    
    if enable_semantic:
        azure_endpoint = os.getenv("AZURE_ENDPOINT")
        azure_api_key = os.getenv("AZURE_API_KEY")
        
        if not azure_endpoint or not azure_api_key:
            print("⚠ Azure not configured - using basic mode")
            enable_semantic = False
        else:
            semantic_linker = SemanticLinker(azure_endpoint, azure_api_key)
            vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
            vector_db_path.mkdir(parents=True, exist_ok=True)
            semantic_linker.initialize_vector_db(str(vector_db_path))
    
    print(f"\n{'='*70}")
    print(f"Processing {len(input_files)} PDF files")
    print(f"Output directory: {output_dir}")
    print(f"Semantic mode: {'ENABLED' if enable_semantic else 'DISABLED'}")
    print(f"{'='*70}\n")
    
    results = []
    
    for i, pdf_file in enumerate(input_files, 1):
        pdf_path = Path(pdf_file)
        
        if not pdf_path.exists():
            print(f"✗ File not found: {pdf_file}")
            continue
        
        print(f"\n[{i}/{len(input_files)}] Processing: {pdf_path.name}")
        print("-" * 70)
        
        try:
            # Convert PDF
            print("  Converting PDF to Markdown...")
            result = markitdown.convert(str(pdf_path))
            markdown_text = result.text_content
            print(f"  ✓ Converted ({len(markdown_text)} characters)")
            
            # Apply semantic processing if enabled
            if enable_semantic:
                print("  Applying semantic processing...")
                markdown_text = semantic_linker.add_semantic_links(
                    markdown_text,
                    pdf_path.name
                )
                print("  ✓ Semantic processing complete")
            
            # Save output
            output_file = output_dir / f"{pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            print(f"  ✓ Saved to: {output_file}")
            
            results.append({
                'input': pdf_path.name,
                'output': output_file,
                'success': True
            })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'input': pdf_path.name,
                'output': None,
                'success': False,
                'error': str(e)
            })
    
    # Show summary
    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n✓ Successfully processed: {successful}/{len(results)}")
    if failed > 0:
        print(f"✗ Failed: {failed}/{len(results)}")
    
    print(f"\nOutput files:")
    for result in results:
        if result['success']:
            print(f"  ✓ {result['output']}")
        else:
            print(f"  ✗ {result['input']} - {result.get('error', 'Unknown error')}")
    
    # Show vector database stats if semantic was enabled
    if enable_semantic:
        total_chunks = semantic_linker.collection.count()
        print(f"\n📊 Vector Database Statistics:")
        print(f"  Total chunks stored: {total_chunks}")
        print(f"  From {successful} documents")
        print(f"  Average: {total_chunks // successful if successful > 0 else 0} chunks per document")
    
    return results


def query_all_documents(query_text, n_results=5):
    """
    Query across all documents in the vector database
    
    Args:
        query_text: Text to search for
        n_results: Number of results to return
    """
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_api_key = os.getenv("AZURE_API_KEY")
    
    if not azure_endpoint or not azure_api_key:
        print("⚠ Azure not configured - query feature requires semantic mode")
        return
    
    semantic_linker = SemanticLinker(azure_endpoint, azure_api_key)
    vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
    semantic_linker.initialize_vector_db(str(vector_db_path))
    
    print(f"\n{'='*70}")
    print(f"Searching for: '{query_text}'")
    print(f"{'='*70}\n")
    
    results = semantic_linker.find_similar_chunks(query_text, n_results)
    
    if not results or not results['documents'][0]:
        print("No results found.")
        return
    
    print(f"Found {len(results['documents'][0])} similar chunks:\n")
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"Result {i}:")
        print(f"  Source: {metadata['source']}")
        print(f"  Chunk ID: {metadata['chunk_id']}")
        print(f"  Similarity: {1 - distance:.2%}")
        print(f"  Preview: {doc[:200]}...")
        print()


def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process multiple PDFs and query across them"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process multiple PDFs')
    process_parser.add_argument('pdfs', nargs='+', help='PDF files to process')
    process_parser.add_argument('-o', '--output', default='data/output',
                               help='Output directory (default: data/output)')
    process_parser.add_argument('--no-semantic', action='store_true',
                               help='Disable semantic processing')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query all processed documents')
    query_parser.add_argument('query', help='Search query')
    query_parser.add_argument('-n', '--results', type=int, default=5,
                            help='Number of results (default: 5)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show vector database statistics')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        process_multiple_pdfs(
            args.pdfs,
            args.output,
            enable_semantic=not args.no_semantic
        )
    
    elif args.command == 'query':
        query_all_documents(args.query, args.results)
    
    elif args.command == 'stats':
        # Show vector database statistics
        vector_db_path = Path.home() / "nerdbuntu" / "data" / "vector_db"
        
        if not vector_db_path.exists():
            print("No vector database found. Process some documents first!")
            return
        
        import chromadb
        client = chromadb.PersistentClient(path=str(vector_db_path))
        collection = client.get_or_create_collection("markdown_chunks")
        
        total_chunks = collection.count()
        
        print(f"\n{'='*70}")
        print("VECTOR DATABASE STATISTICS")
        print(f"{'='*70}")
        print(f"\nTotal chunks: {total_chunks}")
        print(f"Database location: {vector_db_path}")
        
        # Get unique sources
        if total_chunks > 0:
            all_data = collection.get()
            sources = set(m['source'] for m in all_data['metadatas'])
            print(f"Documents: {len(sources)}")
            print(f"\nDocument list:")
            for source in sorted(sources):
                source_chunks = sum(1 for m in all_data['metadatas'] if m['source'] == source)
                print(f"  - {source}: {source_chunks} chunks")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
