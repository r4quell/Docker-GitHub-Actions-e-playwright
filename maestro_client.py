"""Integração com BotCity Maestro, Credentials Vault e DataPool.

Quando MAESTRO_ENABLED=false, usa uma fila JSON local para permitir testes
completos do Dispatcher e Performer sem acesso ao Maestro.
"""

import json
from pathlib import Path

from config import (
    DATAPOOL_LABEL,
    LOGS_DIR,
    MAESTRO_ENABLED,
    MAESTRO_KEY,
    MAESTRO_LOGIN,
    MAESTRO_SERVER,
    VAULT_ENABLED,
)
from logger import get_logger

logger = get_logger(__name__)


class MaestroClient:
    def __init__(self) -> None:
        self.enabled = MAESTRO_ENABLED
        self.vault_enabled = VAULT_ENABLED
        self._sdk = None
        self.task_id = None
        if self.enabled:
            self._connect()
        else:
            logger.warning("MAESTRO_ENABLED=false — execução em modo offline.")

    def _connect(self) -> None:
        from botcity.maestro import BotMaestroSDK

        try:
            self._sdk = BotMaestroSDK()
            self._sdk.login(server=MAESTRO_SERVER, login=MAESTRO_LOGIN, key=MAESTRO_KEY)
            self.task_id = getattr(self._sdk, "task_id", None)
            logger.info("Conectado ao BotCity Maestro com sucesso.")
        except Exception:
            logger.exception("Falha ao conectar ao BotCity Maestro.")
            raise

    def log(self, message: str) -> None:
        if self.enabled and self._sdk:
            try:
                self._sdk.new_log_entry(activity_label="AuditorAcessos", values={"mensagem": message})
            except Exception:
                logger.exception("Falha ao registrar log no Maestro.")
        logger.info(message)

    def alert(self, title: str, message: str, alert_type: str = "ERROR") -> None:
        if self.enabled and self._sdk:
            try:
                from botcity.maestro import AlertType

                alert = getattr(AlertType, alert_type, AlertType.ERROR)
                self._sdk.alert(task_id=self.task_id, title=title, message=message, alert_type=alert)
            except Exception:
                logger.exception("Falha ao emitir alerta no Maestro.")
        logger.warning("ALERTA [%s]: %s — %s", alert_type, title, message)

    def get_credential(self, label: str, key: str) -> str:
        """Obtém credenciais; a senha jamais é registrada em logs."""
        if self.vault_enabled and self._sdk:
            try:
                return self._sdk.get_credential(label=label, key=key)
            except Exception:
                logger.exception("Falha ao buscar credencial '%s/%s'.", label, key)
                raise
        logger.warning("VAULT_ENABLED=false — usando credencial local fictícia para '%s/%s'.", label, key)
        return {"username": "usuario.teste", "password": "SENHA_FICTICIA_OFFLINE"}.get(key, "")

    def get_datapool(self, label: str | None = None):
        label = label or DATAPOOL_LABEL
        if self.enabled and self._sdk:
            try:
                return self._sdk.get_datapool(label=label)
            except Exception:
                return self._sdk.create_datapool(
                    label=label, columns=["cpf", "nome", "sistema"], auto_retry=False
                )
        return _OfflineDataPool(label)

    def post_artifact(self, filepath: str, artifact_name: str | None = None) -> None:
        artifact_name = artifact_name or Path(filepath).name
        if self.enabled and self._sdk:
            try:
                self._sdk.post_artifact(task_id=self.task_id, artifact_name=artifact_name, filepath=filepath)
                logger.info("Artefato '%s' postado no Maestro.", artifact_name)
                return
            except Exception:
                logger.exception("Falha ao postar artefato no Maestro.")
        logger.info("[OFFLINE] Artefato '%s' mantido localmente em: %s", artifact_name, filepath)

    def finish_task(self, status: str = "SUCCESS", message: str = "") -> None:
        if self.enabled and self._sdk:
            try:
                from botcity.maestro import AutomationTaskFinishStatus

                final_status = getattr(AutomationTaskFinishStatus, status, AutomationTaskFinishStatus.SUCCESS)
                self._sdk.finish_task(task_id=self.task_id, status=final_status, message=message)
            except Exception:
                logger.exception("Falha ao finalizar task no Maestro.")
        logger.info("Execução finalizada — status=%s — %s", status, message)


class _OfflineDataPoolItem:
    def __init__(self, data: dict, index: int, pool: "_OfflineDataPool") -> None:
        self._data = data
        self._index = index
        self._pool = pool

    def get(self, key: str):
        return self._data.get(key)

    def report(self, status: str, message: str = "") -> None:
        self._pool._report(self._index, status, message)


class _OfflineDataPool:
    def __init__(self, label: str) -> None:
        self.label = label
        self.path = LOGS_DIR / f"datapool_{label}.json"
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, items: list[dict]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(items, file, ensure_ascii=False, indent=2)

    def create_items(self, items: list[dict]) -> None:
        queued_items = self._load()
        for item in items:
            queued_item = dict(item)
            queued_item.setdefault("_status", "PENDING")
            queued_item.setdefault("_message", "")
            queued_items.append(queued_item)
        self._save(queued_items)
        logger.info("[OFFLINE] %d itens adicionados à fila '%s'.", len(items), self.label)

    def next(self):
        for index, item in enumerate(self._load()):
            if item.get("_status") == "PENDING":
                return _OfflineDataPoolItem(item, index, self)
        return None

    def _report(self, index: int, status: str, message: str) -> None:
        items = self._load()
        items[index]["_status"] = status
        items[index]["_message"] = message
        self._save(items)
