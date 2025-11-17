# 성능 최적화 - Java

## What to Check

- **비효율적인 컬렉션 사용**
  - ArrayList에서 contains() 반복 호출
  - HashSet/HashMap 미사용
  - Stream API 과다 사용으로 성능 저하

- **String concatenation**
  - + 연산자 반복 사용
  - StringBuilder 미사용

## Best Practices

### 1. 적절한 컬렉션 선택
```java
// Bad - O(n)
List<Integer> ids = new ArrayList<>();
if (ids.contains(targetId)) {  // 선형 탐색
}

// Good - O(1)
Set<Integer> ids = new HashSet<>();
if (ids.contains(targetId)) {  // 해시 탐색
}
```

### 2. StringBuilder 사용
```java
// Bad
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i + ",";  // 1000개 객체 생성
}

// Good
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i).append(',');
}
String result = sb.toString();
```

### 3. Stream API 적절히 사용
```java
// Bad - 여러 번 순회
List<User> users = getUsers();
List<User> activeUsers = users.stream()
    .filter(User::isActive)
    .collect(Collectors.toList());
List<User> adultUsers = activeUsers.stream()
    .filter(u -> u.getAge() >= 18)
    .collect(Collectors.toList());

// Good - 단일 순회
List<User> users = getUsers().stream()
    .filter(u -> u.isActive() && u.getAge() >= 18)
    .collect(Collectors.toList());
```

### 4. 병렬 Stream 활용
```java
// 대량 데이터 처리
List<User> processedUsers = users.parallelStream()
    .map(this::processUser)
    .collect(Collectors.toList());
```

## References

- [Java Performance](https://docs.oracle.com/javase/8/docs/technotes/guides/performance/)
- [Stream API](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html)
