# GTA ANALYTICS V2 - CRITICAL SECURITY FIXES

## SUMMARY OF CRITICAL ISSUES TO FIX

1. API Keys exposed in git (4 keys: 2 OpenAI, 2 OpenRouter)
2. CORS wildcard allows any origin  
3. Export endpoint has no authentication
4. WebSocket endpoints unprotected
5. Gateway has no input validation
6. No rate limiting on endpoints
7. No security logging
8. No HTTPS encryption
9. Docker runs as root
10. Docker images unpinned

## IMMEDIATE ACTION REQUIRED

### 1. ROTATE API KEYS (30 mins)
- https://platform.openai.com/api-keys (delete old, create new)
- https://openrouter.ai/keys (delete old, create new)
- Update backend/.env with new keys

### 2. REMOVE FROM GIT (30 mins)
```bash
pip install git-filter-repo
cd gta-analytics-v2
git filter-repo --path backend/.env --invert-paths
git push origin --force-with-lease
```

### 3. FIX CORS (20 mins)
In main_websocket.py line 320, change:
```python
# BEFORE
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# AFTER
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if not allowed_origins_env:
    ALLOWED_ORIGINS = ["http://localhost:3000"]  # Dev only
else:
    ALLOWED_ORIGINS = allowed_origins_env.split(",")
```

Add to .env:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. ADD AUTHENTICATION (1-2 hours)
Add JWT to main_websocket.py:
```python
import jwt
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi import Depends

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "change-this")

def verify_token(credentials: HTTPAuthCredentials) -> bool:
    try:
        jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return True
    except:
        return False

# Update endpoints
@app.post("/export")
async def export_to_excel(
    format: str = "luis",
    credentials: HTTPAuthCredentials = Depends(security)
):
    if not verify_token(credentials):
        raise HTTPException(status_code=403)
    # ... rest of code
```

### 5. ADD INPUT VALIDATION TO GATEWAY (1-2 hours)
In gateway/websocket.go:
```go
const MAX_FRAME_SIZE = 10 * 1024 * 1024  // 10MB

func (h *WebSocketHandler) handleFrame(msg map[string]interface{}) error {
    frameData, ok := msg["data"].(string)
    if !ok || len(frameData) == 0 {
        return fmt.Errorf("invalid frame data")
    }
    
    if len(frameData) > MAX_FRAME_SIZE {
        return fmt.Errorf("frame too large")
    }
    
    if _, err := base64.StdEncoding.DecodeString(frameData); err != nil {
        return fmt.Errorf("invalid base64")
    }
    
    // ... rest of validation
}
```

## TOTAL EFFORT: 4-6 hours for CRITICAL issues

DO NOT DEPLOY UNTIL THESE ARE FIXED!

