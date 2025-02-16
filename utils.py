import logging
from aiogram import types
from typing import Optional, List, Dict, Tuple
from datetime import datetime

# Configurar logging
def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)
setup_logging()

async def is_admin(chat_id: int, user_id: int, bot) -> bool:
    """
    Verifica si un usuario es administrador en el chat.
    """
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error al verificar estado de admin para el usuario {user_id}: {e}", exc_info=True)
        return False

async def get_user_profile_status(user_id: int, bot) -> Tuple[bool, bool]:
    """
    Verifica el estado de la foto de perfil de un usuario.
    Devuelve: (tiene_foto, es_pública)
    """
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count == 0:
            return False, False

        try:
            photo = photos.photos[0][-1]
            await bot.get_file(photo.file_id)
            return True, True
        except Exception:
            return True, False

    except Exception as e:
        logger.error(f"Error al verificar la foto de perfil del usuario {user_id}: {e}", exc_info=True)
        return False, False

async def check_profile_changes(user: types.User, chat_id: int, bot) -> Dict[str, bool]:
    """
    Verifica violaciones en el perfil del usuario.
    Devuelve un diccionario con las violaciones detectadas.
    """
    try:
        violations = {
            "no_photo": False,
            "private_photo": False,
            "no_username": False
        }

        if await is_admin(chat_id, user.id, bot):
            logger.info(f"Usuario {user.id} es admin, se omiten verificaciones")
            return violations

        has_photo, is_public = await get_user_profile_status(user.id, bot)
        if not has_photo:
            violations["no_photo"] = True
            logger.info(f"Usuario {user.id} no tiene foto de perfil")
        elif not is_public:
            violations["private_photo"] = True
            logger.info(f"Usuario {user.id} tiene foto de perfil privada")

        if not user.username:
            violations["no_username"] = True
            logger.info(f"Usuario {user.id} no tiene username")

        logger.info(f"Verificación de perfil completada para usuario {user.id}, violaciones detectadas: {violations}")
        return violations

    except Exception as e:
        logger.error(f"Error al verificar cambios de perfil para usuario {user.id}: {e}", exc_info=True)
        return {}

def format_violation_message(violations: Dict[str, bool], username: str) -> Optional[str]:
    """
    Formatea un mensaje de advertencia basado en las violaciones detectadas.
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
    return (f"""
⚠️ @{username}, se ha detectado que {violations_text}.

🕐 Tienes 5 minutos para corregir esto o serás expulsado del grupo.

<i>Este es un mensaje automático del sistema de moderación.</i>
""")
