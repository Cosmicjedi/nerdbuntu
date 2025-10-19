#!/usr/bin/env python3
"""
Export ChromaDB data to Qdrant-compatible format
Backs up all vectors, metadata, and documents for migration to Qdrant
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import pickle


class ChromaDBToQdrantExporter:
    """Export ChromaDB collections to Qdrant-compatible format"""
    
    def __init__(self, chroma_db_path, export_dir):
        self.chroma_db_path = Path(chroma_db_path)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        print(f"📂 Connecting to ChromaDB at: {self.chroma_db_path}")
        self.client = chromadb.PersistentClient(path=str(self.chroma_db_path))
        
        # Initialize embedding model (must match the one used in ChromaDB)
        print("🔧 Loading embedding model: all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def list_collections(self):
        """List all collections in ChromaDB"""
        collections = self.client.list_collections()
        print(f"\n📋 Found {len(collections)} collection(s):")
        for col in collections:
            print(f"  - {col.name}")
        return collections
    
    def export_collection(self, collection_name):
        """Export a single collection to JSON format"""
        print(f"\n🔄 Exporting collection: {collection_name}")
        
        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"❌ Error getting collection: {e}")
            return None
        
        # Get all data from collection
        print("  Fetching all data from collection...")
        try:
            # Get all items (ChromaDB uses limit parameter)
            all_data = collection.get(
                include=['embeddings', 'documents', 'metadatas']
            )
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
        
        total_items = len(all_data['ids'])
        print(f"  Found {total_items} items")
        
        if total_items == 0:
            print("  ⚠️  Collection is empty, skipping...")
            return None
        
        # Prepare export data structure
        export_data = {
            'collection_info': {
                'name': collection_name,
                'export_date': datetime.now().isoformat(),
                'total_items': total_items,
                'embedding_model': 'all-MiniLM-L6-v2',
                'embedding_dimension': 384,
                'distance_metric': 'cosine'
            },
            'vectors': []
        }
        
        # Process each item
        print("  Processing vectors...")
        for i in range(total_items):
            vector_data = {
                'id': all_data['ids'][i],
                'vector': all_data['embeddings'][i] if all_data['embeddings'] else None,
                'payload': {
                    'document': all_data['documents'][i] if all_data['documents'] else '',
                    'metadata': all_data['metadatas'][i] if all_data['metadatas'] else {}
                }
            }
            export_data['vectors'].append(vector_data)
            
            if (i + 1) % 100 == 0:
                print(f"    Processed {i + 1}/{total_items} vectors...")
        
        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = self.export_dir / f"{collection_name}_export_{timestamp}.json"
        
        print(f"  💾 Saving to: {json_filename}")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Create a compact binary backup as well (more efficient for large datasets)
        pickle_filename = self.export_dir / f"{collection_name}_export_{timestamp}.pkl"
        print(f"  💾 Creating binary backup: {pickle_filename}")
        with open(pickle_filename, 'wb') as f:
            pickle.dump(export_data, f)
        
        # Generate statistics
        stats = {
            'collection_name': collection_name,
            'total_vectors': total_items,
            'export_files': {
                'json': str(json_filename),
                'pickle': str(pickle_filename)
            },
            'file_sizes': {
                'json': f"{json_filename.stat().st_size / 1024 / 1024:.2f} MB",
                'pickle': f"{pickle_filename.stat().st_size / 1024 / 1024:.2f} MB"
            }
        }
        
        # Save statistics
        stats_filename = self.export_dir / f"{collection_name}_export_{timestamp}_stats.json"
        with open(stats_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"  ✅ Export complete!")
        print(f"     JSON: {stats['file_sizes']['json']}")
        print(f"     Binary: {stats['file_sizes']['pickle']}")
        
        return stats
    
    def export_all_collections(self):
        """Export all collections"""
        collections = self.list_collections()
        
        if not collections:
            print("\n⚠️  No collections found to export")
            return []
        
        results = []
        for collection in collections:
            stats = self.export_collection(collection.name)
            if stats:
                results.append(stats)
        
        return results
    
    def create_import_guide(self, export_stats):
        """Create a guide for importing into Qdrant"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        guide_filename = self.export_dir / f"QDRANT_IMPORT_GUIDE_{timestamp}.md"
        
        guide_content = f"""# Qdrant Import Guide

Export Date: {datetime.now().isoformat()}
Source: ChromaDB
Target: Qdrant Vector Database

## Export Summary

"""
        
        for stats in export_stats:
            guide_content += f"""### Collection: {stats['collection_name']}
- **Total Vectors**: {stats['total_vectors']:,}
- **JSON File**: `{Path(stats['export_files']['json']).name}`
- **Binary File**: `{Path(stats['export_files']['pickle']).name}`
- **JSON Size**: {stats['file_sizes']['json']}
- **Binary Size**: {stats['file_sizes']['pickle']}

"""
        
        guide_content += """## Prerequisites

Install required packages:

```bash
pip install qdrant-client sentence-transformers
```

## Import to Qdrant

### Option 1: Using the Import Script (Recommended)

```bash
python import_to_qdrant.py --json-file <export_file>.json --collection-name <collection_name>
```

### Option 2: Manual Import

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import json

# Initialize Qdrant client
client = QdrantClient(url="http://localhost:6333")  # or your Qdrant URL

# Load export data
with open("markdown_chunks_export_TIMESTAMP.json", 'r') as f:
    data = json.load(f)

# Create collection
collection_name = data['collection_info']['name']
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=data['collection_info']['embedding_dimension'],
        distance=Distance.COSINE
    )
)

# Prepare points for upload
points = []
for item in data['vectors']:
    point = PointStruct(
        id=item['id'],
        vector=item['vector'],
        payload=item['payload']
    )
    points.append(point)

# Upload in batches (Qdrant recommends batch size of 100-1000)
batch_size = 500
for i in range(0, len(points), batch_size):
    batch = points[i:i + batch_size]
    client.upsert(
        collection_name=collection_name,
        points=batch
    )
    print(f"Uploaded {i + len(batch)}/{len(points)} points")

print("Import complete!")
```

## Verify Import

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Check collection info
collection_info = client.get_collection(collection_name="markdown_chunks")
print(f"Vectors count: {collection_info.vectors_count}")

# Test search
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_vector = model.encode("your test query").tolist()

results = client.search(
    collection_name="markdown_chunks",
    query_vector=query_vector,
    limit=5
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Document: {result.payload['document'][:100]}...")
    print("---")
```

## Important Notes

1. **Embedding Model**: The vectors were created with `all-MiniLM-L6-v2` (384 dimensions)
   - You must use the same model for queries
   - Dimension size: 384
   - Distance metric: Cosine similarity

2. **Data Format**:
   - Each vector has an ID, embedding vector, and payload
   - Payload contains the original document text and metadata
   - IDs are strings in format: `{filename}_chunk_{number}`

3. **Performance Tips**:
   - Use batch uploads (500-1000 points per batch)
   - Consider using Qdrant's async client for faster uploads
   - Monitor memory usage during large imports

4. **Qdrant Setup**:
   - Default Qdrant runs on port 6333
   - For production, consider using Qdrant Cloud or Docker deployment
   - Configure persistent storage for your collections

## Troubleshooting

**Issue: "Collection already exists"**
```python
client.delete_collection(collection_name="markdown_chunks")
# Then recreate and import
```

**Issue: "Vector dimension mismatch"**
- Ensure you're using `all-MiniLM-L6-v2` model (384 dimensions)
- Check that collection was created with correct vector size

**Issue: "Out of memory during import"**
- Reduce batch size to 100-200 points
- Process in multiple sessions
- Increase available memory for Qdrant

## Next Steps

1. Set up Qdrant (Docker or Cloud)
2. Run the import script
3. Verify the import
4. Update your application to use Qdrant instead of ChromaDB
5. Test queries to ensure results match expectations

## Migration Checklist

- [ ] Qdrant installed and running
- [ ] Export files copied to destination
- [ ] Collections created in Qdrant
- [ ] Vectors imported successfully
- [ ] Verified vector counts match
- [ ] Test queries return expected results
- [ ] Application updated to use Qdrant
- [ ] Old ChromaDB backup created
- [ ] Performance tested

## Support

For issues with:
- **Nerdbuntu**: https://github.com/Cosmicjedi/nerdbuntu/issues
- **Qdrant**: https://qdrant.tech/documentation/
- **ChromaDB Export**: Check export logs and stats files

---

Generated by: ChromaDB to Qdrant Exporter
Date: {datetime.now().isoformat()}
"""
        
        with open(guide_filename, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"\n📖 Import guide created: {guide_filename}")
        return guide_filename


def main():
    """Main export function"""
    print("=" * 60)
    print("  ChromaDB to Qdrant Export Tool")
    print("=" * 60)
    
    # Default paths
    project_dir = Path.home() / "nerdbuntu"
    chroma_db_path = project_dir / "data" / "vector_db"
    export_dir = project_dir / "exports" / "qdrant" / datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Check if ChromaDB exists
    if not chroma_db_path.exists():
        print(f"\n❌ ChromaDB not found at: {chroma_db_path}")
        print("Please ensure you have processed some documents first.")
        sys.exit(1)
    
    # Initialize exporter
    exporter = ChromaDBToQdrantExporter(chroma_db_path, export_dir)
    
    # Export all collections
    print("\n" + "=" * 60)
    print("  Starting Export")
    print("=" * 60)
    
    export_stats = exporter.export_all_collections()
    
    if not export_stats:
        print("\n⚠️  No data exported")
        sys.exit(0)
    
    # Create import guide
    print("\n" + "=" * 60)
    print("  Creating Import Guide")
    print("=" * 60)
    
    guide_file = exporter.create_import_guide(export_stats)
    
    # Summary
    print("\n" + "=" * 60)
    print("  Export Complete! 🎉")
    print("=" * 60)
    print(f"\n📁 Export directory: {export_dir}")
    print(f"\n📊 Exported Collections:")
    
    total_vectors = 0
    for stats in export_stats:
        print(f"  - {stats['collection_name']}: {stats['total_vectors']:,} vectors")
        total_vectors += stats['total_vectors']
    
    print(f"\n📈 Total vectors exported: {total_vectors:,}")
    print(f"\n📖 Import guide: {guide_file.name}")
    
    print("\n" + "=" * 60)
    print("  Next Steps:")
    print("=" * 60)
    print(f"  1. Review the import guide: {guide_file}")
    print(f"  2. Set up Qdrant on your destination system")
    print(f"  3. Use import_to_qdrant.py to import the data")
    print(f"  4. Verify the import with test queries")
    print("\n✅ Backup ready for Qdrant migration!")


if __name__ == "__main__":
    main()
