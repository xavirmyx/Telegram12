import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Bot Configuration
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Web Server Configuration
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8000

# Get Replit domain
REPLIT_DOMAIN = os.getenv('REPLIT_DOMAIN')
if not REPLIT_DOMAIN:
    logger.warning("REPLIT_DOMAIN not found, trying alternative domain configuration...")
    REPL_SLUG = os.getenv('REPL_SLUG')
    REPL_OWNER = os.getenv('REPL_OWNER')
    if REPL_SLUG and REPL_OWNER:
        REPLIT_DOMAIN = f"{REPL_SLUG}.{REPL_OWNER}.repl.co"
        logger.info(f"Using constructed domain: {REPLIT_DOMAIN}")
    else:
        logger.error("No valid Replit domain configuration found")
        raise ValueError("REPLIT_DOMAIN or REPL_SLUG/REPL_OWNER environment variables are required")

# Webhook Configuration
WEBHOOK_HOST = f"https://{REPLIT_DOMAIN}"
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logger.info(f"Webhook configuration:")
logger.info(f"Host: {WEBHOOK_HOST}")
logger.info(f"Path: {WEBHOOK_PATH}")
logger.info(f"URL: {WEBHOOK_URL}")

# Group Configuration
try:
    GROUP_ID = int(os.getenv("GROUP_ID", "0"))
    if GROUP_ID == 0:
        logger.warning("GROUP_ID not set in environment variables")
except ValueError:
    logger.error("Invalid GROUP_ID format in environment variables")
    GROUP_ID = 0

BOT_USERNAME = os.getenv("BOT_USERNAME", "EntreClean_bot")

# Mensajes del bot
WELCOME_MESSAGE = """
🤖 <b>Bot de Moderación EntresHijos</b>

✅ Sistema iniciado correctamente
📝 Funciones activas:
• Monitoreo de fotos de perfil
• Detección de cambios de username
• Sistema automático de advertencias

<i>Bot de moderación profesional - EntresHijos</i>
"""

WARNING_MESSAGE = """
⚠️ <b>Atención @{username}</b>

Se ha detectado un cambio en tu {change_type}.
⏳ Tienes 5 minutos para revertir este cambio.

<i>Este es un mensaje automático del sistema de moderación.</i>
"""

KICK_MESSAGE = """
❌ <b>Usuario Expulsado</b>

• Usuario: @{username}
• Motivo: {change_type}
• Tiempo otorgado: 5 minutos

<i>Acción ejecutada automáticamente por el sistema de moderación.</i>
"""