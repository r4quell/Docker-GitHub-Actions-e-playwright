"""Ponto de entrada do robô no BotCity Maestro."""

import os

from botcity.maestro import AutomationTaskFinishStatus, BotMaestroSDK

from main import main


def executar_bot():
    maestro = BotMaestroSDK.from_sys_args()
    task_id = None

    if maestro.is_online:
        task_id = maestro.get_execution().task_id
        os.environ.setdefault("APP_HEADLESS", "true")

    try:
        resultado = main()
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message=resultado,
            )
    except Exception as erro:
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Falha no cadastro do lote: {erro}",
            )
        raise


if __name__ == "__main__":
    executar_bot()
