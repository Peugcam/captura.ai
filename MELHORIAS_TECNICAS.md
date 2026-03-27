# 🔧 MELHORIAS TÉCNICAS - Detalhamento de Implementação

**Versão:** 1.0
**Data:** 27/03/2026

---

## 1. POSTGRESQL + REDIS 💾

### **Problema Atual:**
- Todos os dados em memória (RAM)
- Perde tudo ao reiniciar app
- Não escala horizontalmente
- Arquivo: `backend/src/team_tracker.py:77-88`

### **Solução:**
**PostgreSQL:** Dados permanentes (partidas, players, kills históricos)
**Redis:** Cache e estado temporário (partidas ativas)

### **Implementação:**

#### **1.1 Setup PostgreSQL no Fly.io**
```bash
# Criar PostgreSQL no Fly.io
fly postgres create --name gta-analytics-db --region gru

# Conectar ao backend
fly postgres attach gta-analytics-db -a gta-analytics-v2

# Vai criar variável de ambiente: DATABASE_URL
```

#### **1.2 Setup Redis Cloud**
```bash
# https://redis.com/ - Plano gratuito 30MB
# Ou Fly.io Redis:
fly redis create --name gta-analytics-redis --region gru
```

#### **1.3 Migração de Code**

**requirements.txt:**
```txt
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
alembic==1.13.0  # migrations
```

**backend/database.py (NOVO):**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis
import redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
```

**backend/models.py (NOVO):**
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True)
    game_type = Column(String)  # gta, naruto, etc
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String)  # active, finished, cancelled

    teams = relationship("Team", back_populates="match")
    kills = relationship("Kill", back_populates="match")

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    name = Column(String)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)

    match = relationship("Match", back_populates="teams")
    players = relationship("Player", back_populates="team")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    name = Column(String)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)

    team = relationship("Team", back_populates="players")

class Kill(Base):
    __tablename__ = "kills"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    killer = Column(String)
    victim = Column(String)
    weapon = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="kills")
```

**backend/src/team_tracker.py (REFATORAR):**
```python
import json
from ..database import redis_client, SessionLocal
from ..models import Match, Team, Player, Kill

class TeamTracker:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.redis_key = f"match:{match_id}"

    def get_state(self):
        """Busca estado do Redis (cache)"""
        cached = redis_client.get(self.redis_key)
        if cached:
            return json.loads(cached)

        # Se não tem cache, busca do PostgreSQL
        db = SessionLocal()
        match = db.query(Match).filter(Match.match_id == self.match_id).first()
        if match:
            state = self._match_to_dict(match)
            self._cache_state(state)
            return state
        return None

    def update_state(self, state: dict):
        """Atualiza Redis (rápido) e PostgreSQL (persistente)"""
        # Cache imediato
        redis_client.setex(
            self.redis_key,
            3600,  # 1 hora TTL
            json.dumps(state)
        )

        # Persistir no PostgreSQL (assíncrono)
        self._save_to_db(state)

    def add_kill(self, killer: str, victim: str, weapon: str):
        """Registra kill"""
        db = SessionLocal()
        try:
            # Salvar no PostgreSQL
            kill = Kill(
                match_id=self._get_match_db_id(),
                killer=killer,
                victim=victim,
                weapon=weapon
            )
            db.add(kill)
            db.commit()

            # Atualizar cache
            state = self.get_state()
            # ... lógica de atualização ...
            self.update_state(state)
        finally:
            db.close()
```

#### **1.4 Migrations**
```bash
# Criar migrations
alembic init alembic
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

**Esforço:** 5-7 dias
**Benefício:** Persistência + escala 10x

---

## 2. CI/CD PIPELINE + TESTES 🤖

### **Problema Atual:**
- Deploys manuais
- Sem testes automáticos
- Alto risco de bugs em produção
- Cobertura de testes <20%

### **Solução:**
GitHub Actions + Pytest + Cobertura automática

### **Implementação:**

#### **2.1 GitHub Actions Workflow**

**.github/workflows/ci.yml (NOVO):**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test
        REDIS_URL: redis://localhost:6379
      run: |
        cd backend
        pytest --cov=. --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 backend --max-line-length=100

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Fly.io
      uses: superfly/flyctl-actions@1.3
      with:
        args: "deploy"
      env:
        FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

#### **2.2 Testes Automatizados**

**backend/tests/test_team_tracker.py (NOVO):**
```python
import pytest
from src.team_tracker import TeamTracker

@pytest.fixture
def tracker():
    return TeamTracker(match_id="test-match-001")

def test_add_kill(tracker):
    """Testa adicionar kill"""
    tracker.add_kill(
        killer="Player1",
        victim="Player2",
        weapon="AK-47"
    )

    state = tracker.get_state()
    assert state["kills_count"] == 1

def test_team_statistics(tracker):
    """Testa estatísticas de time"""
    tracker.add_kill("TeamA-Player1", "TeamB-Player1", "M4")

    team_a_kills = tracker.get_team_kills("TeamA")
    assert team_a_kills == 1

@pytest.mark.asyncio
async def test_concurrent_kills(tracker):
    """Testa kills simultâneas"""
    import asyncio

    tasks = [
        tracker.add_kill(f"P{i}", f"V{i}", "AK")
        for i in range(10)
    ]
    await asyncio.gather(*tasks)

    state = tracker.get_state()
    assert state["kills_count"] == 10
```

**backend/pytest.ini (NOVO):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --tb=short
    --cov-report=term-missing
```

**Esforço:** 5-7 dias
**Benefício:** 50% menos bugs

---

## 3. PROCESSAMENTO PARALELO 🚀

### **Problema Atual:**
- Frames processados sequencialmente
- 1 frame por vez
- Throughput: ~1-2 FPS
- Arquivo: `backend/processor.py:934-1000`

### **Solução:**
asyncio.gather para processamento paralelo

### **Implementação:**

**backend/processor.py (REFATORAR):**
```python
import asyncio

# ANTES (Sequencial):
async def process_frames(self, frames: list):
    results = []
    for frame in frames:
        result = await self.process_single_frame(frame)
        results.append(result)
    return results

# DEPOIS (Paralelo):
async def process_frames(self, frames: list):
    """Processa múltiplos frames em paralelo"""
    tasks = [
        self.process_single_frame(frame)
        for frame in frames
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]

async def process_single_frame(self, frame: bytes):
    """Processa um frame individual"""
    try:
        # OCR pre-filter
        if not await self.ocr_filter.has_text(frame):
            return None

        # Vision API
        result = await self.vision_client.analyze(frame)

        # Parse kills
        kills = self.parse_kills(result)
        return kills
    except Exception as e:
        logger.error(f"Frame processing error: {e}")
        return None
```

**Controle de Concorrência:**
```python
from asyncio import Semaphore

class FrameProcessor:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = Semaphore(max_concurrent)

    async def process_single_frame(self, frame: bytes):
        async with self.semaphore:
            # Limita concorrência para não sobrecarregar API
            return await self._process(frame)
```

**Configuração:**
```python
# backend/config.py
MAX_CONCURRENT_FRAMES = int(os.getenv("MAX_CONCURRENT_FRAMES", "5"))
```

**Esforço:** 2-3 dias
**Ganho:** 3-5x throughput

---

## 4. FLORENCE-2 SELF-HOSTED 🤖

### **Problema Atual:**
- Vision API custa $50-150/mês
- Dependente de serviços externos
- Latência de rede

### **Solução:**
Microsoft Florence-2 open-source model

### **Implementação:**

#### **4.1 Setup GPU VM**
```bash
# RunPod (mais barato) ou Fly.io GPU
# GPU: NVIDIA T4 (16GB) - $0.40/hora = ~$300/mês
# OU GPU: RTX 3060 (12GB) - $0.25/hora = ~$180/mês
```

#### **4.2 Deploy Florence-2**

**florence-service/Dockerfile (NOVO):**
```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN pip install transformers pillow fastapi uvicorn

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**florence-service/app.py (NOVO):**
```python
from fastapi import FastAPI, File, UploadFile
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import io

app = FastAPI()

# Carregar modelo (uma vez no startup)
model = AutoModelForVision2Seq.from_pretrained(
    "microsoft/Florence-2-large",
    trust_remote_code=True
)
processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-large",
    trust_remote_code=True
)

@app.post("/analyze")
async def analyze_frame(file: UploadFile = File(...)):
    """Analisa frame e detecta kills"""

    # Carregar imagem
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # Processar
    prompt = "<OD>"  # Object Detection
    inputs = processor(text=prompt, images=image, return_tensors="pt")

    # Gerar resposta
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        num_beams=3
    )

    result = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

    # Parse kill feed
    kills = parse_kill_feed(result)

    return {"kills": kills}

def parse_kill_feed(text: str):
    """Extrai kills do texto"""
    # Lógica de parsing similar ao atual
    # ...
    pass
```

#### **4.3 Integrar no Backend**

**backend/src/vision_client.py (MODIFICAR):**
```python
import httpx
from config import FLORENCE_SERVICE_URL, USE_FLORENCE

class VisionClient:
    def __init__(self):
        self.florence_url = FLORENCE_SERVICE_URL
        self.use_florence = USE_FLORENCE

    async def analyze(self, frame: bytes):
        """Analisa frame (Florence-2 ou API paga)"""

        if self.use_florence:
            try:
                return await self._analyze_florence(frame)
            except Exception as e:
                logger.warning(f"Florence failed, falling back to API: {e}")

        # Fallback para API paga
        return await self._analyze_litellm(frame)

    async def _analyze_florence(self, frame: bytes):
        """Usa Florence-2 self-hosted"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.florence_url}/analyze",
                files={"file": frame},
                timeout=30.0
            )
            return response.json()
```

**backend/config.py:**
```python
USE_FLORENCE = os.getenv("USE_FLORENCE", "true").lower() == "true"
FLORENCE_SERVICE_URL = os.getenv("FLORENCE_SERVICE_URL", "http://florence:8000")
```

**Esforço:** 3-5 dias
**Economia:** $100+/mês em alto volume

---

## 5. BACKUP AUTOMÁTICO 🔒

### **Problema Atual:**
- Sem backup
- Risco de perda de dados

### **Solução:**
Snapshots automáticos para S3

### **Implementação:**

**backend/src/backup.py (NOVO):**
```python
import asyncio
import boto3
import json
from datetime import datetime
from .database import SessionLocal
from .models import Match

class BackupService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = "gta-analytics-backups"

    async def start_periodic_backup(self):
        """Backup a cada 6 horas"""
        while True:
            try:
                await self.create_backup()
                await asyncio.sleep(6 * 3600)  # 6 horas
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                await asyncio.sleep(3600)  # Retry após 1h

    async def create_backup(self):
        """Cria snapshot completo"""
        timestamp = datetime.utcnow().isoformat()
        filename = f"backup-{timestamp}.json"

        db = SessionLocal()
        try:
            # Exportar todos os dados
            matches = db.query(Match).all()
            data = {
                "timestamp": timestamp,
                "matches": [self._match_to_dict(m) for m in matches]
            }

            # Upload para S3
            self.s3.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=json.dumps(data),
                ServerSideEncryption='AES256'
            )

            logger.info(f"Backup created: {filename}")
        finally:
            db.close()

    async def restore_from_backup(self, backup_filename: str):
        """Restaura de um backup"""
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=backup_filename
        )
        data = json.loads(response['Body'].read())

        # Restaurar no banco
        # ... lógica de restore ...
```

**backend/main_websocket.py (ADICIONAR):**
```python
from src.backup import BackupService

@app.on_event("startup")
async def startup_event():
    backup_service = BackupService()
    asyncio.create_task(backup_service.start_periodic_backup())
```

**Custo:** ~$5/mês (S3)
**Esforço:** 2 dias

---

## 6. AUTENTICAÇÃO DASHBOARD 🔐

### **Problema Atual:**
- Dashboards públicos
- Qualquer um pode acessar
- Dados expostos

### **Solução:**
API key simples + JWT

### **Implementação:**

**backend/src/auth.py (NOVO):**
```python
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from config import API_KEYS

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifica API key"""
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(403, "Invalid API key")
    return api_key
```

**backend/main_websocket.py (MODIFICAR):**
```python
from src.auth import verify_api_key

@app.get("/dashboard")
async def dashboard(api_key: str = Security(verify_api_key)):
    """Dashboard protegido"""
    return FileResponse("dashboard-obs.html")

@app.websocket("/events")
async def events_websocket(websocket: WebSocket, api_key: str = Query(...)):
    """WebSocket protegido"""
    if api_key not in API_KEYS:
        await websocket.close(code=403)
        return

    await websocket.accept()
    # ... resto da lógica ...
```

**dashboard-obs.html (MODIFICAR):**
```javascript
// Solicitar API key no primeiro acesso
let apiKey = localStorage.getItem('api_key');

if (!apiKey) {
    apiKey = prompt('Digite sua API key:');
    localStorage.setItem('api_key', apiKey);
}

// WebSocket com auth
const ws = new WebSocket(`wss://gta-analytics-v2.fly.dev/events?api_key=${apiKey}`);
```

**Esforço:** 2 dias

---

## 7. SISTEMA DE CHAVES (BRACKETS) 🏆

### **Implementação:**

**backend/models.py (ADICIONAR):**
```python
class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    bracket_type = Column(String)  # single_elim, double_elim
    status = Column(String)  # upcoming, active, finished

    matches = relationship("TournamentMatch", back_populates="tournament")

class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    round = Column(Integer)
    match_number = Column(Integer)
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    status = Column(String)  # pending, active, finished
```

**backend/api/brackets.py (NOVO):**
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/tournaments")
async def create_tournament(name: str, teams: list[str]):
    """Cria torneio com chaves"""
    # Gerar bracket
    bracket = generate_single_elimination(teams)
    # Salvar no DB
    # ...

def generate_single_elimination(teams: list[str]):
    """Gera chave de eliminação simples"""
    import math
    rounds = math.ceil(math.log2(len(teams)))
    # Lógica de geração...
```

**Esforço:** 2 semanas

---

## 📊 RESUMO DE ESFORÇOS

| Melhoria | Esforço | Impacto | Custo/mês |
|----------|---------|---------|-----------|
| PostgreSQL + Redis | 1 semana | CRÍTICO | $35 |
| CI/CD + Testes | 1 semana | CRÍTICO | $0 |
| Backup | 2 dias | ALTO | $5 |
| Processamento Paralelo | 3 dias | ALTO | $0 |
| Florence-2 | 5 dias | ALTO | $50 (economiza $100) |
| Autenticação | 2 dias | ALTO | $0 |
| Sistema de Chaves | 2 semanas | ALTO | $0 |

**Total:** ~6 semanas de desenvolvimento
**Custo adicional:** ~$90/mês
**Economia:** ~$100/mês (APIs)
**Resultado:** Sistema 10x mais robusto e escalável

---

**Última Atualização:** 27/03/2026
