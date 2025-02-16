import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from aiohttp import web, ClientSession, ClientTimeout
from dotenv import load_dotenv
from handlers import register_handlers
from database import init_db

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram12.onrender.com")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "¡Bot iniciado!")
GROUP_ID = os.getenv("GROUP_ID")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def verify_webhook_url(url: str) -> bool:
    """Verificar si la URL del webhook es accesible."""
    test_url = url.replace(TOKEN, 'dummy_token')
    logger.info(f"Verificando webhook URL (sanitizada): {test_url}")

    try:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            async with session.get(test_url) as response:
                status = response.status
                logger.info(f"Estado de verificación del webhook: {status}")
                return status != 404
    except Exception as e:
        logger.error(f"Error verificando la URL del webhook: {e}")
        return False

async def setup_webhook(bot: Bot) -> bool:
    """Configurar el webhook con verificación."""
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook eliminado")

        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=["message", "chat_member"]
        )
        logger.info("✅ Webhook establecido")
        return True
    except Exception as e:
        logger.error(f"Error en la configuración del webhook: {e}")
        return False

async def on_startup(bot: Bot):
    logger.info("Iniciando aplicación...")
    try:
        me = await bot.get_me()
        logger.info(f"Bot iniciado: @{me.username}")

        if not await setup_webhook(bot):
            raise Exception("No se pudo configurar el webhook")

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
        register_handlers(dp)
        init_db()

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        app.on_startup.append(lambda _: asyncio.create_task(on_startup(bot)))
        app.on_shutdown.append(lambda _: asyncio.create_task(on_shutdown(bot)))

        async def handle(request):
            return web.Response(text="Webhook activo", status=200)
        app.router.add_get("/", handle)
        
        logger.info(f"Servidor web en {WEBAPP_HOST}:{WEBAPP_PORT}")
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
