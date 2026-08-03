"""Operações comuns aos Page Objects Playwright."""

from pathlib import Path


class BasePage:
    def __init__(self, page, timeout=10):
        self.page = page
        self.timeout_ms = timeout * 1000
        self.page.set_default_timeout(self.timeout_ms)

    def abrir(self, url):
        self.page.goto(url)

    def salvar_screenshot(self, destino):
        caminho = Path(destino)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(caminho), full_page=True)
        return caminho
