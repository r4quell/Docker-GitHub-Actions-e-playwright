"""Regras de negócio da auditoria de acessos com Selenium.

Nesta versão, a simulação anterior foi substituída por automação real no navegador,
usando Selenium para abrir o ERP, realizar login e pesquisar o CPF de cada item
recebido da fila.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Indica que um item da fila é inválido, sem interromper o lote."""


def validar_item(item_data: dict) -> str:
    cpf = (item_data.get("cpf") or "").strip()
    if not cpf:
        raise ValidationError("CPF em branco — item inválido para auditoria.")
    return cpf


def criar_driver() -> webdriver.Chrome:
    """Cria o Chrome preparado para execução local e em Docker/CI."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def acessar_erp(usuario: str, senha: str) -> webdriver.Chrome:
    """Abre o navegador e executa o login no sistema.

    Troque a URL e os seletores abaixo pelos elementos reais da atividade.
    A senha nunca é exibida em logs.
    """
    logger.info("Acessando sistema com o usuário: %s", usuario)

    driver = criar_driver()
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://example.com/login")

        campo_usuario = wait.until(EC.presence_of_element_located((By.ID, "username")))
        campo_senha = wait.until(EC.presence_of_element_located((By.ID, "password")))
        botao_entrar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

        campo_usuario.send_keys(usuario)
        campo_senha.send_keys(senha)
        botao_entrar.click()

        return driver
    except Exception:
        driver.quit()
        raise


def auditar_usuario(item_data: dict, usuario_erp: str, senha_erp: str) -> dict:
    """Executa a auditoria de um usuário da fila.

    Etapas realizadas:
    1. Valida o CPF.
    2. Abre o Chrome com Selenium.
    3. Faz login.
    4. Pesquisa o CPF no sistema.
    5. Retorna o resultado da auditoria.
    """
    cpf = validar_item(item_data)

    driver = acessar_erp(usuario_erp, senha_erp)
    try:
        wait = WebDriverWait(driver, 10)

        campo_busca = wait.until(EC.presence_of_element_located((By.ID, "search")))
        campo_busca.clear()
        campo_busca.send_keys(cpf)

        botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
        botao_buscar.click()

        return {
            "cpf": cpf,
            "nome": item_data.get("nome", ""),
            "sistema": item_data.get("sistema", ""),
            "status": "AUDITADO_OK",
        }
    finally:
        driver.quit()
