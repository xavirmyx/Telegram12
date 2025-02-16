import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import aiohttp
from config import (
    TOKEN, WEBHOOK_PATH, WEBHOOK_URL, 
    WEBAPP_HOST, WEBAPP_PORT, WELCOME_MESSAGE,
    GROUP_ID, REPLIT_DOMAIN
)
from handlers import register_handlers
from database import init_db

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_domain_accessibility():
    """
    Check if the webhook domain is accessible
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Try to access the domain
            url = f"https://{REPLIT_DOMAIN}"
            logger.info(f"Checking domain accessibility: {url}")
            async with session.get(url) as response:
                status = response.status
                logger.info(f"Domain check response status: {status}")
                return status < 500  # Accept any response that's not a server error
    except Exception as e:
        logger.error(f"Error checking domain accessibility: {e}")
        return False

async def on_startup():
    """
    Startup handler with improved error handling and logging
    """
    try:
        # Initialize database first
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")

        # Get bot information for verification
        me = await bot.get_me()
        logger.info(f"Bot initialized: @{me.username}")

        # Check domain accessibility
        logger.info("Checking domain accessibility...")
        if not await check_domain_accessibility():
            logger.error("Domain is not accessible")
            raise RuntimeError("Domain is not accessible")

        # Set webhook
        logger.info(f"Setting webhook URL: {WEBHOOK_URL}")
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )

        # Verify webhook was set
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            logger.error(f"Webhook URL mismatch. Current: {webhook_info.url}, Expected: {WEBHOOK_URL}")
            raise RuntimeError("Failed to set webhook URL correctly")

        logger.info("Webhook set successfully")

        # Send welcome message to configured groups
        try:
            logger.info(f"Sending welcome message to group {GROUP_ID}")
            await bot.send_message(
                chat_id=GROUP_ID,
                text=WELCOME_MESSAGE,
                parse_mode="HTML"
            )
            logger.info("Welcome message sent successfully")
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            # Don't raise here, as this is not critical for bot operation

    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
        raise  # Re-raise to prevent the bot from running in a bad state

async def on_shutdown():
    """
    Shutdown handler with improved error handling
    """
    try:
        logger.info("Shutting down bot...")

        # Delete webhook
        await bot.delete_webhook()
        logger.info("Webhook deleted successfully")

        # Close bot session
        session = await bot.get_session()
        await session.close()
        logger.info("Bot session closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise

def main():
    # Register all handlers
    register_handlers(dp)

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

    # Setup startup and shutdown handlers
    app.on_startup.append(lambda _: asyncio.create_task(on_startup()))
    app.on_shutdown.append(lambda _: asyncio.create_task(on_shutdown()))

    # Start web server
    logger.info(f"Starting bot on {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )

if __name__ == '__main__':
    main()