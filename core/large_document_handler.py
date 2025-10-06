"""
Large Document Handler - Process documents exceeding GPT-4 context limits
Handles documents up to millions of words by intelligent chunking
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path


class LargeDocumentHandler:
    """Handle documents that exceed GPT-4 context limits"""
    
    def __init__(self, max_chunk_words=50000):
        """
        Args:
            max_chunk_words: Maximum words per chunk (default: 50K, well under GPT-4 limit)
        """
        self.max_chunk_words = max_chunk_words
        self.max_chunk_chars = max_chunk_words * 6  # Rough estimate: 6 chars per word
    
    def estimate_words(self, text: str) -> int:
        """Estimate word count"""
        return len(text.split())
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (1 token ≈ 0.75 words)"""
        words = self.estimate_words(text)
        return int(words / 0.75)
    
    def split_by_sections(self, markdown_text: str) -> List[Dict]:
        """
        Split document by major sections (H1, H2 headers)
        Respects document structure
        
        Returns list of sections with metadata
        """
        lines = markdown_text.split('\n')
        sections = []
        current_section = {
            'header': 'Introduction',
            'level': 1,
            'start_line': 0,
            'lines': []
        }
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # New section found
                level = len(line) - len(line.lstrip('#'))
                
                # Only split on H1 or H2
                if level <= 2:
                    # Save previous section
                    if current_section['lines']:
                        current_section['end_line'] = i
                        current_section['content'] = '\n'.join(current_section['lines'])
                        current_section['word_count'] = self.estimate_words(current_section['content'])
                        sections.append(current_section)
                    
                    # Start new section
                    header_text = line.lstrip('#').strip()
                    current_section = {
                        'header': header_text,
                        'level': level,
                        'start_line': i,
                        'lines': [line]
                    }
                else:
                    current_section['lines'].append(line)
            else:
                current_section['lines'].append(line)
        
        # Add last section
        if current_section['lines']:
            current_section['end_line'] = len(lines)
            current_section['content'] = '\n'.join(current_section['lines'])
            current_section['word_count'] = self.estimate_words(current_section['content'])
            sections.append(current_section)
        
        return sections
    
    def merge_small_sections(self, sections: List[Dict], min_words=5000) -> List[Dict]:
        """
        Merge sections that are too small
        Combines adjacent sections until they reach min_words
        """
        if not sections:
            return []
        
        merged = []
        current_merged = sections[0].copy()
        
        for i in range(1, len(sections)):
            section = sections[i]
            
            # If current merged section is too small, keep merging
            if current_merged['word_count'] < min_words:
                # Merge with next section
                current_merged['lines'].extend(section['lines'])
                current_merged['content'] = '\n'.join(current_merged['lines'])
                current_merged['word_count'] = self.estimate_words(current_merged['content'])
                current_merged['end_line'] = section['end_line']
                current_merged['header'] += f" & {section['header']}"
            else:
                # Current section is big enough, save it
                merged.append(current_merged)
                current_merged = section.copy()
        
        # Add last merged section
        merged.append(current_merged)
        
        return merged
    
    def split_large_sections(self, sections: List[Dict], max_words=50000) -> List[Dict]:
        """
        Split sections that are too large
        Maintains context by keeping some overlap
        """
        result = []
        
        for section in sections:
            if section['word_count'] <= max_words:
                result.append(section)
            else:
                # Section is too large, need to split
                lines = section['lines']
                chunk_lines = []
                chunk_words = 0
                chunk_num = 1
                
                for line in lines:
                    line_words = self.estimate_words(line)
                    
                    if chunk_words + line_words > max_words and chunk_lines:
                        # Save current chunk
                        chunk_section = {
                            'header': f"{section['header']} (Part {chunk_num})",
                            'level': section['level'],
                            'content': '\n'.join(chunk_lines),
                            'word_count': chunk_words,
                            'lines': chunk_lines
                        }
                        result.append(chunk_section)
                        
                        # Start new chunk with overlap (last 20 lines for context)
                        overlap_lines = chunk_lines[-20:] if len(chunk_lines) > 20 else []
                        chunk_lines = overlap_lines + [line]
                        chunk_words = sum(self.estimate_words(l) for l in chunk_lines)
                        chunk_num += 1
                    else:
                        chunk_lines.append(line)
                        chunk_words += line_words
                
                # Save last chunk
                if chunk_lines:
                    chunk_section = {
                        'header': f"{section['header']} (Part {chunk_num})" if chunk_num > 1 else section['header'],
                        'level': section['level'],
                        'content': '\n'.join(chunk_lines),
                        'word_count': chunk_words,
                        'lines': chunk_lines
                    }
                    result.append(chunk_section)
        
        return result
    
    def prepare_document(self, markdown_text: str) -> Tuple[List[Dict], Dict]:
        """
        Prepare a large document for processing
        
        Returns:
            - List of processable chunks
            - Statistics about the document
        """
        total_words = self.estimate_words(markdown_text)
        
        print(f"\n{'='*70}")
        print(f"LARGE DOCUMENT HANDLER")
        print(f"{'='*70}")
        print(f"Total words: {total_words:,}")
        print(f"Estimated tokens: {self.estimate_tokens(markdown_text):,}")
        print(f"Target chunk size: {self.max_chunk_words:,} words")
        print()
        
        # Step 1: Split by sections
        print("Step 1: Splitting by document sections...")
        sections = self.split_by_sections(markdown_text)
        print(f"  Found {len(sections)} sections")
        
        # Step 2: Merge small sections
        print("\nStep 2: Merging small sections...")
        sections = self.merge_small_sections(sections, min_words=5000)
        print(f"  After merging: {len(sections)} sections")
        
        # Step 3: Split large sections
        print("\nStep 3: Splitting oversized sections...")
        sections = self.split_large_sections(sections, max_words=self.max_chunk_words)
        print(f"  After splitting: {len(sections)} processable chunks")
        
        # Statistics
        print(f"\n{'='*70}")
        print("CHUNK SUMMARY")
        print(f"{'='*70}")
        for i, section in enumerate(sections, 1):
            print(f"{i}. {section['header']}")
            print(f"   Words: {section['word_count']:,}")
            print(f"   Tokens: ~{self.estimate_tokens(section['content']):,}")
        
        stats = {
            'total_words': total_words,
            'total_chunks': len(sections),
            'avg_words_per_chunk': total_words // len(sections) if sections else 0,
            'largest_chunk': max((s['word_count'] for s in sections), default=0),
            'smallest_chunk': min((s['word_count'] for s in sections), default=0)
        }
        
        print(f"\nStatistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Avg words/chunk: {stats['avg_words_per_chunk']:,}")
        print(f"  Largest chunk: {stats['largest_chunk']:,} words")
        print(f"  Smallest chunk: {stats['smallest_chunk']:,} words")
        print(f"{'='*70}\n")
        
        return sections, stats
    
    def process_in_batches(self, sections: List[Dict], process_func, 
                          progress_callback=None) -> List:
        """
        Process chunks in batches with progress tracking
        
        Args:
            sections: List of document chunks
            process_func: Function to process each chunk (takes section dict)
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of processing results
        """
        results = []
        total = len(sections)
        
        for i, section in enumerate(sections, 1):
            if progress_callback:
                progress_callback(f"Processing chunk {i}/{total}: {section['header']}")
            
            try:
                result = process_func(section)
                results.append({
                    'section': section,
                    'result': result,
                    'success': True
                })
            except Exception as e:
                if progress_callback:
                    progress_callback(f"  Error: {e}")
                results.append({
                    'section': section,
                    'error': str(e),
                    'success': False
                })
        
        return results


def create_chunk_summary(markdown_text: str, max_words: int = 50000) -> str:
    """
    Create a summary suitable for GPT-4 processing
    Extracts key information without exceeding limits
    """
    handler = LargeDocumentHandler(max_chunk_words=max_words)
    
    # Get first and last parts
    words = markdown_text.split()
    total_words = len(words)
    
    # Take first 20% and last 10%
    first_part_words = int(total_words * 0.2)
    last_part_words = int(total_words * 0.1)
    
    first_part = ' '.join(words[:first_part_words])
    last_part = ' '.join(words[-last_part_words:])
    
    # Extract all headers
    headers = []
    for line in markdown_text.split('\n'):
        if line.startswith('#'):
            headers.append(line)
    
    # Create summary
    summary = f"""# Document Summary for Large Document ({total_words:,} words)

## Document Structure
{chr(10).join(headers[:50])}  <!-- First 50 headers -->

## Beginning of Document
{first_part}

## End of Document
{last_part}

---
*This is a summary of a {total_words:,}-word document, containing the beginning, end, and structural outline.*
"""
    
    return summary
