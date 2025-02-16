import logging
from aiogram import types
from typing import Optional

logger = logging.getLogger(__name__)

async def check_profile_changes(user: types.User) -> Optional[str]:
    """
    Check for changes in user profile
    Returns the type of change or None if no changes detected
    """
    try:
        # Check for profile photo
        photos = await user.get_profile_photos()
        if photos.total_count == 0:
            return "foto de perfil"
        
        # Check for username changes
        # Note: This would require maintaining a cache of previous usernames
        # which would need to be implemented separately
        if not user.username:
            return "nombre de usuario"
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking profile changes: {e}")
        return None
