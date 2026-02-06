# Instalação do WebSocket Gateway (Go)

## Pré-requisitos

### 1. Instalar Go

**Windows:**
1. Baixar: https://go.dev/dl/
2. Executar instalador (go1.21.x.windows-amd64.msi ou superior)
3. Verificar instalação:
```bash
go version
```

### 2. Baixar Dependências

```bash
cd gateway
go mod download
```

## Compilação

### Desenvolvimento (com hot reload):
```bash
go run main.go websocket.go buffer.go
```

### Produção (binário otimizado):
```bash
go build -o gateway.exe -ldflags="-s -w" .
```

## Executar

### Modo debug:
```bash
./gateway.exe -debug
```

### Modo produção:
```bash
./gateway.exe -port 8000 -buffer 200
```

## Parâmetros

- `-port`: Porta do servidor (padrão: 8000)
- `-buffer`: Tamanho do buffer de frames (padrão: 200)
- `-debug`: Ativar logs detalhados

## Endpoints

### WebSocket
- `ws://localhost:8000/ws` - Conexão WebSocket para frames

### HTTP
- `GET /health` - Status do servidor
- `GET /stats` - Estatísticas (frames/s, buffer usage, etc.)
- `GET /frames` - Pegar batch de frames (para Python backend)

## Teste Rápido

```bash
# Terminal 1: Iniciar gateway
go run main.go websocket.go buffer.go -debug

# Terminal 2: Ver estatísticas
curl http://localhost:8000/stats

# Terminal 3: Health check
curl http://localhost:8000/health
```

## Performance Esperada

- **Throughput**: 10.000+ frames/segundo
- **Latência**: <1ms por frame
- **Memória**: ~50-100MB (buffer de 200 frames)
- **CPU**: <5% em idle, <20% sob carga
- **Conexões simultâneas**: 1000+

## Troubleshooting

### Go não encontrado
```bash
# Verificar PATH
echo $PATH | grep -i go

# Adicionar Go ao PATH (Windows PowerShell)
$env:Path += ";C:\Program Files\Go\bin"
```

### Porta em uso
```bash
# Usar outra porta
./gateway.exe -port 8001
```

### Buffer muito pequeno
```bash
# Aumentar buffer
./gateway.exe -buffer 500
```
