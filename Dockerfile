# syntax=docker/dockerfile:1

# ============================================================
# Auditor de Acessos v1.0 - Dockerfile
# Imagem base oficial do Python (slim para reduzir superfície e tamanho)
# ============================================================
FROM python:3.11-slim

# Metadados da imagem
LABEL maintainer="Equipe de Hyperautomation" \
      description="Auditor de Acessos - BotCity Maestro / DataPool / Credentials Vault"

# Evita geração de arquivos .pyc e garante logs sem buffer (aparecem em tempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências de sistema necessárias para Playwright (browsers) e libs nativas
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        ca-certificates \
        gnupg \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# Camada de dependências: copiada e instalada ANTES do código
# para que o Docker reaproveite o cache sempre que somente o
# código da aplicação mudar (e não o requirements.txt).
# ----------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala os browsers do Playwright (necessário apenas se a lib estiver no requirements.txt)
RUN python -m playwright install --with-deps chromium

# ----------------------------------------------------------
# Camada de código da aplicação (muda com mais frequência)
# ----------------------------------------------------------
COPY . .

# Diretório de logs (persistido via volume no docker-compose)
RUN mkdir -p /app/logs

# Variáveis de contexto padrão (podem ser sobrescritas em runtime via --env ou .env)
ENV BOT_ID="auditor001" \
    EXECUTION_ID=""

# Comando padrão de execução do bot
CMD ["python", "main.py"]
