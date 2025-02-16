import logging
from aiogram import types
from typing import Optional, List, Dict, Tuple
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

async def get_user_profile_status(user_id: int, bot) -> Tuple[bool, bool]:
    """
    Check user's profile photo status
    Returns: (has_photo, is_public)
    """
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count == 0:
            return False, False

        # Try to get the photo file to check if it's public
        try:
            photo = photos.photos[0][-1]
            await bot.get_file(photo.file_id)
            return True, True
        except Exception:
            return True, False

    except Exception as e:
        logger.error(f"Error checking profile photo for user {user_id}: {e}", exc_info=True)
        return False, False

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
            "no_username": False
        }

        # Skip checks for admins
        if await is_admin(chat_id, user.id, bot):
            logger.info(f"User {user.id} is admin, skipping profile checks")
            return violations

        # Check for profile photo
        has_photo, is_public = await get_user_profile_status(user.id, bot)
        if not has_photo:
            violations["no_photo"] = True
            logger.info(f"User {user.id} has no profile photo")
        elif not is_public:
            violations["private_photo"] = True
            logger.info(f"User {user.id} has private profile photo")

        # Check for username
        if not user.username:
            violations["no_username"] = True
            logger.info(f"User {user.id} has no username")

        logger.info(f"Profile check completed for user {user.id}")
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
    if violations.get("no_photo"):
        violation_texts.append("no tienes foto de perfil")
    if violations.get("private_photo"):
        violation_texts.append("tu foto de perfil es privada")
    if violations.get("no_username"):
        violation_texts.append("no tienes @username")

    if not violation_texts:
        return None

    violations_text = " y ".join(violation_texts)
    return f"""⚠️ @{username}, se ha detectado que {violations_text}.

🕐 Tienes 5 minutos para corregir esto o serás expulsado del grupo.

<i>Este es un mensaje automático del sistema de moderación.</i>"""