import asyncio
import logging
from aiogram import types, Router, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from database import log_event, save_warning, remove_warning
from config import WARNING_MESSAGE, KICK_MESSAGE, GROUP_ID
from utils import check_profile_changes

logger = logging.getLogger(__name__)
router = Router()

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER))
async def on_user_update(event: types.ChatMemberUpdated):
    """
    Handler for user updates in the group
    """
    try:
        # Only process events from the configured group
        if event.chat.id != GROUP_ID:
            return

        # Get the updated user
        user = event.new_chat_member.user
        chat_id = event.chat.id

        # Check for profile changes
        changes = await check_profile_changes(user)

        if changes:
            # Send warning
            warning_msg = await event.answer(
                WARNING_MESSAGE.format(
                    username=user.username or user.id,
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
                # Try to kick user
                try:
                    await event.chat.ban(user.id)
                    # Send kick message
                    await event.answer(
                        KICK_MESSAGE.format(
                            username=user.username or user.id,
                            change_type=changes
                        ),
                        parse_mode="HTML"
                    )
                    # Log kick event
                    log_event(user.id, f"User kicked: {changes}", chat_id)
                except Exception as e:
                    logger.error(f"Failed to kick user {user.id}: {e}")

                # Try to delete warning message
                try:
                    await warning_msg.delete()
                except Exception as e:
                    logger.error(f"Failed to delete warning message: {e}")

    except Exception as e:
        logger.error(f"Error in user update handler: {e}", exc_info=True)

def register_handlers(dp):
    """
    Register all handlers
    """
    dp.include_router(router)