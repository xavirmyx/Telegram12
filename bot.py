import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
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

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def on_startup():
    """
    Startup handler that sets webhook and sends welcome message
    """
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logger.info("Webhook set successfully")

        # Send welcome message to configured groups
        await bot.send_message(
            chat_id=GROUP_ID,
            text=WELCOME_MESSAGE,
            parse_mode="HTML"
        )

        # Initialize database
        init_db()

    except Exception as e:
        logger.error(f"Error during startup: {e}")

async def on_shutdown():
    """
    Shutdown handler that removes webhook and closes connections
    """
    await bot.delete_webhook()
    logger.info("Webhook deleted")

def main():
    # Register all handlers
    register_handlers(dp)

    # Create aiohttp application
    app = web.Application()

    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Setup application
    setup_application(app, dp, bot=bot)

    # Setup startup and shutdown handlers
    app.on_startup.append(lambda _: on_startup())
    app.on_shutdown.append(lambda _: on_shutdown())

    # Start web server
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )

if __name__ == '__main__':
    main()