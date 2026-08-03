"""Orquestrador da execução Playwright."""

from playwright.sync_api import sync_playwright

from fluxo_lotes import processar_lotes
from pages.form_page import FormPage
from pages.login_page import LoginPage


def executar(configuracao):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=configuracao.headless)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        try:
            return processar_lotes(
                configuracao,
                LoginPage(page, configuracao.timeout),
                FormPage(page, configuracao.timeout),
            )
        finally:
            browser.close()
