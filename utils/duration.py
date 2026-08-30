#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: duration.py
Author: Maria Kevin
Created: 2026-08-27
Description: Parse admin day-duration input into whole seconds.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Optional

from loguru import logger

SECONDS_PER_DAY = 86400
# 1/86400 ≈ 1.16e-5; keep ~6 fractional day digits for whole-second resolution.
MAX_FRACTIONAL_DIGITS = 6


@dataclass(frozen=True)
class DurationParseResult:
    """Parsed membership duration for storage and confirmation text."""

    duration_seconds: int
    breakdown: str


class DurationUtils:
    def parse_days_float(self, text: str) -> Optional[DurationParseResult]:
        """Parse a days number string into whole seconds with digit truncation.

        Accepts ints/floats as text (e.g. ``7``, ``1.5``). Rejects empty,
        non-numeric, non-positive, NaN, and infinite values by returning
        ``None`` so the caller can re-ask.
        """
        raw = (text or "").strip()
        if not raw:
            logger.bind(raw=text).debug("Duration parse rejected: empty input")
            return None

        try:
            value = Decimal(raw)
        except InvalidOperation:
            logger.bind(raw=raw).debug("Duration parse rejected: non-numeric")
            return None

        if not value.is_finite() or value <= 0:
            logger.bind(raw=raw, value=str(value)).debug(
                "Duration parse rejected: non-positive or non-finite"
            )
            return None

        quant = Decimal(1).scaleb(-MAX_FRACTIONAL_DIGITS)
        truncated = value.quantize(quant, rounding=ROUND_DOWN)
        duration_seconds = int(truncated * SECONDS_PER_DAY)
        if duration_seconds <= 0:
            logger.bind(raw=raw, truncated=str(truncated)).debug(
                "Duration parse rejected: truncates to zero seconds"
            )
            return None

        breakdown = self._format_breakdown(duration_seconds)
        logger.bind(
            raw=raw,
            truncated=str(truncated),
            duration_seconds=duration_seconds,
            breakdown=breakdown,
        ).info("Duration parsed from days float")
        return DurationParseResult(
            duration_seconds=duration_seconds,
            breakdown=breakdown,
        )

    def _format_breakdown(self, total_seconds: int) -> str:
        """Build a human-readable d/h/m/s breakdown for confirmation text."""
        days, rem = divmod(total_seconds, SECONDS_PER_DAY)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        parts: list[str] = []
        if days:
            parts.append(f"{days} day" if days == 1 else f"{days} days")
        if hours:
            parts.append(f"{hours} hour" if hours == 1 else f"{hours} hours")
        if minutes:
            parts.append(f"{minutes} minute" if minutes == 1 else f"{minutes} minutes")
        if seconds:
            parts.append(f"{seconds} second" if seconds == 1 else f"{seconds} seconds")
        return ", ".join(parts)


duration_utils = DurationUtils()
