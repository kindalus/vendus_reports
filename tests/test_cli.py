"""Tests for CLI functionality."""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from vendus_reports.cli import (
    format_number,
    format_date,
    remove_accents,
    InvoicingRow,
    TaxRow,
    ReceiptRow,
    RelatedDoc,
)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_format_number(self):
        """Test number formatting with comma separator."""
        assert format_number(1234.56) == "1234,56"
        assert format_number(0.00) == "0,00"
        assert format_number(999.99) == "999,99"
    
    def test_format_date(self):
        """Test date formatting from YYYY-MM-DD to DD/MM/YYYY."""
        assert format_date("2024-01-15") == "15/01/2024"
        assert format_date("2023-12-31") == "31/12/2023"
    
    def test_remove_accents(self):
        """Test accent removal from text."""
        assert remove_accents("Pagamento à vista") == "Pagamento a vista"
        assert remove_accents("Depósito bancário") == "Deposito bancario"
        assert remove_accents("Transferência") == "Transferencia"
        assert remove_accents("") == ""
        assert remove_accents("Normal text") == "Normal text"


class TestDataClasses:
    """Test data classes."""
    
    def test_invoicing_row_str(self):
        """Test InvoicingRow string representation."""
        row = InvoicingRow(
            date="15/01/2024",
            number="FT001",
            client="Test Client",
            gross="100,00",
            payvat="87,72",
            exempt="0,00",
            vat="12,28",
            obs="Test obs"
        )
        expected = "15/01/2024;FT001;Test Client;100,00;87,72;0,00;12,28;Test obs"
        assert str(row) == expected
    
    def test_tax_row_str(self):
        """Test TaxRow string representation."""
        row = TaxRow(
            tax_rate="14%",
            num_documents=10,
            vat_amount=140.0,
            taxable_base=1000.0,
            total=1140.0
        )
        expected = "14%;10;140,00;1000,00;1140,00"
        assert str(row) == expected
    
    def test_related_doc(self):
        """Test RelatedDoc functionality."""
        doc = RelatedDoc("FT001", 100.50)
        assert doc.number == "FT001"
        assert doc.amount == 100.50
        assert doc.amount_str() == "100,50"
    
    def test_receipt_row_str(self):
        """Test ReceiptRow string representation."""
        related = [RelatedDoc("FT001", 50.0), RelatedDoc("FT002", 25.0)]
        row = ReceiptRow(
            date="2024-01-15",
            number="RG001",
            client="Test Client",
            amount=75.0,
            obs="Test receipt",
            related=related
        )
        expected = "15/01/2024;RG001;Test Client;75,00;Test receipt\n;FT001;50,00\n;FT002;25,00"
        assert str(row) == expected


class TestAPIFunctions:
    """Test API functions with mocking."""
    
    @patch('vendus_reports.cli.requests.get')
    def test_invoicing_api_call(self, mock_get):
        """Test invoicing API call structure."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'date': '2024-01-15',
                'number': 'FT001',
                'amount_gross': '114.00',
                'amount_net': '100.00',
                'type': 'FT',
                'client': {'name': 'Test Client'},
                'payments': []
            }
        ]
        mock_get.return_value = mock_response
        
        from vendus_reports.cli import invoicing
        
        result = invoicing("test_api_key", "2024-01-01", "2024-01-31")
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        assert "api_key=test_api_key" in call_args
        assert "since=2024-01-01" in call_args
        assert "until=2024-01-31" in call_args
        assert "type=FT,FR,NC" in call_args
        
        # Verify result structure
        assert len(result.lines) == 1
        assert result.lines[0].number == 'FT001'
        assert result.lines[0].client == 'Test Client'


@pytest.mark.integration
class TestEnvironmentVariable:
    """Test environment variable handling."""
    
    @patch.dict('os.environ', {}, clear=True)
    def test_missing_api_key(self):
        """Test behavior when API key is missing."""
        from vendus_reports.cli import run_invoicing
        
        with pytest.raises(SystemExit) as exc_info:
            run_invoicing("2024-01-01", "2024-01-31", None)
        
        assert exc_info.value.code == 1