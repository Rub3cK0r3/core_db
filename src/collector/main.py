"""
Compatibility wrapper for the async collector implementation.

The existing tests and some integration code import `collector.main.Collector`.
This module exposes a minimal API that forwards to the async implementation
under `core.async_lib.collector.main`.
"""

from core.async_lib.collector.main import AsyncCollector as Collector

# ---------------------------------------------------------
# © 2026 Rub3ck0r3 — Open Source (MIT License)
# Permission is granted to use, copy, modify, and distribute
# this software under the terms of the MIT License.
# See https://opensource.org/licenses/MIT for details.
# ---------------------------------------------------------
