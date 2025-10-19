# Migration GUI Server Connection Support

## Update for ChromaDB Server URLs

The migration GUI has been updated to support **both** file-based and server-based ChromaDB connections.

### Using ChromaDB Server URL

1. **Start ChromaDB Server:**
```bash
docker-compose up -d
```

2. **In the Migration GUI:**
   - Go to "Export (Server 1)" tab
   - In the "ChromaDB Path" field, enter the server URL instead of a path:
     ```
     http://localhost:8000
     ```
   - Or for remote server:
     ```
     http://server-ip:8000
     ```

3. The GUI will automatically detect if you're using:
   - **File path** (starts with `/` or `~`) → Uses PersistentClient
   - **Server URL** (starts with `http://` or `https://`) → Uses HttpClient

### Quick Test

Test your ChromaDB server connection:

```bash
# Check if server is running
curl http://localhost:8000/api/v1/heartbeat

# Use diagnostic tool
./check_chromadb.sh http://localhost:8000
```

### Configuration File

You can also set the default in `~/.nerdbuntu_migration_config.json`:

```json
{
  "chromadb_path": "http://localhost:8000",
  "chromadb_host": "http://localhost:8000",
  ...
}
```

### Examples

**File-based (old way):**
```
/home/user/nerdbuntu/data/vector_db
~/nerdbuntu/data/vector_db
```

**Server-based (new way):**
```
http://localhost:8000
http://192.168.1.100:8000
https://chromadb-server.example.com
```

### Benefits of Server Mode

✅ **No zip/transfer needed** - Server 2 can connect directly to Server 1  
✅ **Real-time verification** - See data immediately  
✅ **Simpler workflow** - Direct network connection  
✅ **Better for large datasets** - No intermediate file creation

### For Your Two-Server Setup

**Server 1:**
```bash
# Start ChromaDB server
docker-compose up -d

# Allow connections from Server 2
# Edit docker-compose.yml:
ports:
  - "0.0.0.0:8000:8000"  # Bind to all interfaces
```

**Server 2:**
```bash
# Test connection
curl http://server1-ip:8000/api/v1/heartbeat

# Use in migration GUI
# ChromaDB Path: http://server1-ip:8000
```

The updated GUI code automatically handles both connection types!
