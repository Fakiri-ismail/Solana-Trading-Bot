from typing import List
from datetime import datetime
from database.connection import get_cursor
from database.models.tokens import TopTradingTokens


def insert_top_trading_tokens(top_trading_tokens: List[dict]) -> int:
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO top_trading_tokens (date, top_tokens)
            VALUES (%s, %s)
            RETURNING id
            """,
            (datetime.now(), top_trading_tokens)
        )
        return cursor.fetchone()['id']


def get_all_top_trading_tokens(limit: int = 100, offset: int = 0) -> List[TopTradingTokens]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM top_trading_tokens
            ORDER BY date DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

        return [
            TopTradingTokens(
                id=row['id'],
                date=row['date'],
                top_tokens=row['top_tokens'],
            )
            for row in cursor.fetchall()
        ]


def get_last_top_trading_tokens() -> TopTradingTokens:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM top_trading_tokens
            ORDER BY date DESC
            LIMIT 1
            """
        )
        data = cursor.fetchone()
        if data:
            return TopTradingTokens(
                id=data['id'],
                date=data['date'],
                top_tokens=data['top_tokens'],
            )
        return None


def get_top_trading_tokens_by_date(start_date: datetime, end_date: datetime) -> List[TopTradingTokens]:
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM top_trading_tokens
            WHERE date BETWEEN %s AND %s
            ORDER BY date
            """,
            (start_date, end_date)
        )
        return [
            TopTradingTokens(
                id=row['id'],
                date=row['date'],
                top_tokens=row['top_tokens'],
            )
            for row in cursor.fetchall()
        ]


def delete_top_trading_tokens(token_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM top_trading_tokens
            WHERE id = %s
            """,
            (token_id,)
        )
        return cursor.rowcount > 0
