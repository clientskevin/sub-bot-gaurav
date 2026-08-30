#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: admin.py
Author: Maria Kevin
Created: 2025-12-13
Description: Admin repository using Beanie.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from model import Admin


class AdminRepository:
    async def get_admin_by_user_id(self, user_id: int):
        """Fetch an admin by Telegram user id."""
        return await Admin.get(user_id)

    async def add_admin(self, user_id: int):
        """Insert a new admin document."""
        admin = Admin(id=user_id)
        await admin.insert()
        return admin

    async def remove_admin(self, user_id: int):
        """Delete an admin by Telegram user id."""
        admin = await Admin.get(user_id)
        if admin:
            await admin.delete()

    async def get_admins(self):
        """Return all admin documents."""
        return await Admin.find_all().to_list()


admin_repository = AdminRepository()
