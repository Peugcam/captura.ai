# Guia - Configurar OBS para Naruto Online

## Passo a Passo

### 1. Preparar o Gateway
O gateway ja esta rodando! Verifique:
- URL: http://localhost:8000
- Status: http://localhost:8000/health

### 2. Abrir o OBS Studio

1. Inicie o OBS Studio
2. Se nao tiver instalado, baixe em: https://obsproject.com/

### 3. Adicionar Fonte de Captura

1. Na janela "Fontes", clique em **+** (Adicionar)
2. Selecione **"Captura de Janela"**
3. Nome: "Naruto Online" (ou qualquer nome)
4. Clique OK

5. Na janela de propriedades:
   - **Janela**: Selecione a janela do Naruto Online
   - **Metodo de Captura**: "Captura Automatica"
   - Marque: "Capturar Cursor"
   - Clique OK

### 4. Configurar Captura de Frames

Existem 3 metodos para enviar frames ao gateway:

#### Metodo A: Plugin OBS Browser Source (Mais Simples)

1. Adicione uma fonte **"Navegador"** (Browser Source)
2. URL: `file:///C:/Users/paulo/OneDrive/Desktop/gta-analytics-v2/obs-capture.html`
3. Largura: 1920, Altura: 1080
4. Marque: "Atualizar navegador quando a cena estiver ativa"

#### Metodo B: OBS WebSocket + Script Python

Ja esta configurado! O obs-websocket vem integrado no OBS 28+.

1. Va em **Ferramentas** → **obs-websocket Settings**
2. Certifique-se que esta habilitado
3. Porta: 4455 (padrao)
4. Senha: deixe em branco se nao configurou

O script Python ja conecta automaticamente!

#### Metodo C: Virtual Camera + Captura

1. No OBS, clique em **Iniciar Camera Virtual**
2. O sistema captura frames da camera virtual

### 5. Iniciar Transmissao/Gravacao

**IMPORTANTE**: O OBS so envia frames quando esta transmitindo OU gravando!

Opcao 1: Iniciar Gravacao
- Clique em **"Iniciar Gravacao"**

Opcao 2: Iniciar Transmissao
- Configure uma transmissao (pode ser para arquivo local)
- Clique em **"Iniciar Transmissao"**

### 6. Monitorar Frames

Execute o script de monitoramento:

```bash
cd backend
python monitor_obs_frames.py
```

Voce vera:
- Total de frames recebidos
- FPS em tempo real
- Status da conexao

## Resolucao de Problemas

### Nenhum frame sendo detectado?

1. **Verifique se o OBS esta gravando/transmitindo**
   - O OBS so captura frames quando ativo!

2. **Verifique o gateway**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Verifique a fila de frames**
   ```bash
   curl http://localhost:8000/frames
   ```

4. **Veja os logs do gateway**
   - Deve mostrar "Frame uploaded via HTTP"

### FPS muito baixo?

- Ajuste a resolucao da captura no OBS
- Reduza a taxa de frames no OBS (30 fps e ideal)

### Jogo nao aparece na lista?

- Certifique-se que o Naruto Online esta em modo janela (nao fullscreen)
- Use "Captura de Tela" em vez de "Captura de Janela"

## Proximos Passos

Depois que os frames estiverem sendo detectados:

1. O backend processa os frames
2. Analisa o conteudo com Vision API
3. Detecta kills e eventos
4. Atualiza o dashboard em tempo real

Tudo automatico!
