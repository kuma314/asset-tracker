import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "asset_tracker.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY,
                major_category TEXT NOT NULL,
                sub_category TEXT,
                name_or_ticker TEXT NOT NULL,
                account_type TEXT NOT NULL,
                quantity REAL,
                value_jpy INTEGER CHECK (value_jpy IS NULL OR value_jpy >= 0),
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def fetch_holdings(db_path: Path = DEFAULT_DB_PATH) -> List[sqlite3.Row]:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            SELECT id, major_category, sub_category, name_or_ticker, account_type,
                   quantity, value_jpy, updated_at
            FROM holdings
            ORDER BY updated_at DESC, id DESC
            """
        )
        return list(cursor.fetchall())


def upsert_holding(
    *,
    holding_id: Optional[int],
    major_category: str,
    sub_category: Optional[str],
    name_or_ticker: str,
    account_type: str,
    quantity: Optional[float],
    value_jpy: int,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    if value_jpy is not None and value_jpy < 0:
        raise ValueError("value_jpy must be 0 or greater")

    updated_at = _utc_now_iso()
    with get_connection(db_path) as connection:
        if holding_id is None:
            connection.execute(
                """
                INSERT INTO holdings (
                    major_category, sub_category, name_or_ticker, account_type,
                    quantity, value_jpy, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    major_category,
                    sub_category,
                    name_or_ticker,
                    account_type,
                    quantity,
                    value_jpy,
                    updated_at,
                ),
            )
        else:
            connection.execute(
                """
                UPDATE holdings
                SET major_category = ?,
                    sub_category = ?,
                    name_or_ticker = ?,
                    account_type = ?,
                    quantity = ?,
                    value_jpy = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    major_category,
                    sub_category,
                    name_or_ticker,
                    account_type,
                    quantity,
                    value_jpy,
                    updated_at,
                    holding_id,
                ),
            )
        connection.commit()


def delete_holding(holding_id: int, db_path: Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
        connection.commit()


def replace_holdings(
    rows: Iterable[dict],
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM holdings")
        _insert_rows(connection, rows)
        connection.commit()


def insert_holdings(
    rows: Iterable[dict],
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    with get_connection(db_path) as connection:
        _insert_rows(connection, rows)
        connection.commit()


def upsert_holdings_by_key(
    rows: Iterable[dict],
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    with get_connection(db_path) as connection:
        updated_at = _utc_now_iso()
        for row in rows:
            value_jpy = row.get("value_jpy")
            if value_jpy is not None and int(value_jpy) < 0:
                raise ValueError("value_jpy must be 0 or greater")

            major_category = row.get("major_category")
            name_or_ticker = row.get("name_or_ticker")
            account_type = row.get("account_type")

            cursor = connection.execute(
                """
                SELECT id
                FROM holdings
                WHERE major_category = ? AND name_or_ticker = ? AND account_type = ?
                """,
                (major_category, name_or_ticker, account_type),
            )
            existing = cursor.fetchone()
            if existing:
                connection.execute(
                    """
                    UPDATE holdings
                    SET sub_category = ?,
                        quantity = ?,
                        value_jpy = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        row.get("sub_category"),
                        row.get("quantity"),
                        int(value_jpy) if value_jpy is not None else None,
                        updated_at,
                        existing["id"],
                    ),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO holdings (
                        major_category, sub_category, name_or_ticker, account_type,
                        quantity, value_jpy, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        major_category,
                        row.get("sub_category"),
                        name_or_ticker,
                        account_type,
                        row.get("quantity"),
                        int(value_jpy) if value_jpy is not None else None,
                        updated_at,
                    ),
                )
        connection.commit()


def _insert_rows(connection: sqlite3.Connection, rows: Iterable[dict]) -> None:
    payload = []
    for row in rows:
        value_jpy = row.get("value_jpy")
        if value_jpy is not None and int(value_jpy) < 0:
            raise ValueError("value_jpy must be 0 or greater")
        payload.append(
            (
                row.get("major_category"),
                row.get("sub_category"),
                row.get("name_or_ticker"),
                row.get("account_type"),
                row.get("quantity"),
                int(value_jpy) if value_jpy is not None else None,
                _utc_now_iso(),
            )
        )

    connection.executemany(
        """
        INSERT INTO holdings (
            major_category, sub_category, name_or_ticker, account_type,
            quantity, value_jpy, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        payload,
    )


def summarize_by(column: str, db_path: Path = DEFAULT_DB_PATH) -> List[sqlite3.Row]:
    if column not in {"major_category", "account_type"}:
        raise ValueError("unsupported column")

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            f"""
            SELECT {column} AS label, SUM(value_jpy) AS total_value
            FROM holdings
            GROUP BY {column}
            ORDER BY total_value DESC
            """
        )
        return list(cursor.fetchall())


def top_holdings(limit: int = 10, db_path: Path = DEFAULT_DB_PATH) -> List[sqlite3.Row]:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            SELECT name_or_ticker, major_category, account_type, value_jpy
            FROM holdings
            ORDER BY value_jpy DESC
            LIMIT ?
            """,
            (limit,),
        )
        return list(cursor.fetchall())
