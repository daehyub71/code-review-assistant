# 설정 관리 - Python

## What to Check

- **하드코딩된 값**
  - 소스 코드에 DB 연결 문자열
  - 하드코딩된 API 키
  - 환경별 값이 코드에 포함

- **Magic Number/String**
  - 의미 불명확한 숫자
  - 반복되는 문자열 리터럴

## Best Practices

### 1. 환경 변수 사용
```python
# Bad
DB_URL = "postgresql://localhost:5432/mydb"
API_KEY = "sk-1234567890"  # ❌

# Good
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

DB_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

### 2. .env 파일
```.env
# .env (git에 추가하지 않음!)
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=sk-1234567890
DEBUG=True
LOG_LEVEL=INFO
```

```python
# .env.example (git에 추가)
DATABASE_URL=
API_KEY=
DEBUG=False
LOG_LEVEL=WARNING
```

### 3. pydantic Settings
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False
    max_connections: int = 10

    class Config:
        env_file = ".env"

# 사용
settings = Settings()
print(settings.database_url)
```

### 4. config.py 모듈
```python
# config.py
import os

class Config:
    DEBUG = False
    TESTING = False
    DATABASE_URL = os.getenv("DATABASE_URL")

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = "sqlite:///dev.db"

class ProductionConfig(Config):
    DATABASE_URL = os.getenv("DATABASE_URL")

# 환경에 따라 선택
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
```

### 5. 상수 정의
```python
# Bad - Magic Number
def calculate_discount(amount: float) -> float:
    if amount > 100:
        return amount * 0.1  # 0.1이 무엇?
    return 0

# Good - 상수 정의
# constants.py
PREMIUM_THRESHOLD = 100.0
PREMIUM_DISCOUNT_RATE = 0.1
STANDARD_DISCOUNT_RATE = 0.05

# service.py
from .constants import PREMIUM_THRESHOLD, PREMIUM_DISCOUNT_RATE

def calculate_discount(amount: float) -> float:
    if amount > PREMIUM_THRESHOLD:
        return amount * PREMIUM_DISCOUNT_RATE
    return 0.0
```

### 6. dataclass로 설정 그룹화
```python
from dataclasses import dataclass
import os

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    echo: bool = False

@dataclass
class CacheConfig:
    ttl: int = 3600
    max_size: int = 1000

@dataclass
class AppConfig:
    database: DatabaseConfig
    cache: CacheConfig
    debug: bool = False

# 사용
config = AppConfig(
    database=DatabaseConfig(
        url=os.getenv("DATABASE_URL"),
        pool_size=int(os.getenv("DB_POOL_SIZE", "10"))
    ),
    cache=CacheConfig(
        ttl=int(os.getenv("CACHE_TTL", "3600"))
    ),
    debug=os.getenv("DEBUG", "False").lower() == "true"
)
```

## Example

**Before**:
```python
# Bad
class UserService:
    def __init__(self):
        self.db_url = "postgresql://localhost:5432/mydb"  # ❌
        self.api_key = "sk-1234567890"  # ❌

    def send_email(self, to: str):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        password = "password123"  # ❌

    def calculate_fee(self, amount: float) -> float:
        if amount > 1000:  # Magic number
            return amount * 0.02  # Magic number
        return 0
```

**After**:
```python
# .env
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=sk-1234567890
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_PASSWORD=password123
FEE_PREMIUM_THRESHOLD=1000
FEE_PREMIUM_RATE=0.02

# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    smtp_server: str
    smtp_port: int
    email_password: str
    fee_premium_threshold: float
    fee_premium_rate: float

    class Config:
        env_file = ".env"

settings = Settings()

# service.py
class UserService:
    def __init__(self):
        self.db_url = settings.database_url
        self.api_key = settings.api_key

    def send_email(self, to: str):
        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        password = settings.email_password

    def calculate_fee(self, amount: float) -> float:
        if amount > settings.fee_premium_threshold:
            return amount * settings.fee_premium_rate
        return 0.0
```

## References

- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [The Twelve-Factor App - Config](https://12factor.net/config)
