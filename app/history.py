"""
Module containing functions to manage and store history.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Deque
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """
    Represents a single entry in the history.

    Attributes:
        instructions: User's input instructions
        code: Original code
        output_code: Processed/modified code
        raw_response: Complete response from the system
        timestamp: When the entry was created
    """

    instructions: str
    code: str
    output_code: str
    raw_response: str
    timestamp: datetime = field(default_factory=datetime.now)


class HistoryHandler:
    """
    Manages and stores history entries in a circular buffer.

    The handler maintains a fixed-size collection of history entries,
    automatically removing oldest entries when the maximum size is reached.

    Attributes:
        history_max_length (int): Maximum length of the history. Defaults to 10.

    Methods:
        add_new_entry: Adds a new entry to the history.
        get_history: Returns a list of all history entries.
    """

    DEFAULT_MAX_LENGTH: int = 10

    def __init__(self, max_history_length: int = DEFAULT_MAX_LENGTH) -> None:
        """
        Initialize a new HistoryHandler instance.

        Args:
            max_history_length: Maximum number of entries to store. Must be greater than 0.
        """
        if max_history_length <= 0:
            logger.warning(
                'Invalid max_length: %d, using default value: %d',
                max_history_length,
                self.DEFAULT_MAX_LENGTH,
            )
            max_history_length = self.DEFAULT_MAX_LENGTH

        self._history_max_length: int = max_history_length
        self._history: Deque[HistoryEntry] = deque([], self._history_max_length)
        logger.info('Initialized HistoryHandler with max length: %d', self._history_max_length)

    def add_new_entry(self, entry: HistoryEntry) -> None:
        """
        Add a new history entry to the collection.

        When the collection reaches history_max_length, the oldest entry is automatically removed.

        Args:
            entry: The new history entry to be added.
        """
        # Add the new entry to the history
        self._history.append(entry)
        logger.info('Added new history entry: %s', entry)

    def get_history(self) -> List[HistoryEntry]:
        """
        Retrieve all stored history entries.

        Returns:
            List of all history entries in chronological order.
        """
        return list(self._history)
