import logging
from aiogram import types
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

async def check_profile_changes(user: types.User) -> Optional[str]:
    """
    Check for changes in user profile
    Returns the type of change detected or None if no changes
    """
    try:
        # Check for profile photo
        photos = await user.get_profile_photos()
        if photos.total_count == 0:
            logger.info(f"User {user.id} has no profile photo")
            return "foto de perfil"

        # Check for username
        # Note: This is a basic check, for a more complete solution
        # we would need to maintain a database of previous usernames
        if not user.username:
            logger.info(f"User {user.id} has no username")
            return "nombre de usuario"

        logger.info(f"No changes detected for user {user.id}")
        return None

    except Exception as e:
        logger.error(f"Error checking profile changes for user {user.id}: {e}", exc_info=True)
        return None