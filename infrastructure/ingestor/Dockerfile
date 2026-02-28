# Imagen base oficial de Python 3.12 sobre Debian Bookworm (versión slim = más ligera)
# Ya incluye Python y pip correctamente instalados y mantenidos.
FROM python:3.12-slim-bookworm

# Evita que Python genere archivos .pyc (bytecode).
# Reduce escrituras innecesarias en disco dentro del contenedor.
ENV PYTHONDONTWRITEBYTECODE=1
# Hace que stdout y stderr no se buferen.
# Esto es importante para que los logs se vean inmediatamente en `docker logs`.
ENV PYTHONUNBUFFERED=1

# Define el directorio de trabajo dentro del contenedor.
# Todos los comandos siguientes se ejecutarán desde /app.
WORKDIR /app

# Copia únicamente el archivo de dependencias primero.
# Esto permite aprovechar el cache de Docker si el código cambia
# pero las dependencias no.
COPY requirements.txt .

# Instala las dependencias Python.
# --no-cache-dir evita guardar cache de pip, reduciendo tamaño final.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente al contenedor.
COPY src/ingestor ./ingestor

# Comando por defecto al arrancar el contenedor.
# Ejecuta tu aplicación principal.
CMD ["python", "-m", "ingestor.main"]