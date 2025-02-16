import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
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
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_application():
    try:
        # Initialize bot and dispatcher
        logger.info("Initializing bot and dispatcher...")
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        dp = Dispatcher()

        # Register handlers
        logger.info("Registering message handlers...")
        register_handlers(dp)

        # Create aiohttp application
        logger.info("Creating web application...")
        app = web.Application()

        # Setup webhook handler
        logger.info("Setting up webhook handler...")
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        # Setup application
        setup_application(app, dp, bot=bot)

        # Initialize database
        logger.info("Initializing database...")
        init_db()

        async def on_startup(app):
            logger.info("Starting up...")
            try:
                # Get bot information for verification
                me = await bot.get_me()
                logger.info(f"Bot initialized: @{me.username}")

                # Delete existing webhook
                logger.info("Deleting existing webhook...")
                await bot.delete_webhook(drop_pending_updates=True)

                # Set webhook
                logger.info(f"Setting webhook URL: {WEBHOOK_URL}")
                await bot.set_webhook(
                    url=WEBHOOK_URL,
                    drop_pending_updates=True
                )

                # Send welcome message
                if GROUP_ID:
                    try:
                        await bot.send_message(
                            chat_id=GROUP_ID,
                            text=WELCOME_MESSAGE
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
                await bot.session.close()
                await bot.delete_webhook()
                logger.info("Shutdown completed successfully")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        return app

    except Exception as e:
        logger.error(f"Error in start_application: {e}")
        raise

def main():
    try:
        logger.info("Starting bot application...")
        app = asyncio.run(start_application())

        logger.info(f"Starting web server on {WEBAPP_HOST}:{WEBAPP_PORT}")
        web.run_app(
            app,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            access_log=logger
        )
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()