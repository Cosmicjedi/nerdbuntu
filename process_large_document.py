#!/usr/bin/env python3
"""
Process Large Documents (handles 100K+ word documents)
Splits into manageable chunks and processes with topic detection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from core.large_document_handler import LargeDocumentHandler
from core.topic_splitter import TopicSplitter
from markitdown import MarkItDown


def process_large_pdf(pdf_path, output_dir, max_chunk_words=50000):
    """
    Process a large PDF (100K+ words) by:
    1. Converting to markdown
    2. Splitting into manageable chunks
    3. Detecting topics in each chunk
    4. Creating interconnected topic files
    
    Args:
        pdf_path: Path to PDF
        output_dir: Output directory
        max_chunk_words: Maximum words per chunk (default: 50K, safe for GPT-4)
    """
    
    print("="*70)
    print("LARGE DOCUMENT PROCESSOR")
    print("Handles documents exceeding GPT-4 context limits")
    print("="*70)
    print()
    
    # Check Azure
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_api_key = os.getenv("AZURE_API_KEY")
    
    if not azure_endpoint or not azure_api_key:
        print("✗ Azure AI not configured - required for large documents")
        print("  Run: ./configure_azure.sh")
        return
    
    print(f"Input: {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"Max chunk size: {max_chunk_words:,} words")
    print()
    
    # Initialize
    markitdown = MarkItDown()
    handler = LargeDocumentHandler(max_chunk_words=max_chunk_words)
    splitter = TopicSplitter(azure_endpoint, azure_api_key)
    splitter.set_progress_callback(print)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Convert PDF
    print("\n" + "="*70)
    print("STEP 1: Converting PDF to Markdown")
    print("="*70)
    result = markitdown.convert(pdf_path)
    markdown_text = result.text_content
    word_count = len(markdown_text.split())
    print(f"✓ Converted: {word_count:,} words")
    
    # Check if document is actually large
    if word_count < 80000:
        print("\n⚠ This document is small enough for normal processing")
        print("  Use: python3 split_by_topics.py instead")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return
    
    # Step 2: Prepare document (chunk it)
    print("\n" + "="*70)
    print("STEP 2: Preparing Large Document")
    print("="*70)
    chunks, stats = handler.prepare_document(markdown_text)
    
    print(f"\n✓ Document prepared: {stats['total_chunks']} processable chunks")
    print(f"  Each chunk: {stats['avg_words_per_chunk']:,} words average")
    print(f"  Estimated processing time: {stats['total_chunks'] * 2}-{stats['total_chunks'] * 4} minutes")
    
    # Confirm before processing
    estimated_cost = (stats['total_words'] / 1000) * 0.03 * 2  # Rough estimate
    print(f"\n⚠ Estimated Azure cost: ${estimated_cost:.2f}")
    response = input("\nProceed with processing? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled")
        return
    
    # Step 3: Process each chunk
    print("\n" + "="*70)
    print("STEP 3: Processing Chunks")
    print("="*70)
    
    all_topics = []
    all_topic_files = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i}/{len(chunks)}: {chunk['header']} ---")
        print(f"Words: {chunk['word_count']:,}")
        
        try:
            # Create subdirectory for this chunk
            chunk_dir = output_path / f"chunk_{i:02d}_{chunk['header'][:30].replace(' ', '_')}"
            chunk_dir.mkdir(parents=True, exist_ok=True)
            
            # Detect topics in this chunk
            topics = splitter.detect_topics(
                chunk['content'],
                min_topics=2,
                max_topics=5
            )
            
            # Extract topic contents
            topic_contents = {}
            for topic in topics:
                content = splitter.extract_topic_content(chunk['content'], topic)
                topic_contents[topic['topic_name']] = content
            
            # Generate links
            links = splitter.generate_semantic_links(topics, topic_contents)
            
            # Create files
            for topic in topics:
                topic_name = topic['topic_name']
                content = topic_contents[topic_name]
                related = links.get(topic_name, [])
                
                md = splitter.create_topic_markdown(
                    topic, content, related,
                    f"{Path(pdf_path).name} - Chunk {i}"
                )
                
                output_file = chunk_dir / f"{topic_name}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md)
                
                all_topic_files.append(output_file)
            
            all_topics.extend(topics)
            print(f"✓ Chunk {i} complete: {len(topics)} topics created")
            
        except Exception as e:
            print(f"✗ Error processing chunk {i}: {e}")
            continue
    
    # Step 4: Create master index
    print("\n" + "="*70)
    print("STEP 4: Creating Master Index")
    print("="*70)
    
    master_index = output_path / "00_MASTER_INDEX.md"
    with open(master_index, 'w', encoding='utf-8') as f:
        f.write(f"# Master Index: {Path(pdf_path).name}\n\n")
        f.write(f"**Source:** {pdf_path}\n")
        f.write(f"**Total Words:** {word_count:,}\n")
        f.write(f"**Chunks:** {len(chunks)}\n")
        f.write(f"**Topics:** {len(all_topics)}\n\n")
        f.write("---\n\n")
        f.write("## Document Chunks\n\n")
        
        for i, chunk in enumerate(chunks, 1):
            chunk_name = f"chunk_{i:02d}_{chunk['header'][:30].replace(' ', '_')}"
            f.write(f"### {i}. {chunk['header']}\n\n")
            f.write(f"- Words: {chunk['word_count']:,}\n")
            f.write(f"- Location: `{chunk_name}/`\n\n")
        
        f.write("\n---\n\n")
        f.write("## All Topics\n\n")
        
        for topic in all_topics:
            f.write(f"- **{topic['topic_name']}**: {topic['description']}\n")
    
    all_topic_files.append(master_index)
    
    # Final summary
    print("\n" + "="*70)
    print("PROCESSING COMPLETE!")
    print("="*70)
    print(f"\nTotal files created: {len(all_topic_files)}")
    print(f"Output directory: {output_path}")
    print(f"\nStart with: {master_index.name}")
    print("\nEach chunk is in its own subdirectory with topic files")
    print("Topics within chunks are semantically linked")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process large PDFs (100K+ words) with topic splitting"
    )
    parser.add_argument('pdf', help='PDF file to process')
    parser.add_argument('-o', '--output', default='data/large_doc',
                       help='Output directory (default: data/large_doc)')
    parser.add_argument('--max-chunk-words', type=int, default=50000,
                       help='Maximum words per chunk (default: 50000)')
    
    args = parser.parse_args()
    
    if not Path(args.pdf).exists():
        print(f"✗ File not found: {args.pdf}")
        sys.exit(1)
    
    process_large_pdf(
        args.pdf,
        args.output,
        max_chunk_words=args.max_chunk_words
    )


if __name__ == "__main__":
    main()
