from repository import admin_repository


async def get_or_create_admin(user_id):
    admin = await admin_repository.get_admin_by_user_id(user_id)
    if admin:
        return admin, False
    admin = await admin_repository.add_admin(user_id)
    return admin, True


async def get_admins():
    admins = await admin_repository.get_admins()
    return [admin.id for admin in admins]


async def add_admin(user_id):
    admin, is_new = await get_or_create_admin(user_id)
    if is_new:
        return True
    return False


async def remove_admin(user_id):
    await admin_repository.remove_admin(user_id)
    return True
