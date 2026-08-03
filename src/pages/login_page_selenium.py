"""Page Object Selenium da tela de login."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page_selenium import BasePageSelenium


class LoginPage(BasePageSelenium):
    CAMPO_USUARIO = (By.ID, "user-name")
    CAMPO_SENHA = (By.ID, "password")
    BOTAO_LOGIN = (By.ID, "login-button")
    FORMULARIO_LOTE = (By.ID, "pagina_formulario")

    def fazer_login(self, usuario, senha):
        campo_usuario = self.wait.until(EC.visibility_of_element_located(self.CAMPO_USUARIO))
        campo_usuario.clear()
        campo_usuario.send_keys(usuario)
        campo_senha = self.wait.until(EC.visibility_of_element_located(self.CAMPO_SENHA))
        campo_senha.clear()
        campo_senha.send_keys(senha)
        self.wait.until(EC.element_to_be_clickable(self.BOTAO_LOGIN)).click()
        self.wait.until(EC.visibility_of_element_located(self.FORMULARIO_LOTE))
