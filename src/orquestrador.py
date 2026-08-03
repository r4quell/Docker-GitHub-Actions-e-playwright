"""Seleciona o orquestrador da tecnologia configurada."""


def executar(configuracao):
    if configuracao.tecnologia == "playwright":
        from web_automation import executar as executar_playwright

        return executar_playwright(configuracao)
    if configuracao.tecnologia == "selenium":
        from selenium_automation import executar as executar_selenium

        return executar_selenium(configuracao)
    raise ValueError("APP_TECNOLOGIA deve ser 'playwright' ou 'selenium'.")
