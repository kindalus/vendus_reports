# Upgrade to Version 0.1.0

## Changes Summary

This document summarizes the changes made to upgrade the project to version 0.1.0.

## Major Changes

### 1. UV-Enabled Project
- Converted from setuptools to hatchling build backend
- Added `uv.lock` for reproducible dependency management
- Updated build configuration in `pyproject.toml`
- Version changed from 1.0.0 to 0.1.0 to align with git tagging

### 2. Enhanced CLI Options

#### Global Options
- `--version`: Display version number aligned with git tags
- `--help` / `-h`: Show comprehensive help messages
- `--output DIR` / `-o DIR`: Specify output directory for all reports

#### Command-Specific Options
- Each subcommand (facturas, recibos, saft, impostos) supports `-o FILE` to override the global output directory
- Improved help text for all commands

### 3. Improved Functionality
- Automatic directory creation for output paths
- Console feedback when files are saved
- Better error handling and user messages
- Enhanced argument parsing with detailed descriptions

### 4. Git Tagging
- Created v0.1.0 git tag for version tracking
- Version in code (`__version__`) matches git tag

## Installation

### Using UV (Recommended)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/kindalus/vendus-reports
cd vendus-reports
uv sync
uv pip install -e .
```

### Using pip
```bash
git clone https://github.com/kindalus/vendus-reports
cd vendus-reports
pip install -e .
```

## Usage Examples

```bash
# Show version
vendus-reports --version

# Show help
vendus-reports --help
vendus-reports all --help

# Generate all reports with output directory
vendus-reports --output ./reports all 2024-01

# Generate specific report with custom filename
vendus-reports facturas 2024-01-01 2024-01-31 -o my_invoices.csv

# Use global output directory
vendus-reports --output /path/to/reports facturas 2024-01-01 2024-01-31
```

## Breaking Changes

None - all existing functionality remains backward compatible.

## Migration Guide

If you were using the old version:

1. Install uv (optional but recommended)
2. Run `uv sync` to update dependencies
3. Existing commands work as before
4. New options are available but not required

## Documentation Updates

- README.md now includes:
  - Quick start guide with uv
  - Detailed installation instructions
  - Enhanced command reference
  - Usage examples
  - Configuration guide
  - Development setup with uv

## Files Changed

- `pyproject.toml`: Updated build system to hatchling, version to 0.1.0
- `src/vendus_reports/cli.py`: Added --version, --help, --output options
- `README.md`: Comprehensive documentation updates
- `uv.lock`: New file for dependency locking
- Removed `requirements-dev.txt` (dependencies now in pyproject.toml)

## Testing

All new options have been tested:
- ✅ `--version` displays correct version
- ✅ `--help` shows comprehensive help
- ✅ `--output DIR` works for all commands
- ✅ `-o FILE` overrides work for individual commands
- ✅ Automatic directory creation works
- ✅ File save confirmations display correctly

## Next Steps

To push changes to remote:
```bash
git push origin main
git push origin v0.1.0
```
