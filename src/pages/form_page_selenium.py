"""Page Object Selenium da tela de formulário de lote."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pages.base_page_selenium import BasePageSelenium


class FormPage(BasePageSelenium):
    CAMPO_NUMERO_LOTE = (By.ID, "numero_lote")
    CAMPO_PRODUTO = (By.ID, "produto")
    CAMPO_STATUS = (By.ID, "status")
    BOTAO_ENVIAR = (By.ID, "btn_enviar")
    MENSAGEM_SUCESSO = (By.ID, "mensagem_sucesso")
    TEXTO_SUCESSO = "Lote cadastrado com sucesso!"

    def preencher_formulario(self, dados_lote: dict):
        numero_lote = dados_lote.get("lote", dados_lote.get("numero_lote"))
        campo_lote = self.wait.until(EC.visibility_of_element_located(self.CAMPO_NUMERO_LOTE))
        campo_lote.clear()
        campo_lote.send_keys(numero_lote)
        Select(self.wait.until(EC.element_to_be_clickable(self.CAMPO_PRODUTO))).select_by_visible_text(dados_lote["produto"])
        Select(self.wait.until(EC.element_to_be_clickable(self.CAMPO_STATUS))).select_by_visible_text(dados_lote["status"])
        self.wait.until(EC.element_to_be_clickable(self.BOTAO_ENVIAR)).click()

    def is_sucesso(self) -> bool:
        try:
            mensagem = self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_SUCESSO))
            return mensagem.text.strip() == self.TEXTO_SUCESSO
        except TimeoutException:
            return False
