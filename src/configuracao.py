"""Configuração segura e centralizada da automação."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _booleano(nome, padrao=False):
    valor = os.getenv(nome, str(padrao)).strip().lower()
    return valor in {"1", "true", "yes", "sim"}


def obter_url_aplicacao():
    portal = BASE_DIR / "resources" / "portal_fake" / "index.html"
    url = os.getenv("APP_URL", "").strip()
    marcadores = (
        "URL-REAL-DO-LABORATORIO",
        "SUBSTITUA-PELA-URL",
        "ENDERECO-REAL-DA-APLICACAO",
    )
    if not url or any(item in url.upper() for item in marcadores):
        return portal.as_uri()
    return url


def _variavel_obrigatoria(nome):
    valor = os.getenv(nome, "").strip()
    if not valor:
        raise RuntimeError(
            f"Variável {nome} não configurada. Copie .env.example para .env."
        )
    return valor


@dataclass(frozen=True)
class Configuracao:
    url: str
    usuario: str
    credencial: str
    headless: bool
    timeout: int
    datapool_entrada: Path
    datapool_resultado: Path
    evidencias_dir: Path
    logs_dir: Path
    tecnologia: str = "selenium"


def carregar_configuracao():
    """Carrega ambiente sem manter credenciais no código-fonte."""
    tecnologia = os.getenv("APP_TECNOLOGIA", "selenium").strip().lower()
    return Configuracao(
        url=obter_url_aplicacao(),
        usuario=_variavel_obrigatoria("APP_USUARIO"),
        credencial=_variavel_obrigatoria("APP_SENHA"),
        headless=_booleano("APP_HEADLESS"),
        timeout=int(os.getenv("APP_TIMEOUT", "10")),
        datapool_entrada=Path(
            os.getenv(
                "DATAPOOL_ENTRADA",
                BASE_DIR / "resources" / "datapool_lotes.json",
            )
        ),
        datapool_resultado=Path(
            os.getenv(
                "DATAPOOL_RESULTADO",
                BASE_DIR / "logs" / "datapool_resultado.json",
            )
        ),
        evidencias_dir=Path(
            os.getenv("EVIDENCIAS_DIR", BASE_DIR / "evidencias")
        ),
        logs_dir=Path(os.getenv("LOGS_DIR", BASE_DIR / "logs")),
        tecnologia=tecnologia,
    )
