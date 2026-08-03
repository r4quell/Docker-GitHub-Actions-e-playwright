"""Configuração dos logs estruturados da automação."""

import logging
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter


def configurar_logger(logs_dir):
    diretorio = Path(logs_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("projeto_pom")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formato = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "nivel"},
    )
    arquivo = logging.FileHandler(
        diretorio / "execucao.log", encoding="utf-8"
    )
    arquivo.setFormatter(formato)
    logger.addHandler(arquivo)
    return logger
