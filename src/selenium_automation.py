"""Orquestrador da execução Selenium."""

from navegador import criar_driver
from fluxo_lotes import processar_lotes
from pages.form_page_selenium import FormPage as FormPageSelenium
from pages.login_page_selenium import LoginPage as LoginPageSelenium


def executar(configuracao):
    driver = criar_driver(configuracao.headless)
    try:
        return processar_lotes(
            configuracao,
            LoginPageSelenium(driver, configuracao.timeout),
            FormPageSelenium(driver, configuracao.timeout),
        )
    finally:
        driver.quit()
