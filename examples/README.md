# Examples

This directory contains example scripts and usage patterns for the Vendus Reports CLI tool.

## Files

### `generate_monthly_reports.py`

A comprehensive example script that demonstrates how to use the new "all" command functionality. This script shows:

- How to check for the required API key
- Different ways to use the `all` command
- Error handling and output interpretation
- Best practices for batch report generation

#### Usage

```bash
# Make sure your API key is set
export VENDUS_API_KEY="your_api_key_here"

# Run the example script
python examples/generate_monthly_reports.py
```

#### What it demonstrates

1. **Automatic previous month**: `vendus-reports all`
2. **Specific month**: `vendus-reports all 2024-01`
3. **Custom output directory**: `vendus-reports all 2024-01 -o /path/to/output`
4. **Help information**: `vendus-reports all --help`

## Common Usage Patterns

### Monthly Business Cycle

Generate reports for your monthly business cycle:

```bash
# Generate all reports for the previous month (most common)
vendus-reports all

# Generate reports for a specific month
vendus-reports all 2024-01

# Generate with organized output
mkdir -p ~/reports/2024-01
vendus-reports all 2024-01 -o ~/reports/2024-01
```

### Batch Processing Multiple Months

```bash
#!/bin/bash
# Generate reports for multiple months
for month in 2024-01 2024-02 2024-03; do
    echo "Generating reports for $month..."
    mkdir -p ~/reports/$month
    vendus-reports all $month -o ~/reports/$month
done
```

### Integration with Scripts

```python
import subprocess
import os

def generate_reports(year_month, output_dir=None):
    """Generate all Vendus reports for a given month."""
    cmd = ["vendus-reports", "all", year_month]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cmd.extend(["-o", output_dir])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

## Prerequisites

Before running any examples:

1. **Install the package**:
   ```bash
   pip install vendus-reports
   ```

2. **Set your API key**:
   ```bash
   export VENDUS_API_KEY="your_api_key_here"
   ```

3. **Verify installation**:
   ```bash
   vendus-reports --help
   ```

## Expected Output Files

When successful, the `all` command generates these files:

- `facturas-YYYY-MM.csv` - Invoicing report
- `recibos-YYYY-MM.csv` - Receipts report
- `saft-YYYY-MM.xml` - SAFT XML for tax authorities
- `impostos-YYYY-MM.csv` - Tax analysis by rates

## Error Handling

Common errors and solutions:

- **Missing API key**: Set `VENDUS_API_KEY` environment variable
- **Invalid month format**: Use `YYYY-MM` format (e.g., `2024-01`)
- **Permission errors**: Ensure write access to output directory
- **Network errors**: Check internet connection and API availability

## Contributing

Feel free to add more examples that demonstrate useful patterns or integration scenarios.
