#!/usr/bin/env python3
"""
Local LLM Topic Generator from Vector DB
Uses existing embeddings + local LLM (no Azure cost!)

Requirements:
- Ollama installed (https://ollama.ai)
- A model pulled (ollama pull llama3.1 or mistral)
- Existing vector database populated from previous processing
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from typing import List, Dict, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent))

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: Required packages not installed")
    print("Run: pip install chromadb sentence-transformers")
    sys.exit(1)

# Check for Ollama
try:
    import requests
    ollama_response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if ollama_response.status_code == 200:
        OLLAMA_AVAILABLE = True
        available_models = [m['name'] for m in ollama_response.json().get('models', [])]
    else:
        OLLAMA_AVAILABLE = False
        available_models = []
except:
    OLLAMA_AVAILABLE = False
    available_models = []


class LocalLLMTopicGenerator:
    """Generate topics from vector DB using local LLM (no Azure cost!)"""
    
    def __init__(self, vector_db_path: str, model_name: str = "llama3.1"):
        """
        Args:
            vector_db_path: Path to ChromaDB vector database
            model_name: Ollama model to use (e.g., 'llama3.1', 'mistral', 'llama2')
        """
        self.vector_db_path = Path(vector_db_path)
        self.model_name = model_name
        self.chroma_client = None
        self.collection = None
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"Initializing Local LLM Topic Generator")
        print(f"  Vector DB: {vector_db_path}")
        print(f"  Model: {model_name}")
        print()
        
    def load_vector_db(self):
        """Load existing vector database"""
        if not self.vector_db_path.exists():
            raise FileNotFoundError(f"Vector DB not found: {self.vector_db_path}")
        
        print("Loading vector database...")
        self.chroma_client = chromadb.PersistentClient(path=str(self.vector_db_path))
        
        # Get collection
        collections = self.chroma_client.list_collections()
        if not collections:
            raise ValueError("No collections found in vector database")
        
        self.collection = collections[0]  # Use first collection
        count = self.collection.count()
        
        print(f"✓ Loaded collection: {self.collection.name}")
        print(f"  Total chunks: {count}")
        print()
        
        return count
    
    def get_all_chunks(self) -> Dict:
        """Retrieve all chunks from vector database"""
        print("Retrieving all chunks from vector DB...")
        
        # Get everything
        results = self.collection.get(
            include=['documents', 'metadatas', 'embeddings']
        )
        
        print(f"✓ Retrieved {len(results['ids'])} chunks")
        return results
    
    def cluster_by_similarity(self, embeddings: List, threshold: float = 0.7) -> List[List[int]]:
        """
        Cluster chunks by semantic similarity
        Returns list of clusters (each cluster is list of chunk indices)
        """
        print(f"\nClustering chunks by similarity (threshold: {threshold})...")
        
        embeddings_array = np.array(embeddings)
        n = len(embeddings_array)
        
        # Calculate similarity matrix
        similarities = np.dot(embeddings_array, embeddings_array.T)
        norms = np.linalg.norm(embeddings_array, axis=1)
        similarities = similarities / np.outer(norms, norms)
        
        # Simple clustering: chunks above threshold are in same cluster
        visited = set()
        clusters = []
        
        for i in range(n):
            if i in visited:
                continue
            
            # Start new cluster
            cluster = [i]
            visited.add(i)
            
            # Add similar chunks
            for j in range(i + 1, n):
                if j not in visited and similarities[i][j] >= threshold:
                    cluster.append(j)
                    visited.add(j)
            
            clusters.append(cluster)
        
        print(f"✓ Created {len(clusters)} clusters")
        for i, cluster in enumerate(clusters, 1):
            print(f"  Cluster {i}: {len(cluster)} chunks")
        
        return clusters
    
    def call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Call local Ollama LLM"""
        import requests
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                raise Exception(f"Ollama error: {response.status_code}")
        
        except Exception as e:
            raise Exception(f"Failed to call Ollama: {e}")
    
    def generate_topic_name(self, chunks: List[str]) -> Dict:
        """Use local LLM to generate topic name and description"""
        
        # Combine chunks (limit to first 2000 chars to avoid overwhelming LLM)
        combined = "\n\n---\n\n".join(chunks[:3])  # First 3 chunks
        if len(combined) > 2000:
            combined = combined[:2000] + "..."
        
        prompt = f"""Analyze these related text chunks and identify the main topic.

Text chunks:
{combined}

Provide a response in JSON format:
{{
    "topic_name": "concise_topic_name_with_underscores",
    "description": "One sentence description of what this topic covers",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Return ONLY the JSON, no other text."""
        
        system_prompt = "You are a helpful assistant that analyzes text and identifies topics. Always respond with valid JSON."
        
        try:
            response = self.call_ollama(prompt, system_prompt)
            
            # Extract JSON from response
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            result = json.loads(response.strip())
            return result
        
        except Exception as e:
            # Fallback: generate simple topic name
            print(f"  Warning: LLM failed, using fallback - {e}")
            return {
                "topic_name": f"topic_{hash(chunks[0]) % 10000}",
                "description": "Auto-generated topic from related chunks",
                "keywords": []
            }
    
    def create_topic_file(self, topic_name: str, description: str, keywords: List[str],
                         chunks: List[str], chunk_ids: List[str], output_dir: Path) -> Path:
        """Create a markdown file for a topic"""
        
        # Sanitize filename
        filename = topic_name.lower().replace(' ', '_')
        filename = ''.join(c for c in filename if c.isalnum() or c == '_')
        output_file = output_dir / f"{filename}.md"
        
        # Build markdown
        md = f"""---
topic: {topic_name}
description: {description}
keywords: {', '.join(keywords)}
chunks: {len(chunks)}
source: vector_database
---

# {description}

"""
        
        # Add all chunks
        for i, (chunk_id, chunk) in enumerate(zip(chunk_ids, chunks), 1):
            md += f"\n## Section {i}\n\n"
            md += f"*Source: {chunk_id}*\n\n"
            md += chunk + "\n"
        
        # Add metadata
        md += f"\n---\n\n"
        md += f"**Keywords:** {', '.join(keywords)}\n\n"
        md += f"**Chunks:** {len(chunks)}\n"
        
        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return output_file
    
    def generate_topics(self, output_dir: str, similarity_threshold: float = 0.7):
        """
        Main function: Generate topic files from vector DB using local LLM
        
        Args:
            output_dir: Where to save topic files
            similarity_threshold: How similar chunks need to be to cluster (0.0-1.0)
        """
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("="*70)
        print("GENERATING TOPICS FROM VECTOR DB (LOCAL LLM)")
        print("="*70)
        print()
        
        # Load vector DB
        chunk_count = self.load_vector_db()
        
        if chunk_count == 0:
            print("✗ No chunks in vector database!")
            print("  Process some PDFs first to populate the vector DB")
            return
        
        # Get all chunks
        results = self.get_all_chunks()
        
        # Cluster by similarity
        clusters = self.cluster_by_similarity(
            results['embeddings'],
            threshold=similarity_threshold
        )
        
        # Generate topics
        print(f"\nGenerating topics using {self.model_name}...")
        print("(This may take a few minutes)")
        print()
        
        created_files = []
        
        for i, cluster_indices in enumerate(clusters, 1):
            print(f"Processing cluster {i}/{len(clusters)}...")
            
            # Get chunks in this cluster
            cluster_chunks = [results['documents'][idx] for idx in cluster_indices]
            cluster_ids = [results['ids'][idx] for idx in cluster_indices]
            
            # Generate topic info using local LLM
            topic_info = self.generate_topic_name(cluster_chunks)
            
            print(f"  Topic: {topic_info['topic_name']}")
            print(f"  Chunks: {len(cluster_chunks)}")
            
            # Create file
            output_file = self.create_topic_file(
                topic_info['topic_name'],
                topic_info['description'],
                topic_info.get('keywords', []),
                cluster_chunks,
                cluster_ids,
                output_path
            )
            
            created_files.append(output_file)
            print(f"  ✓ Created: {output_file.name}")
            print()
        
        # Create index
        print("Creating index file...")
        index_file = self._create_index(created_files, output_path)
        
        print("="*70)
        print("COMPLETE!")
        print("="*70)
        print(f"\nCreated {len(created_files)} topic files")
        print(f"Output directory: {output_path}")
        print(f"Start with: {index_file.name}")
        print()
        print("💰 Total cost: $0 (used local LLM!)")
        print()
    
    def _create_index(self, files: List[Path], output_dir: Path) -> Path:
        """Create index file"""
        index_file = output_dir / "00_INDEX.md"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# Topic Index\n\n")
            f.write(f"Generated from vector database using local LLM ({self.model_name})\n\n")
            f.write("---\n\n")
            f.write("## Topics\n\n")
            
            for file_path in files:
                topic_name = file_path.stem.replace('_', ' ').title()
                f.write(f"- [[{file_path.stem}|{topic_name}]]\n")
        
        return index_file


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate topics from vector DB using local LLM (FREE!)"
    )
    parser.add_argument('--vector-db', default='data/vector_db',
                       help='Path to vector database (default: data/vector_db)')
    parser.add_argument('--output', '-o', default='data/local_topics',
                       help='Output directory (default: data/local_topics)')
    parser.add_argument('--model', default='llama3.1',
                       help='Ollama model to use (default: llama3.1)')
    parser.add_argument('--similarity', type=float, default=0.7,
                       help='Similarity threshold for clustering (default: 0.7)')
    
    args = parser.parse_args()
    
    # Check Ollama
    if not OLLAMA_AVAILABLE:
        print("✗ Ollama is not running or not installed")
        print("\nPlease install Ollama:")
        print("  macOS: brew install ollama")
        print("  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  Windows: Download from https://ollama.ai")
        print("\nThen start it:")
        print("  ollama serve")
        print("\nAnd pull a model:")
        print("  ollama pull llama3.1")
        sys.exit(1)
    
    print("✓ Ollama is running")
    print(f"  Available models: {', '.join(available_models)}")
    
    if args.model not in available_models:
        print(f"\n✗ Model '{args.model}' not found")
        print(f"\nAvailable models: {', '.join(available_models)}")
        print(f"\nPull it with:")
        print(f"  ollama pull {args.model}")
        sys.exit(1)
    
    print()
    
    # Generate topics
    generator = LocalLLMTopicGenerator(args.vector_db, args.model)
    generator.generate_topics(args.output, args.similarity)


if __name__ == "__main__":
    main()
