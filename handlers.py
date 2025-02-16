import asyncio
import logging
from aiogram import types, Router, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.filters.command import Command
from database import log_event, save_warning, remove_warning
from config import WARNING_MESSAGE, KICK_MESSAGE, GROUP_ID, WELCOME_MESSAGE
from utils import check_profile_changes, format_violation_message

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def handle_start(message: types.Message):
    """
    Handler for /start command
    """
    try:
        # Solo responder en el grupo configurado
        if message.chat.id == GROUP_ID:
            await message.answer(
                WELCOME_MESSAGE,
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Error handling start command: {e}", exc_info=True)

@router.message()
async def handle_message(message: types.Message):
    """
    Handler for all messages to check user profile compliance
    """
    try:
        # Solo procesar mensajes del grupo configurado
        if message.chat.id != GROUP_ID:
            return

        # Verificar violaciones del perfil
        violations = await check_profile_changes(message.from_user, message.chat.id, message.bot)

        if any(violations.values()):
            # Intentar eliminar el mensaje
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"Error deleting message: {e}")

            # Enviar advertencia
            warning_text = format_violation_message(violations, message.from_user.username or message.from_user.id)
            if warning_text:
                warning_msg = await message.answer(
                    warning_text,
                    parse_mode="HTML"
                )

                # Guardar advertencia en la base de datos
                save_warning(message.from_user.id, warning_msg.message_id)
                log_event(message.from_user.id, f"Warning sent: {violations}", message.chat.id)

                # Programar expulsión si no se corrige
                asyncio.create_task(
                    schedule_kick(
                        message.from_user.id,
                        message.from_user.username or str(message.from_user.id),
                        message.chat.id,
                        warning_msg,
                        message.bot
                    )
                )

    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER))
async def on_user_update(event: types.ChatMemberUpdated):
    """
    Handler for user updates in the group
    """
    try:
        if event.chat.id != GROUP_ID:
            return

        user = event.new_chat_member.user
        violations = await check_profile_changes(user, event.chat.id, event.bot)

        if any(violations.values()):
            warning_text = format_violation_message(violations, user.username or user.id)
            if warning_text:
                warning_msg = await event.answer(
                    warning_text,
                    parse_mode="HTML"
                )

                save_warning(user.id, warning_msg.message_id)
                log_event(user.id, f"Warning sent on update: {violations}", event.chat.id)

                asyncio.create_task(
                    schedule_kick(
                        user.id,
                        user.username or str(user.id),
                        event.chat.id,
                        warning_msg,
                        event.bot
                    )
                )

    except Exception as e:
        logger.error(f"Error in user update handler: {e}", exc_info=True)

async def schedule_kick(user_id: int, username: str, chat_id: int, warning_msg: types.Message, bot):
    """
    Schedule user kick after warning period
    """
    await asyncio.sleep(300)  # 5 minutes

    try:
        # Verificar si la advertencia aún existe
        if remove_warning(user_id):
            # Verificar el estado actual del perfil
            violations = await check_profile_changes(await bot.get_chat_member(chat_id, user_id), chat_id, bot)

            if any(violations.values()):
                # Ejecutar expulsión
                await bot.ban_chat_member(chat_id, user_id)
                await bot.send_message(
                    chat_id,
                    KICK_MESSAGE.format(
                        username=username,
                        change_type=", ".join(k for k, v in violations.items() if v)
                    ),
                    parse_mode="HTML"
                )
                log_event(user_id, f"User kicked: {violations}", chat_id)

                # Eliminar mensaje de advertencia
                try:
                    await warning_msg.delete()
                except Exception as e:
                    logger.error(f"Failed to delete warning message: {e}")

    except Exception as e:
        logger.error(f"Error in schedule_kick: {e}", exc_info=True)

def register_handlers(dp):
    """
    Register all handlers
    """
    dp.include_router(router)