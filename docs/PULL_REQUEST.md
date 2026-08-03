## Objetivo

Refatorar a automação de cadastro de lotes para Page Object Model nas versões
Playwright e Selenium, preservando DataPool, evidências e logs.

## Alterações realizadas

- Adicionados Page Objects independentes para Playwright e Selenium.
- Removidos seletores e comandos de interação dos orquestradores.
- Extraída a regra de negócio comum para `fluxo_lotes.py`.
- Criado DataPool JSON fictício com atualização por item.
- Criada screenshot única por item e registro do caminho no resultado.
- Implementados logs estruturados e resumo final.
- Removidas credenciais do código; configuração via `.env`.
- Adicionados Portal Fake, PDD, documentação BotCity e teste integrado.
- Reforçado `.gitignore` para artefatos e dados locais.

## Checklist

- [x] Fluxo completo executado
- [x] DataPool simulado integrado
- [x] Page Object Model Playwright e Selenium
- [x] Locators robustos por ID
- [x] Esperas explícitas, sem `sleep`
- [x] Screenshot por item
- [x] Caminho salvo no DataPool
- [x] Logs estruturados
- [x] Resumo final
- [x] README e PDD
- [x] Dados fictícios e segredos fora do Git
- [x] Teste integrado

## Testes executados

```text
pytest: 1 passed
python main.py: 3 processados, 3 sucessos, 0 erros
python bot.py: 3 processados, 3 sucessos, 0 erros
python pack_bot.py: pacote gerado e auditado sem .env ou cache
```

## Evidências

As evidências são geradas localmente em `evidencias/` e não são versionadas.
Compartilhar somente pelo mecanismo seguro definido para a avaliação.

## Observações

O DataPool é simulado porque não foram fornecidos workspace, rótulo e
autorização de um DataPool remoto. O desenho permite adicionar outro adaptador
sem alterar os Page Objects.
