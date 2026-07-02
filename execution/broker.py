"""
Abstract broker interface for live/paper trading.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class Broker(ABC):
    @abstractmethod
    def get_balance(self) -> float:
        pass

    @abstractmethod
    def open_position(self, symbol: str, side: str, size: float, 
                      stop_loss: float, take_profit: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def close_position(self, position_id: str) -> None:
        pass

    @abstractmethod
    def get_open_positions(self) -> list:
        pass