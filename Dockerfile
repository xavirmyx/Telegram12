# Usa una imagen ligera de Python
FROM python:3.9-slim

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Actualizar pip antes de instalar dependencias
RUN pip install --upgrade pip

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar el bot
CMD ["python", "bot.py"]
