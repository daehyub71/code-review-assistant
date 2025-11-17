# 코드 문서화 - Python

## What to Check

- **Docstring 누락**
  - 함수/클래스에 주석 없음
  - 매개변수/반환값 설명 없음
  - Google/NumPy 스타일 미사용

- **불명확한 주석**
  - 오래된 주석
  - 자명한 코드에 불필요한 주석

## Best Practices

### 1. Docstring (Google Style)
```python
def get_user(user_id: int) -> Optional[User]:
    """사용자 조회

    지정된 ID의 사용자를 데이터베이스에서 조회합니다.

    Args:
        user_id: 조회할 사용자 ID (양수)

    Returns:
        사용자 객체. 없으면 None

    Raises:
        ValueError: user_id가 0 이하인 경우
        DatabaseError: DB 연결 실패 시

    Examples:
        >>> user = get_user(123)
        >>> print(user.name)
        'John Doe'
    """
    if user_id <= 0:
        raise ValueError("user_id must be positive")
    return db.query(User).get(user_id)
```

### 2. 클래스 Docstring
```python
class UserService:
    """사용자 관리 서비스

    사용자 생성, 조회, 수정, 삭제 기능을 제공합니다.

    Attributes:
        db: 데이터베이스 세션
        cache: 사용자 캐시 (Optional)

    Examples:
        >>> service = UserService(db_session)
        >>> user = service.create_user("john@example.com")
    """

    def __init__(self, db: Session, cache: Optional[Cache] = None):
        """초기화

        Args:
            db: 데이터베이스 세션
            cache: 선택적 캐시 인스턴스
        """
        self.db = db
        self.cache = cache
```

### 3. Type Hints로 문서화 강화
```python
from typing import List, Dict, Optional, Union

def process_users(
    users: List[User],
    filter_func: Optional[Callable[[User], bool]] = None
) -> Dict[int, str]:
    """사용자 목록 처리

    Args:
        users: 사용자 객체 리스트
        filter_func: 선택적 필터 함수

    Returns:
        사용자 ID를 키, 이름을 값으로 하는 딕셔너리
    """
    pass
```

### 4. TODO/FIXME 주석
```python
def calculate_discount(amount: float) -> float:
    # TODO: 사용자 등급별 할인율 적용 필요 (Issue #123)
    # FIXME: 소수점 계산 오류 수정 필요
    return amount * 0.1

# NOTE: 임시 해결책 - v2.0에서 제거 예정
def legacy_method():
    pass
```

## References

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [NumPy Docstring Style](https://numpydoc.readthedocs.io/en/latest/format.html)
