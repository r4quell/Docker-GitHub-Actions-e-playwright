"""
web_automation.py

Modulo de automacao web com Playwright para o Auditor de Acessos.

Usa exclusivamente locators semanticos (get_by_role, get_by_label,
get_by_placeholder) em vez de seletores CSS/XPath frageis, tornando
os scripts mais resilientes a mudancas de layout/HTML.
"""

import os

from playwright.sync_api import sync_playwright

from logger_config import get_logger

logger = get_logger(__name__)


def _get_headless_value(value: str) -> bool:
    """Converte uma variável de ambiente em valor booleano."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def run_form_automation(target_url: str | None = None, headless: bool | None = None) -> dict:
    """Abre uma pagina de teste, preenche um formulario e retorna o resultado.

    Args:
        target_url: URL da pagina de teste. Se None, usa PLAYWRIGHT_TARGET_URL do .env.
        headless: Executar sem interface grafica. Se None, usa PLAYWRIGHT_HEADLESS do .env.

    Returns:
        dict com o resumo da execucao (sucesso, url, timestamp de log ja registrado).
    """
    target_url = target_url or os.getenv(
        "PLAYWRIGHT_TARGET_URL", "http://localhost:8080/formulario-teste"
    )
    if headless is None:
        headless = _get_headless_value(os.getenv("PLAYWRIGHT_HEADLESS", "true"))

    logger.info("Iniciando automacao web com Playwright", extra={"target_url": target_url})

    resultado = {"sucesso": False, "url": target_url}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            page.goto(target_url, wait_until="domcontentloaded")

            # --- Preenchimento com locators semanticos ---
            page.get_by_label("Nome").fill("Usuário Teste")

            # Selecao de opcao em <select>, referenciado pelo role de combobox
            page.get_by_role("combobox").select_option("opcao1")

            # Campo de usuario, buscado por placeholder quando nao ha <label> associado
            page.get_by_placeholder("Digite seu usuário").fill("teste")

            # Envio do formulario via role semantico de botao
            page.get_by_role("button", name="Enviar").click()

            resultado["sucesso"] = True
            logger.info("Automacao web concluida com sucesso")

        except Exception as exc:  # noqa: BLE001
            logger.exception("Falha na automacao web: %s", str(exc))
            resultado["erro"] = str(exc)
            raise

        finally:
            browser.close()

    return resultado


if __name__ == "__main__":
    run_form_automation()
