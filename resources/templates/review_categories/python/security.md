# 보안 모범 사례 - Python

## What to Check

- **SQL Injection**
  - f-string이나 % 포매팅으로 쿼리 생성
  - 파라미터 바인딩 미사용
  - ORM 미사용

- **민감 정보 노출**
  - 하드코딩된 비밀번호
  - 로그에 민감 정보 출력

## Best Practices

### 1. SQL Injection 방지
```python
# Bad - SQL Injection 취약
username = request.form['username']
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)  # ❌

# Good - 파라미터 바인딩
username = request.form['username']
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))  # ✅

# Best - ORM 사용
from sqlalchemy.orm import Session

user = session.query(User).filter(User.username == username).first()
```

### 2. 비밀번호 해싱
```python
from passlib.hash import bcrypt

# 해싱
hashed = bcrypt.hash("password123")

# 검증
is_valid = bcrypt.verify("password123", hashed)
```

### 3. 환경 변수로 비밀 관리
```python
# Bad
API_KEY = "sk-1234567890"  # ❌ 하드코딩

# Good
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not set")
```

### 4. 입력 검증
```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: int

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('age')
    def valid_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v
```

## References

- [OWASP Python Security](https://cheatsheetseries.owasp.org/cheatsheets/Python_Security_Cheat_Sheet.html)
- [pydantic](https://docs.pydantic.dev/)
- [passlib](https://passlib.readthedocs.io/)
