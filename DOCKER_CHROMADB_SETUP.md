# Docker Setup for ChromaDB Server

This guide explains how to run ChromaDB as a server using Docker, making it accessible over HTTP for migrations and remote access.

## Quick Start

### **1. Start ChromaDB Server**

```bash
cd ~/nerdbuntu
docker-compose up -d
```

### **2. Verify It's Running**

```bash
# Check Docker container
docker-compose ps

# Test the API
curl http://localhost:8000/api/v1/heartbeat

# Check your data
./check_chromadb.sh http://localhost:8000
```

### **3. View Logs (if needed)**

```bash
docker-compose logs -f chromadb
```

---

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs chromadb

# Follow logs in real-time
docker-compose logs -f chromadb

# Check status
docker-compose ps

# Stop but keep data
docker-compose stop

# Remove containers (data is preserved in ./data/vector_db)
docker-compose down
```

---

## Configuration Details

### **Ports**

- **ChromaDB**: `http://localhost:8000`
  - HTTP API endpoint
  - Use this URL in migration tools and applications

### **Data Location**

Your existing ChromaDB data is mounted from:
```
./data/vector_db  →  /chroma/chroma (inside container)
```

This means:
- ✅ Your existing data is used
- ✅ All changes persist to your local filesystem
- ✅ Data survives container restarts/removals

### **Environment Variables**

Set in `docker-compose.yml`:
- `IS_PERSISTENT=TRUE` - Enables data persistence
- `ANONYMIZED_TELEMETRY=FALSE` - Disables telemetry

---

## Two-Server Migration Setup

### **Server 1 (ChromaDB)**

1. Start ChromaDB server:
```bash
cd ~/nerdbuntu
docker-compose up -d
```

2. Make it accessible from Server 2:
```bash
# Option A: Use SSH tunnel from Server 2
ssh -L 8000:localhost:8000 user@server1

# Option B: Bind to all interfaces (edit docker-compose.yml)
# Change ports to: "0.0.0.0:8000:8000"
```

3. Verify from Server 2:
```bash
curl http://server1-ip:8000/api/v1/heartbeat
./check_chromadb.sh http://server1-ip:8000
```

### **Server 2 (Qdrant)**

For Qdrant on Server 2, you can use Docker too:

```bash
# Create docker-compose.yml on Server 2
docker run -d \
  -p 6333:6333 \
  -p 6334:6334 \
  -v ~/qdrant_storage:/qdrant/storage \
  --name qdrant-server \
  qdrant/qdrant:latest
```

Or uncomment the Qdrant section in the provided `docker-compose.yml` if running both on one server.

---

## Network Access Configuration

### **Allow Remote Connections (Server 1)**

If Server 2 needs to connect directly to ChromaDB on Server 1:

**Option 1: Edit docker-compose.yml**
```yaml
services:
  chromadb:
    ports:
      - "0.0.0.0:8000:8000"  # Bind to all interfaces
```

**Option 2: Firewall Rules**
```bash
# Allow port 8000 from Server 2's IP
sudo ufw allow from SERVER2_IP to any port 8000

# Or allow from any IP (less secure)
sudo ufw allow 8000
```

**Security Note**: For production, use authentication:
```yaml
environment:
  - CHROMA_SERVER_AUTH_CREDENTIALS=your-secret-token
  - CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token.TokenAuthServerProvider
```

---

## Using ChromaDB Server in Your Applications

### **Migration GUI**

The migration GUI can now connect to ChromaDB server directly:

1. Add to your `.env`:
```bash
CHROMADB_HOST=http://localhost:8000
# Or for remote:
CHROMADB_HOST=http://server1-ip:8000
```

2. Or specify in the GUI when exporting

### **Python Applications**

```python
import chromadb

# Connect to server
client = chromadb.HttpClient(host='localhost', port=8000)

# Or with full URL
client = chromadb.HttpClient(host='http://localhost:8000')

# List collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")
```

---

## Troubleshooting

### **Port Already in Use**

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill the process or change the port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### **Can't See Data**

```bash
# Check if data directory exists
ls -la ~/nerdbuntu/data/vector_db/

# Check permissions
ls -ld ~/nerdbuntu/data/vector_db/

# Should be readable by your user
# If not, fix permissions:
chmod -R 755 ~/nerdbuntu/data/vector_db/
```

### **Container Won't Start**

```bash
# View detailed logs
docker-compose logs chromadb

# Check Docker status
docker-compose ps

# Try removing and recreating
docker-compose down
docker-compose up -d
```

### **Connection Refused from Remote Server**

```bash
# On Server 1, check if listening on all interfaces
docker-compose exec chromadb netstat -tulpn | grep 8000

# Check firewall
sudo ufw status

# Test from Server 1 first
curl http://localhost:8000/api/v1/heartbeat

# Then test from Server 2
curl http://server1-ip:8000/api/v1/heartbeat
```

---

## Data Backup and Migration

### **Backup Your Data**

```bash
# Stop container first
docker-compose stop

# Backup data directory
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz data/vector_db/

# Restart
docker-compose start
```

### **Restore Data**

```bash
# Stop container
docker-compose stop

# Restore backup
tar -xzf chromadb_backup_YYYYMMDD.tar.gz

# Start container
docker-compose start
```

### **Migrate to Different Server**

```bash
# On original server - backup
docker-compose stop
tar -czf chromadb_data.tar.gz data/vector_db/

# Transfer to new server
scp chromadb_data.tar.gz user@new-server:~/nerdbuntu/

# On new server - restore
cd ~/nerdbuntu
tar -xzf chromadb_data.tar.gz
docker-compose up -d
```

---

## Performance Optimization

### **Resource Limits**

Add to `docker-compose.yml`:
```yaml
services:
  chromadb:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
```

### **Persistent Volume for Better Performance**

Instead of bind mount, use Docker volume:
```yaml
volumes:
  - chromadb_data:/chroma/chroma

volumes:
  chromadb_data:
    driver: local
```

---

## Monitoring

### **Health Check**

Add to `docker-compose.yml`:
```yaml
services:
  chromadb:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Check Health**

```bash
docker-compose ps
# Should show "healthy" status
```

---

## Next Steps

1. ✅ Start ChromaDB server with docker-compose
2. ✅ Verify data is accessible
3. ✅ Update migration GUI to use server URL
4. ✅ Test connection from Server 2 (if applicable)
5. ✅ Run migration

**Key URLs:**
- ChromaDB Server: `http://localhost:8000`
- Diagnostic Check: `./check_chromadb.sh http://localhost:8000`
- API Documentation: `http://localhost:8000/docs` (when running)
