# Imagen base de Python
FROM python:3.9

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Especificar comando de inicio
CMD ["python", "bot.py"]
