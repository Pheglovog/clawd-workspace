# FastAPI 最佳实践和异步编程指南

## 📋 概述

FastAPI 是一个现代、快速（高性能）的 Web 框架，用于基于 Python 的 API 开发。它基于标准 Python 类型提示，支持异步编程。

## 🚀 核心特性

### 1. 类型提示
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item}
```

### 2. 自动文档生成
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

### 3. 数据验证
使用 Pydantic 进行自动验证：

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=120)
```

## 🔧 最佳实践

### 1. 项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   └── items.py
│   │   │   └── api.py    # 路由聚合
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py    # 配置
│   │   └── security.py  # 安全
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py      # Pydantic 模型
│   ├── crud/
│   │   ├── __init__.py
│   │   └── user.py      # 数据库操作
│   └── db/
│       ├── __init__.py
│       └── session.py    # 数据库会话
├── alembic/              # 数据库迁移
├── tests/
├── requirements.txt
└── README.md
```

### 2. 配置管理

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

使用：
```python
from app.core.config import settings

@app.get("/")
async def root():
    return {"app_name": settings.APP_NAME}
```

### 3. 异步数据库操作

#### SQLModel / SQLAlchemy 2.0

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

#### MongoDB (Motor)

```python
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends

client = AsyncIOMotorClient("mongodb://localhost:27017")
database = client.mydatabase

async def get_database():
    return database

@app.post("/users/")
async def create_user(
    user: UserCreate,
    db = Depends(get_database)
):
    user_dict = user.dict()
    await db.users.insert_one(user_dict)
    return user_dict
```

### 4. 异步操作

#### 异步 HTTP 请求

```python
import httpx

@app.get("/weather")
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/{city}"
        )
        return response.json()
```

#### 并发请求

```python
import asyncio
import httpx

async def fetch_weather(city: str, client: httpx.AsyncClient):
    response = await client.get(f"https://api.weather.com/{city}")
    return city, response.json()

@app.get("/weather/multiple")
async def get_multiple_weather(cities: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_weather(city, client)
            for city in cities
        ]
        results = await asyncio.gather(*tasks)
        return {city: data for city, data in results}
```

### 5. 依赖注入

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### 6. 中间件

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 7. CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8. 错误处理

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something."}
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
```

### 9. 后台任务

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # 模拟发送邮件
    time.sleep(3)
    print(f"Email sent to {email}: {message}")

@app.post("/send-email/{email}")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Hello!")
    return {"message": "Email will be sent in the background"}
```

### 10. WebSocket

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

## 📊 性能优化

### 1. 使用异步 I/O

```python
# ❌ 同步阻塞
@app.get("/")
def root():
    time.sleep(1)  # 阻塞
    return {"message": "Hello"}

# ✅ 异步非阻塞
@app.get("/")
async def root():
    await asyncio.sleep(1)  # 非阻塞
    return {"message": "Hello"}
```

### 2. 连接池

```python
import httpx

# ✅ 使用连接池
client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_connections=100)
)

@app.on_event("startup")
async def startup():
    global client
    client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
```

### 3. 缓存

```python
from functools import lru_cache
from fastapi_cache import FastAPICache, Coder
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/expensive")
@cache(expire=60)  # 缓存 60 秒
async def expensive_operation():
    # 昂贵的操作
    return {"result": "computed"}
```

## 🔐 安全性

### 1. 密码哈希

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Token

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 3. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/protected")
@limiter.limit("5/minute")
async def protected(request: Request):
    return {"message": "This endpoint is rate limited"}
```

## 🧪 测试

### pytest + httpx

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_read_item():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/5?q=somequery")
        assert response.status_code == 200
        assert response.json() == {"item_id": 5, "q": "somequery"}
```

## 📝 日志

```python
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

## 🚀 部署

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Gunicorn + Uvicorn

```bash
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

---

**更新时间**: 2026-02-03
