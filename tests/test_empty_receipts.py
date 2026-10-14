"""A month without receipts must not abort monthly report generation."""

import base64
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vendus_reports import cli

NO_DATA = {"errors": [{"code": "A001", "message": "No data"}]}


def response(status, data):
    return Mock(status_code=status, json=Mock(return_value=data))


@pytest.mark.parametrize("reply", [response(404, NO_DATA), response(200, [])])
def test_no_receipts_produces_header_only_csv(reply, tmp_path, monkeypatch):
    monkeypatch.setenv("VENDUS_API_KEY", "test-key")
    with patch.object(cli.requests, "get", return_value=reply):
        path = cli.run_receipts("2026-08-01", "2026-08-31", None, str(tmp_path))
    assert Path(path).read_text() == "DATA;NUMERO;CLIENTE;VALOR;OBS"


@pytest.mark.parametrize(
    "status,data",
    [
        (400, NO_DATA),
        (401, {"errors": [{"code": "AUTH", "message": "Unauthorized"}]}),
        (404, {"errors": [{"code": "OTHER", "message": "Not found"}]}),
        (404, {"errors": []}),
        (404, {"errors": NO_DATA["errors"] + [{"code": "OTHER"}]}),
        (404, []),
        (500, NO_DATA),
    ],
)
def test_other_errors_remain_fatal(status, data):
    with patch.object(cli.requests, "get", return_value=response(status, data)):
        with pytest.raises(Exception, match=f"Invalid status code: {status}"):
            cli.receipts("test-key", "2026-08-01", "2026-08-31")


def test_individual_receipt_not_found_remains_fatal():
    with patch.object(cli.requests, "get", return_value=response(404, NO_DATA)):
        with pytest.raises(Exception, match="Invalid status code: 404"):
            cli.get_receipt("test-key", 123)


def test_existing_receipts_still_load():
    row = {
        "date": "2026-08-10",
        "number": "RG 1/1",
        "amount_gross": "100.00",
        "client": {"name": "Client"},
        "items": [],
        "observations": "Paid",
    }
    with patch.object(
        cli.requests,
        "get",
        side_effect=[
            response(200, [{"id": 123}]),
            response(200, row),
        ],
    ):
        report = cli.receipts("test-key", "2026-08-01", "2026-08-31")
    assert len(report.lines) == 1
    assert report.lines[0].number == "RG 1/1"
    assert report.lines[0].amount == 100.0


def test_all_without_receipts_generates_four_files_and_reaches_archive(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("VENDUS_API_KEY", "test-key")
    invoice = {
        "id": 1,
        "date": "2026-08-10",
        "number": "FT 1/1",
        "type": "FT",
        "amount_gross": "114.00",
        "amount_net": "100.00",
        "client": {"name": "Client"},
        "payments": [],
    }
    replies = [
        response(200, [invoice]),
        response(404, NO_DATA),
        response(200, {"xml": base64.b64encode(b"<AuditFile/>").decode()}),
        response(200, [invoice]),
    ]
    with patch.object(
        cli.sys,
        "argv",
        ["vendus-reports", "--output", str(tmp_path), "--archive", "all", "2026-08"],
    ), patch.object(cli.requests, "get", side_effect=replies), patch.object(
        cli, "archive_to_drive"
    ) as archive:
        cli.main()
    files, month = archive.call_args.args
    assert month == "2026-08"
    assert len(files) == 4
    assert all(Path(f).is_file() for f in files)
    assert (
        tmp_path / "recibos-2026-08-01-2026-08-31.csv"
    ).read_text() == "DATA;NUMERO;CLIENTE;VALOR;OBS"
    archive.assert_called_once()
