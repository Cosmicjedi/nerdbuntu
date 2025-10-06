"""
TopicSplitter - Split documents by topic and create semantic backlinks
Creates a network of interconnected markdown files based on topics
"""

import json
import re
from typing import List, Dict, Tuple
from pathlib import Path
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from sentence_transformers import SentenceTransformer
import numpy as np


class TopicSplitter:
    """Splits documents into topic-based files with semantic backlinks"""
    
    def __init__(self, azure_endpoint, azure_api_key):
        self.azure_endpoint = azure_endpoint
        self.azure_api_key = azure_api_key
        self.client = ChatCompletionsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(azure_api_key)
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    def _log(self, message):
        """Log progress"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
    
    def detect_topics(self, markdown_text: str, min_topics: int = 3, max_topics: int = 10) -> List[Dict]:
        """
        Use Azure AI to detect main topics and their content boundaries
        
        Returns list of topics with:
        - topic_name: string
        - description: string
        - keywords: list of strings
        - content_start: approximate line number
        - content_end: approximate line number
        """
        self._log(f"Detecting topics in document (target: {min_topics}-{max_topics} topics)...")
        
        # Get document structure
        lines = markdown_text.split('\n')
        headers = []
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                headers.append({
                    'line': i,
                    'level': level,
                    'text': text
                })
        
        # Create a summary for AI analysis
        doc_length = len(markdown_text)
        doc_preview = markdown_text[:3000]  # First 3000 chars
        
        # Ask Azure AI to identify topics
        prompt = f"""Analyze this document and identify {min_topics} to {max_topics} distinct topics or themes.

Document Preview:
{doc_preview}

Document has {len(lines)} lines and {len(headers)} headers.
Headers found: {[h['text'] for h in headers[:20]]}

For each topic, provide:
1. A clear, concise topic name (3-5 words, use underscores for spaces)
2. A brief description (one sentence)
3. 3-5 keywords related to this topic
4. Which section/header this topic corresponds to (if any)

Return as JSON array:
[
  {{
    "topic_name": "executive_summary",
    "description": "Overview of company performance and key achievements",
    "keywords": ["performance", "overview", "highlights", "achievements"],
    "related_headers": ["Executive Summary", "Overview"]
  }},
  ...
]

Focus on semantic topics, not just structural divisions. Group related content together.
"""
        
        try:
            response = self.client.complete(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing documents and identifying distinct topics and themes. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4",
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            topics = json.loads(content.strip())
            
            # Map topics to line numbers based on headers
            for topic in topics:
                topic['content_start'] = 0
                topic['content_end'] = len(lines)
                
                # Try to find matching headers
                related_headers = topic.get('related_headers', [])
                for header_text in related_headers:
                    for i, header in enumerate(headers):
                        if header_text.lower() in header['text'].lower():
                            topic['content_start'] = header['line']
                            # Find next header of same or higher level
                            for j in range(i + 1, len(headers)):
                                if headers[j]['level'] <= header['level']:
                                    topic['content_end'] = headers[j]['line']
                                    break
                            break
                    if topic['content_start'] > 0:
                        break
            
            self._log(f"✓ Detected {len(topics)} topics")
            for topic in topics:
                self._log(f"  - {topic['topic_name']}: {topic['description']}")
            
            return topics
            
        except Exception as e:
            self._log(f"✗ Error detecting topics: {e}")
            # Fallback: use headers as topics
            return self._fallback_topic_detection(markdown_text, headers, min_topics)
    
    def _fallback_topic_detection(self, markdown_text: str, headers: List[Dict], min_topics: int) -> List[Dict]:
        """Fallback: use document structure to create topics"""
        self._log("Using fallback topic detection based on document structure...")
        
        lines = markdown_text.split('\n')
        topics = []
        
        # Use top-level headers as topics
        top_headers = [h for h in headers if h['level'] <= 2]
        
        for i, header in enumerate(top_headers):
            topic_name = re.sub(r'[^\w\s-]', '', header['text'].lower())
            topic_name = re.sub(r'[-\s]+', '_', topic_name)
            
            content_start = header['line']
            content_end = len(lines)
            
            # Find next header of same or higher level
            for j in range(i + 1, len(top_headers)):
                if top_headers[j]['level'] <= header['level']:
                    content_end = top_headers[j]['line']
                    break
            
            topics.append({
                'topic_name': topic_name,
                'description': header['text'],
                'keywords': [],
                'content_start': content_start,
                'content_end': content_end
            })
        
        if len(topics) < min_topics:
            # Document doesn't have enough structure, create single topic
            topics = [{
                'topic_name': 'main_content',
                'description': 'Main document content',
                'keywords': [],
                'content_start': 0,
                'content_end': len(lines)
            }]
        
        return topics
    
    def extract_topic_content(self, markdown_text: str, topic: Dict) -> str:
        """Extract content for a specific topic"""
        lines = markdown_text.split('\n')
        start = topic['content_start']
        end = topic['content_end']
        
        topic_lines = lines[start:end]
        return '\n'.join(topic_lines)
    
    def generate_semantic_links(self, topics: List[Dict], topic_contents: Dict[str, str], 
                                similarity_threshold: float = 0.3) -> Dict[str, List[Tuple[str, float]]]:
        """
        Generate semantic backlinks between topics based on content similarity
        
        Returns dict mapping topic_name -> [(related_topic_name, similarity_score), ...]
        """
        self._log("Generating semantic links between topics...")
        
        # Generate embeddings for each topic
        topic_embeddings = {}
        for topic_name, content in topic_contents.items():
            # Use first 1000 chars for embedding
            preview = content[:1000]
            embedding = self.embedding_model.encode([preview])[0]
            topic_embeddings[topic_name] = embedding
        
        # Calculate similarities
        links = {}
        topic_names = list(topic_embeddings.keys())
        
        for i, topic_name in enumerate(topic_names):
            links[topic_name] = []
            
            for j, other_name in enumerate(topic_names):
                if i == j:
                    continue
                
                # Calculate cosine similarity
                similarity = np.dot(topic_embeddings[topic_name], topic_embeddings[other_name])
                similarity = similarity / (
                    np.linalg.norm(topic_embeddings[topic_name]) * 
                    np.linalg.norm(topic_embeddings[other_name])
                )
                
                if similarity >= similarity_threshold:
                    links[topic_name].append((other_name, float(similarity)))
            
            # Sort by similarity
            links[topic_name].sort(key=lambda x: x[1], reverse=True)
            
            self._log(f"  - {topic_name}: {len(links[topic_name])} related topics")
        
        return links
    
    def create_topic_markdown(self, topic: Dict, content: str, related_topics: List[Tuple[str, float]], 
                             source_file: str) -> str:
        """Create markdown file for a single topic with backlinks"""
        
        # Add frontmatter
        md = f"""---
topic: {topic['topic_name']}
description: {topic['description']}
keywords: {', '.join(topic['keywords'])}
source: {source_file}
---

# {topic['description']}

{content}

---

## Related Topics

"""
        # Add backlinks
        if related_topics:
            for related_name, similarity in related_topics[:5]:  # Top 5 related topics
                # Create wiki-style link
                md += f"- [[{related_name}]] (similarity: {similarity:.0%})\n"
        else:
            md += "*No related topics found*\n"
        
        md += "\n---\n\n"
        md += f"*This is part of the [[{Path(source_file).stem}]] document network*\n"
        
        return md
    
    def split_by_topics(self, markdown_text: str, source_filename: str, output_dir: Path, 
                       min_topics: int = 3, max_topics: int = 10) -> List[Path]:
        """
        Split document into topic-based markdown files with semantic backlinks
        
        Returns list of created file paths
        """
        self._log("="*70)
        self._log("Starting topic-based document splitting")
        self._log("="*70)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Detect topics
        topics = self.detect_topics(markdown_text, min_topics, max_topics)
        
        if len(topics) == 0:
            self._log("✗ No topics detected, cannot split document")
            return []
        
        # Step 2: Extract content for each topic
        self._log("\nExtracting content for each topic...")
        topic_contents = {}
        for topic in topics:
            content = self.extract_topic_content(markdown_text, topic)
            topic_contents[topic['topic_name']] = content
            self._log(f"  - {topic['topic_name']}: {len(content)} characters")
        
        # Step 3: Generate semantic links
        links = self.generate_semantic_links(topics, topic_contents)
        
        # Step 4: Create markdown files
        self._log("\nCreating topic markdown files...")
        created_files = []
        
        for topic in topics:
            topic_name = topic['topic_name']
            content = topic_contents[topic_name]
            related = links.get(topic_name, [])
            
            # Create markdown
            md = self.create_topic_markdown(topic, content, related, source_filename)
            
            # Save file
            output_file = output_dir / f"{topic_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md)
            
            created_files.append(output_file)
            self._log(f"  ✓ Created: {output_file.name}")
        
        # Step 5: Create index file
        self._log("\nCreating index file...")
        index_md = self._create_index_file(topics, links, source_filename)
        index_file = output_dir / f"{Path(source_filename).stem}_index.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_md)
        created_files.append(index_file)
        
        self._log("="*70)
        self._log(f"✓ Document split complete: {len(created_files)} files created")
        self._log("="*70)
        
        return created_files
    
    def _create_index_file(self, topics: List[Dict], links: Dict, source_filename: str) -> str:
        """Create an index file linking all topics"""
        
        md = f"""---
title: Document Index
source: {source_filename}
topics: {len(topics)}
---

# Document Topic Index

This document has been split into {len(topics)} topic-based files with semantic backlinking.

## Topics

"""
        for topic in topics:
            topic_name = topic['topic_name']
            description = topic['description']
            num_links = len(links.get(topic_name, []))
            
            md += f"### [[{topic_name}]]\n\n"
            md += f"{description}\n\n"
            md += f"*Connected to {num_links} other topics*\n\n"
        
        md += "\n---\n\n## Topic Network\n\n"
        md += "This visualization shows how topics are connected:\n\n"
        
        # Simple text-based network visualization
        for topic_name, related in links.items():
            if related:
                md += f"- **{topic_name}**\n"
                for related_name, similarity in related[:3]:
                    md += f"  - → [[{related_name}]] ({similarity:.0%})\n"
        
        return md
