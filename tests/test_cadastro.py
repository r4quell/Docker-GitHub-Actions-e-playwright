"""Teste integrado do DataPool, POM, evidências e logs."""

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from configuracao import Configuracao, obter_url_aplicacao
from orquestrador import executar


@pytest.mark.parametrize("tecnologia", ["selenium", "playwright"])
def test_processar_datapool_com_sucesso(tmp_path, tecnologia):
    configuracao = Configuracao(
        url=obter_url_aplicacao(),
        usuario="usuario_teste",
        credencial="credencial_teste",
        headless=True,
        timeout=10,
        datapool_entrada=PROJECT_ROOT / "resources" / "datapool_lotes.json",
        datapool_resultado=tmp_path / "logs" / "datapool_resultado.json",
        evidencias_dir=tmp_path / "evidencias",
        logs_dir=tmp_path / "logs",
        tecnologia=tecnologia,
    )

    resumo = executar(configuracao)

    assert resumo.processados == 3
    assert resumo.sucessos == 3
    assert resumo.erros == 0

    with configuracao.datapool_resultado.open(encoding="utf-8") as arquivo:
        itens = json.load(arquivo)

    assert all(item["resultado"]["status"] == "Sucesso" for item in itens)
    assert all(
        Path(item["resultado"]["screenshot"]).is_file() for item in itens
    )
    assert (configuracao.logs_dir / "execucao.log").is_file()
