# Vendus Reports

A Python CLI tool to generate invoicing, receipts, SAFT, and tax analysis reports from the Vendus API.

## Features

- **Facturas (Invoicing)**: Generate detailed invoice reports with VAT calculations
- **Recibos (Receipts)**: Generate receipt reports with related document information
- **SAFT**: Generate SAFT XML reports for tax authorities
- **Impostos (Tax Analysis)**: Generate tax analysis reports grouped by tax rates

## Installation

### From Source

```bash
git clone https://github.com/kindalus/vendus-reports
cd vendus-reports
pip install -e .
```

### Using pip (when published)

```bash
pip install vendus-reports
```

## Configuration

Set your Vendus API key as an environment variable:

```bash
export VENDUS_API_KEY="your_api_key_here"
```

## Usage

The tool provides four main commands:

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

- `-o, --output`: Specify custom output file path
- `--help`: Show help message

### Date Formats

- **Date range commands** (facturas, recibos): `YYYY-MM-DD` format
- **Monthly commands** (saft, impostos): `YYYY-MM` format

## Examples

```bash
# Set API key
export VENDUS_API_KEY="abc123xyz789"

# Generate all reports for January 2024
vendus-reports facturas 2024-01-01 2024-01-31
vendus-reports recibos 2024-01-01 2024-01-31
vendus-reports saft 2024-01
vendus-reports impostos 2024-01

# Custom output files
vendus-reports facturas 2024-01-01 2024-01-31 -o january_invoices.csv
vendus-reports saft 2024-01 -o january_saft.xml
```

## Output Files

When no output file is specified, the tool automatically generates filenames:

- `facturas-2024-01-01-2024-01-31.csv`
- `recibos-2024-01-01-2024-01-31.csv`
- `saft-2024-01.xml`
- `impostos-2024-01.csv`

## Development

### Setup Development Environment

```bash
git clone https://github.com/kindalus/vendus-reports
cd vendus-reports
pip install -e .[dev]
```

### Alternative Development Setup

If you prefer using requirements files:

```bash
pip install -e .
pip install -r requirements-dev.txt
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

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open an issue on the GitHub repository.