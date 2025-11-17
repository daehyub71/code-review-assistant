# Null/Undefined 안전성 - Java

## What to Check

- **NullPointerException 발생 가능성**
  - null 체크 없이 메서드 호출
  - 컬렉션 요소 접근 전 null 확인 누락
  - Optional 미사용

- **Null 반환**
  - null 대신 Optional 미사용
  - 빈 컬렉션 대신 null 반환
  - @Nullable / @NonNull 애노테이션 누락

## Best Practices

### 1. Optional 사용
```java
// Bad
public User findUser(Long id) {
    return userRepository.findById(id);  // null 반환 가능
}

public void processUser(Long id) {
    User user = findUser(id);
    String email = user.getEmail();  // NPE 위험
}

// Good
public Optional<User> findUser(Long id) {
    return userRepository.findById(id);
}

public void processUser(Long id) {
    findUser(id)
        .map(User::getEmail)
        .ifPresent(this::sendEmail);
}
```

### 2. Objects.requireNonNull() 사용
```java
import java.util.Objects;

public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = Objects.requireNonNull(
            repository,
            "repository must not be null"
        );
    }

    public void saveUser(User user) {
        Objects.requireNonNull(user, "user must not be null");
        repository.save(user);
    }
}
```

### 3. 빈 컬렉션 반환
```java
// Bad
public List<User> getUsers() {
    List<User> users = repository.findAll();
    return users.isEmpty() ? null : users;  // ❌
}

// Good
public List<User> getUsers() {
    List<User> users = repository.findAll();
    return users != null ? users : Collections.emptyList();
}

// Best
public List<User> getUsers() {
    return repository.findAll();  // 빈 리스트 반환, null 아님
}
```

### 4. @Nullable / @NonNull 애노테이션
```java
import org.springframework.lang.NonNull;
import org.springframework.lang.Nullable;

public class UserService {
    @NonNull
    public User createUser(@NonNull String name, @Nullable String nickname) {
        User user = new User();
        user.setName(name);
        user.setNickname(nickname != null ? nickname : "Anonymous");
        return user;
    }
}
```

## Example

**Before**:
```java
public class UserService {
    public String getUserEmail(Long userId) {
        User user = userRepository.findById(userId);  // null 가능
        return user.getEmail();  // NPE!
    }

    public List<Order> getUserOrders(Long userId) {
        User user = findUser(userId);
        if (user == null) return null;  // ❌
        return user.getOrders();
    }
}
```

**After**:
```java
public class UserService {
    public Optional<String> getUserEmail(Long userId) {
        return userRepository.findById(userId)
            .map(User::getEmail);
    }

    public List<Order> getUserOrders(Long userId) {
        return userRepository.findById(userId)
            .map(User::getOrders)
            .orElse(Collections.emptyList());  // ✅ 빈 리스트 반환
    }

    public void processUser(@NonNull Long userId) {
        Objects.requireNonNull(userId, "userId cannot be null");

        userRepository.findById(userId)
            .ifPresentOrElse(
                user -> log.info("Processing user: {}", user.getName()),
                () -> log.warn("User not found: {}", userId)
            );
    }
}
```

## References

- [Optional (Java 8+)](https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html)
- [Objects.requireNonNull()](https://docs.oracle.com/javase/8/docs/api/java/util/Objects.html#requireNonNull-T-)
- [Null Safety Annotations](https://www.jetbrains.com/help/idea/nullable-and-notnull-annotations.html)
