#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: user.py
Author: Maria Kevin
Created: 2025-12-13
Description: User repository using Beanie.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from typing import Optional

from model import User


class UserRepository:
    async def get_user_by_user_id(self, user_id: int):
        """Fetch a user by Telegram user id."""
        return await User.get(user_id)

    async def add_user(self, user_id: int):
        """Insert a new user document."""
        await User(id=user_id).insert()

    async def remove_user(self, user_id: int):
        """Delete a user by Telegram user id."""
        user = await User.get(user_id)
        if user:
            await user.delete()

    async def get_users(self, skip: int = 0, limit: Optional[int] = None):
        """Return a paginated list of users."""
        query = User.find_all().skip(skip)
        if limit:
            query = query.limit(limit)
        return await query.to_list()

    async def get_users_count(self):
        """Return the total number of users."""
        return await User.count()

    async def ban_user(self, user_id: int):
        """Mark a user as banned."""
        user = await User.get(user_id)
        if user:
            user.banned = True
            await user.save()

    async def unban_user(self, user_id: int):
        """Clear the banned flag on a user."""
        user = await User.get(user_id)
        if user:
            user.banned = False
            await user.save()


user_repository = UserRepository()
