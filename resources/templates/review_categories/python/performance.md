# 성능 최적화 - Python

## What to Check

- **비효율적인 자료구조**
  - list에서 in 연산 반복
  - set/dict 미사용
  - List comprehension 대신 반복문

- **문자열 연결**
  - + 연산자 반복 사용
  - join() 미사용

## Best Practices

### 1. set/dict 활용
```python
# Bad - O(n)
user_ids = [1, 2, 3, ..., 1000]
if target_id in user_ids:  # 선형 탐색
    pass

# Good - O(1)
user_ids = {1, 2, 3, ..., 1000}
if target_id in user_ids:  # 해시 탐색
    pass
```

### 2. List Comprehension
```python
# Bad
result = []
for item in items:
    if item.is_active:
        result.append(item.name.upper())

# Good
result = [item.name.upper() for item in items if item.is_active]
```

### 3. Generator Expression (메모리 효율)
```python
# Bad - 전체 리스트 메모리 적재
total = sum([x**2 for x in range(1000000)])

# Good - lazy evaluation
total = sum(x**2 for x in range(1000000))
```

### 4. join() for 문자열 연결
```python
# Bad
result = ""
for item in items:
    result += str(item) + ","  # 매번 새 문자열 생성

# Good
result = ",".join(str(item) for item in items)
```

### 5. functools.lru_cache
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## References

- [Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [functools](https://docs.python.org/3/library/functools.html)
