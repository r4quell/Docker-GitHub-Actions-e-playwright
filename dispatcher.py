"""Etapa A: lê o CSV de entrada e insere seus itens no DataPool."""

import csv
import sys

from config import CSV_ENTRADA, DADOS_ENTRADA_DIR, DATAPOOL_LABEL, ensure_dirs
from logger import get_logger
from maestro_client import MaestroClient

logger = get_logger(__name__)


def ler_csv() -> list[dict]:
    """Lê e normaliza os registros de auditoria do CSV."""
    path = DADOS_ENTRADA_DIR / CSV_ENTRADA
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {
                "cpf": (row.get("cpf") or "").strip(),
                "nome": (row.get("nome") or "").strip(),
                "sistema": (row.get("sistema") or "").strip(),
            }
            for row in csv.DictReader(file, delimiter=";")
        ]


def main() -> int:
    ensure_dirs()
    maestro = MaestroClient()
    maestro.log("Dispatcher: iniciando carga da fila de auditoria")

    if not DADOS_ENTRADA_DIR.is_dir():
        message = f"Pasta de dados de entrada ausente: {DADOS_ENTRADA_DIR}."
        logger.error(message)
        maestro.alert(title="Pasta de dados de entrada ausente", message=message)
        return 1

    try:
        items = ler_csv()
    except FileNotFoundError:
        message = f"Arquivo '{CSV_ENTRADA}' não encontrado em {DADOS_ENTRADA_DIR}."
        logger.error(message)
        maestro.alert(title="Arquivo CSV ausente", message=message)
        return 1

    if not items:
        logger.warning("CSV lido, mas nenhum item foi encontrado.")

    maestro.get_datapool(DATAPOOL_LABEL).create_items(items)
    maestro.log("Dispatcher: %d itens enviados para a fila '%s'." % (len(items), DATAPOOL_LABEL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
