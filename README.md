# Auditor de Acessos 

Bot de auditoria de acessos construído em Python sobre o ecossistema
**BotCity Maestro**, **DataPool** e **Credentials Vault**, agora com:

- ✅ Containerização via Docker / Docker Compose
- ✅ Pipeline de CI com GitHub Actions
- ✅ Logs estruturados em JSON com `execution_id` e `bot_id`
- ✅ Automação web com Playwright usando locators semânticos

## Estrutura do projeto

```
.
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── .env
├── requirements.txt
├── main.py                # ponto de entrada: auditoria + automação web
├── logger_config.py        # logging estruturado (JSON) com contexto
├── web_automation.py        # automação Playwright com locators semânticos
├── logs/                    # logs persistidos (montado como volume)
└── .github/workflows/ci.yml # pipeline de integração contínua
```

## Pré-requisitos

- Docker e Docker Compose
- (Para rodar localmente sem Docker) Python 3.11+

## Configuração

1. Preencha `.env` com as credenciais do BotCity Maestro e demais parâmetros.

## Executando com Docker

Build da imagem:

```bash
docker compose build
```

Executar o bot:

```bash
docker compose run bot
```

Isso deve:

- Iniciar o container e executar `main.py`.
- Gerar logs estruturados em `logs/execucao.log`, visíveis também na
  máquina host graças ao volume `./logs:/app/logs`.

## Executando localmente (sem Docker)

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
python main.py
```

## Logs estruturados

Cada linha do arquivo `logs/execucao.log` é um JSON no formato:

```json
{
  "timestamp": "2026-07-22T10:00:00",
  "level": "INFO",
  "execution_id": "12345",
  "bot_id": "auditor001",
  "message": "Auditoria iniciada"
}
```

- `EXECUTION_ID`: definido via variável de ambiente; se ausente, um
  UUID é gerado automaticamente a cada execução.
- `BOT_ID`: identifica o bot (padrão: `auditor001`), configurável via `.env`.

## Automação web (Playwright)

O módulo `web_automation.py` implementa o preenchimento de um
formulário de teste utilizando **locators semânticos**, em vez de
seletores CSS/XPath frágeis:

```python
page.get_by_label("Nome").fill("Usuário Teste")
page.get_by_role("combobox").select_option("opcao1")
page.get_by_placeholder("Digite seu usuário").fill("teste")
page.get_by_role("button", name="Enviar").click()
```

Configure a URL de teste em `PLAYWRIGHT_TARGET_URL` no `.env`.

## CI/CD (GitHub Actions)

O workflow em `.github/workflows/ci.yml` executa a cada push/PR:

1. Checkout do código (`actions/checkout`)
2. Setup do Python (`actions/setup-python`)
3. Instalação de dependências (`pip install -r requirements.txt`)
4. Instalação dos browsers do Playwright
5. Validação de sintaxe (`compileall`) e testes (`pytest`, se existirem)
6. Build da imagem Docker

## Branches sugeridas para esta evolução

```bash
git checkout -b feature/playwright-web-inicial
git checkout -b feature/refatoracao-locators
```

> Neste pacote de entrega, a automação web já foi implementada
> diretamente com locators semânticos, unificando as etapas 4 e 5 da
> especificação original. Ao aplicar ao repositório real, você pode
> distribuir os commits entre as duas branches acima conforme sua
> convenção de versionamento.

## Checklist de entrega

- [x] Dockerfile funcional
- [x] .dockerignore configurado
- [x] docker-compose.yml funcionando
- [x] Logs persistidos no host
- [x] Workflow GitHub Actions criado
- [x] Logs estruturados com execution_id e bot_id
- [x] Automação Playwright funcionando
- [x] Locators semânticos implementados
- [x] README atualizado com instruções de execução
