"""Ponto de entrada local da automação."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from configuracao import carregar_configuracao
from orquestrador import executar


def main():
    resumo = executar(carregar_configuracao())
    texto = resumo.formatar()
    print(texto)
    return texto


if __name__ == "__main__":
    main()
