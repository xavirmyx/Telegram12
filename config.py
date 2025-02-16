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
WEBAPP_PORT = int(os.getenv("PORT", "8000"))

# Determine Replit domain
def get_replit_domain():
    """Get the Replit domain with proper validation"""
    repl_id = os.getenv('REPL_ID')
    repl_slug = os.getenv('REPL_SLUG', '').lower()

    if repl_id:
        domain = f"{repl_id}.id.repl.co"
        logger.info(f"Using Repl ID domain: {domain}")
        return domain
    elif repl_slug:
        domain = f"{repl_slug}.repl.co"
        logger.info(f"Using Repl slug domain: {domain}")
        return domain
    else:
        raise ValueError("No valid Replit configuration found")

try:
    REPLIT_DOMAIN = get_replit_domain()
    logger.info(f"Final Replit domain: {REPLIT_DOMAIN}")
except Exception as e:
    logger.error(f"Error determining Replit domain: {e}")
    raise

# Webhook Configuration
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://{REPLIT_DOMAIN}{WEBHOOK_PATH}"
logger.info(f"Webhook URL configured as: {WEBHOOK_URL}")

# Group Configuration
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "EntreClean_bot")

# Bot Messages
WELCOME_MESSAGE = """
🤖 <b>Bot de Moderación EntresHijos</b>

✅ Sistema iniciado correctamente
📝 Funciones activas:
• Monitoreo de fotos de perfil
• Detección de cambios de username
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