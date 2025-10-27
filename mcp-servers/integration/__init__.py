"""
Integration Module - Unified orchestration and autonomous agents
"""

__version__ = "1.0.0"

from .orchestrator import AIOrchestrator
from .autonomous_agent import AutonomousAgent

__all__ = [
    "AIOrchestrator",
    "AutonomousAgent",
]
