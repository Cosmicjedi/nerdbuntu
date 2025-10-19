#!/usr/bin/env python3
"""
ChromaDB Diagnostic Script
Check what data exists in your ChromaDB before migration
"""

import sys
from pathlib import Path
from datetime import datetime

def check_chromadb(db_path=None):
    """Check ChromaDB contents and display statistics"""
    
    # Try to import chromadb
    try:
        import chromadb
        print("✅ ChromaDB library found")
    except ImportError:
        print("❌ ChromaDB not installed")
        print("\nInstall with: pip install chromadb")
        return False
    
    # Determine database path
    if db_path is None:
        # Try default locations
        possible_paths = [
            Path.home() / "nerdbuntu" / "data" / "vector_db",
            Path("data") / "vector_db",
            Path("vector_db"),
        ]
        
        # Also check .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("VECTOR_DB_DIR="):
                        env_path = line.split("=", 1)[1].strip()
                        possible_paths.insert(0, Path(env_path))
        
        db_path = None
        for path in possible_paths:
            if path.exists():
                db_path = path
                break
        
        if db_path is None:
            print("❌ Could not find ChromaDB directory")
            print("\nSearched in:")
            for path in possible_paths:
                print(f"  - {path}")
            print("\nSpecify path with: python check_chromadb.py /path/to/vector_db")
            return False
    else:
        db_path = Path(db_path)
        if not db_path.exists():
            print(f"❌ Path does not exist: {db_path}")
            return False
    
    print(f"📂 Using ChromaDB path: {db_path.absolute()}")
    print()
    
    # Connect to ChromaDB
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        print("✅ Connected to ChromaDB successfully")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        return False
    
    print()
    print("=" * 70)
    print("CHROMADB CONTENTS")
    print("=" * 70)
    print()
    
    # List all collections
    try:
        collections = client.list_collections()
        
        if not collections:
            print("⚠️  NO COLLECTIONS FOUND")
            print()
            print("This means ChromaDB is empty. Possible reasons:")
            print("  1. You haven't processed any documents yet")
            print("  2. Documents were processed to a different location")
            print("  3. The database was cleared")
            print()
            print("To add data, process documents using the GUI or:")
            print("  python3 examples.py batch data/input data/output")
            return False
        
        print(f"📊 Found {len(collections)} collection(s)\n")
        
        total_vectors = 0
        
        for i, collection in enumerate(collections, 1):
            print(f"\n{'─' * 70}")
            print(f"Collection #{i}: {collection.name}")
            print(f"{'─' * 70}")
            
            # Get collection data
            col = client.get_collection(collection.name)
            
            # Get count
            count = col.count()
            total_vectors += count
            print(f"  📈 Total items: {count}")
            
            if count == 0:
                print("  ⚠️  Collection is empty!")
                continue
            
            # Get sample data
            try:
                sample = col.get(limit=5, include=['embeddings', 'documents', 'metadatas'])
                
                print(f"  📝 Sample data:")
                
                for j, doc_id in enumerate(sample['ids'][:3], 1):
                    print(f"\n    Item {j}:")
                    print(f"      ID: {doc_id}")
                    
                    # Show metadata
                    if sample['metadatas'] and j-1 < len(sample['metadatas']):
                        metadata = sample['metadatas'][j-1]
                        if metadata:
                            print(f"      Metadata: {metadata}")
                    
                    # Show document preview
                    if sample['documents'] and j-1 < len(sample['documents']):
                        doc = sample['documents'][j-1]
                        if doc:
                            preview = doc[:150].replace('\n', ' ')
                            print(f"      Document: {preview}...")
                    
                    # Check if embeddings exist
                    if sample['embeddings'] and j-1 < len(sample['embeddings']):
                        embedding = sample['embeddings'][j-1]
                        if embedding:
                            print(f"      Embedding: Vector of dimension {len(embedding)}")
                        else:
                            print(f"      ⚠️  No embedding found!")
                
                if count > 3:
                    print(f"\n    ... and {count - 3} more items")
                    
            except Exception as e:
                print(f"  ❌ Error getting sample data: {e}")
        
        print()
        print("=" * 70)
        print(f"📊 SUMMARY")
        print("=" * 70)
        print(f"  Total Collections: {len(collections)}")
        print(f"  Total Vectors: {total_vectors}")
        print()
        
        if total_vectors > 0:
            print("✅ ChromaDB contains data and is ready for migration!")
            print()
            print("Next steps:")
            print("  1. Run the migration GUI: ./launch_migration_gui.sh")
            print("  2. Use the 'Export (Server 1)' tab")
            print(f"  3. ChromaDB path: {db_path.absolute()}")
        else:
            print("⚠️  Collections exist but contain no data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print()
    print("=" * 70)
    print("CHROMADB DIAGNOSTIC TOOL")
    print("=" * 70)
    print()
    
    db_path = None
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        print(f"Using specified path: {db_path}")
    else:
        print("Searching for ChromaDB in default locations...")
    
    print()
    
    success = check_chromadb(db_path)
    
    print()
    if not success:
        print("💡 Usage:")
        print("  python3 check_chromadb.py                    # Auto-detect path")
        print("  python3 check_chromadb.py /path/to/vector_db # Specify path")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
