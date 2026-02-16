"""Backward-compatible entry point for the LimbGuard-Cortex API.

This module re-exports the FastAPI ``app`` from ``main`` so that both
``uvicorn api:app`` and ``uvicorn main:app`` work as start commands.
"""

from main import app  # noqa: F401

__all__ = ["app"]
