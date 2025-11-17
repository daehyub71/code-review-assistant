# 리소스 관리 - Python

## What to Check

- **with 문 미사용**
  - 파일, 연결 등 수동 close()
  - try-finally로 리소스 정리
  - Context Manager 미활용

- **메모리 누수**
  - 전역 변수에 대용량 데이터
  - 순환 참조
  - 캐시 무제한 증가

## Best Practices

### 1. with 문 사용
```python
# Bad
file = open("data.txt")
content = file.read()
file.close()  # 예외 발생 시 호출 안 됨

# Good
with open("data.txt") as file:
    content = file.read()
# 자동 close()
```

### 2. 여러 리소스 관리
```python
# Bad
file1 = open("input.txt")
file2 = open("output.txt", "w")
try:
    file2.write(file1.read())
finally:
    file1.close()
    file2.close()

# Good
with open("input.txt") as file1, \
     open("output.txt", "w") as file2:
    file2.write(file1.read())
```

### 3. Custom Context Manager
```python
from contextlib import contextmanager

@contextmanager
def database_transaction(db):
    """트랜잭션 컨텍스트 매니저"""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 사용
with database_transaction(db) as session:
    session.add(user)
```

### 4. __enter__/__exit__ 구현
```python
class DatabaseConnection:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.conn = None

    def __enter__(self):
        self.conn = connect(self.conn_string)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        return False  # 예외 전파

# 사용
with DatabaseConnection(conn_str) as conn:
    cursor = conn.cursor()
```

## References

- [Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
- [contextlib](https://docs.python.org/3/library/contextlib.html)
