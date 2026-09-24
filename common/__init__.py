"""Shared plumbing used by every day's lab (env loading, OpenAI client).

This is not a course "day" -- it only holds infrastructure (API keys, model
name, a client factory) so each day folder can stay self-contained and focus on
what was taught that day.
"""

from __future__ import annotations

from common.config import Settings, settings
from common.client import build_client, chat

__all__ = ["Settings", "settings", "build_client", "chat"]
