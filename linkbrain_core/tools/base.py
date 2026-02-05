# linkbrain_tools/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseToolDevice(ABC):
    """
    Abstract base class for AI-controllable tool devices.
    This wraps a physical device and exposes actions to the AI layer.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def on(self) -> None:
        pass

    @abstractmethod
    async def off(self) -> None:
        pass

    @abstractmethod
    async def status(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def supported_actions(self) -> set[str]:
        """
        Actions supported by this tool (e.g. on, off, status, lock).
        """
        pass