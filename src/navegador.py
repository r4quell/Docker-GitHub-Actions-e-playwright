"""Criação padronizada do navegador."""

from selenium import webdriver


def criar_driver(headless=False):
    opcoes = webdriver.ChromeOptions()
    if headless:
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opcoes)
