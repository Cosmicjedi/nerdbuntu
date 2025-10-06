"""
SemanticLinker - Handles semantic analysis and backlinking using Azure AI and embeddings
"""

import json
from datetime import datetime
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import chromadb
from sentence_transformers import SentenceTransformer


class SemanticLinker:
    """Handles semantic analysis and backlinking using Azure AI and embeddings"""
    
    def __init__(self, azure_endpoint, azure_api_key):
        self.azure_endpoint = azure_endpoint
        self.azure_api_key = azure_api_key
        self.client = ChatCompletionsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(azure_api_key)
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = None
        self.collection = None
        self.azure_available = True
        
    def initialize_vector_db(self, db_path):
        """Initialize ChromaDB for vector storage"""
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="markdown_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
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
            return concepts if isinstance(concepts, list) else []
        except HttpResponseError as e:
            if e.status_code == 404:
                print(f"Azure AI Error (404): Resource not found.")
                print(f"This usually means:")
                print(f"  1. The endpoint URL is incorrect")
                print(f"  2. The model deployment name doesn't exist")
                print(f"  3. The deployment is not in the specified region")
                print(f"\nCurrent endpoint: {self.azure_endpoint}")
                print(f"\nPlease check your .env file and ensure:")
                print(f"  - AZURE_ENDPOINT is correct (e.g., https://YOUR-RESOURCE.openai.azure.com/)")
                print(f"  - Your deployment name matches what's configured in Azure Portal")
                print(f"\nDisabling Azure AI features for this session.")
                self.azure_available = False
            else:
                print(f"Azure AI Error ({e.status_code}): {e.message}")
            return []
        except Exception as e:
            print(f"Error extracting concepts: {e}")
            return []
    
    def generate_embeddings(self, texts):
        """Generate embeddings for text chunks"""
        return self.embedding_model.encode(texts)
    
    def find_similar_chunks(self, query_text, n_results=5):
        """Find similar chunks using vector similarity"""
        if not self.collection:
            return []
        
        query_embedding = self.embedding_model.encode([query_text])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        return results
    
    def add_semantic_links(self, markdown_text, filename):
        """Add semantic backlinks to markdown"""
        chunks = self.chunk_markdown(markdown_text)
        
        # Generate embeddings for all chunks
        embeddings = self.generate_embeddings(chunks)
        
        # Store in vector database
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=[{"source": filename, "chunk_id": i} for i in range(len(chunks))]
        )
        
        # Extract key concepts (will skip if Azure unavailable)
        key_concepts = self.extract_key_concepts(markdown_text)
        
        # Add metadata section to markdown
        metadata = f"""---
source: {filename}
processed: {datetime.now().isoformat()}
key_concepts: {', '.join(key_concepts[:10]) if key_concepts else 'N/A (Azure AI unavailable)'}
chunks: {len(chunks)}
---

"""
        
        # Add backlinks section at the end
        backlinks = "\n\n---\n\n## Semantic Backlinks\n\n"
        backlinks += "This document is semantically linked in the vector database.\n"
        if key_concepts:
            backlinks += f"- **Key Concepts**: {', '.join(key_concepts[:10])}\n"
        else:
            backlinks += "- **Key Concepts**: Not extracted (Azure AI unavailable)\n"
        backlinks += f"- **Total Chunks**: {len(chunks)}\n"
        
        return metadata + markdown_text + backlinks
