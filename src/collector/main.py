"""
Compatibility wrapper for the async collector implementation.

The existing tests and some integration code import `collector.main.Collector`.
This module exposes a minimal API that forwards to the async implementation
under `core.async_lib.collector.main`.
"""

from core.async_lib.collector.main import AsyncCollector as Collector

