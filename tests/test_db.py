from pathlib import Path

import sqlite3

import db


def test_init_db_creates_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    db.init_db(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='holdings'"
        )
        result = cursor.fetchone()

    assert result is not None


def test_summaries_and_top_holdings(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    db.init_db(db_path)
    db.insert_holdings(
        [
            {
                "major_category": "Stocks",
                "sub_category": "US",
                "name_or_ticker": "AAPL",
                "account_type": "Taxable",
                "quantity": 10,
                "value_jpy": 150000,
            },
            {
                "major_category": "Bonds",
                "sub_category": "JP",
                "name_or_ticker": "JGB",
                "account_type": "NISA",
                "quantity": 5,
                "value_jpy": 50000,
            },
            {
                "major_category": "Stocks",
                "sub_category": "JP",
                "name_or_ticker": "7203",
                "account_type": "Taxable",
                "quantity": 100,
                "value_jpy": 200000,
            },
        ],
        db_path=db_path,
    )

    major_summary = db.summarize_by("major_category", db_path)
    assert {row["label"]: row["total_value"] for row in major_summary} == {
        "Stocks": 350000,
        "Bonds": 50000,
    }

    account_summary = db.summarize_by("account_type", db_path)
    assert {row["label"]: row["total_value"] for row in account_summary} == {
        "Taxable": 350000,
        "NISA": 50000,
    }

    top = db.top_holdings(2, db_path)
    assert [row["name_or_ticker"] for row in top] == ["7203", "AAPL"]


def test_upsert_holdings_by_key_updates_matching_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    db.init_db(db_path)
    db.insert_holdings(
        [
            {
                "major_category": "投資信託",
                "sub_category": "米国株",
                "name_or_ticker": "ＳＢＩ・Ｖ・Ｓ＆Ｐ５００インデックス・ファンド",
                "account_type": "Taxable",
                "quantity": 5,
                "value_jpy": 100000,
            }
        ],
        db_path=db_path,
    )

    inserted, updated, skipped = db.upsert_holdings_by_key(
        [
            {
                "major_category": "投資信託",
                "sub_category": "米国株",
                "name_or_ticker": "SBI・V・S&P500 インデックス・ファンド",
                "account_type": "Taxable",
                "quantity": 10,
                "value_jpy": 150000,
            }
        ],
        db_path=db_path,
    )

    rows = db.fetch_holdings(db_path)
    assert len(rows) == 1
    assert rows[0]["quantity"] == 10
    assert rows[0]["value_jpy"] == 150000
    assert (inserted, updated, skipped) == (0, 1, 0)
