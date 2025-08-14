from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TopTradingTokens:
    id: Optional[int] = None
    date: datetime = None
    top_tokens: list = []

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now()
