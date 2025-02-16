import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web, ClientSession, ClientTimeout
from config import (
    TOKEN, WEBHOOK_PATH, WEBHOOK_URL, 
    WEBAPP_HOST, WEBAPP_PORT, WELCOME_MESSAGE,
    GROUP_ID
)
from handlers import register_handlers
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def verify_webhook_url(url: str) -> bool:
    """Verify if the webhook URL is accessible"""
    test_url = url.replace(TOKEN, 'dummy_token')
    logger.info(f"Verifying webhook URL (sanitized): {test_url}")

    try:
        timeout = ClientTimeout(total=30)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(test_url) as response:
                status = response.status
                logger.info(f"Webhook URL verification status: {status}")
                return status != 404
    except Exception as e:
        logger.error(f"Error verifying webhook URL: {e}")
        return False

async def setup_webhook(bot: Bot) -> bool:
    """Set up webhook with verification"""
    try:
        # Delete any existing webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Removed existing webhook")

        # Set the new webhook
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "chat_member"]
        )
        logger.info("✅ Set new webhook")

        # Verify the webhook was set correctly
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Current webhook info: {webhook_info}")

        return True

    except Exception as e:
        logger.error(f"Error in webhook setup: {e}")
        return False

async def retry_webhook_setup(bot: Bot, max_retries=5, initial_delay=30):
    """Retry webhook setup with exponential backoff"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Webhook setup attempt {attempt + 1}/{max_retries}")

            # Wait for DNS propagation on first attempt
            if attempt == 0:
                logger.info(f"Waiting {initial_delay}s for DNS propagation...")
                await asyncio.sleep(initial_delay)

            # Verify URL is accessible
            if not await verify_webhook_url(WEBHOOK_URL):
                raise ValueError("Webhook URL is not accessible")

            # Attempt webhook setup
            if await setup_webhook(bot):
                return True

            raise ValueError("Webhook setup verification failed")

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = initial_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("Max retries reached for webhook setup")
                return False

def main():
    try:
        logger.info("Starting bot application...")

        # Initialize bot and dispatcher
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        dp = Dispatcher()

        # Register handlers
        register_handlers(dp)

        # Initialize database
        init_db()

        # Create aiohttp application
        app = web.Application()

        # Setup webhook handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        # Setup application
        setup_application(app, dp, bot=bot)

        async def on_startup(app):
            logger.info("Starting up...")
            try:
                # Get bot information
                me = await bot.get_me()
                logger.info(f"Bot initialized: @{me.username}")

                # Setup webhook with retry mechanism
                if not await retry_webhook_setup(bot):
                    raise Exception("Failed to set up webhook after multiple retries")

                # Send welcome message
                if GROUP_ID:
                    try:
                        await bot.send_message(
                            chat_id=GROUP_ID,
                            text=WELCOME_MESSAGE,
                            parse_mode="HTML"
                        )
                        logger.info("Welcome message sent successfully")
                    except Exception as e:
                        logger.error(f"Failed to send welcome message: {e}")
            except Exception as e:
                logger.error(f"Startup error: {e}")
                raise

        async def on_shutdown(app):
            logger.info("Shutting down...")
            try:
                await bot.delete_webhook()
                logger.info("✅ Webhook deleted")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        # Start web server
        logger.info(f"Starting web server on {WEBAPP_HOST}:{WEBAPP_PORT}")
        web.run_app(
            app,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT
        )

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main().