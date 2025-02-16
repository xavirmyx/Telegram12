# Usar una imagen ligera de Python
FROM python:3.9-slim

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto (no necesario para bots, pero útil si agregas un panel)
EXPOSE 8000

# Ejecutar el bot
CMD ["python", "bot.py"]
