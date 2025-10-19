"""
SemanticLinker (Qdrant Version) - Handles semantic analysis and backlinking using Azure AI and Qdrant
This is the Qdrant-compatible version of semantic_linker.py
"""

import json
from datetime import datetime
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer


class SemanticLinkerQdrant:
    """Handles semantic analysis and backlinking using Azure AI and Qdrant embeddings"""
    
    def __init__(self, azure_endpoint, azure_api_key, qdrant_url="http://localhost:6333", qdrant_api_key=None):
        self.azure_endpoint = azure_endpoint
        self.azure_api_key = azure_api_key
        self.client = ChatCompletionsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(azure_api_key)
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Qdrant client
        if qdrant_api_key:
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            self.qdrant_client = QdrantClient(url=qdrant_url)
        
        self.collection_name = None
        self.azure_available = True
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set a callback function for progress updates"""
        self.progress_callback = callback
        
    def _log_progress(self, message):
        """Log progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
        
    def initialize_vector_db(self, collection_name="markdown_chunks"):
        """Initialize Qdrant collection for vector storage"""
        self.collection_name = collection_name
        
        try:
            # Try to get existing collection
            self.qdrant_client.get_collection(collection_name)
            self._log_progress(f"Using existing collection: {collection_name}")
        except:
            # Create new collection if it doesn't exist
            self._log_progress(f"Creating new collection: {collection_name}")
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
                    distance=Distance.COSINE
                )
            )
            self._log_progress(f"Collection created successfully")
        
    def chunk_markdown(self, markdown_text, chunk_size=1000):
        """Split markdown into semantic chunks"""
        lines = markdown_text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        current_headers = []
        
        for line in lines:
            # Track headers for context
            if line.startswith('#'):
                current_headers.append(line)
                if len(current_headers) > 3:
                    current_headers.pop(0)
            
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                # Add header context to chunk
                chunk_text = '\n'.join(current_headers + current_chunk)
                chunks.append(chunk_text)
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunk_text = '\n'.join(current_headers + current_chunk)
            chunks.append(chunk_text)
        
        return chunks
    
    def extract_key_concepts(self, text):
        """Use Azure AI to extract key concepts from text"""
        if not self.azure_available:
            return []
            
        try:
            self._log_progress("Calling Azure AI to extract key concepts...")
            response = self.client.complete(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts key concepts, entities, and topics from text. Return them as a JSON array of strings."
                    },
                    {
                        "role": "user",
                        "content": f"Extract the main concepts, entities, and topics from this text:\n\n{text[:2000]}"
                    }
                ],
                model="gpt-4"
            )
            
            concepts = json.loads(response.choices[0].message.content)
            self._log_progress(f"Extracted {len(concepts) if isinstance(concepts, list) else 0} concepts")
            return concepts if isinstance(concepts, list) else []
        except HttpResponseError as e:
            if e.status_code == 404:
                self._log_progress("⚠ Azure AI Error (404): Resource not found")
                self._log_progress("  The deployment name or endpoint is incorrect")
                self._log_progress("  Disabling Azure AI features for this session")
                self.azure_available = False
            else:
                self._log_progress(f"⚠ Azure AI Error ({e.status_code}): {e.message}")
            return []
        except Exception as e:
            self._log_progress(f"⚠ Error extracting concepts: {e}")
            return []
    
    def generate_embeddings(self, texts):
        """Generate embeddings for text chunks"""
        self._log_progress(f"Generating embeddings for {len(texts)} chunks (this may take a moment)...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        self._log_progress("Embeddings generated successfully")
        return embeddings
    
    def find_similar_chunks(self, query_text, n_results=5):
        """Find similar chunks using vector similarity in Qdrant"""
        if not self.collection_name:
            return []
        
        query_embedding = self.embedding_model.encode(query_text).tolist()
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=n_results
        )
        
        # Convert to ChromaDB-like format for compatibility
        formatted_results = {
            'ids': [[r.id for r in results]],
            'documents': [[r.payload.get('document', '') for r in results]],
            'metadatas': [[r.payload.get('metadata', {}) for r in results]],
            'distances': [[1 - r.score for r in results]]  # Convert similarity to distance
        }
        
        return formatted_results
    
    def add_semantic_links(self, markdown_text, filename):
        """Add semantic backlinks to markdown"""
        self._log_progress("Starting semantic processing...")
        
        # Chunk the markdown
        self._log_progress("Chunking markdown text...")
        chunks = self.chunk_markdown(markdown_text)
        self._log_progress(f"Created {len(chunks)} chunks")
        
        # Generate embeddings for all chunks
        embeddings = self.generate_embeddings(chunks)
        
        # Store in Qdrant vector database
        self._log_progress("Storing in Qdrant vector database...")
        
        # Prepare points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = f"{filename}_chunk_{i}"
            
            point = PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "document": chunk,
                    "metadata": {
                        "source": filename,
                        "chunk_id": i
                    }
                }
            )
            points.append(point)
        
        # Upload to Qdrant (handles batching internally)
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        self._log_progress("Vector database updated")
        
        # Extract key concepts (will skip if Azure unavailable)
        key_concepts = self.extract_key_concepts(markdown_text) if self.azure_available else []
        
        # Add metadata section to markdown
        metadata = f"""---
source: {filename}
processed: {datetime.now().isoformat()}
key_concepts: {', '.join(key_concepts[:10]) if key_concepts else 'N/A (Azure AI unavailable)'}
chunks: {len(chunks)}
vector_db: Qdrant
---

"""
        
        # Add backlinks section at the end
        backlinks = "\n\n---\n\n## Semantic Backlinks\n\n"
        backlinks += "This document is semantically linked in the Qdrant vector database.\n"
        if key_concepts:
            backlinks += f"- **Key Concepts**: {', '.join(key_concepts[:10])}\n"
        else:
            backlinks += "- **Key Concepts**: Not extracted (Azure AI unavailable)\n"
        backlinks += f"- **Total Chunks**: {len(chunks)}\n"
        backlinks += f"- **Vector Database**: Qdrant\n"
        
        self._log_progress("Semantic processing complete")
        return metadata + markdown_text + backlinks
    
    def delete_document(self, filename):
        """Delete all chunks associated with a document"""
        if not self.collection_name:
            self._log_progress("⚠ No collection initialized")
            return
        
        self._log_progress(f"Deleting chunks for: {filename}")
        
        # Qdrant doesn't have a direct "delete by metadata" feature like ChromaDB
        # We need to scroll through and find matching points
        offset = None
        deleted_count = 0
        
        while True:
            # Scroll through collection
            result, next_offset = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True
            )
            
            if not result:
                break
            
            # Find points matching this filename
            ids_to_delete = [
                point.id for point in result
                if point.payload.get('metadata', {}).get('source') == filename
            ]
            
            if ids_to_delete:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=ids_to_delete
                )
                deleted_count += len(ids_to_delete)
            
            if next_offset is None:
                break
            offset = next_offset
        
        self._log_progress(f"Deleted {deleted_count} chunks")
    
    def get_collection_stats(self):
        """Get statistics about the current collection"""
        if not self.collection_name:
            return {"error": "No collection initialized"}
        
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}
