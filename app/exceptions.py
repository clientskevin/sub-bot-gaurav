#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: exceptions.py
Author: Maria Kevin
Created: 2026-08-27
Description: Application-specific exceptions with user-facing messages.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


class AppError(Exception):
    """Base application error carrying a user-facing message."""

    def __init__(self, user_message: str):
        self.user_message = user_message
        super().__init__(user_message)


class ChannelResolveError(AppError):
    """Raised when a channel cannot be resolved from owner input."""


class InviteCreateError(AppError):
    """Raised when Telegram invite link creation fails."""
