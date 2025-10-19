#!/usr/bin/env python3
"""
ChromaDB Diagnostic Script
Check what data exists in your ChromaDB before migration
Supports both file-based and server-based ChromaDB
"""

import sys
from pathlib import Path
from datetime import datetime

def check_chromadb(connection_string=None):
    """Check ChromaDB contents and display statistics
    
    Args:
        connection_string: Either a file path or server URL (http://host:port)
    """
    
    # Try to import chromadb
    try:
        import chromadb
        print("✅ ChromaDB library found")
    except ImportError:
        print("❌ ChromaDB not installed")
        print("\nInstall with: pip install chromadb")
        return False
    
    # Determine if we're using server or file-based connection
    is_server = False
    if connection_string and (connection_string.startswith('http://') or connection_string.startswith('https://')):
        is_server = True
        print(f"🌐 Connecting to ChromaDB server: {connection_string}")
    elif connection_string:
        # File path specified
        db_path = Path(connection_string)
        if not db_path.exists():
            print(f"❌ Path does not exist: {db_path}")
            return False
        print(f"📂 Using ChromaDB path: {db_path.absolute()}")
    else:
        # Auto-detect file path
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
                    elif line.startswith("CHROMADB_HOST="):
                        # Support server configuration in .env
                        host = line.split("=", 1)[1].strip()
                        if host.startswith('http'):
                            connection_string = host
                            is_server = True
                            print(f"🌐 Using ChromaDB server from .env: {connection_string}")
                            break
        
        if not is_server:
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
                print("\nUsage:")
                print("  ./check_chromadb.sh /path/to/vector_db    # File-based")
                print("  ./check_chromadb.sh http://localhost:8000 # Server-based")
                return False
            
            print(f"📂 Using ChromaDB path: {db_path.absolute()}")
    
    print()
    
    # Connect to ChromaDB
    try:
        if is_server:
            # Server connection
            client = chromadb.HttpClient(host=connection_string)
            print("✅ Connected to ChromaDB server successfully")
        else:
            # File-based connection
            client = chromadb.PersistentClient(path=str(db_path))
            print("✅ Connected to ChromaDB successfully")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        if is_server:
            print("\n💡 Tips for server connection:")
            print("  - Ensure ChromaDB server is running")
            print("  - Check the URL and port are correct")
            print("  - Try: docker ps | grep chromadb")
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
        if is_server:
            print(f"  Connection: Server ({connection_string})")
        else:
            print(f"  Connection: File-based ({db_path.absolute()})")
        print()
        
        if total_vectors > 0:
            print("✅ ChromaDB contains data and is ready for migration!")
            print()
            print("Next steps:")
            print("  1. Run the migration GUI: ./launch_migration_gui.sh")
            print("  2. Use the 'Export (Server 1)' tab")
            if is_server:
                print(f"  3. Use server URL: {connection_string}")
            else:
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
    
    connection_string = None
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
        if connection_string.startswith('http'):
            print(f"Using ChromaDB server: {connection_string}")
        else:
            print(f"Using specified path: {connection_string}")
    else:
        print("Auto-detecting ChromaDB location...")
    
    print()
    
    success = check_chromadb(connection_string)
    
    print()
    if not success:
        print("💡 Usage:")
        print("  ./check_chromadb.sh                          # Auto-detect")
        print("  ./check_chromadb.sh /path/to/vector_db       # File-based")
        print("  ./check_chromadb.sh http://localhost:8000    # Server-based")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
