# Release Notes - Version 0.2.0

**Release Date:** 2025-11-03

## Overview

Version 0.2.0 introduces Google Drive integration, allowing automatic archiving of generated reports to Google Drive with organized folder structures.

## 🎉 New Features

### Google Drive Archive (`--archive` flag)

Archive generated reports directly to Google Drive with a single flag:

```bash
vendus-reports --archive all 2024-01
```

**Key Features:**
- Automatic folder structure creation: `[root]/[yyyy]/[yyyy-mm]/`
- Works with all commands: `all`, `facturas`, `recibos`, `saft`, `impostos`
- Service account authentication with domain-wide delegation
- Automatic file type detection (CSV, XML)
- Progress feedback during upload

### Environment Variables

Three new environment variables for Google Drive integration:

| Variable | Description | Required |
|----------|-------------|----------|
| `SERVICE_ACCOUNT_KEY_PATH` | Path to Google service account JSON key | Yes |
| `ROOT_FOLDER_ID` | Google Drive root folder ID | Yes |
| `IMPERSONATED_EMAIL` | Email for domain-wide delegation | Yes |

## 📦 Dependencies

New dependencies added:
- `google-auth>=2.0.0`
- `google-api-python-client>=2.0.0`

Total new packages installed: 15

## 🔧 Technical Changes

### New Module
- `src/vendus_reports/google_drive.py` - Complete Google Drive API integration

### Modified Functions
- All `run_*` functions now return absolute file paths
- `run_all()` returns tuple of `(year_month, file_paths)`
- `main()` handles archive flag and coordinates file uploads

### API Integration
- Service account authentication
- Domain-wide delegation support
- Automatic folder creation/retrieval
- File upload with proper MIME types

## 📚 Documentation

### README Updates
- Google Drive configuration section
- Environment variables table
- Archive workflow examples
- Updated command syntax
- Real-world usage examples

### Examples

```bash
# Generate and archive all reports
vendus-reports --archive all 2024-01

# Archive with custom output directory
vendus-reports --output ./backup --archive all 2024-01

# Archive individual reports
vendus-reports --archive facturas 2024-01-01 2024-01-31
vendus-reports --archive saft 2024-01
```

## 🗂️ Folder Organization

Files are automatically organized in Google Drive:

```
[ROOT_FOLDER_ID]/
  └── 2024/
      └── 2024-01/
          ├── facturas-2024-01-01-2024-01-31.csv
          ├── recibos-2024-01-01-2024-01-31.csv
          ├── saft-2024-01.xml
          └── impostos-2024-01.csv
```

## ⚙️ Setup Instructions

1. **Set up Google Cloud Service Account:**
   - Create a service account in Google Cloud Console
   - Enable Google Drive API
   - Download JSON key file
   - Set up domain-wide delegation (if needed)

2. **Configure Environment Variables:**
   ```bash
   export VENDUS_API_KEY="your_api_key"
   export SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account.json"
   export ROOT_FOLDER_ID="your_drive_folder_id"
   export IMPERSONATED_EMAIL="user@yourdomain.com"
   ```

3. **Use the Archive Feature:**
   ```bash
   vendus-reports --archive all 2024-01
   ```

## 🧪 Testing

All features tested and verified:
- ✅ `--archive` flag recognized by CLI
- ✅ Help text displays correctly
- ✅ Google Drive module imports successfully
- ✅ Version command shows 0.2.0
- ✅ All dependencies installed correctly

## 🔄 Migration from v0.1.0

No breaking changes. The `--archive` flag is completely optional:

- **Without `--archive`**: Works exactly as v0.1.0
- **With `--archive`**: Adds Google Drive upload functionality

Existing scripts and commands continue to work without modification.

## 📋 Complete Changelog

- **New Feature**: Added `--archive` option to automatically upload reports to Google Drive
- **Integration**: Google Drive API integration with service account authentication
- **Feature**: Automatic folder structure creation in Google Drive: `[root]/[yyyy]/[yyyy-mm]/`
- **Enhancement**: All run functions now return file paths for archiving support
- **Dependency**: Added `google-auth` and `google-api-python-client` dependencies

## 🚀 Next Steps

To push changes to remote:

```bash
git push origin main
git push origin v0.2.0
```

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/kindalus/vendus_reports/issues
- Repository: https://github.com/kindalus/vendus_reports

---

**Full Changelog:** v0.1.0...v0.2.0
