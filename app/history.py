from dataclasses import dataclass, field
from typing import List, Dict
from collections import deque
from datetime import datetime


@dataclass
class HistoryEntry:
    """Represents a single entry in the history."""
    instructions: str
    code: str
    output_code: str
    raw_response: str
    timestamp: datetime = field(default_factory=datetime.now)


class HistoryHandler:
    """
    A class to manage and store history entries.

    Attributes:
        max_length (int): Maximum length of the history. Defaults to 10.
    """

    def __init__(self, max_length=10):
        """Initializes a new instance of the HistoryHandler."""
        self.history_max_length = max_length
        self._history = deque([], self.history_max_length)

    def add_new_entry(self, entry: HistoryEntry) -> None:
        """
        Adds a new history entry to the handler's history.

        Args:
            entry (HistoryEntry): The new entry to be added.
        """
        # Add the new entry to the history
        self._history.append(entry)

    def get_history(self) -> List[HistoryEntry]:
        """Returns a list of all history entries."""
        return list(self._history)
