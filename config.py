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

# Determine Replit domain with better error handling
try:
    # Get the REPL_ID first
    REPL_ID = os.getenv("REPL_ID")
    if REPL_ID:
        REPLIT_DOMAIN = f"{REPL_ID}.id.repl.co"
        logger.info(f"Using REPL_ID domain: {REPLIT_DOMAIN}")
    else:
        # Fallback to REPL_SLUG and REPL_OWNER if REPL_ID is not available
        REPL_SLUG = os.getenv("REPL_SLUG")
        REPL_OWNER = os.getenv("REPL_OWNER")
        if not (REPL_SLUG and REPL_OWNER):
            raise ValueError("Neither REPL_ID nor REPL_SLUG/REPL_OWNER are available")
        REPLIT_DOMAIN = f"{REPL_SLUG}.{REPL_OWNER}.repl.co"
        logger.info(f"Using classic domain format: {REPLIT_DOMAIN}")

    # Set up webhook configuration
    WEBHOOK_HOST = f'https://{REPLIT_DOMAIN}'
    WEBHOOK_PATH = f'/webhook/{TOKEN}'
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

except Exception as e:
    logger.error(f"Error configuring Replit domain: {e}")
    raise ValueError("Failed to configure Replit domain. Check environment variables and logs.")

# Web Server Configuration
WEBAPP_HOST = "0.0.0.0"  # Listen on all interfaces
WEBAPP_PORT = 8000

# Group Configuration
try:
    GROUP_ID = int(os.getenv("GROUP_ID", "0"))
    if GROUP_ID == 0:
        logger.warning("GROUP_ID not set in environment variables")
except ValueError:
    logger.error("Invalid GROUP_ID format in environment variables")
    GROUP_ID = 0

BOT_USERNAME = os.getenv("BOT_USERNAME", "EntresHijosBot")

# Mensajes profesionales y estructurados
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

<i>Este es un mensaje automático del sistema de moderación de EntresHijos.</i>
"""

KICK_MESSAGE = """
❌ <b>Usuario Expulsado</b>

• Usuario: @{username}
• Motivo: No revirtió los cambios en {change_type}
• Tiempo otorgado: 5 minutos

<i>Acción ejecutada automáticamente por el sistema de moderación.</i>
"""