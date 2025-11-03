#!/usr/bin/env python3
"""
Example script demonstrating how to use the new "all" command functionality.

This script shows different ways to generate all reports for a given month
using the vendus-reports CLI tool.
"""

import os
import subprocess
import sys
from datetime import datetime


def check_api_key():
    """Check if the VENDUS_API_KEY environment variable is set."""
    api_key = os.getenv('VENDUS_API_KEY')
    if not api_key:
        print("❌ Error: VENDUS_API_KEY environment variable is not set")
        print("Please set it with: export VENDUS_API_KEY='your_api_key_here'")
        return False
    print("✅ VENDUS_API_KEY environment variable is set")
    return True


def run_command(command):
    """Run a CLI command and display the output."""
    print(f"🔄 Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("✅ Command completed successfully")
        if result.stdout:
            print("Output:", result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stderr:
            print("Error:", e.stderr.strip())
        return False
    except FileNotFoundError:
        print("❌ vendus-reports command not found. Please install the package first.")
        return False


def main():
    """Demonstrate the new 'all' command functionality."""
    print("=== Vendus Reports - 'all' Command Examples ===\n")

    # Check prerequisites
    if not check_api_key():
        sys.exit(1)

    print("\n=== Example 1: Generate all reports for previous month (automatic) ===")
    print("This will automatically use the previous month")
    success = run_command(["vendus-reports", "all"])
    if not success:
        print("Note: This is expected to fail without a valid API key\n")

    print("\n=== Example 2: Generate all reports for a specific month ===")
    print("This will generate all reports for January 2024")
    success = run_command(["vendus-reports", "all", "2024-01"])
    if not success:
        print("Note: This is expected to fail without a valid API key\n")

    print("\n=== Example 3: Generate all reports with custom output directory ===")
    output_dir = "/tmp/vendus_reports_example"
    os.makedirs(output_dir, exist_ok=True)
    print(f"This will generate all reports in {output_dir}")
    success = run_command(["vendus-reports", "all", "2024-01", "-o", output_dir])
    if not success:
        print("Note: This is expected to fail without a valid API key\n")

    print("\n=== Example 4: Help information ===")
    print("Display help for the 'all' command:")
    run_command(["vendus-reports", "all", "--help"])

    print("\n=== Summary ===")
    print("The 'all' command provides these benefits:")
    print("• Generates all 4 report types with a single command")
    print("• Automatically calculates date ranges for the specified month")
    print("• Uses previous month if no month is specified")
    print("• Consistent file naming across all reports")
    print("• Optional output directory for organized file storage")

    print("\n=== File outputs (when successful) ===")
    print("• facturas-YYYY-MM.csv (invoicing report)")
    print("• recibos-YYYY-MM.csv (receipts report)")
    print("• saft-YYYY-MM.xml (SAFT XML report)")
    print("• impostos-YYYY-MM.csv (tax analysis report)")


if __name__ == "__main__":
    main()
