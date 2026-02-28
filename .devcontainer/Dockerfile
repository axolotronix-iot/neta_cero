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
    postgresql-client \
    bash-completion \
    zsh \
    fzf \
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
        paho-mqtt==2.1.0 \
        aiomqtt==2.5.0 \
        fastapi==0.129.0 \
        uvicorn[standard]==0.34.0 \
        psycopg2-binary==2.9.10 \
        sqlalchemy==2.0.46 \
        alembic==1.14.0 \
        asyncpg==0.30.0 \
        pydantic==2.10.0 \
        pydantic-settings==2.7.0
# && /opt/venv/bin/pip install grafanalib

# ----------------------------------------
# Usuario y Directorio
# ----------------------------------------
WORKDIR /workspace
RUN useradd -ms /bin/bash vscode && chown -R vscode:vscode /workspace

# El venv se activa para todo el sistema (incluyendo VS Code) aquí:
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER vscode

# ----------------------------------------
# Mantener contenedor corriendo
CMD ["sleep", "infinity"]
