import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración del bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Se requiere la variable de entorno BOT_TOKEN")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_data.db")

# Configuración del servidor web
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", "8000"))

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Determinar la definición del dominio de Replit
def get_replit_domain():
    """Obtener el dominio de Replit con la validación adecuada"""
    repl_id = os.getenv('REPL_ID')
    repl_slug = os.getenv('REPL_SLUG', '').lower()

    if repl_id:
        domain = f"{repl_id}.id.repl.co"
        logger.info(f"Usando el dominio de Replit ID: {domain}")
        return domain
    elif repl_slug:
        domain = f"{repl_slug}.repl.co"
        logger.info(f"Usando el dominio de Repl slug: {domain}")
        return domain
    else:
        raise ValueError("No se encontró una configuración de Replit válida")

try:
    REPLIT_DOMAIN = get_replit_domain()
    logger.info(f"Dominio final de Replit: {REPLIT_DOMAIN}")
except Exception as e:
    logger.error(f"Error al determinar el dominio de Replit: {e}")
    raise

# Configuración de Webhook
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{REPLIT_DOMAIN}{WEBHOOK_PATH}"
logger.info(f"URL de Webhook configurada como: {WEBHOOK_URL}")

# Configuración de grupo
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "EntreClean_bot")

# Mensajes del bot
WELCOME_MESSAGE = """
🤖 <b>Bot de Moderación EntresHijos</b>

✅ Sistema iniciado correctamente
📝 Funciones activas:
• Monitoreo de fotos de perfil
• Detección de cambios de nombre de usuario
• Sistema automático de advertencias

<i>Bot de moderación profesional - EntresHijos</i>
"""

KICK_MESSAGE = """
❌ <b>Usuario Expulsado</b>

• Usuario: @{username}
• Motivo: {change_type}
• Tiempo otorgado: 5 minutos

<i>Acción ejecutada automáticamente por el sistema de moderación.</i>
"""
