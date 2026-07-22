"""Etapa B: Performer que consome e audita os itens do DataPool."""

import json
import sys
from datetime import datetime
from pathlib import Path

from bot import ValidationError, auditar_usuario
from config import CREDENTIAL_LABEL, DATAPOOL_LABEL, LOGS_DIR, ensure_dirs
from logger import get_logger
from maestro_client import MaestroClient

logger = get_logger(__name__)


class ExecutionResult:
    """Resumo serializável da execução do Performer."""

    def __init__(self) -> None:
        self.inicio = datetime.now()
        self.fim: datetime | None = None
        self.total_processados = 0
        self.total_sucesso = 0
        self.total_erro = 0
        self.erros: list[dict] = []

    def registrar_sucesso(self) -> None:
        self.total_processados += 1
        self.total_sucesso += 1

    def registrar_erro(self, item_data: dict, motivo: str) -> None:
        self.total_processados += 1
        self.total_erro += 1
        self.erros.append({"item": item_data, "motivo": motivo})

    def finalizar(self) -> None:
        self.fim = datetime.now()

    def to_dict(self) -> dict:
        return {
            "inicio": self.inicio.isoformat(),
            "fim": self.fim.isoformat() if self.fim else None,
            "duracao_segundos": (self.fim - self.inicio).total_seconds() if self.fim else None,
            "total_processados": self.total_processados,
            "total_sucesso": self.total_sucesso,
            "total_erro": self.total_erro,
            "erros": self.erros,
        }

    def salvar_json(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2)


def main() -> int:
    ensure_dirs()
    maestro = MaestroClient()
    maestro.log("Iniciando auditoria de acessos")

    try:
        usuario_erp = maestro.get_credential(CREDENTIAL_LABEL, "username")
        senha_erp = maestro.get_credential(CREDENTIAL_LABEL, "password")
    except Exception:
        message = "Não foi possível obter as credenciais do ERP."
        logger.exception(message)
        maestro.alert(title="Falha ao obter credenciais", message=message)
        maestro.finish_task(status="FAILED", message=message)
        return 1

    datapool = maestro.get_datapool(DATAPOOL_LABEL)
    result = ExecutionResult()

    while item := datapool.next():
        item_data = {key: item.get(key) for key in ("cpf", "nome", "sistema")}
        try:
            auditar_usuario(item_data, usuario_erp, senha_erp)
            item.report(status="DONE", message="Auditado com sucesso")
            result.registrar_sucesso()
            logger.info("Item auditado com sucesso: %s (%s)", item_data["nome"], item_data["cpf"])
        except ValidationError as error:
            item.report(status="ERROR", message=str(error))
            result.registrar_erro(item_data, str(error))
            logger.error("Erro de validação no item %s: %s", item_data, error)
        except Exception as error:  # noqa: BLE001
            message = f"Erro inesperado: {error}"
            item.report(status="ERROR", message=message)
            result.registrar_erro(item_data, message)
            logger.exception("Erro inesperado ao processar o item %s", item_data)

    result.finalizar()
    report_path = LOGS_DIR / "relatorio_execucao.json"
    result.salvar_json(report_path)
    maestro.post_artifact(str(report_path), "relatorio_execucao.json")

    final_status = "SUCCESS" if result.total_erro == 0 else "PARTIAL_SUCCESS"
    maestro.finish_task(
        status=final_status,
        message=f"{result.total_sucesso} sucesso(s), {result.total_erro} erro(s)",
    )
    logger.info("Execução concluída: %s", result.to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
