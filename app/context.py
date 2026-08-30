#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: context.py
Author: Maria Kevin
Created: 2025-12-15
Description: Brief description
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from pyrogram.client import Client
from pyrogram.types import User


class Context(object):
    bot: Client
    owner: User
