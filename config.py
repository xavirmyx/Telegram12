import os

# Bot Configuration
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")  # Will be replaced by secret
REPLIT_DOMAIN = os.getenv("REPL_SLUG", "") + "." + os.getenv("REPL_OWNER", "") + ".repl.co"
WEBHOOK_HOST = f'https://{REPLIT_DOMAIN}'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Web Server Configuration
WEBAPP_HOST = "0.0.0.0"  # Para que sea accesible desde fuera
WEBAPP_PORT = 8000

# Group Configuration
GROUP_ID = -1001234567890  # Replace with actual group ID
BOT_USERNAME = "EntresHijosBot"

# Messages
WELCOME_MESSAGE = """
🤖 Bot de moderación EntresHijos iniciado
✅ Monitoreando cambios de perfil y username
"""

WARNING_MESSAGE = """
⚠️ @{username}, has realizado cambios en tu {change_type}.
⏳ Tienes 5 minutos para revertir el cambio o serás expulsado.
"""

KICK_MESSAGE = """
❌ @{username} ha sido expulsado.
📝 Motivo: No revirtió los cambios de {change_type} en el tiempo establecido.
"""