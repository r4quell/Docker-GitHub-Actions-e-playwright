"""Page Object Playwright da tela de login."""

from pages.base_page import BasePage


class LoginPage(BasePage):
    CAMPO_USUARIO = "#user-name"
    CAMPO_SENHA = "#password"
    BOTAO_LOGIN = "#login-button"
    FORMULARIO_LOTE = "#pagina_formulario"

    def __init__(self, page, timeout=10):
        super().__init__(page, timeout)
        self.campo_usuario = page.locator(self.CAMPO_USUARIO)
        self.campo_senha = page.locator(self.CAMPO_SENHA)
        self.botao_login = page.locator(self.BOTAO_LOGIN)
        self.formulario_lote = page.locator(self.FORMULARIO_LOTE)

    def fazer_login(self, usuario, senha):
        self.campo_usuario.fill(usuario)
        self.campo_senha.fill(senha)
        self.botao_login.click()
        self.formulario_lote.wait_for(state="visible")
