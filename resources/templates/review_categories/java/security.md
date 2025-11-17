# 보안 모범 사례 - Java

## What to Check

- **SQL Injection**
  - 문자열 연결로 쿼리 생성
  - PreparedStatement 미사용
  - JPA/MyBatis 파라미터 바인딩 미사용

- **민감 정보 노출**
  - 하드코딩된 비밀번호
  - 로그에 민감 정보 출력

## Best Practices

### 1. PreparedStatement 사용
```java
// Bad - SQL Injection 취약
String query = "SELECT * FROM users WHERE username = '" + username + "'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(query);

// Good
String query = "SELECT * FROM users WHERE username = ?";
PreparedStatement pstmt = conn.prepareStatement(query);
pstmt.setString(1, username);
ResultSet rs = pstmt.executeQuery();

// Best - JPA 사용
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
}
```

### 2. 비밀번호 해싱
```java
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class UserService {
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    public String hashPassword(String password) {
        return encoder.encode(password);
    }

    public boolean verifyPassword(String password, String hashedPassword) {
        return encoder.matches(password, hashedPassword);
    }
}
```

### 3. 입력 검증
```java
import javax.validation.constraints.*;

public class UserRequest {
    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    @Size(max = 255)
    private String email;

    @NotBlank
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$",
             message = "Password must be at least 8 characters with letters and numbers")
    private String password;
}

@PostMapping("/users")
public ResponseEntity<?> createUser(@Valid @RequestBody UserRequest request) {
    // 검증 통과 시에만 실행
}
```

### 4. 민감 정보 보호
```java
// Bad
log.info("User login: {} with password: {}", username, password);  // ❌

// Good
log.info("User login attempt: {}", username);  // ✅

// application.yml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    # 민감 정보 마스킹
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Spring Security](https://spring.io/projects/spring-security)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
