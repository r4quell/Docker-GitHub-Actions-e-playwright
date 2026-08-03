"""DataPool local e fictício para execução segura do laboratório."""

import json
from copy import deepcopy
from pathlib import Path


class DataPoolSimulado:
    """Lê itens fictícios e persiste o resultado de cada processamento."""

    def __init__(self, entrada, resultado):
        self.entrada = Path(entrada)
        self.resultado = Path(resultado)
        self._itens = self._carregar()

    def _carregar(self):
        with self.entrada.open(encoding="utf-8") as arquivo:
            itens = json.load(arquivo)
        if not isinstance(itens, list):
            raise ValueError("O DataPool deve conter uma lista de itens.")
        return itens

    def itens_pendentes(self):
        for item in self._itens:
            yield deepcopy(item)

    def atualizar(self, item_id, status, screenshot, mensagem):
        for item in self._itens:
            if item.get("id") == item_id:
                item["resultado"] = {
                    "status": status,
                    "screenshot": str(screenshot),
                    "mensagem": mensagem,
                }
                self._salvar()
                return
        raise KeyError(f"Item inexistente no DataPool: {item_id}")

    def _salvar(self):
        self.resultado.parent.mkdir(parents=True, exist_ok=True)
        with self.resultado.open("w", encoding="utf-8") as arquivo:
            json.dump(self._itens, arquivo, ensure_ascii=False, indent=2)
