import asyncio
import logging
from aiogram import types, Router, Dispatcher
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.filters.command import Command
from database import log_event, save_warning, remove_warning
import config
from utils import check_profile_changes, format_violation_message, get_user_profile_status

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def handle_start(message: types.Message):
    """
    Handler for /start command
    """
    try:
        if message.chat.id == GROUP_ID:
            await message.answer(WELCOME_MESSAGE, parse_mode="HTML")
        else:
            await message.answer("Este bot solo funciona en el grupo autorizado.")
    except Exception as e:
        logger.error(f"Error handling start command: {e}", exc_info=True)


@router.message()
async def handle_message(message: types.Message):
    """
    Handler for all messages to check user profile compliance
    """
    try:
        if message.chat.id != GROUP_ID:
            return

        user = message.from_user
        violations = await check_profile_changes(user, message.chat.id, message.bot)

        if any(violations.values()):
            try:
                await message.delete()
                logger.info(f"Deleted message from user {user.id}")
            except Exception as e:
                logger.error(f"Error deleting message: {e}")

            warning_text = format_violation_message(violations, user.username or str(user.id))

            if warning_text:
                warning_msg = await message.answer(warning_text, parse_mode="HTML")

                save_warning(user.id, warning_msg.message_id)
                log_event(user.id, f"Warning sent: {violations}", message.chat.id)

                asyncio.create_task(
                    schedule_kick(user.id, user.username or str(user.id), message.chat.id, warning_msg, message.bot)
                )

    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    """
    Handler for new users joining the group
    """
    try:
        if event.chat.id != GROUP_ID:
            return

        user = event.new_chat_member.user
        violations = await check_profile_changes(user, event.chat.id, event.bot)

        if any(violations.values()):
            warning_text = format_violation_message(violations, user.username or str(user.id))

            if warning_text:
                warning_msg = await event.bot.send_message(event.chat.id, warning_text, parse_mode="HTML")

                save_warning(user.id, warning_msg.message_id)
                log_event(user.id, f"Warning sent on join: {violations}", event.chat.id)

                asyncio.create_task(
                    schedule_kick(user.id, user.username or str(user.id), event.chat.id, warning_msg, event.bot)
                )

    except Exception as e:
        logger.error(f"Error in user join handler: {e}", exc_info=True)


async def schedule_kick(user_id: int, username: str, chat_id: int, warning_msg: types.Message, bot):
    """
    Schedule user kick after warning period
    """
    await asyncio.sleep(300)  # 5 minutos

    try:
        if remove_warning(user_id):
            # Re-check profile status before kicking
            has_photo, is_public = await get_user_profile_status(user_id, bot)
            user = await bot.get_chat_member(chat_id, user_id)
            current_violations = await check_profile_changes(user, chat_id, bot)

            if any(current_violations.values()):
                try:
                    await bot.ban_chat_member(chat_id, user_id)
                    logger.info(f"User {user_id} banned from chat {chat_id}")

                    violation_types = []
                    if current_violations.get("no_photo"):
                        violation_types.append("sin foto de perfil")
                    if current_violations.get("private_photo"):
                        violation_types.append("foto de perfil privada")
                    if current_violations.get("no_username"):
                        violation_types.append("sin @username")

                    await bot.send_message(
                        chat_id,
                        KICK_MESSAGE.format(username=username, change_type=", ".join(violation_types)),
                        parse_mode="HTML"
                    )
                    log_event(user_id, f"User kicked: {current_violations}", chat_id)
                except Exception as e:
                    logger.error(f"Error banning user {user_id}: {e}")

                try:
                    await warning_msg.delete()
                except Exception as e:
                    logger.error(f"Failed to delete warning message: {e}")

    except Exception as e:
        logger.error(f"Error in schedule_kick: {e}", exc_info=True)


def register_handlers(dp: Dispatcher):
    """
    Register all handlers
    """
    dp.include_router(router)
