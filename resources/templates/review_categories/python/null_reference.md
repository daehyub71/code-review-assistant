# Null/Type 안전성 - Python

## What to Check

- **None 체크 누락**
  - None 반환 가능한 함수의 결과를 체크 없이 사용
  - Optional 타입 힌트 미사용
  - if x is None 대신 if not x 사용 (잘못된 패턴)

- **Type Hints 미사용**
  - 함수 매개변수/반환값 타입 힌트 없음
  - Optional, Union 타입 명시 안 함
  - mypy 타입 체킹 미사용

## Best Practices

### 1. Type Hints 사용
```python
# Bad
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

def process_user(user):
    return user.name.upper()  # user가 None이면 AttributeError

# Good
from typing import Optional

def get_user(user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def process_user(user: Optional[User]) -> str:
    if user is None:
        return "Unknown"
    return user.name.upper()
```

### 2. None 체크 (is None vs falsy)
```python
# Bad - 빈 문자열/0도 False로 판단
def get_value(data):
    if not data:  # ❌ data가 ""이나 0일 때도 True
        return "default"
    return data

# Good - 명시적 None 체크
def get_value(data: Optional[str]) -> str:
    if data is None:  # ✅ None만 체크
        return "default"
    return data
```

### 3. Optional과 Union 활용
```python
from typing import Optional, Union

# Optional[T] = Union[T, None]
def find_user(name: str) -> Optional[User]:
    return db.query(User).filter(User.name == name).first()

# Union으로 여러 타입 허용
def process_data(data: Union[str, int, None]) -> str:
    if data is None:
        return ""
    return str(data)
```

### 4. Walrus Operator로 간결하게
```python
# Bad
user = get_user(user_id)
if user is not None:
    print(user.name)

# Good (Python 3.8+)
if (user := get_user(user_id)) is not None:
    print(user.name)
```

### 5. dataclass와 default 값
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    name: str
    email: Optional[str] = None  # 기본값 None
    age: int = 0

user = User(name="John")  # email은 자동으로 None
```

## Example

**Before**:
```python
def get_user_email(user_id):
    user = database.find_user(user_id)
    return user.email  # user가 None이면 에러!

def calculate_discount(user):
    if not user:  # ❌ 잘못된 체크
        return 0
    return user.total_purchases * 0.1

class UserService:
    def __init__(self, db):
        self.db = db  # 타입 힌트 없음

    def save_user(self, data):  # 타입 불명확
        user = User(**data)
        self.db.add(user)
        return user
```

**After**:
```python
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    total_purchases: float = 0.0

class Database:
    def find_user(self, user_id: int) -> Optional[User]:
        """사용자 조회 - 없으면 None 반환"""
        # Implementation
        pass

def get_user_email(user_id: int) -> Optional[str]:
    """사용자 이메일 조회"""
    user = database.find_user(user_id)

    if user is None:
        return None

    return user.email

def calculate_discount(user: Optional[User]) -> float:
    """할인율 계산"""
    if user is None:  # ✅ 명시적 None 체크
        return 0.0

    return user.total_purchases * 0.1

class UserService:
    def __init__(self, db: Database) -> None:
        self.db: Database = db

    def save_user(self, data: Dict[str, Any]) -> User:
        """사용자 저장"""
        user = User(**data)
        self.db.add(user)
        return user

    def get_user_safely(self, user_id: int) -> str:
        """안전한 사용자 정보 조회"""
        if (user := self.db.find_user(user_id)) is not None:
            return f"User: {user.name} ({user.email})"
        return "User not found"
```

## mypy 타입 체킹

```bash
# mypy 설치
pip install mypy

# 타입 체킹 실행
mypy your_file.py

# pyproject.toml 또는 mypy.ini 설정
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## References

- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [typing module](https://docs.python.org/3/library/typing.html)
- [mypy - Static Type Checker](https://mypy.readthedocs.io/)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
