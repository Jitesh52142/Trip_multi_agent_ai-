"""
agents/base_agent.py
---------------------
Abstract base class for all agents in the Trip Planner system.

Every concrete agent must:
  1. Inherit from BaseAgent.
  2. Implement the ``run()`` method.
  3. Communicate exclusively through SharedMemory, never by calling
     sibling agents directly (loose coupling principle).
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from memory import SharedMemory

# Module-level logger — each agent overrides with its own name
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s → %(message)s",
)


class BaseAgent(ABC):
    """
    Abstract base for all Trip Planner agents.

    Attributes
    ----------
    name : str
        Human-readable agent identifier (used in logging and output).
    role : str
        One-line description of the agent's responsibility.
    memory : SharedMemory
        Reference to the system-wide shared memory (singleton).
    _local_memory : dict
        Agent-level private state.  Agents may store intermediate
        results here before committing to shared memory.
    logger : logging.Logger
        Per-agent logger.
    """

    def __init__(self, name: str, role: str) -> None:
        self.name: str = name
        self.role: str = role
        self.memory: SharedMemory = SharedMemory()   # singleton
        self._local_memory: dict[str, Any] = {}
        self.logger: logging.Logger = logging.getLogger(self.name)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self) -> bool:
        """
        Execute the agent's primary task.

        Returns
        -------
        bool
            ``True`` if the agent completed successfully, ``False`` on
            any handled error (the agent should also call
            ``self.memory.add_error(...)`` before returning False).
        """

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _log_start(self) -> None:
        """Log a standardised start banner."""
        self.logger.info("Starting — role: %s", self.role)

    def _log_success(self, summary: str = "") -> None:
        """Log a standardised success message."""
        self.logger.info("Completed successfully. %s", summary)

    def _log_error(self, message: str) -> None:
        """Log an error and store it in shared memory."""
        self.logger.error(message)
        self.memory.add_error(f"[{self.name}] {message}")

    def _store_local(self, key: str, value: Any) -> None:
        """Write *value* to this agent's private local memory."""
        self._local_memory[key] = value

    def _read_local(self, key: str, default: Any = None) -> Any:
        """Read *key* from this agent's private local memory."""
        return self._local_memory.get(key, default)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, role={self.role!r})"
