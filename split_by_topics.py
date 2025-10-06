#!/usr/bin/env python3
"""
Topic-Based PDF Splitter Demo
Convert a PDF into multiple topic-based markdown files with semantic backlinks
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from core.topic_splitter import TopicSplitter
from markitdown import MarkItDown


def split_pdf_by_topics(pdf_path, output_dir, min_topics=3, max_topics=10):
    """
    Split a PDF into topic-based markdown files with semantic backlinks
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save topic files
        min_topics: Minimum number of topics to detect
        max_topics: Maximum number of topics to detect
    """
    
    print("="*70)
    print("PDF TO TOPIC-BASED MARKDOWN CONVERTER")
    print("="*70)
    print()
    
    # Check Azure configuration
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_api_key = os.getenv("AZURE_API_KEY")
    
    if not azure_endpoint or not azure_api_key:
        print("✗ Azure AI is NOT configured")
        print("  This feature requires Azure AI for topic detection")
        print("  Run: ./configure_azure.sh")
        return
    
    print("✓ Azure AI configured")
    print(f"  Input: {pdf_path}")
    print(f"  Output: {output_dir}")
    print(f"  Target topics: {min_topics}-{max_topics}")
    print()
    
    # Initialize components
    print("Initializing...")
    markitdown = MarkItDown()
    topic_splitter = TopicSplitter(azure_endpoint, azure_api_key)
    topic_splitter.set_progress_callback(print)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Convert PDF to markdown
    print("\nStep 1: Converting PDF to Markdown...")
    result = markitdown.convert(pdf_path)
    markdown_text = result.text_content
    print(f"✓ Converted ({len(markdown_text)} characters)")
    
    # Step 2: Split by topics
    print("\nStep 2: Analyzing and splitting by topics...")
    created_files = topic_splitter.split_by_topics(
        markdown_text,
        Path(pdf_path).name,
        output_path,
        min_topics=min_topics,
        max_topics=max_topics
    )
    
    # Step 3: Summary
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print(f"\nCreated {len(created_files)} files:")
    for file_path in created_files:
        file_size = file_path.stat().st_size
        print(f"  - {file_path.name} ({file_size:,} bytes)")
    
    print(f"\nAll files saved to: {output_path}")
    print("\nYou can now:")
    print("  1. Open the files in Obsidian or any markdown editor")
    print("  2. Use [[wiki-links]] to navigate between topics")
    print("  3. Start with the *_index.md file for an overview")
    print()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Split PDF into topic-based markdown files with semantic backlinks"
    )
    parser.add_argument('pdf', help='PDF file to process')
    parser.add_argument('-o', '--output', default='data/topics',
                       help='Output directory (default: data/topics)')
    parser.add_argument('--min-topics', type=int, default=3,
                       help='Minimum number of topics (default: 3)')
    parser.add_argument('--max-topics', type=int, default=10,
                       help='Maximum number of topics (default: 10)')
    
    args = parser.parse_args()
    
    # Check if PDF exists
    if not Path(args.pdf).exists():
        print(f"✗ Error: File not found: {args.pdf}")
        sys.exit(1)
    
    # Run splitting
    split_pdf_by_topics(
        args.pdf,
        args.output,
        min_topics=args.min_topics,
        max_topics=args.max_topics
    )


if __name__ == "__main__":
    main()
