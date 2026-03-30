# GTA Analytics — Melhorias do App Electron

**Data:** 2026-03-30
**Autor:** Paulo Eugenio Campos
**Escopo:** electron-app (capture.js, main.js, preload.js, renderer/)
**Restrições:** Sem aumento de custo, sem alteração nas configs de API LLM

---

## Visão Geral

Aplicar 4 melhorias sequenciais ao app GTA Analytics Electron. Cada etapa valida a anterior: corrigir bugs antes de auditar segurança, auditar antes de testar, testar antes de polir a UI.

---

## Etapa 1 — Debugging Sistemático

**Skill:** `systematic-debugging`
**Arquivos:** `capture.js`, `main.js`

### O que revisar

- **Memory leak no setInterval:** `this.timer` em `capture.js` — verificar se `clearInterval` é sempre chamado em todos os caminhos de saída, incluindo erros não tratados no `captureAndSend`.
- **Race condition:** `captureAndSend` é async e chamada por setInterval. Se uma chamada demorar mais que o intervalo (ex: servidor dormindo + retries = até 16s), a próxima já inicia. Resultado: múltiplas chamadas simultâneas acumulando.
- **Erros silenciosos:** o bloco `catch` em `captureAndSend` apenas loga e continua — verificar se há casos onde `this.running` deveria ser setado para false.
- **GTA V detection:** `isGtaActive()` usa PowerShell com timeout de 2000ms. Se o PowerShell demorar mais, resolve `true` por erro — verificar se isso não causa envios falsos.
- **Stop durante retry:** se `stop()` for chamado enquanto `sendWithRetry` está em loop de espera, a captura continua até o retry terminar. Adicionar verificação de `this.running` dentro do loop de retry.

### Critério de sucesso
Nenhum memory leak detectável após 30 minutos de uso. Sem chamadas simultâneas acumulando.

---

## Etapa 2 — Segurança

**Skill:** `security-check`
**Arquivos:** `preload.js`, `renderer/js/app.js`, `main.js`

### O que auditar

- **XSS no terminal de log:** `app.js` usa `escapeHtml()` antes de inserir no DOM — confirmar que está sendo aplicado em todos os pontos de inserção de dados externos.
- **Validação de URL:** o servidor URL vem do usuário e é passado diretamente para `axios.post`. Validar formato e limitar a `https://`.
- **IPC surface:** `preload.js` expõe `openExternal(url)` sem validação — URL poderia ser `file://` ou `javascript:`. Adicionar whitelist de protocolos permitidos.
- **contextIsolation:** já está `true` e `nodeIntegration: false` — confirmar que isso está correto.
- **Dados sensíveis no renderer:** verificar se chaves ou tokens transitam pelo IPC.

### Critério de sucesso
Nenhuma entrada externa inserida no DOM sem sanitização. URLs externas restritas a `https://`.

---

## Etapa 3 — Testes Automatizados

**Skill:** `automated-testing`
**Arquivo novo:** `electron-app/tests/capture.test.js`

### Funções a testar

| Função | Cenários |
|--------|----------|
| `getFrameDiff(buf1, buf2)` | buf1 null, buffers iguais, buffers diferentes, tamanhos distintos |
| `sendWithRetry(buffer, maxRetries)` | sucesso na 1ª tentativa, sucesso na 3ª, falha em todas, stop() chamado durante retry |
| `isGtaActive()` | PowerShell retorna 0, retorna 1, retorna erro |
| `captureAndSend()` | GTA não ativo, frame vazio, diff < 3%, envio bem-sucedido |

### Stack de testes
Jest + mocks para `electron`, `axios`, `child_process`. Sem dependências de build extras além do que já existe.

### Critério de sucesso
Cobertura mínima de 80% das funções críticas de `capture.js`.

---

## Etapa 4 — Interface Visual

**Skill:** `frontend-design`
**Arquivos:** `renderer/index.html`, `renderer/css/styles.css`, `renderer/js/app.js`

### Melhorias planejadas

- **Indicadores animados:** os badges GTA V / Servidor pulsam quando ativos (CSS animation), em vez de apenas mudar texto.
- **Estado de "acordando":** quando servidor está waking (🟡), mostrar barra de progresso indeterminada abaixo dos controles.
- **Log com cores por tipo:** erros em vermelho, warnings em amarelo, sucesso em verde — já parcialmente implementado, mas uniformizar.
- **Botão de início mais destacado:** hierarquia visual mais clara entre Iniciar e Parar.
- **Transições suaves:** mudanças de estado (parado → capturando) com fade/slide em vez de troca abrupta.

### Critério de sucesso
Visual profissional adequado para apresentação ao cliente Luis Otavio. Sem mudanças de comportamento — apenas UI.

---

## Ordem de execução

```
debugging → security → testing → frontend
    ↓           ↓          ↓         ↓
 fix bugs   fix vulns  lock fixes  polish
```

## Fora do escopo

- Memória contínua / histórico de partidas (custo elevado, decisão do cliente)
- Alterações nas APIs LLM ou configurações do fly.io
- Novas funcionalidades de gameplay
