"""Operações comuns aos Page Objects Selenium."""

from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait


class BasePageSelenium:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def abrir(self, url):
        self.driver.get(url)

    def salvar_screenshot(self, destino):
        caminho = Path(destino)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not self.driver.save_screenshot(str(caminho)):
            raise RuntimeError(f"Não foi possível salvar a evidência: {caminho}")
        return caminho
