"""
logger_config.py

Modulo central de logging estruturado do Auditor de Acessos.

Adiciona contexto de rastreabilidade (EXECUTION_ID e BOT_ID) a cada
linha de log, emitindo registros em formato JSON via python-json-logger.

Uso:
    from logger_config import get_logger

    logger = get_logger(__name__)
    logger.info("Auditoria iniciada")
"""

import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

# Carrega a configuração local antes de qualquer módulo consultar o ambiente.
# No Docker, as variáveis já são injetadas pelo compose e têm precedência.
load_dotenv()

LOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.getenv("LOGS_DIR", "logs")
)
LOG_FILE = os.path.join(LOG_DIR, "execucao.log")

# EXECUTION_ID: se não vier definido via variável de ambiente (ex: injetado
# pelo Maestro ou pelo docker-compose), geramos um identificador único
# para esta execução do processo.
EXECUTION_ID = os.getenv("EXECUTION_ID") or str(uuid.uuid4())
BOT_ID = os.getenv("BOT_ID", "auditor001")


class ContextFilter(logging.Filter):
    """Injeta execution_id e bot_id em todo registro de log."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.execution_id = EXECUTION_ID
        record.bot_id = BOT_ID
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Garante ordem/campos fixos no JSON de saída."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["execution_id"] = getattr(record, "execution_id", EXECUTION_ID)
        log_record["bot_id"] = getattr(record, "bot_id", BOT_ID)
        log_record["message"] = record.getMessage()
        # Remove duplicidade do campo "msg" padrão do logging, se presente
        log_record.pop("msg", None)


def _build_handler(handler: logging.Handler) -> logging.Handler:
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(execution_id)s %(bot_id)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())
    return handler


def get_logger(name: str = "auditor_acessos") -> logging.Logger:
    """Retorna um logger configurado com saída estruturada em JSON,
    gravando simultaneamente em arquivo (logs/execucao.log) e no console.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Já configurado (evita handlers duplicados em múltiplas chamadas)
        return logger

    logger.setLevel(logging.INFO)

    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    console_handler = logging.StreamHandler(sys.stdout)

    logger.addHandler(_build_handler(file_handler))
    logger.addHandler(_build_handler(console_handler))

    logger.propagate = False
    return logger
