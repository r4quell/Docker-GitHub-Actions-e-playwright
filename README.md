# Automação de cadastro de lotes com Playwright, Selenium, POM e BotCity

## Objetivo

Automatizar o cadastro de lotes em um Portal Fake, processando dados de um
DataPool simulado e produzindo evidências e logs rastreáveis. O projeto foi
preparado para a Aula 20 sem acessar sistemas reais ou armazenar segredos.

## Arquitetura

O fluxo usa separação de responsabilidades:

- `main.py`: ponto de entrada local.
- `bot.py`: integração e finalização da tarefa no BotCity Maestro.
- `orquestrador.py`: seleciona a tecnologia configurada.
- `web_automation.py`: ciclo de vida do navegador Playwright.
- `selenium_automation.py`: ciclo de vida do navegador Selenium.
- `fluxo_lotes.py`: regra de negócio compartilhada, logs, evidências e DataPool.
- `datapool.py`: leitura e atualização do DataPool fictício.
- `configuracao.py`: variáveis de ambiente e caminhos.
- `navegador.py`: criação do Chrome para Selenium.
- `pages/`: locators, esperas e ações das duas tecnologias.
- `resources/portal_fake/`: sistema web estático e fictício.

```text
main.py / bot.py
        |
        v
  Orquestrador -----> DataPool simulado
        |
        v
 LoginPage -> FormPage -> evidências + logs + resultado
```

O detalhamento técnico está no [PDD](docs/PDD.md).

## Estrutura

```text
Docker-GitHub-Actions-e-playwright/
├── docs/
│   ├── PDD.md
│   └── PULL_REQUEST.md
├── resources/
│   ├── datapool_lotes.json
│   └── portal_fake/
├── src/
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   ├── form_page.py
│   │   ├── base_page_selenium.py
│   │   ├── login_page_selenium.py
│   │   └── form_page_selenium.py
│   ├── configuracao.py
│   ├── datapool.py
│   ├── fluxo_lotes.py
│   ├── logging_config.py
│   ├── navegador.py
│   ├── orquestrador.py
│   ├── selenium_automation.py
│   └── web_automation.py
├── tests/
│   └── test_cadastro.py
├── .env.example
├── bot.py
├── bot.yaml
├── main.py
├── pack_bot.py
└── requirements.txt
```

As pastas `logs/` e `evidencias/` são criadas durante a execução e estão
ignoradas pelo Git.

## Tecnologias

- Python 3.10+
- Playwright
- Selenium 4
- pytest
- BotCity Maestro SDK
- python-dotenv
- python-json-logger

## Requisitos

- Python instalado e disponível no terminal.
- Google Chrome instalado.
- Acesso ao BotCity Runner somente para execução no Maestro; a execução local
  não depende de serviços externos.

## Instalação

Na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```

O repositório de trabalho já pode possuir um `.env` local. Nunca faça commit
desse arquivo.

## Configuração

Variáveis aceitas:

| Variável | Obrigatória | Finalidade |
|---|---:|---|
| `APP_USUARIO` | Sim | Identificação fictícia do Portal Fake |
| `APP_SENHA` | Sim | Credencial fictícia do Portal Fake |
| `APP_HEADLESS` | Não | Executa o Chrome sem interface |
| `APP_TIMEOUT` | Não | Tempo máximo das esperas explícitas |
| `APP_TECNOLOGIA` | Não | `selenium` (padrão) ou `playwright` |
| `APP_URL` | Não | Sobrescreve o Portal Fake local |
| `DATAPOOL_ENTRADA` | Não | Arquivo JSON de entrada |
| `DATAPOOL_RESULTADO` | Não | Arquivo JSON atualizado |
| `EVIDENCIAS_DIR` | Não | Diretório das screenshots |
| `LOGS_DIR` | Não | Diretório dos logs |

O `.env.example` contém somente dados demonstrativos. O Portal Fake aceita
qualquer usuário e credencial não vazios e não realiza autenticação real.

## Execução

```powershell
python main.py
```

Para escolher explicitamente a implementação:

```powershell
$env:APP_TECNOLOGIA="playwright"  # ou "selenium"
python main.py
```

Ao final, o terminal apresenta quantidade processada, sucessos, erros e tempo.

Para simular o modo Runner/CI:

```powershell
$env:APP_HEADLESS="true"
python main.py
```

## Testes

Antes da primeira execução, instale as dependências Python e o navegador do
Playwright e crie o arquivo de configuração local:

```powershell
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```

### Teste automatizado

Para testar as implementações Selenium e Playwright, além da geração de
screenshots, logs e registros no DataPool, execute na raiz do projeto:

```powershell
pytest -q
```

Resultado esperado:

```text
2 passed
```

Os testes integrados abrem o Portal Fake em modo headless, processam todos os
itens e validam o resumo, o resultado do DataPool, as screenshots e o arquivo
de log nas duas tecnologias.

### Teste manual com Selenium

```powershell
$env:APP_TECNOLOGIA="selenium"
$env:APP_HEADLESS="true"
python main.py
```

### Teste manual com Playwright

```powershell
$env:APP_TECNOLOGIA="playwright"
$env:APP_HEADLESS="true"
python main.py
```

Em ambas as execuções, o resultado esperado é:

```text
Resumo
Itens processados: 3
Sucesso: 3
Erro: 0
```

Para acompanhar a automação com a janela do navegador visível, altere o modo
headless antes de executar:

```powershell
$env:APP_HEADLESS="false"
python main.py
```

Após a execução, confira os artefatos gerados:

- screenshots em `evidencias/`;
- log estruturado em `logs/execucao.log`;
- DataPool atualizado em `logs/datapool_resultado.json`.

## DataPool

`resources/datapool_lotes.json` é uma simulação segura. Cada item possui:

- `id`;
- `numero_lote`;
- `produto`;
- `status`.

Depois do processamento, `logs/datapool_resultado.json` contém:

```json
{
  "resultado": {
    "status": "Sucesso",
    "screenshot": "evidencias/item001_20260729_120000_000000.png",
    "mensagem": "Lote cadastrado com sucesso!"
  }
}
```

O arquivo é persistido após cada item, reduzindo perda de rastreabilidade em
caso de interrupção.

## Page Object Model

Foi escolhida a separação por tecnologia para evitar condicionais dentro dos
Page Objects. `login_page.py` e `form_page.py` implementam Playwright;
`login_page_selenium.py` e `form_page_selenium.py` implementam Selenium. Cada
par recebe `page` ou `driver` por injeção no construtor e encapsula navegação,
locators, esperas, preenchimento, envio, validação e screenshot.

Regras de negócio, contadores, tratamento por item, logs e atualização do
DataPool ficam em `fluxo_lotes.py`. Assim, uma mudança na interface exige
alteração apenas no Page Object da tecnologia afetada. Selenium usa esperas
explícitas e Playwright usa os mecanismos nativos de auto-wait.

## Screenshots e logs

Uma screenshot PNG é criada para cada item, inclusive quando ocorre erro. O
nome combina o ID fictício com timestamp e microssegundos para evitar colisão.

Os eventos são gravados em `logs/execucao.log` no formato JSON, incluindo:

- início e fim;
- item atual;
- status e exceções;
- caminho da screenshot;
- totais e duração.

`logs/`, `evidencias/`, imagens, bancos, arquivos `.log`, `.env` e pacotes ZIP
estão excluídos no `.gitignore`.

## BotCity Maestro

O manifesto `bot.yaml` aponta para `bot.py`. Quando executado pelo Runner, o
robô usa modo headless e finaliza a tarefa como `SUCCESS` ou `FAILED`.

O DataPool deste laboratório é deliberadamente local. Uma integração com um
DataPool remoto do Maestro exigiria configuração do workspace e rótulo do
recurso, que não foram fornecidos.

Para gerar o pacote:

```powershell
python pack_bot.py
```

## Branch e Pull Request

A refatoração está preparada na branch `feature/page-objects`. Para
publicar as alterações:

```powershell
git add .
git commit -m "feat(pages): adiciona Page Objects Playwright e Selenium"
git push -u origin feature/page-objects
```

Use [docs/PULL_REQUEST.md](docs/PULL_REQUEST.md) como descrição da PR.

## Boas práticas e segurança

- Responsabilidade única entre módulos.
- Dependências explícitas e configuração centralizada.
- Dados exclusivamente fictícios.
- Credenciais somente via ambiente.
- Encerramento do navegador em bloco `finally`.
- Evidências e logs fora do versionamento.
- Teste integrado automatizado.

## Limitações

- O DataPool é local e simulado.
- O teste requer Chrome disponível.
- O Portal Fake usa `localStorage`, sem banco de dados.
- A integração online só pode ser validada em um workspace BotCity autorizado.

## Melhorias futuras

- Adaptador de DataPool remoto implementando a mesma interface.
- Fixtures unitárias com driver simulado para testes rápidos.
- Relatório HTML de testes no pipeline.
- Upload automático das evidências como artefatos do Maestro.
- Execução paralela quando o sistema de destino permitir.
