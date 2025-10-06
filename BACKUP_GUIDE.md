# Backup & Restore Quick Reference

## Overview

The `backup_restore.sh` script provides complete backup and restoration of your Nerdbuntu RAG data, including all processed markdown files and the ChromaDB vector database.

## Quick Commands

### Create a Backup
```bash
cd ~/nerdbuntu
./backup_restore.sh backup
```

### Restore from Backup
```bash
./backup_restore.sh restore ~/nerdbuntu/exports/nerdbuntu_backup_*.zip
```

## Backup Details

### What Gets Backed Up
- ✅ All processed markdown files (`data/output/`)
- ✅ Complete ChromaDB vector database (`data/vector_db/`)
- ✅ Backup metadata with timestamp
- ✅ Restore instructions

### Backup Location
`~/nerdbuntu/exports/nerdbuntu_backup_YYYYMMDD_HHMMSS.zip`

Example: `nerdbuntu_backup_20251006_143022.zip`

### Backup Contents
```
nerdbuntu_backup_20251006_143022/
├── markdown/           # All .md files with semantic metadata
├── vector_db/         # Complete ChromaDB database
├── BACKUP_INFO.txt    # Backup metadata
└── RESTORE_README.md  # Detailed restore instructions
```

## Restore Modes

### 1. Merge Mode (Recommended - Safe)
- **What it does:** Adds backup data to existing data
- **Safe:** Won't delete anything
- **Use case:** Combining multiple backups, adding old data
- **Choose:** Option 1

### 2. Replace Mode (Careful - Destructive)
- **What it does:** Deletes ALL existing data, then restores
- **Dangerous:** Permanent deletion of current data
- **Use case:** Clean restore, disaster recovery
- **Choose:** Option 2
- **Confirmation:** Must type "DELETE" to proceed

## Common Scenarios

### Regular Backups
```bash
# Create daily/weekly backups
./backup_restore.sh backup

# Backups are automatically timestamped
ls ~/nerdbuntu/exports/
# nerdbuntu_backup_20251006_120000.zip
# nerdbuntu_backup_20251007_120000.zip
```

### Move Data Between Machines
```bash
# Machine A (processing machine)
cd ~/nerdbuntu
./backup_restore.sh backup

# Transfer file
scp ~/nerdbuntu/exports/nerdbuntu_backup_*.zip user@machineB:~/

# Machine B (RAG server)
./backup_restore.sh restore ~/nerdbuntu_backup_*.zip
# Choose: Merge (1)
```

### Combine Multiple Backups
```bash
# Restore first backup
./backup_restore.sh restore backup_monday.zip
# Choose: Merge (1)

# Add second backup
./backup_restore.sh restore backup_tuesday.zip
# Choose: Merge (1)

# Now you have all data from both backups!
```

### Disaster Recovery
```bash
# If your data is corrupted/lost
./backup_restore.sh restore ~/safe-storage/last_good_backup.zip
# Choose: Replace (2)
# Type: DELETE
# Your data is now restored to the backup state
```

### Test Restore (Safe)
```bash
# Test a backup without affecting current data
# Create a test directory
mkdir ~/test_restore
cd ~/test_restore

# Extract backup manually
unzip ~/nerdbuntu/exports/backup.zip

# Verify contents
ls -la nerdbuntu_backup_*/markdown/
ls -la nerdbuntu_backup_*/vector_db/
```

## Transport Methods

### Local Network (SCP)
```bash
scp ~/nerdbuntu/exports/backup.zip user@destination:/path/
```

### Cloud Storage (AWS S3)
```bash
aws s3 cp ~/nerdbuntu/exports/backup.zip s3://my-bucket/backups/
```

### Cloud Storage (Google Cloud)
```bash
gsutil cp ~/nerdbuntu/exports/backup.zip gs://my-bucket/backups/
```

### USB/External Drive
```bash
cp ~/nerdbuntu/exports/backup.zip /media/usb/nerdbuntu-backups/
```

### Network Share
```bash
cp ~/nerdbuntu/exports/backup.zip /mnt/nas/backups/
```

## Verification

### After Backup
```bash
# Verify backup was created
ls -lh ~/nerdbuntu/exports/

# Test backup integrity
unzip -t ~/nerdbuntu/exports/nerdbuntu_backup_*.zip
```

### After Restore
```bash
# Verify files were restored
ls ~/nerdbuntu/data/output/
ls ~/nerdbuntu/data/vector_db/

# Test with a query
source ~/nerdbuntu/venv/bin/activate
python examples.py query "test"

# Check restore info
cat ~/nerdbuntu/LAST_RESTORE_INFO.txt
```

## Automation

### Automated Daily Backup (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd ~/nerdbuntu && ./backup_restore.sh backup

# Or with logging
0 2 * * * cd ~/nerdbuntu && ./backup_restore.sh backup >> ~/nerdbuntu/backup.log 2>&1
```

### Automated Cleanup (Keep Last 7 Backups)
```bash
# Create cleanup script
cat > ~/nerdbuntu/cleanup_old_backups.sh << 'EOF'
#!/bin/bash
cd ~/nerdbuntu/exports
ls -t nerdbuntu_backup_*.zip | tail -n +8 | xargs rm -f
EOF

chmod +x ~/nerdbuntu/cleanup_old_backups.sh

# Run weekly
crontab -e
# Add: 0 3 * * 0 ~/nerdbuntu/cleanup_old_backups.sh
```

## Troubleshooting

### Backup Issues

**Issue:** "No files found in output directory"
```bash
# Solution: Process some PDFs first
python app.py
# Then create backup
./backup_restore.sh backup
```

**Issue:** Backup is very large
```bash
# Check what's consuming space
du -sh ~/nerdbuntu/data/output/
du -sh ~/nerdbuntu/data/vector_db/

# The vector database grows with more documents
# This is normal and expected
```

### Restore Issues

**Issue:** "Archive not found"
```bash
# Verify file path
ls -l ~/path/to/backup.zip

# Use absolute path
./backup_restore.sh restore ~/nerdbuntu/exports/backup.zip
```

**Issue:** "Collection not found" after restore
```bash
# Verify database files were restored
ls ~/nerdbuntu/data/vector_db/

# If empty, try restore again with Replace mode
./backup_restore.sh restore backup.zip
# Choose: Replace (2)
```

**Issue:** Database seems corrupted
```bash
# Clean restore
./backup_restore.sh restore backup.zip
# Choose: Replace (2)
# Type: DELETE
```

## Best Practices

### 1. Regular Backups
- Create backups after processing important documents
- Set up automated daily/weekly backups
- Keep multiple backup versions

### 2. Off-site Storage
- Store backups on different machines
- Use cloud storage for critical data
- Keep at least one backup off-site

### 3. Test Restores
- Periodically test that backups can be restored
- Verify data integrity after restore
- Keep backup restore procedures documented

### 4. Backup Retention
- Keep daily backups for 1 week
- Keep weekly backups for 1 month
- Keep monthly backups for 1 year
- Adjust based on your data importance

### 5. Before Major Changes
- Always create a backup before:
  - Updating Nerdbuntu
  - Bulk processing many files
  - Changing configurations
  - System maintenance

## Storage Requirements

### Backup Size Estimation
- **Markdown files:** ~1-5KB per page (text)
- **Vector database:** ~1-2MB per 100 pages
- **Example:** 1000-page PDF → ~10-20MB markdown + ~20-40MB database = ~30-60MB backup

### Storage Recommendations
- Local storage: 1-5 backups (recent)
- Cloud storage: 10-20 backups (historical)
- Archive storage: Unlimited (long-term)

## Quick Reference Table

| Command | Action | Destructive? | Use Case |
|---------|--------|--------------|----------|
| `backup` | Create new backup | No | Regular backups |
| `restore` (Merge) | Add to existing | No | Combine data |
| `restore` (Replace) | Delete & restore | **YES** | Clean restore |

## Need Help?

- **Documentation:** README.md
- **Issues:** https://github.com/Cosmicjedi/nerdbuntu/issues
- **Discussions:** https://github.com/Cosmicjedi/nerdbuntu/discussions

---

**Remember: Backups are only useful if you can restore them! Test your backups regularly! 💾**
