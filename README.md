# Vendus Reports

A Python CLI tool to generate invoicing, receipts, SAFT, and tax analysis reports from the Vendus API.

## Features

- **All Reports**: Generate all reports for a given month with a single command
- **Facturas (Invoicing)**: Generate detailed invoice reports with VAT calculations
- **Recibos (Receipts)**: Generate receipt reports with related document information
- **SAFT**: Generate SAFT XML reports for tax authorities
- **Impostos (Tax Analysis)**: Generate tax analysis reports grouped by tax rates

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install the project
git clone https://github.com/kindalus/vendus_reports
cd vendus_reports
uv sync
uv pip install -e .
```

### Using pip

```bash
git clone https://github.com/kindalus/vendus_reports
cd vendus_reports
pip install -e .
```

### Using pip (when published to PyPI)

```bash
pip install vendus-reports
```

## Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/kindalus/vendus_reports
cd vendus_reports
uv sync && uv pip install -e .

# Set your API key
export VENDUS_API_KEY="your_api_key_here"

# Generate all reports for previous month
vendus-reports all

# Show help
vendus-reports --help

# Show version
vendus-reports --version
```

## Configuration

### Required Environment Variables

Set your Vendus API key as an environment variable:

```bash
export VENDUS_API_KEY="your_api_key_here"
```

To make this permanent, add it to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export VENDUS_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Optional: Google Drive Archive Configuration

If you want to use the `--archive` option to automatically upload reports to Google Drive, set these environment variables:

| Variable                   | Description                                  | Required for --archive |
| -------------------------- | -------------------------------------------- | ---------------------- |
| `SERVICE_ACCOUNT_KEY_PATH` | Path to Google service account JSON key      | Yes                    |
| `ROOT_FOLDER_ID`           | Google Drive root folder ID for organization | Yes                    |
| `IMPERSONATED_EMAIL`       | Email for domain-wide delegation             | Yes                    |

```bash
export SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account-key.json"
export ROOT_FOLDER_ID="your_google_drive_folder_id"
export IMPERSONATED_EMAIL="user@yourdomain.com"
```

Files will be organized in Google Drive as: `[root folder]/[yyyy]/[yyyy-mm]/`

## Usage

The tool provides five main commands:

### All Reports (Recommended)

Generate all reports for a given month with a single command:

```bash
# Generate all reports for the previous month (automatic)
vendus-reports all

# Generate all reports for a specific month
vendus-reports all 2024-01

# Generate all reports with custom output directory
vendus-reports all 2024-01 -o /path/to/output/directory

# Generate and archive to Google Drive
vendus-reports --archive all 2024-01
```

This command will generate:

- `facturas-2024-01.csv` (invoicing report)
- `recibos-2024-01.csv` (receipts report)
- `saft-2024-01.xml` (SAFT XML report)
- `impostos-2024-01.csv` (tax analysis report)

**Date range**: Automatically calculates the first and last day of the specified month for date-range reports.

### Facturas (Invoicing Reports)

Generate invoice reports for a date range:

```bash
vendus-reports facturas 2024-01-01 2024-01-31
```

With custom output file:

```bash
vendus-reports facturas 2024-01-01 2024-01-31 -o invoices_january.csv
```

**Output format**: `facturas-YYYY-MM-DD-YYYY-MM-DD.csv`

**Columns**: DATA;NUMERO;CLIENTE;TOTAL;VALOR SUJEITO;VALOR ISENTO;IVA;OBS

### Recibos (Receipt Reports)

Generate receipt reports for a date range:

```bash
vendus-reports recibos 2024-01-01 2024-01-31
```

**Output format**: `recibos-YYYY-MM-DD-YYYY-MM-DD.csv`

**Columns**: DATA;NUMERO;CLIENTE;VALOR;OBS

### SAFT Reports

Generate SAFT XML reports for tax authorities:

```bash
vendus-reports saft 2024-01
```

**Output format**: `saft-YYYY-MM.xml`

### Impostos (Tax Analysis)

Generate tax analysis reports grouped by tax rates:

```bash
vendus-reports impostos 2024-01
```

**Output format**: `impostos-YYYY-MM.csv`

**Columns**: Taxa;# Documentos;IVA;Base Incidencia;Total

## Command Reference

### General Options

- `--version`: Show program version and exit
- `--help`, `-h`: Show help message and exit
- `--output DIR`, `-o DIR`: Output directory for generated reports (applies to all commands)
- `--archive`: Archive generated files to Google Drive (requires service account configuration)

### Command-Specific Options

Each subcommand (facturas, recibos, saft, impostos) supports:

- `-o FILE`, `--output FILE`: Specify custom output file path (overrides global --output directory)

### Date Formats

- **All command**: `YYYY-MM` format (optional, defaults to previous month)
- **Date range commands** (facturas, recibos): `YYYY-MM-DD` format
- **Monthly commands** (saft, impostos): `YYYY-MM` format

### Command Syntax

```bash
# Show version
vendus-reports --version

# Show help
vendus-reports --help
vendus-reports COMMAND --help

# All reports
vendus-reports [--output DIR] [--archive] all [YYYY-MM]

# Individual commands with global output directory
vendus-reports --output DIR facturas FROM_DATE TO_DATE
vendus-reports --output DIR recibos FROM_DATE TO_DATE
vendus-reports --output DIR saft YYYY-MM
vendus-reports --output DIR impostos YYYY-MM

# Individual commands with specific output file
vendus-reports facturas FROM_DATE TO_DATE -o OUTPUT_FILE
vendus-reports recibos FROM_DATE TO_DATE -o OUTPUT_FILE
vendus-reports saft YYYY-MM -o OUTPUT_FILE
vendus-reports impostos YYYY-MM -o OUTPUT_FILE

# Archive to Google Drive
vendus-reports --archive all 2024-01
vendus-reports --archive facturas 2024-01-01 2024-01-31
vendus-reports --archive saft 2024-01
```

## Examples

### Quick Start - Generate All Reports

```bash
# Set API key
export VENDUS_API_KEY="abc123xyz789"

# Generate all reports for previous month
vendus-reports all

# Generate all reports for January 2024
vendus-reports all 2024-01

# Generate all reports in a specific directory
vendus-reports all 2024-01 -o /home/user/reports/january/
```

### Individual Commands

```bash
# Generate specific reports for January 2024
vendus-reports facturas 2024-01-01 2024-01-31
vendus-reports recibos 2024-01-01 2024-01-31
vendus-reports saft 2024-01
vendus-reports impostos 2024-01

# Custom output files
vendus-reports facturas 2024-01-01 2024-01-31 -o january_invoices.csv
vendus-reports saft 2024-01 -o january_saft.xml
```

### Monthly Workflow

```bash
# Generate all reports for the current business cycle
vendus-reports all 2024-01  # January reports
vendus-reports all 2024-02  # February reports
vendus-reports all          # Previous month (automatic)
```

### Google Drive Archive Workflow

```bash
# Set up environment variables (one-time setup)
export VENDUS_API_KEY="your_api_key"
export SERVICE_ACCOUNT_KEY_PATH="/path/to/service-account.json"
export ROOT_FOLDER_ID="your_drive_folder_id"
export IMPERSONATED_EMAIL="user@yourdomain.com"

# Generate and archive all reports for a month
vendus-reports --archive all 2024-01

# Generate locally first, then archive individual reports
vendus-reports --output ./local-reports --archive all 2024-01

# Archive individual reports
vendus-reports --archive facturas 2024-01-01 2024-01-31
vendus-reports --archive saft 2024-01

# The files will be organized in Drive as:
# [ROOT_FOLDER_ID]/
#   └── 2024/
#       └── 2024-01/
#           ├── facturas-2024-01-01-2024-01-31.csv
#           ├── recibos-2024-01-01-2024-01-31.csv
#           ├── saft-2024-01.xml
#           └── impostos-2024-01.csv
```

### More Examples

See the `examples/` directory for comprehensive usage examples and integration patterns:

- `examples/generate_monthly_reports.py` - Interactive demonstration of all command features
- `examples/README.md` - Additional usage patterns and batch processing examples

## Output Files

### Using the `all` Command

When using the `all` command, files are automatically named with the month:

- Without output directory: Files created in current directory
  - `facturas-2024-01.csv`
  - `recibos-2024-01.csv`
  - `saft-2024-01.xml`
  - `impostos-2024-01.csv`

- With output directory (`-o /path/to/dir/`): Files created in specified directory
  - `/path/to/dir/facturas-2024-01.csv`
  - `/path/to/dir/recibos-2024-01.csv`
  - `/path/to/dir/saft-2024-01.xml`
  - `/path/to/dir/impostos-2024-01.csv`

### Using Individual Commands

When no output file is specified, individual commands generate filenames automatically:

- `facturas-2024-01-01-2024-01-31.csv`
- `recibos-2024-01-01-2024-01-31.csv`
- `saft-2024-01.xml`
- `impostos-2024-01.csv`

## Development

### Setup Development Environment

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone https://github.com/kindalus/vendus_reports
cd vendus_reports

# Install dependencies using uv
uv sync

# Install the package in editable mode with dev dependencies
uv pip install -e ".[dev]"
```

### Alternative Development Setup (using pip)

```bash
git clone https://github.com/kindalus/vendus_reports
cd vendus_reports
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vendus_reports

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

### Code Quality

#### Code Formatting

```bash
# Format code
black src/ tests/

# Check formatting without applying changes
black --check src/ tests/
```

#### Type Checking

```bash
# Run type checking
mypy src/

# Run type checking with verbose output
mypy --verbose src/
```

#### Linting

```bash
# Run flake8 linting
flake8 src/ tests/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before commits:

```bash
pre-commit install
pre-commit run --all-files
```

### Building Distribution

```bash
# Build source and wheel distributions
python -m build

# Check distribution
twine check dist/*

# Upload to PyPI (for maintainers)
twine upload dist/*
```

### Testing Different Python Versions

This package supports Python 3.8+. To test across versions:

```bash
# Using pyenv (install versions first)
pyenv local 3.8.18 3.9.18 3.10.13 3.11.7 3.12.1

# Using tox (if configured)
tox
```

## API Requirements

This tool requires access to the Vendus API with the following endpoints:

- `/documents/` - For invoicing and receipt data
- `/taxauthority/saft` - For SAFT XML generation

## Data Processing

### Tax Calculations

- **VAT Rate**: Automatically calculated from document amounts
- **Exempt Values**: Set to 0 if calculated value is less than 0.09
- **Credit Notes**: NC documents are processed as negative values
- **Tax Groups**: Simplified to 0% (exempt) and 14% (taxed)

### Data Formatting

- **Numbers**: Use comma as decimal separator (European format)
- **Dates**: Converted from YYYY-MM-DD to DD/MM/YYYY
- **Text**: Accents removed from observation fields
- **Currency**: Formatted to 2 decimal places

### Month Processing

The `all` command intelligently handles month calculations:

- **Previous Month**: If no month specified, automatically uses the previous month
- **Year Boundaries**: Correctly handles December → January transitions
- **Month Range**: Automatically calculates first and last day of the month for date-range reports
- **Leap Years**: Uses Python's `calendar` module for accurate month-end dates

## Error Handling

The tool provides comprehensive error handling:

- **API Key Validation**: Checks for required `VENDUS_API_KEY` environment variable
- **Date Validation**: Validates date formats and ranges
- **Month Validation**: Ensures months are between 1-12
- **File System**: Handles file creation and directory permissions
- **Network**: Graceful handling of API connection issues

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Changelog

### Version 0.2.0 (TBD)

- **New Feature**: Added `--archive` option to automatically upload reports to Google Drive
- **Integration**: Google Drive API integration with service account authentication
- **Feature**: Automatic folder structure creation in Google Drive: `[root]/[yyyy]/[yyyy-mm]/`
- **Enhancement**: All run functions now return file paths for archiving support
- **Dependency**: Added `google-auth` and `google-api-python-client` dependencies

### Version 0.1.0 (2025-11-03)

- **Project Structure**: Converted to uv-enabled project for faster, more reliable dependency management
- **New Feature**: Added `--version` option to display version aligned with git tags
- **Enhancement**: Added `--help` option with detailed command documentation
- **Enhancement**: Added global `--output DIR` option for specifying output directory across all commands
- **Enhancement**: Command-specific `-o FILE` option now overrides global output directory
- **Enhancement**: Automatic directory creation for output paths
- **Enhancement**: Improved console feedback with file save confirmations
- **Feature**: `all` command to generate all reports for a given month
- **Feature**: Automatic previous month calculation when no month specified
- **Feature**: Consistent file naming across all report types
