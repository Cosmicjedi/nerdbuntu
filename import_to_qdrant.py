#!/usr/bin/env python3
"""
Import exported ChromaDB data into Qdrant
Reads JSON export files and uploads to Qdrant vector database
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pickle
from typing import Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Batch
except ImportError:
    print("❌ Qdrant client not installed!")
    print("Install it with: pip install qdrant-client")
    sys.exit(1)


class QdrantImporter:
    """Import ChromaDB export data into Qdrant"""
    
    def __init__(self, qdrant_url: str = "http://localhost:6333", api_key: Optional[str] = None):
        """
        Initialize Qdrant client
        
        Args:
            qdrant_url: Qdrant server URL (default: http://localhost:6333)
            api_key: Optional API key for Qdrant Cloud
        """
        print(f"🔗 Connecting to Qdrant at: {qdrant_url}")
        
        if api_key:
            self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        else:
            self.client = QdrantClient(url=qdrant_url)
        
        # Test connection
        try:
            collections = self.client.get_collections()
            print(f"✅ Connected successfully! Found {len(collections.collections)} existing collection(s)")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            print("Make sure Qdrant is running and accessible")
            sys.exit(1)
    
    def load_export_file(self, filepath: Path, use_pickle: bool = False):
        """Load export data from JSON or pickle file"""
        print(f"\n📂 Loading export file: {filepath}")
        
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        try:
            if use_pickle or filepath.suffix == '.pkl':
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                print("✅ Loaded pickle file")
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("✅ Loaded JSON file")
            
            # Validate data structure
            if 'collection_info' not in data or 'vectors' not in data:
                print("❌ Invalid export file format")
                sys.exit(1)
            
            info = data['collection_info']
            print(f"\n📊 Export Info:")
            print(f"  Collection: {info['name']}")
            print(f"  Export Date: {info['export_date']}")
            print(f"  Total Items: {info['total_items']}")
            print(f"  Embedding Model: {info['embedding_model']}")
            print(f"  Vector Dimension: {info['embedding_dimension']}")
            print(f"  Distance Metric: {info['distance_metric']}")
            
            return data
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            sys.exit(1)
    
    def create_collection(self, collection_name: str, vector_size: int, distance: str = "cosine"):
        """Create a new collection in Qdrant"""
        print(f"\n🔧 Creating collection: {collection_name}")
        
        # Map distance metric
        distance_map = {
            'cosine': Distance.COSINE,
            'euclidean': Distance.EUCLID,
            'dot': Distance.DOT
        }
        
        distance_metric = distance_map.get(distance.lower(), Distance.COSINE)
        
        try:
            # Check if collection already exists
            existing_collections = self.client.get_collections()
            collection_names = [c.name for c in existing_collections.collections]
            
            if collection_name in collection_names:
                print(f"⚠️  Collection '{collection_name}' already exists")
                response = input("Delete and recreate? (y/n): ").lower()
                if response == 'y':
                    self.client.delete_collection(collection_name)
                    print("🗑️  Deleted existing collection")
                else:
                    print("❌ Aborted. Please use a different collection name or delete manually.")
                    sys.exit(1)
            
            # Create new collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_metric
                )
            )
            print(f"✅ Collection created with {vector_size}D vectors and {distance} distance")
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            sys.exit(1)
    
    def import_vectors(self, collection_name: str, vectors_data: list, batch_size: int = 500):
        """Import vectors into Qdrant collection"""
        print(f"\n📤 Importing {len(vectors_data)} vectors...")
        print(f"  Batch size: {batch_size}")
        
        total = len(vectors_data)
        imported = 0
        errors = 0
        
        try:
            for i in range(0, total, batch_size):
                batch = vectors_data[i:i + batch_size]
                
                # Prepare points
                points = []
                for item in batch:
                    # Handle string IDs (Qdrant prefers them)
                    point_id = str(item['id']) if not isinstance(item['id'], str) else item['id']
                    
                    # Skip items without vectors
                    if item['vector'] is None:
                        print(f"⚠️  Skipping item {point_id}: no vector")
                        errors += 1
                        continue
                    
                    point = PointStruct(
                        id=point_id,
                        vector=item['vector'],
                        payload=item['payload']
                    )
                    points.append(point)
                
                # Upload batch
                if points:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    imported += len(points)
                
                # Progress update
                progress = min(i + batch_size, total)
                percentage = (progress / total) * 100
                print(f"  Progress: {progress}/{total} ({percentage:.1f}%)", end='\r')
            
            print(f"\n✅ Import complete!")
            print(f"  Successfully imported: {imported}")
            if errors > 0:
                print(f"  ⚠️  Errors/Skipped: {errors}")
            
        except Exception as e:
            print(f"\n❌ Error during import: {e}")
            print(f"  Imported {imported}/{total} vectors before error")
            sys.exit(1)
    
    def verify_import(self, collection_name: str, expected_count: int):
        """Verify that import was successful"""
        print(f"\n🔍 Verifying import...")
        
        try:
            collection_info = self.client.get_collection(collection_name)
            actual_count = collection_info.vectors_count
            
            print(f"  Expected: {expected_count} vectors")
            print(f"  Actual: {actual_count} vectors")
            
            if actual_count == expected_count:
                print("✅ Verification successful! Counts match.")
                return True
            else:
                print(f"⚠️  Warning: Count mismatch!")
                difference = abs(expected_count - actual_count)
                print(f"  Difference: {difference} vectors")
                return False
                
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False
    
    def test_search(self, collection_name: str):
        """Run a test search to verify functionality"""
        print(f"\n🔎 Running test search...")
        
        try:
            # Get a sample point to use as query
            scroll_result = self.client.scroll(
                collection_name=collection_name,
                limit=1
            )
            
            if not scroll_result[0]:
                print("⚠️  No vectors found for test search")
                return
            
            # Use the first vector as a test query
            test_vector = scroll_result[0][0].vector
            
            results = self.client.search(
                collection_name=collection_name,
                query_vector=test_vector,
                limit=3
            )
            
            print(f"✅ Search successful! Found {len(results)} results:")
            for idx, result in enumerate(results[:3], 1):
                doc_preview = result.payload.get('document', '')[:80]
                print(f"  {idx}. Score: {result.score:.4f}")
                print(f"     Doc: {doc_preview}...")
            
        except Exception as e:
            print(f"❌ Error during test search: {e}")


def main():
    """Main import function"""
    parser = argparse.ArgumentParser(
        description="Import ChromaDB export data into Qdrant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import from JSON file
  python import_to_qdrant.py --json-file exports/qdrant/20231215_120000/markdown_chunks_export_20231215_120000.json
  
  # Import from pickle file (faster for large datasets)
  python import_to_qdrant.py --json-file exports/qdrant/20231215_120000/markdown_chunks_export_20231215_120000.pkl
  
  # Import to Qdrant Cloud
  python import_to_qdrant.py --json-file export.json --url https://xyz.qdrant.io:6333 --api-key your-api-key
  
  # Custom collection name and batch size
  python import_to_qdrant.py --json-file export.json --collection my_docs --batch-size 1000
        """
    )
    
    parser.add_argument(
        '--json-file', '-f',
        required=True,
        help='Path to the export JSON or pickle file'
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:6333',
        help='Qdrant server URL (default: http://localhost:6333)'
    )
    
    parser.add_argument(
        '--api-key',
        help='Qdrant API key (for Qdrant Cloud)'
    )
    
    parser.add_argument(
        '--collection',
        help='Override collection name (uses name from export file if not specified)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=500,
        help='Batch size for uploads (default: 500)'
    )
    
    parser.add_argument(
        '--skip-verify',
        action='store_true',
        help='Skip verification step'
    )
    
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='Skip test search'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  ChromaDB to Qdrant Import Tool")
    print("=" * 70)
    
    # Initialize importer
    importer = QdrantImporter(qdrant_url=args.url, api_key=args.api_key)
    
    # Load export file
    export_data = importer.load_export_file(Path(args.json_file))
    
    # Determine collection name
    collection_name = args.collection or export_data['collection_info']['name']
    print(f"\n🎯 Target collection: {collection_name}")
    
    # Create collection
    importer.create_collection(
        collection_name=collection_name,
        vector_size=export_data['collection_info']['embedding_dimension'],
        distance=export_data['collection_info']['distance_metric']
    )
    
    # Import vectors
    importer.import_vectors(
        collection_name=collection_name,
        vectors_data=export_data['vectors'],
        batch_size=args.batch_size
    )
    
    # Verify import
    if not args.skip_verify:
        importer.verify_import(
            collection_name=collection_name,
            expected_count=export_data['collection_info']['total_items']
        )
    
    # Test search
    if not args.skip_test:
        importer.test_search(collection_name)
    
    # Success summary
    print("\n" + "=" * 70)
    print("  Import Complete! 🎉")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  Collection: {collection_name}")
    print(f"  Vectors: {export_data['collection_info']['total_items']}")
    print(f"  Qdrant URL: {args.url}")
    print("\n✅ Your ChromaDB data is now available in Qdrant!")
    print("\n💡 Next steps:")
    print("  1. Update your application to use Qdrant instead of ChromaDB")
    print("  2. Test queries with your actual use cases")
    print("  3. Monitor performance and adjust as needed")


if __name__ == "__main__":
    main()
