import logging
from aiogram import types
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

async def is_admin(chat_id: int, user_id: int, bot) -> bool:
    """
    Check if user is an admin in the chat
    """
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status for user {user_id}: {e}", exc_info=True)
        return False

async def check_profile_changes(user: types.User, chat_id: int, bot) -> Dict[str, bool]:
    """
    Check for all possible profile violations
    Returns a dictionary with the types of violations found
    """
    try:
        # Initialize violations dictionary
        violations = {
            "no_photo": False,
            "private_photo": False,
            "no_username": False,
            "removed_username": False,
            "removed_photo": False
        }

        # Skip checks for admins
        if await is_admin(chat_id, user.id, bot):
            logger.info(f"User {user.id} is admin, skipping profile checks")
            return violations

        # Check for profile photo
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count == 0:
            violations["no_photo"] = True
            logger.info(f"User {user.id} has no profile photo")
        else:
            try:
                # Try to get the photo file, if it fails, the photo is private
                photo = photos[0][-1]  # Get the last size of the first photo
                await bot.get_file(photo.file_id)
            except Exception as e:
                violations["private_photo"] = True
                logger.info(f"User {user.id} has private profile photo")

        # Check for username
        if not user.username:
            violations["no_username"] = True
            logger.info(f"User {user.id} has no username")

        # Add detailed logging
        logger.info(f"Profile check completed for user {user.id}")
        logger.info(f"Photos count: {photos.total_count}")
        logger.info(f"Username present: {bool(user.username)}")
        logger.info(f"Violations found: {violations}")

        return violations

    except Exception as e:
        logger.error(f"Error checking profile changes for user {user.id}: {e}", exc_info=True)
        return {}

def format_violation_message(violations: Dict[str, bool], username: str) -> Optional[str]:
    """
    Format violation message based on detected violations
    """
    if not any(violations.values()):
        return None

    violation_texts = []
    if violations["no_photo"] or violations["removed_photo"]:
        violation_texts.append("no tienes foto de perfil")
    if violations["private_photo"]:
        violation_texts.append("tu foto de perfil es privada")
    if violations["no_username"] or violations["removed_username"]:
        violation_texts.append("no tienes @username")

    if not violation_texts:
        return None

    return f"⚠️ @{username}, se ha detectado que {' y '.join(violation_texts)}.\n" \
           f"Tienes 5 minutos para corregir esto o serás expulsado del grupo.\n" \
           f"\n<i>Este es un mensaje automático del sistema de moderación.</i>"