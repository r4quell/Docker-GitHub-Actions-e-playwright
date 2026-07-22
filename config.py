"""Configuração central do Auditor de Acessos."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DADOS_ENTRADA_DIR = BASE_DIR / os.getenv("DADOS_ENTRADA_DIR", "dados_entrada")
LOGS_DIR = BASE_DIR / os.getenv("LOGS_DIR", "logs")
LOG_FILE = LOGS_DIR / "execucao.log"
CSV_ENTRADA = os.getenv("CSV_ENTRADA", "usuarios_auditoria.csv")

MAESTRO_ENABLED = os.getenv("MAESTRO_ENABLED", "false").strip().lower() == "true"
VAULT_ENABLED = os.getenv("VAULT_ENABLED", "false").strip().lower() == "true"
# Aceita os nomes usados no bot de origem e os nomes já existentes neste projeto.
MAESTRO_SERVER = os.getenv("MAESTRO_SERVER", os.getenv("BOTCITY_MAESTRO_SERVER", ""))
MAESTRO_LOGIN = os.getenv("MAESTRO_LOGIN", os.getenv("BOTCITY_MAESTRO_LOGIN", ""))
MAESTRO_KEY = os.getenv("MAESTRO_KEY", os.getenv("BOTCITY_MAESTRO_KEY", ""))
DATAPOOL_LABEL = os.getenv("DATAPOOL_LABEL", "FilaAuditoriaRH")
CREDENTIAL_LABEL = os.getenv("CREDENTIAL_LABEL", "credencial_erp")


def ensure_dirs() -> None:
    """Garante a existência do diretório de logs."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
