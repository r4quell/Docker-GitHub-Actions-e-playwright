"""Regras de negócio da auditoria de acessos."""

import time

from logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Indica que um item da fila é inválido, sem interromper o lote."""


def validar_item(item_data: dict) -> str:
    cpf = (item_data.get("cpf") or "").strip()
    if not cpf:
        raise ValidationError("CPF em branco — item inválido para auditoria.")
    return cpf


def acessar_erp(usuario: str, senha: str) -> bool:
    """Simula o login no ERP sem expor a senha em logs."""
    del senha
    logger.info("Acessando sistema com o usuário: %s", usuario)
    time.sleep(1)
    return True


def auditar_usuario(item_data: dict, usuario_erp: str, senha_erp: str) -> dict:
    """Audita um usuário da fila e retorna seu resultado."""
    cpf = validar_item(item_data)
    acessar_erp(usuario_erp, senha_erp)
    time.sleep(1)
    return {
        "cpf": cpf,
        "nome": item_data.get("nome", ""),
        "sistema": item_data.get("sistema", ""),
        "status": "AUDITADO_OK",
    }
