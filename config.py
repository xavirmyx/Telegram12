import os
import logging
import asyncio
import ssl
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from dotenv import load_dotenv
import handlers
from database import init_db

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", 8000))
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "¡Bienvenido al grupo!")
GROUP_ID = os.getenv("GROUP_ID")

# Verificar si el token está presente
if not TOKEN:
    raise ValueError("Falta la variable de entorno BOT_TOKEN")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Manejo de SSL para evitar errores en entornos restringidos
try:
    ssl_context = ssl.create_default_context()
except AttributeError:
    ssl_context = None

async def on_startup(bot: Bot):
    logger.info("Iniciando aplicación...")
    try:
        me = await bot.get_me()
        logger.info(f"Bot iniciado: @{me.username}")

        if GROUP_ID:
            try:
                await bot.send_message(chat_id=GROUP_ID, text=WELCOME_MESSAGE, parse_mode="HTML")
                logger.info("Mensaje de bienvenida enviado")
            except Exception as e:
                logger.error(f"Error enviando mensaje de bienvenida: {e}")
    except Exception as e:
        logger.error(f"Error en el inicio: {e}")
        raise

async def on_shutdown(bot: Bot):
    logger.info("Apagando aplicación...")
    try:
        await bot.delete_webhook()
        logger.info("✅ Webhook eliminado")
    except Exception as e:
        logger.error(f"Error durante la desconexión: {e}")

def main():
    try:
        logger.info("Iniciando bot...")
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        dp = Dispatcher()
        handlers.register_handlers(dp)
        init_db()

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        app.on_startup.append(lambda _: asyncio.create_task(on_startup(bot)))
        app.on_shutdown.append(lambda _: asyncio.create_task(on_shutdown(bot)))

        logger.info(f"Servidor web en {WEBAPP_HOST}:{WEBAPP_PORT}")
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=ssl_context)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
