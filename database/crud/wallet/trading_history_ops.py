from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from database.connection import get_cursor
from database.models.wallet import TradingHistory


def create_trading_history(mint: str, symbol: str, usdt_value: Decimal,
                           buy_price: Optional[Decimal] = None, sell_price: Optional[Decimal] = None,
                           date: Optional[datetime] = None) -> int:
    """
    Create a new trading history record.
    """
    if date is None:
        date = datetime.now()
        
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO trading_history (mint, symbol, buy_price, sell_price, usdt_value, date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (mint, symbol, buy_price, sell_price, usdt_value, date)
        )
        return cursor.fetchone()['id']


def get_all_trading_history(limit: int = 100, offset: int = 0) -> List[TradingHistory]:
    """
    Get all trading history records.
    args:
        limit (int): The maximum number of records to return.
        offset (int): The number of records to skip before starting to collect the result set.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM trading_history
            ORDER BY date DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        
        return [
            TradingHistory(
                id=row['id'],
                mint=row['mint'],
                symbol=row['symbol'],
                usdt_value=row['usdt_value'],
                buy_price=row['buy_price'],
                sell_price=row['sell_price'],
                date=row['date']
            )
            for row in cursor.fetchall()
        ]


def get_trading_history_by_token(mint: str) -> List[TradingHistory]:
    """
    Get trading history records for a specific token.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM trading_history
            WHERE mint = %s
            ORDER BY date DESC
            """,
            (mint,)
        )
        
        return [
            TradingHistory(
                id=row['id'],
                mint=row['mint'],
                symbol=row['symbol'],
                usdt_value=row['usdt_value'],
                buy_price=row['buy_price'],
                sell_price=row['sell_price'],
                date=row['date']
            )
            for row in cursor.fetchall()
        ]


def get_trading_history_by_date_range(start_date: datetime, end_date: datetime) -> List[TradingHistory]:
    """
    Get trading history records within a specific date range.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM trading_history
            WHERE date BETWEEN %s AND %s
            ORDER BY date
            """,
            (start_date, end_date)
        )

        return [
            TradingHistory(
                id=row['id'],
                mint=row['mint'],
                symbol=row['symbol'],
                usdt_value=row['usdt_value'],
                buy_price=row['buy_price'],
                sell_price=row['sell_price'],
                date=row['date']
            )
            for row in cursor.fetchall()
        ]


def delete_trading_history(history_id: int) -> bool:
    """
    Delete a trading history record by its ID.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM trading_history
            WHERE id = %s
            """,
            (history_id,)
        )
        return cursor.rowcount > 0
