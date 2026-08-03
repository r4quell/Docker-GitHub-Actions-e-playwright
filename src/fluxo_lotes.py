"""Regra de negócio compartilhada pelos orquestradores web."""

from dataclasses import dataclass
from datetime import datetime
from time import monotonic

from datapool import DataPoolSimulado
from logging_config import configurar_logger


@dataclass
class ResumoExecucao:
    processados: int = 0
    sucessos: int = 0
    erros: int = 0
    duracao_segundos: float = 0

    def formatar(self):
        segundos = int(self.duracao_segundos)
        tempo = f"{segundos // 3600:02d}:{(segundos % 3600) // 60:02d}:{segundos % 60:02d}"
        return (
            "\nResumo\n"
            f"Itens processados: {self.processados}\n"
            f"Sucesso: {self.sucessos}\n"
            f"Erro: {self.erros}\n"
            f"Tempo: {tempo}"
        )


def _nome_evidencia(item_id):
    agora = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    identificador = "".join(c if c.isalnum() else "_" for c in str(item_id))
    return f"{identificador}_{agora}.png"


def processar_lotes(configuracao, login_page, form_page):
    """Executa decisões, logs, evidências e persistência sem acessar a UI diretamente."""
    inicio = monotonic()
    resumo = ResumoExecucao()
    logger = configurar_logger(configuracao.logs_dir)
    datapool = DataPoolSimulado(configuracao.datapool_entrada, configuracao.datapool_resultado)

    logger.info("Execução iniciada", extra={"tecnologia": configuracao.tecnologia})
    login_page.abrir(configuracao.url)
    login_page.fazer_login(configuracao.usuario, configuracao.credencial)

    for item in datapool.itens_pendentes():
        resumo.processados += 1
        item_id = item.get("id", f"item_{resumo.processados}")
        screenshot = configuracao.evidencias_dir / _nome_evidencia(item_id)
        logger.info("Item iniciado", extra={"item_id": item_id})
        try:
            form_page.preencher_formulario(item)
            if not form_page.is_sucesso():
                raise AssertionError("A confirmação de cadastro não foi exibida.")
            form_page.salvar_screenshot(screenshot)
            datapool.atualizar(item_id, "Sucesso", screenshot, form_page.TEXTO_SUCESSO)
            resumo.sucessos += 1
            logger.info("Item processado", extra={"item_id": item_id, "screenshot": str(screenshot)})
        except Exception as erro:
            resumo.erros += 1
            screenshot_registrado = ""
            try:
                form_page.salvar_screenshot(screenshot)
                screenshot_registrado = screenshot
            except Exception as erro_screenshot:
                logger.warning("Falha ao gerar screenshot", extra={"item_id": item_id, "erro": str(erro_screenshot)})
            datapool.atualizar(item_id, "Erro", screenshot_registrado, str(erro))
            logger.exception("Falha ao processar item", extra={"item_id": item_id, "screenshot": str(screenshot_registrado)})

    resumo.duracao_segundos = monotonic() - inicio
    logger.info("Execução finalizada", extra={"processados": resumo.processados, "sucessos": resumo.sucessos, "erros": resumo.erros, "duracao_segundos": round(resumo.duracao_segundos, 3)})
    return resumo
