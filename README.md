# Auditor de Acessos V2 com Selenium

Bot corporativo para auditoria de acessos, baseado no fluxo original fornecido:

1. O **Dispatcher** lê o CSV e envia os usuários para o DataPool.
2. O **Performer** consome a fila, valida os dados, consulta as credenciais e registra o resultado.

O projeto pode operar integrado ao **BotCity Maestro**, **DataPool** e **Credentials Vault** ou em modo offline, com fila persistida em `logs/`.

## Tecnologia
Para a automaização web, utilizou-se selenium

## Estrutura

```text
.
├── bot.py                              # regras de validação e auditoria
├── config.py                           # configuração via .env
├── dispatcher.py                       # Etapa A: carga da fila
├── maestro_client.py                   # Maestro, Vault e DataPool/offline
├── main.py                             # Etapa B: Performer
├── dados_entrada/usuarios_auditoria.csv
├── logger_config.py / logger.py        # logs JSON no console e em arquivo
├── Dockerfile
└── docker-compose.yml
```

## Configuração

Preencha `.env`. Para testar sem serviços externos, mantenha:

```env
MAESTRO_ENABLED=false
VAULT_ENABLED=false
```

Nesse modo, o DataPool é armazenado em `logs/datapool_FilaAuditoriaRH.json`, e credenciais fictícias são usadas apenas em memória. Senhas não são registradas nos logs.

Para integrar ao Maestro, defina `MAESTRO_ENABLED=true`, `VAULT_ENABLED=true`, as credenciais `BOTCITY_MAESTRO_SERVER`, `BOTCITY_MAESTRO_LOGIN` e `BOTCITY_MAESTRO_KEY`, além dos labels de DataPool e Credential Vault.

## Execução local

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Etapa A: carrega dados_entrada/usuarios_auditoria.csv
python dispatcher.py

# Etapa B: processa os itens da fila
python main.py
```

O relatório final é salvo em `logs/relatorio_execucao.json`. Itens sem CPF são marcados como erro, mas não interrompem o processamento dos demais itens.

## Docker

```bash
docker compose build
docker compose run bot python dispatcher.py
docker compose run bot
```
