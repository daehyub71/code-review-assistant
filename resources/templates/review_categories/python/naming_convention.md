# 네이밍 규칙 - Python

## What to Check

- **PEP 8 위반**
  - camelCase 대신 snake_case 미사용
  - 상수 대문자 미사용
  - 클래스명 PascalCase 미사용

- **의미 없는 이름**
  - 단일 문자 변수 남용
  - 축약어 과다 사용

## Best Practices

### 1. 함수/변수: snake_case
```python
# Bad
def ProcessUser(UserName):
    FirstName = GetFirstName(UserName)

# Good
def process_user(user_name):
    first_name = get_first_name(user_name)
```

### 2. 클래스: PascalCase
```python
# Bad
class user_service:
    pass

# Good
class UserService:
    pass
```

### 3. 상수: UPPER_SNAKE_CASE
```python
# Bad
max_retry_count = 3
api_timeout = 30

# Good
MAX_RETRY_COUNT = 3
API_TIMEOUT = 30
```

### 4. Private: _leading_underscore
```python
class User:
    def __init__(self, name: str):
        self.name = name  # public
        self._id = None  # protected
        self.__password = None  # private (name mangling)

    def _internal_method(self):  # protected
        pass
```

### 5. Boolean: is_/has_/can_
```python
# Bad
active = True
authenticated = False

# Good
is_active = True
has_permission = False
can_delete = False
```

## Python 네이밍 규칙 요약

| 타입 | 규칙 | 예시 |
|------|------|------|
| 함수 | snake_case | `get_user()`, `process_data()` |
| 변수 | snake_case | `user_name`, `total_count` |
| 클래스 | PascalCase | `UserService`, `OrderManager` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY`, `API_KEY` |
| Private | _snake_case | `_internal_value`, `_helper()` |
| 모듈 | snake_case | `user_service.py` |
| 패키지 | lowercase | `mypackage/` |

## References

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
