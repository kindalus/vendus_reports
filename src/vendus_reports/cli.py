#!/usr/bin/env python3

import argparse
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional
import re
import os
import base64
import pandas as pd
import unicodedata
import calendar
from datetime import datetime

__version__ = "0.1.0"

URL = "https://www.vendus.co.ao/ws/documents/"
SAFT_URL = "https://www.vendus.co.ao/ws/taxauthority/saft"


@dataclass
class InvoicingRow:
    date: str
    number: str
    client: str
    gross: str
    payvat: str
    exempt: str
    vat: str
    obs: str

    def __str__(self):
        return f"{self.date};{self.number};{self.client};{self.gross};{self.payvat};{self.exempt};{self.vat};{self.obs}"


@dataclass
class RelatedDoc:
    number: str
    amount: float

    def amount_str(self):
        return format_number(self.amount)


@dataclass
class TaxRow:
    tax_rate: str
    num_documents: int
    vat_amount: float
    taxable_base: float
    total: float

    def __str__(self):
        return f"{self.tax_rate};{self.num_documents};{format_number(self.vat_amount)};{format_number(self.taxable_base)};{format_number(self.total)}"


@dataclass
class ReceiptRow:
    date: str
    number: str
    client: str
    amount: float
    obs: str
    related: List[RelatedDoc]

    def date_formatted(self):
        return format_date(self.date)

    def amount_str(self):
        return format_number(self.amount)

    def __str__(self):
        s = f"{format_date(self.date)};{self.number};{self.client};{format_number(self.amount)};{self.obs}"
        for rel in self.related:
            s += f"\n;{rel.number};{format_number(rel.amount)}"
        return s


class InvoicingReport:
    def __init__(self, lines: List[InvoicingRow]):
        self.lines = lines


class ReceiptReport:
    def __init__(self, lines: List[ReceiptRow]):
        self.lines = lines


class TaxReport:
    def __init__(self, lines: List[TaxRow]):
        self.lines = lines


def format_number(n: float) -> str:
    """Format number with comma as decimal separator."""
    return f"{n:.2f}".replace(".", ",")


def format_date(date: str) -> str:
    """Convert date from YYYY-MM-DD format to DD/MM/YYYY format."""
    return f"{date[8:10]}/{date[5:7]}/{date[0:4]}"


def remove_accents(text: str) -> str:
    """Remove accents from text using Unicode normalization."""
    if not text:
        return text
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def invoicing(api_key: str, from_date: str, to_date: str) -> InvoicingReport:
    """
    Generate invoicing report for the specified date range.

    Args:
        api_key: API authentication key
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format

    Returns:
        InvoicingReport containing processed invoice data
    """
    endpoint = f"{URL}?api_key={api_key}&since={from_date}&until={to_date}&view=detailed&type=FT,FR,NC&per_page=1000"

    response = requests.get(endpoint)
    if response.status_code != 200:
        raise Exception(f"Invalid status code: {response.status_code}")

    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Convert amounts to numeric
    df["amount_gross"] = pd.to_numeric(df["amount_gross"])
    df["amount_net"] = pd.to_numeric(df["amount_net"])

    # Calculate VAT components
    df["vat"] = abs(df["amount_gross"] - df["amount_net"])
    df["payvat"] = df["vat"] / 0.14
    df["exempt"] = abs(df["amount_net"] - df["payvat"])

    # Set exempt to 0 if less than 0.09
    df.loc[df["exempt"] < 0.09, "exempt"] = 0

    # Extract client name
    df["client_name"] = df["client"].apply(lambda x: x["name"])

    # Handle observations for FR type
    df["obs"] = ""
    fr_mask = df["type"] == "FR"
    df.loc[fr_mask, "obs"] = df.loc[fr_mask, "payments"].apply(
        lambda x: remove_accents(x[0]["title"]) if x and len(x) > 0 else ""
    )

    # Sort by client name, then by date
    df = df.sort_values(["client_name", "date"]).reset_index(drop=True)

    # Create InvoicingRow objects
    lines = []
    for _, row in df.iterrows():
        line = InvoicingRow(
            date=format_date(row["date"]),
            number=row["number"],
            client=row["client_name"],
            gross=format_number(row["amount_gross"]),
            payvat=format_number(row["payvat"]),
            exempt=format_number(row["exempt"]),
            vat=format_number(row["vat"]),
            obs=row["obs"],
        )
        lines.append(line)

    return InvoicingReport(lines)


def get_receipt(api_key: str, receipt_id: int) -> ReceiptRow:
    """
    Fetch detailed receipt data from API.

    Args:
        api_key: API authentication key
        receipt_id: Unique receipt identifier

    Returns:
        ReceiptRow with receipt details and related documents
    """
    endpoint = f"{URL}/{receipt_id}/?api_key={api_key}"

    response = requests.get(endpoint)
    if response.status_code != 200:
        raise Exception(f"Invalid status code: {response.status_code}")

    data = response.json()

    related = []
    for item in data.get("items", []):
        amount = float(item["amounts"]["gross_total"])
        related.append(RelatedDoc(number=item["reference_document"], amount=amount))

    amount = float(data["amount_gross"])

    # Clean up observations
    obs = re.sub(r"\s+", " ", data.get("observations", ""))

    return ReceiptRow(
        date=data["date"],
        number=data["number"],
        client=data["client"]["name"],
        amount=amount,
        obs=obs,
        related=related,
    )


def receipts(api_key: str, from_date: str, to_date: str) -> ReceiptReport:
    """
    Generate receipts report for the specified date range.

    Args:
        api_key: API authentication key
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format

    Returns:
        ReceiptReport containing processed receipt data
    """
    endpoint = f"{URL}?api_key={api_key}&since={from_date}&until={to_date}&view=detailed&type=RG&per_page=1000"

    response = requests.get(endpoint)
    if response.status_code != 200:
        raise Exception(f"Invalid status code: {response.status_code}")

    data = response.json()

    # Convert to DataFrame for initial processing
    df = pd.DataFrame(data)

    # Use ThreadPoolExecutor for concurrent requests
    lines = [None] * len(df)

    def fetch_receipt(index, receipt_id):
        return index, get_receipt(api_key, receipt_id)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_receipt, i, row["id"]) for i, row in df.iterrows()
        ]

        for future in as_completed(futures):
            index, receipt_row = future.result()
            lines[index] = receipt_row

    return ReceiptReport(lines)


def saft(api_key: str, year: int, month: int) -> str:
    """
    Generate SAFT XML report for the specified month.

    Args:
        api_key: API authentication key
        year: Year as integer
        month: Month as integer (1-12)

    Returns:
        XML content as string
    """
    endpoint = f"{SAFT_URL}?api_key={api_key}&year={year}&month={month}"

    response = requests.get(endpoint)
    if response.status_code != 200:
        raise Exception(f"Invalid status code: {response.status_code}")

    data = response.json()

    # Decode the base64 XML
    xml_content = base64.b64decode(data["xml"]).decode("utf-8")

    return xml_content


def tax_analysis(api_key: str, year: int, month: int) -> TaxReport:
    """
    Generate tax analysis report for the specified month.

    Args:
        api_key: API authentication key
        year: Year as integer
        month: Month as integer (1-12)

    Returns:
        TaxReport containing tax analysis by rate groups
    """
    # Calculate date range for the month
    from_date = f"{year:04d}-{month:02d}-01"

    # Calculate last day of month
    last_day = calendar.monthrange(year, month)[1]
    to_date = f"{year:04d}-{month:02d}-{last_day:02d}"

    endpoint = f"{URL}?api_key={api_key}&since={from_date}&until={to_date}&type=FT,FR,NC&per_page=1000"

    response = requests.get(endpoint)
    if response.status_code != 200:
        raise Exception(f"Invalid status code: {response.status_code}")

    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    print(df.shape)

    # Convert amounts to numeric
    df["amount_gross"] = pd.to_numeric(df["amount_gross"])
    df["amount_net"] = pd.to_numeric(df["amount_net"])

    # Handle NC documents as negative values
    mask_nc = df["type"] == "NC"
    df.loc[mask_nc, "amount_gross"] = -df.loc[mask_nc, "amount_gross"]
    df.loc[mask_nc, "amount_net"] = -df.loc[mask_nc, "amount_net"]

    # Calculate VAT amount
    df["vat_amount"] = df["amount_gross"] - df["amount_net"]

    # Determine tax group: 0% if no tax difference, otherwise 14%
    df["tax_group"] = "14%"
    df.loc[df["vat_amount"] == 0, "tax_group"] = "0%"

    # Group by tax group and aggregate
    result = (
        df.groupby("tax_group")
        .agg(
            {
                "id": "count",  # Number of documents
                "vat_amount": "sum",  # VAT
                "amount_net": "sum",  # Taxable base
                "amount_gross": "sum",  # Total
            }
        )
        .reset_index()
    )

    # Rename columns
    result.columns = ["Tax Rate", "# Documents", "VAT", "Taxable Base", "Total"]

    # Ensure both tax groups exist (0% and 14%)
    if "0%" not in result["Tax Rate"].values:
        new_row = pd.DataFrame(
            {
                "Tax Rate": ["0%"],
                "# Documents": [0],
                "VAT": [0.0],
                "Taxable Base": [0.0],
                "Total": [0.0],
            }
        )
        result = pd.concat([result, new_row], ignore_index=True)

    if "14%" not in result["Tax Rate"].values:
        new_row = pd.DataFrame(
            {
                "Tax Rate": ["14%"],
                "# Documents": [0],
                "VAT": [0.0],
                "Taxable Base": [0.0],
                "Total": [0.0],
            }
        )
        result = pd.concat([result, new_row], ignore_index=True)

    # Sort by tax rate
    result = result.sort_values("Tax Rate").reset_index(drop=True)

    # Create TaxRow objects
    lines = []
    for _, row in result.iterrows():
        line = TaxRow(
            tax_rate=row["Tax Rate"],
            num_documents=int(row["# Documents"]),
            vat_amount=float(row["VAT"]),
            taxable_base=float(row["Taxable Base"]),
            total=float(row["Total"]),
        )
        lines.append(line)

    return TaxReport(lines)


def run_saft(year_month: str, output: Optional[str], output_dir: Optional[str] = None):
    """
    Execute SAFT report generation command.

    Args:
        year_month: Year and month in YYYY-MM format
        output: Optional output file path
        output_dir: Optional output directory path
    """
    api_key = os.getenv("VENDUS_API_KEY")
    if not api_key:
        print("Error: VENDUS_API_KEY environment variable is required")
        sys.exit(1)

    # Parse year-month format (yyyy-mm)
    try:
        year, month = year_month.split("-")
        year = int(year)
        month = int(month)

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

    except ValueError:
        print(f"Error: Invalid date format. Expected yyyy-mm, got: {year_month}")
        sys.exit(1)

    try:
        xml_content = saft(api_key, year, month)

        if output:
            filename = output
        elif output_dir:
            filename = os.path.join(output_dir, f"saft-{year_month}.xml")
        else:
            filename = f"saft-{year_month}.xml"

        # Create output directory if it doesn't exist
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_content)

        print(f"SAFT report saved to: {filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_tax_analysis(
    year_month: str, output: Optional[str], output_dir: Optional[str] = None
):
    """
    Execute tax analysis report generation command.

    Args:
        year_month: Year and month in YYYY-MM format
        output: Optional output file path
        output_dir: Optional output directory path
    """
    api_key = os.getenv("VENDUS_API_KEY")
    if not api_key:
        print("Error: VENDUS_API_KEY environment variable is required")
        sys.exit(1)

    # Parse year-month format (yyyy-mm)
    try:
        year, month = year_month.split("-")
        year = int(year)
        month = int(month)

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

    except ValueError:
        print(f"Error: Invalid date format. Expected yyyy-mm, got: {year_month}")
        sys.exit(1)

    try:
        report = tax_analysis(api_key, year, month)

        content = "Taxa;# Documentos;IVA;Base Incidencia;Total"
        for line in report.lines:
            content += f"\n{line}"

        if output:
            filename = output
        elif output_dir:
            filename = os.path.join(output_dir, f"impostos-{year_month}.csv")
        else:
            filename = f"impostos-{year_month}.csv"

        # Create output directory if it doesn't exist
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Tax analysis report saved to: {filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_receipts(
    from_date: str,
    to_date: str,
    output: Optional[str],
    output_dir: Optional[str] = None,
):
    """
    Execute receipts report generation command.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        output: Optional output file path
        output_dir: Optional output directory path
    """
    api_key = os.getenv("VENDUS_API_KEY")
    if not api_key:
        print("Error: VENDUS_API_KEY environment variable is required")
        sys.exit(1)
    try:
        report = receipts(api_key, from_date, to_date)

        content = "DATA;NUMERO;CLIENTE;VALOR;OBS"
        for line in report.lines:
            content += f"\n{line}\n"

        if output:
            filename = output
        elif output_dir:
            filename = os.path.join(output_dir, f"recibos-{from_date}-{to_date}.csv")
        else:
            filename = f"recibos-{from_date}-{to_date}.csv"

        # Create output directory if it doesn't exist
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Receipts report saved to: {filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_invoicing(
    from_date: str,
    to_date: str,
    output: Optional[str],
    output_dir: Optional[str] = None,
):
    """
    Execute invoicing report generation command.

    Args:
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        output: Optional output file path
        output_dir: Optional output directory path
    """
    api_key = os.getenv("VENDUS_API_KEY")
    if not api_key:
        print("Error: VENDUS_API_KEY environment variable is required")
        sys.exit(1)
    try:
        report = invoicing(api_key, from_date, to_date)

        content = "DATA;NUMERO;CLIENTE;TOTAL;VALOR SUJEITO;VALOR ISENTO;IVA;OBS"
        for line in report.lines:
            content += f"\n{line}"

        if output:
            filename = output
        elif output_dir:
            filename = os.path.join(output_dir, f"facturas-{from_date}-{to_date}.csv")
        else:
            filename = f"facturas-{from_date}-{to_date}.csv"

        # Create output directory if it doesn't exist
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Invoicing report saved to: {filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_all(year_month: Optional[str], output_dir: Optional[str]):
    """
    Execute all report generation commands for a given month.

    Args:
        year_month: Optional year and month in YYYY-MM format. If not provided, uses previous month.
        output_dir: Optional output directory path
    """
    # Determine the target month
    if year_month:
        try:
            year, month = year_month.split("-")
            year = int(year)
            month = int(month)

            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12")

        except ValueError:
            print(f"Error: Invalid date format. Expected yyyy-mm, got: {year_month}")
            sys.exit(1)
    else:
        # Use previous month
        today = datetime.now()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1
        year_month = f"{year:04d}-{month:02d}"

    # Calculate first and last day of the month
    first_day = f"{year:04d}-{month:02d}-01"
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = f"{year:04d}-{month:02d}-{last_day_num:02d}"

    print(f"Generating all reports for {year_month} ({first_day} to {last_day})")

    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Run all reports
    try:
        print("Generating invoicing report...")
        run_invoicing(first_day, last_day, None, output_dir)

        print("Generating receipts report...")
        run_receipts(first_day, last_day, None, output_dir)

        print("Generating SAFT report...")
        run_saft(year_month, None, output_dir)

        print("Generating tax analysis report...")
        run_tax_analysis(year_month, None, output_dir)

        print("\nAll reports generated successfully!")

    except Exception as e:
        print(f"Error generating reports: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        prog="vendus-reports",
        description="Generate invoicing, receipts, SAFT, and tax analysis reports from Vendus API",
        epilog="For more information, visit: https://github.com/kindalus/vendus-reports",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--output",
        "-o",
        metavar="DIR",
        help="Output directory for generated reports (applies to all commands)",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Type of report to generate"
    )

    # All reports command
    all_parser = subparsers.add_parser(
        "all",
        help="Generate all reports for a given month",
        description="Generate all reports (invoicing, receipts, SAFT, tax analysis) for a specified month",
    )
    all_parser.add_argument(
        "month",
        nargs="?",
        help="Year and month (YYYY-MM). If not provided, uses previous month.",
    )

    # Facturas command
    facturas_parser = subparsers.add_parser(
        "facturas",
        help="Generate invoicing report",
        description="Generate detailed invoice reports with VAT calculations",
    )
    facturas_parser.add_argument("from_date", help="Start date (YYYY-MM-DD)")
    facturas_parser.add_argument("to_date", help="End date (YYYY-MM-DD)")
    facturas_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (overrides global --output)",
    )

    # Recibos command
    recibos_parser = subparsers.add_parser(
        "recibos",
        help="Generate receipts report",
        description="Generate receipt reports with related document information",
    )
    recibos_parser.add_argument("from_date", help="Start date (YYYY-MM-DD)")
    recibos_parser.add_argument("to_date", help="End date (YYYY-MM-DD)")
    recibos_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (overrides global --output)",
    )

    # SAFT command
    saft_parser = subparsers.add_parser(
        "saft",
        help="Generate SAFT XML report",
        description="Generate SAFT XML reports for tax authorities",
    )
    saft_parser.add_argument("year_month", help="Year and month (YYYY-MM)")
    saft_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (overrides global --output)",
    )

    # Impostos command
    impostos_parser = subparsers.add_parser(
        "impostos",
        help="Generate tax analysis report",
        description="Generate tax analysis reports grouped by tax rates",
    )
    impostos_parser.add_argument("year_month", help="Year and month (YYYY-MM)")
    impostos_parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file path (overrides global --output)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Determine output directory from global flag
    output_dir = getattr(args, "output", None) if hasattr(args, "output") else None
    if hasattr(parser, "output") and parser.output:
        output_dir = parser.output

    # Extract command-specific output (if provided)
    cmd_output = getattr(args, "output", None) if args.command != "all" else None

    if args.command == "all":
        run_all(args.month, output_dir)
    elif args.command == "facturas":
        run_invoicing(args.from_date, args.to_date, cmd_output, output_dir)
    elif args.command == "recibos":
        run_receipts(args.from_date, args.to_date, cmd_output, output_dir)
    elif args.command == "saft":
        run_saft(args.year_month, cmd_output, output_dir)
    elif args.command == "impostos":
        run_tax_analysis(args.year_month, cmd_output, output_dir)


if __name__ == "__main__":
    main()
