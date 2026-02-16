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
        alembic==1.14.0
# && /opt/venv/bin/pip install grafanalib

# ----------------------------------------
# Crear directorio de trabajo y usuario no root
# ----------------------------------------
WORKDIR /workspace
RUN useradd -ms /usr/bin/zsh vscode \
    && chown -R vscode:vscode /workspace

# Instalar zsh autosuggestions
RUN git clone https://github.com/zsh-users/zsh-autosuggestions \
    /usr/share/zsh-autosuggestions

# Configurar venv automático limpio (sin duplicado)
RUN echo 'export VIRTUAL_ENV=/opt/venv' >> /home/vscode/.zshrc \
    && echo 'export PATH="$VIRTUAL_ENV/bin:$PATH"' >> /home/vscode/.zshrc \
    && echo 'autoload -Uz colors && colors' >> /home/vscode/.zshrc \
    && echo 'PROMPT="%F{green}(venv)%f %F{blue}%n@%m%f:%F{cyan}%~%f %# "' >> /home/vscode/.zshrc \
    && echo 'source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh' >> /home/vscode/.zshrc \
    && chown vscode:vscode /home/vscode/.zshrc

USER vscode

# ----------------------------------------
# Mantener contenedor corriendo
CMD ["sleep", "infinity"]
