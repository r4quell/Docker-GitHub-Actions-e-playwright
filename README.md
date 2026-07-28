# Auditor de Acessos V2 com Selenium

## 1. Sobre o projeto

O **Auditor de Acessos V2** é uma automação desenvolvida em Python para processar uma fila de usuários e realizar auditorias de acesso em um sistema corporativo.

O projeto foi estruturado para separar a preparação dos dados, o processamento dos usuários e a automação do navegador. Dessa forma, o processo pode ser executado de maneira padronizada e acompanhado por logs e relatórios.

A solução utiliza Selenium para automação web e pode ser executada localmente ou em um ambiente Docker. O projeto também possui integração com BotCity Maestro, DataPool e Credentials Vault, além de um modo offline para desenvolvimento e testes.

---

## 2. Objetivo

O objetivo é automatizar um processo que, manualmente, exigiria que um operador acessasse um sistema, informasse os dados de cada usuário e realizasse consultas individualmente.

Com a automação, os usuários são carregados em uma fila e processados um a um. Para cada item, o sistema valida os dados, obtém as credenciais necessárias, abre o navegador através do Selenium, realiza o fluxo de consulta e registra o resultado.

O processamento de um usuário com erro não interrompe automaticamente os demais itens da fila.

---

## 3. Como o projeto funciona

O fluxo geral é:

```text
Arquivo CSV
    |
    v
Dispatcher
    |
    v
DataPool / fila offline
    |
    v
main.py - Performer
    |
    +--> valida dados
    |
    +--> obtém credenciais
    |
    +--> chama bot.py
              |
              v
          Selenium
              |
              v
        Google Chrome
              |
              v
       Sistema corporativo
              |
              v
          Auditoria
              |
              v
      Resultado do item
              |
              v
       Relatório JSON
```

### Etapa A - Dispatcher

O `dispatcher.py` é responsável pela preparação da fila.

Ele lê o arquivo:

```text
dados_entrada/usuarios_auditoria.csv
```

e envia os registros para o DataPool do BotCity Maestro ou, quando o Maestro está desativado, para uma fila persistida localmente em:

```text
logs/datapool_FilaAuditoriaRH.json
```

Essa separação permite que os dados de entrada sejam preparados antes do início do processamento.

### Etapa B - Performer

O `main.py` é o Performer. Ele consome os itens disponíveis na fila e coordena o processamento.

Para cada item, o Performer:

1. obtém o próximo registro;
2. separa os dados necessários;
3. obtém as credenciais;
4. chama a função de auditoria do `bot.py`;
5. registra o item como concluído ou com erro;
6. continua para o próximo registro.

Ao final, o Performer gera um relatório da execução.

---

## 4. Automação web com Selenium

O Selenium é a tecnologia responsável por controlar o navegador.

Em vez de um operador realizar manualmente as ações no sistema, o Python utiliza o Selenium WebDriver para executar essas ações de forma programada.

O fluxo de automação é estruturado da seguinte forma:

```text
Abrir navegador
      |
      v
Acessar sistema
      |
      v
Localizar campos da página
      |
      v
Preencher usuário e senha
      |
      v
Realizar login
      |
      v
Localizar campo de pesquisa
      |
      v
Informar CPF
      |
      v
Executar pesquisa
      |
      v
Registrar resultado
      |
      v
Fechar navegador
```

No `bot.py`, os elementos da página são localizados utilizando os recursos do Selenium, como `By.ID`, e as ações são executadas com métodos como `send_keys()` e `click()`.

Também é utilizado `WebDriverWait` com condições explícitas para evitar que a automação tente interagir com um elemento antes que ele esteja disponível.

Essa abordagem é mais adequada do que depender exclusivamente de pausas fixas, pois o Selenium pode continuar assim que a condição necessária for atendida.

---

## 5. Modo headless

O navegador é configurado para funcionar em modo **headless**.

Nesse modo, o Google Chrome é executado sem abrir uma janela gráfica na tela.

Isso é importante para execução em ambientes como:

- Docker;
- servidores;
- GitHub Actions;
- ambientes de integração contínua.

O Selenium utiliza opções como:

```text
--headless=new
--no-sandbox
--disable-dev-shm-usage
--disable-gpu
```

Essas configurações permitem que o navegador seja executado em um ambiente de container e CI.

---

## 6. Validação dos dados

Antes de iniciar a automação no navegador, o `bot.py` valida os dados recebidos.

Atualmente, o CPF é um dos campos obrigatórios para o processamento.

Caso o CPF esteja vazio, é gerado um `ValidationError`.

O erro é registrado para aquele item e o processamento continua com os próximos registros.

Exemplo:

```text
Usuário 1 -> processado
Usuário 2 -> processado
Usuário 3 -> CPF inválido -> erro registrado
Usuário 4 -> processado
Usuário 5 -> processado
```

Isso evita que um único registro inválido interrompa toda a execução.

---

## 7. Credenciais e segurança

As credenciais utilizadas pela automação não devem ser gravadas diretamente no código-fonte.

Quando a integração com o BotCity Maestro está habilitada, o projeto utiliza o **Credentials Vault** para obter as informações necessárias.

O fluxo é:

```text
Credentials Vault
       |
       v
maestro_client.py
       |
       v
main.py
       |
       v
bot.py
       |
       v
Selenium
```

A senha não é registrada nos logs.

Para execução offline, o projeto utiliza credenciais fictícias apenas em memória, sem registrar senhas nos arquivos de log.

O arquivo `.env` deve permanecer fora do controle de versão e nunca deve conter informações que possam ser expostas publicamente.

---

## 8. DataPool

O DataPool funciona como uma fila de itens que precisam ser processados.

Cada registro pode conter dados como:

```text
CPF
Nome
Sistema
```

O Dispatcher alimenta a fila e o Performer consome os itens.

Essa separação é importante porque permite que o carregamento dos dados e a execução da automação sejam processos independentes.

Quando o Maestro está desativado, o projeto utiliza uma fila local em:

```text
logs/datapool_FilaAuditoriaRH.json
```

---

## 9. BotCity Maestro

O BotCity Maestro pode ser utilizado para gerenciar a execução da automação.

Quando habilitado, ele participa do fluxo fornecendo recursos como:

- DataPool;
- Credentials Vault;
- registro de logs;
- alertas;
- status da tarefa;
- armazenamento de artefatos.

O projeto também pode funcionar offline, o que facilita desenvolvimento e testes sem depender dos serviços externos.

---

## 10. Logs e relatório

O projeto possui registro das informações de execução.

Os logs permitem identificar o que aconteceu durante o processamento, como início da tarefa, processamento de itens, erros e conclusão.

Ao final, o Performer gera:

```text
logs/relatorio_execucao.json
```

O relatório contém informações como:

- início da execução;
- término da execução;
- duração;
- quantidade de itens processados;
- quantidade de sucessos;
- quantidade de erros;
- detalhes dos itens que apresentaram falha.

Exemplo simplificado:

```json
{
  "total_processados": 10,
  "total_sucesso": 9,
  "total_erro": 1
}
```

---

## 11. Estrutura do projeto

```text
.
├── .github/
│   └── workflows/
│       └── selenium.yml
│
├── bot.py                              # regras de validação e automação Selenium
├── config.py                           # configurações via .env
├── dispatcher.py                       # Etapa A: carga da fila
├── maestro_client.py                   # Maestro, Vault e DataPool/offline
├── main.py                             # Etapa B: Performer
├── logger.py                            # configuração dos logs
├── logger_config.py                     # configuração adicional de logging
│
├── dados_entrada/
│   └── usuarios_auditoria.csv          # dados de entrada
│
├── logs/                                # fila offline, logs e relatório
├── Dockerfile                           # imagem Docker
├── docker-compose.yml                   # execução com Docker Compose
├── requirements.txt                     # dependências Python
├── .env                                 # configurações locais e sensíveis
├── .gitignore                            # arquivos que não devem ser versionados
└── README.md                            # documentação do projeto
```

---

## 12. Responsabilidade dos principais arquivos

### `dispatcher.py`

Realiza a primeira etapa do fluxo. Lê os dados do CSV e alimenta o DataPool ou a fila offline.

### `main.py`

É o ponto principal do Performer. Consome os itens, coordena a auditoria e gera o relatório final.

### `bot.py`

Contém as regras de negócio e a automação Selenium. É responsável pela validação do item e pelo controle do navegador.

### `config.py`

Centraliza configurações e variáveis utilizadas pela aplicação.

### `maestro_client.py`

Centraliza a comunicação com o BotCity Maestro e fornece uma camada para DataPool, Credentials Vault, logs, alertas e modo offline.

### `logger.py`

Responsável pelo registro das informações da execução.

### `Dockerfile`

Define o ambiente utilizado para executar a aplicação dentro de um container. A imagem foi preparada para possuir Python e Google Chrome, necessários para o Selenium.

### `docker-compose.yml`

Facilita a execução do projeto utilizando Docker Compose.

### `.github/workflows/selenium.yml`

Define o processo de integração contínua utilizado pelo GitHub Actions.

---

## 13. Alterações realizadas na atividade

A estrutura original foi modificada para transformar a parte de automação web em uma implementação utilizando **Selenium WebDriver**.

As principais alterações foram:

### `bot.py`

- substituição da simulação por automação Selenium;
- criação do WebDriver do Chrome;
- configuração do modo headless;
- utilização de `WebDriverWait`;
- preenchimento de campos com `send_keys()`;
- interação com botões através de `click()`;
- tratamento de erros;
- encerramento do navegador após o processamento.

### `main.py`

- atualização do fluxo do Performer para utilizar a automação Selenium;
- identificação da execução como processo Selenium nos logs;
- registro de sucesso e erro por item;
- geração do relatório final.

### `requirements.txt`

Foram adicionadas as dependências necessárias para a automação:

```text
selenium>=4.21.0
webdriver-manager>=4.0.2
```

### `Dockerfile`

Foi adaptado para executar Selenium em container, incluindo o Google Chrome e as bibliotecas necessárias para execução headless.

### GitHub Actions

Foi criado o workflow:

```text
.github/workflows/selenium.yml
```

O workflow realiza automaticamente:

1. checkout do projeto;
2. configuração do Python;
3. instalação do Google Chrome;
4. instalação das dependências;
5. validação da instalação do Selenium;
6. build da imagem Docker.

O `README.md` foi atualizado para documentar essas alterações e explicar o funcionamento da solução.

---

## 14. GitHub Actions e integração contínua

O GitHub Actions permite automatizar verificações do projeto sempre que alterações são enviadas ao repositório.

O workflow é executado em eventos como:

- `push` na branch `main`;
- `pull_request` para `main`;
- execução manual através do GitHub.

O fluxo do pipeline é:

```text
Push / Pull Request
        |
        v
Checkout do projeto
        |
        v
Configuração do Python 3.11
        |
        v
Instalação do Google Chrome
        |
        v
Instalação das dependências
        |
        v
Validação do Selenium
        |
        v
Build do Docker
        |
        v
Resultado do workflow
```

Dessa forma, alterações no código podem ser verificadas automaticamente antes de serem consideradas prontas.

---

## 15. Execução local

### Criar ambiente virtual

Windows:

```powershell
python -m venv .venv
```

Ativação no PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Executar o Dispatcher

O Dispatcher carrega os usuários do CSV para a fila:

```bash
python dispatcher.py
```

### Executar o Performer

Depois de carregar a fila:

```bash
python main.py
```

O resultado será salvo em:

```text
logs/relatorio_execucao.json
```

---

## 16. Configuração offline

Para testar sem conexão com os serviços externos do BotCity Maestro, o `.env` pode ser configurado com:

```env
MAESTRO_ENABLED=false
VAULT_ENABLED=false
```

Nesse modo:

- o DataPool é persistido localmente;
- as credenciais utilizadas são fictícias e ficam apenas em memória;
- os logs não registram senhas;
- o processamento pode ser testado sem o Maestro.

---

## 17. Configuração com BotCity Maestro

Para utilizar os serviços do Maestro, configure:

```env
MAESTRO_ENABLED=true
VAULT_ENABLED=true
```

Também devem ser configuradas as informações de acesso ao Maestro e os labels utilizados para DataPool e Credentials Vault.

As informações sensíveis devem ser mantidas fora do código-fonte.

---

## 18. Execução com Docker

Para construir a imagem:

```bash
docker compose build
```

Para executar o Dispatcher:

```bash
docker compose run bot python dispatcher.py
```

Para executar o Performer:

```bash
docker compose run bot
```

O Docker fornece um ambiente padronizado para a aplicação e permite que o Selenium utilize o navegador configurado dentro do container.

---

## 19. Configuração dos elementos do sistema

A estrutura Selenium está preparada para receber a URL e os seletores reais da aplicação que será automatizada.

No `bot.py`, devem ser definidos os elementos correspondentes ao sistema utilizado na atividade.

Exemplo de URL:

```python
driver.get("URL_DO_SISTEMA")
```

Exemplos de elementos:

```python
By.ID, "username"
By.ID, "password"
By.ID, "search"
By.ID, "btn-search"
```

Os valores acima são exemplos. Para a execução contra o sistema real, eles devem ser substituídos pelos seletores reais dos elementos da página.

---

## 20. Segurança

Nunca coloque senhas, tokens ou chaves de API diretamente no código.

Não utilizar:

```python
senha = "MinhaSenha123"
```

ou:

```python
API_KEY = "minha-chave"
```

As informações sensíveis devem ser mantidas em mecanismos apropriados, como:

- `.env` para ambiente local;
- BotCity Credentials Vault;
- Secrets do GitHub Actions.

O `.env` deve permanecer no `.gitignore`.

---

## 21. Benefícios da solução

A implementação oferece os seguintes benefícios:

- redução de tarefas manuais;
- padronização do processo de auditoria;
- separação entre dados e lógica de automação;
- tratamento individual de erros;
- rastreabilidade através de logs e relatórios;
- proteção das credenciais;
- execução em Docker;
- validação automatizada com GitHub Actions;
- possibilidade de integração com BotCity Maestro;
- facilidade de manutenção e evolução da automação.

---

## 22. Resultado esperado

Ao final da execução, o projeto deve ser capaz de:

1. carregar os usuários a partir do CSV;
2. inserir os registros no DataPool ou na fila offline;
3. consumir os itens individualmente;
4. validar os dados;
5. obter as credenciais de maneira segura;
6. iniciar o Google Chrome através do Selenium;
7. acessar o sistema;
8. realizar o login;
9. pesquisar o usuário pelo CPF;
10. executar a auditoria;
11. registrar o resultado do item;
12. continuar o processamento mesmo quando um item apresentar erro;
13. gerar o relatório final;
14. permitir execução em Docker;
15. validar a estrutura do projeto através do GitHub Actions.

---

## 23. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Desenvolvimento da automação |
| Selenium WebDriver | Controle automatizado do navegador |
| Google Chrome | Navegador utilizado pelo Selenium |
| WebDriver Manager | Gerenciamento do ChromeDriver |
| BotCity Maestro | Gerenciamento da automação |
| DataPool | Fila de usuários para processamento |
| Credentials Vault | Armazenamento seguro de credenciais |
| Docker | Containerização da aplicação |
| Docker Compose | Execução simplificada dos containers |
| GitHub Actions | Integração e validação contínua |
| JSON | Relatório de execução |
| Git/GitHub | Controle de versão |

---

## 24. Conclusão

A atividade resultou na adaptação da automação para utilização do **Selenium WebDriver**, mantendo a arquitetura de processamento por fila e integrando a solução com Docker e GitHub Actions.

A separação entre Dispatcher, Performer e automação Selenium permite organizar melhor as responsabilidades do projeto. O Dispatcher prepara os dados, o Performer controla o processamento e o `bot.py` concentra as regras de validação e automação do navegador.

A utilização de Docker permite reproduzir o ambiente necessário para execução, enquanto o GitHub Actions automatiza verificações do projeto. O uso do DataPool e do Credentials Vault também possibilita separar dados, credenciais e lógica de automação, contribuindo para uma solução mais organizada e segura.

---

## 25. Autoria

**Raquel Andrade**

Projeto desenvolvido para fins acadêmicos, com foco em automação de processos, Selenium WebDriver, Python, Docker, GitHub Actions e BotCity Maestro.
