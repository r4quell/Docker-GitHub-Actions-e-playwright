"""Gera o pacote ZIP para publicação no BotCity Maestro."""

import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_ZIP = BASE_DIR / "ProjetoPOMCadastroLotes.zip"
INCLUIR = [
    "bot.py",
    "bot.yaml",
    "main.py",
    "requirements.txt",
    "src",
    "resources",
    "docs",
]
IGNORAR = {".git", ".venv", "__pycache__", ".pytest_cache"}


def deve_ignorar(caminho):
    return any(parte in IGNORAR for parte in caminho.parts) or (
        caminho.suffix == ".pyc"
    )


def gerar_pacote():
    with zipfile.ZipFile(ARQUIVO_ZIP, "w", zipfile.ZIP_DEFLATED) as pacote:
        for nome in INCLUIR:
            origem = BASE_DIR / nome
            if origem.is_file():
                pacote.write(origem, origem.relative_to(BASE_DIR))
                continue

            for arquivo in origem.rglob("*"):
                if arquivo.is_file() and not deve_ignorar(arquivo):
                    pacote.write(arquivo, arquivo.relative_to(BASE_DIR))

    print(f"Pacote BotCity gerado: {ARQUIVO_ZIP}")


if __name__ == "__main__":
    gerar_pacote()
