# ========================================
# Dockerfile Dev Container Neta Cero IoT
# ========================================

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ----------------------------------------
# Instalar utilidades básicas
# ----------------------------------------
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    build-essential \
    vim \
    htop \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------
# Configurar python -> python3
# ----------------------------------------
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# ----------------------------------------
# Crear venv fuera del workspace para que no se borre al montar volumen
# ----------------------------------------
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install \
        paho-mqtt \
        fastapi \
        uvicorn[standard] \
        psycopg2-binary \
        sqlalchemy \
        alembic
# && /opt/venv/bin/pip install grafanalib

# ----------------------------------------
# Crear directorio de trabajo y usuario no root
# ----------------------------------------
WORKDIR /workspace
RUN useradd -ms /bin/bash vscode \
    && chown -R vscode:vscode /workspace
USER vscode

# ----------------------------------------
# Activar venv por defecto al abrir shell
ENV PATH="/opt/venv/bin:$PATH"

# ----------------------------------------
# Mantener contenedor corriendo
CMD ["sleep", "infinity"]
