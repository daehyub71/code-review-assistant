# 네이밍 규칙 - Java

## What to Check

- **일관되지 않은 케이스**
  - camelCase, snake_case 혼용
  - 상수 명명 규칙 미준수
  - 패키지명 대문자 사용

- **의미 없는 이름**
  - 단일 문자 변수 남용
  - 축약어 과다 사용

## Best Practices

### 1. 클래스/인터페이스: PascalCase (UpperCamelCase)
```java
// Bad
public class userService { }
public class User_Repository { }

// Good
public class UserService { }
public class UserRepository { }
```

### 2. 메서드/변수: camelCase (lowerCamelCase)
```java
// Bad
public void ProcessUser(String UserName) {
    String First_Name = getFirstName(UserName);
}

// Good
public void processUser(String userName) {
    String firstName = getFirstName(userName);
}
```

### 3. 상수: UPPER_SNAKE_CASE
```java
// Bad
public static final int maxRetryCount = 3;
public static final String defaultConnectionString = "...";

// Good
public static final int MAX_RETRY_COUNT = 3;
public static final String DEFAULT_CONNECTION_STRING = "...";
```

### 4. 패키지: 소문자 + 도메인 역순
```java
// Bad
package com.Company.MyApp.Services;

// Good
package com.company.myapp.services;
package com.company.myapp.domain.users;
```

### 5. Boolean: is/has/can 접두사
```java
// Bad
public boolean active;
public boolean delete() { }

// Good
public boolean isActive;
public boolean canDelete() { }
```

### 6. 컬렉션: 복수형
```java
// Bad
List<User> userList;
Map<Long, User> userMap;

// Good
List<User> users;
Map<Long, User> userById;
```

## Java 네이밍 규칙 요약

| 타입 | 규칙 | 예시 |
|------|------|------|
| 클래스 | PascalCase | `UserService`, `OrderManager` |
| 인터페이스 | PascalCase | `UserRepository`, `Serializable` |
| 메서드 | camelCase | `getUser()`, `processData()` |
| 변수 | camelCase | `userName`, `totalCount` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 패키지 | lowercase | `com.company.project.service` |
| Enum | PascalCase (타입), UPPER_SNAKE_CASE (값) | `enum Status { ACTIVE, INACTIVE }` |

## References

- [Java Naming Conventions](https://www.oracle.com/java/technologies/javase/codeconventions-namingconventions.html)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
