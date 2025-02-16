import asyncio
import logging
from aiogram import types, Router, F, Dispatcher
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import log_event, save_warning, remove_warning
from config import WARNING_MESSAGE, KICK_MESSAGE
from utils import check_profile_changes

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.new_chat_members | F.left_chat_member)
async def handle_user_update(message: types.Message):
    """
    Handler for user updates in the group
    """
    try:
        user = message.from_user
        chat_id = message.chat.id

        # Check for profile changes
        changes = await check_profile_changes(user)

        if changes:
            # Send warning
            warning_msg = await message.answer(
                WARNING_MESSAGE.format(
                    username=user.username,
                    change_type=changes
                ),
                parse_mode="HTML"
            )

            # Save warning to database
            save_warning(user.id, warning_msg.message_id)
            log_event(user.id, f"Warning sent: {changes}", chat_id)

            # Wait 5 minutes
            await asyncio.sleep(300)

            # Check if warning should be acted upon
            if remove_warning(user.id):
                # Kick user
                await message.chat.ban(user.id)

                # Send kick message
                await message.answer(
                    KICK_MESSAGE.format(
                        username=user.username,
                        change_type=changes
                    ),
                    parse_mode="HTML"
                )

                # Log kick event
                log_event(user.id, f"User kicked: {changes}", chat_id)

                # Delete warning message
                await warning_msg.delete()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def register_handlers(dp: Dispatcher):
    """
    Register all handlers
    """
    dp.include_router(router)