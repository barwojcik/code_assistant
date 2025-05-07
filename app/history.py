"""
Module containing functions to manage and store history.

This module provides classes and functions for managing a collection of history entries,
including adding new entries, retrieving the current list of entries, and maintaining a fixed maximum length.

Classes:
    HistoryEntry: Represents an entry in the history log.
    HistoryHandler: Handles a collection of history entries with a fixed maximum length.

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
    Represents an entry in the history log.

    The `HistoryEntry` class is used to store details about a single entry in the
    history log, including the corresponding instructions, code, generated output
    code, raw response from a relevant process, and the timestamp at which the
    entry was created. This can be helpful in cases where tracking historical
    records of generated code or transformations is needed.

    Attributes:
        instructions: User's input instructions
        code: Original code
        output_code: Processed/modified code
        raw_response: Complete response from the model
        timestamp: When the entry was created
    """

    instructions: str
    code: str
    output_code: str
    raw_response: str
    timestamp: datetime = field(default_factory=datetime.now)


class HistoryHandler:
    """
    Handles a collection of history entries with a fixed maximum length.

    This class is designed to maintain a collection of history entries up to a predefined or user-specified maximum
    length. When the maximum limit is reached, the oldest entry is automatically removed as new entries are added.
    It also provides methods for adding new history entries and retrieving the current list of history entries.

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
                "Invalid max_length: %d, using default value: %d",
                max_history_length,
                self.DEFAULT_MAX_LENGTH,
            )
            max_history_length = self.DEFAULT_MAX_LENGTH

        self._history_max_length: int = max_history_length
        self._history: Deque[HistoryEntry] = deque([], self._history_max_length)
        logger.info("Initialized HistoryHandler with max length: %d", self._history_max_length)

    def add_new_entry(self, entry: HistoryEntry) -> None:
        """
        Add a new history entry to the collection.

        When the collection reaches history_max_length, the oldest entry is automatically removed.

        Args:
            entry: The new history entry to be added.
        """
        # Add the new entry to the history
        self._history.append(entry)
        logger.info("Added new history entry: %s", entry)

    def get_history(self) -> List[HistoryEntry]:
        """
        Retrieve all stored history entries.

        Returns:
            List of all history entries in chronological order.
        """
        return list(self._history)
