# 예외/에러 처리 - Python

## What to Check

- **bare except 사용**
  - except: 또는 except Exception: 과도한 사용
  - 예외 삼키기 (pass)
  - 구체적 예외 타입 지정 없음

- **에러 정보 손실**
  - raise 시 원본 예외 체인 끊김
  - 로깅 없이 예외 무시

## Best Practices

### 1. 구체적 예외 캐치
```python
# Bad
try:
    data = json.loads(text)
except:  # ❌ 모든 예외 캐치 (KeyboardInterrupt도!)
    print("Error")

# Good
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 2. Context Manager (with 문)
```python
# Bad
file = open("data.txt")
try:
    content = file.read()
finally:
    file.close()

# Good
with open("data.txt") as file:
    content = file.read()
# 자동으로 close() 호출
```

### 3. Custom Exception
```python
class UserNotFoundError(Exception):
    """사용자를 찾을 수 없음"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")

# 사용
def get_user(user_id: int) -> User:
    user = db.query(User).get(user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user
```

### 4. 예외 체이닝 (from)
```python
# Bad
try:
    data = external_api.fetch()
except ApiError as e:
    raise DataError("Failed to fetch")  # 원본 예외 손실

# Good
try:
    data = external_api.fetch()
except ApiError as e:
    raise DataError("Failed to fetch") from e  # 원본 예외 보존
```

### 5. else와 finally
```python
try:
    file = open("data.txt")
except FileNotFoundError:
    logger.error("File not found")
else:
    # 예외 발생하지 않았을 때만 실행
    content = file.read()
finally:
    # 항상 실행
    if 'file' in locals():
        file.close()
```

## Example

**Before**:
```python
def process_file(path):
    try:
        with open(path) as f:
            data = json.load(f)
            return process_data(data)
    except:  # ❌
        print("Error occurred")
        return None
```

**After**:
```python
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """데이터 처리 오류"""
    pass

def process_file(path: str) -> Optional[Dict[str, Any]]:
    """파일 처리"""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return process_data(data)

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return None

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        raise DataProcessingError(f"Invalid data format") from e

    except Exception as e:
        logger.error(f"Unexpected error processing {path}: {e}")
        raise
```

## References

- [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [Context Managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
