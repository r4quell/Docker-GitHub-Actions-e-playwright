"""Page Object Playwright da tela de formulário de lote."""

from pages.base_page import BasePage


class FormPage(BasePage):
    CAMPO_NUMERO_LOTE = "#numero_lote"
    CAMPO_PRODUTO = "#produto"
    CAMPO_STATUS = "#status"
    BOTAO_ENVIAR = "#btn_enviar"
    MENSAGEM_SUCESSO = "#mensagem_sucesso"
    TEXTO_SUCESSO = "Lote cadastrado com sucesso!"

    def __init__(self, page, timeout=10):
        super().__init__(page, timeout)
        self.campo_numero_lote = page.locator(self.CAMPO_NUMERO_LOTE)
        self.campo_produto = page.locator(self.CAMPO_PRODUTO)
        self.campo_status = page.locator(self.CAMPO_STATUS)
        self.botao_enviar = page.locator(self.BOTAO_ENVIAR)
        self.mensagem_sucesso = page.locator(self.MENSAGEM_SUCESSO)

    def preencher_formulario(self, dados_lote: dict):
        numero_lote = dados_lote.get("lote", dados_lote.get("numero_lote"))
        self.campo_numero_lote.fill(numero_lote)
        self.campo_produto.select_option(label=dados_lote["produto"])
        self.campo_status.select_option(label=dados_lote["status"])
        self.botao_enviar.click()

    def is_sucesso(self) -> bool:
        try:
            self.mensagem_sucesso.wait_for(state="visible")
            return self.mensagem_sucesso.inner_text().strip() == self.TEXTO_SUCESSO
        except Exception:
            return False
