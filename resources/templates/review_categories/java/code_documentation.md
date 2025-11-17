# 코드 문서화 - Java

## What to Check

- **JavaDoc 주석 누락**
  - Public API에 주석 없음
  - 메서드 매개변수/반환값 설명 누락
  - 예외 발생 조건 미문서화

- **불명확한 주석**
  - 오래된 주석 (코드와 불일치)
  - 자명한 코드에 불필요한 주석

## Best Practices

### 1. JavaDoc 주석
```java
/**
 * 사용자 관리 서비스를 제공합니다.
 * <p>
 * 이 클래스는 사용자 생성, 조회, 수정, 삭제 기능을 제공하며
 * 트랜잭션 관리를 자동으로 처리합니다.
 * </p>
 *
 * @author 김개발
 * @version 1.0
 * @since 2024-01-01
 */
public class UserService {

    /**
     * 지정된 ID의 사용자를 조회합니다.
     *
     * @param id 조회할 사용자 ID (양수여야 함)
     * @return 사용자 정보를 담은 Optional
     * @throws IllegalArgumentException id가 0 이하인 경우
     */
    public Optional<User> getUser(Long id) {
        if (id <= 0) {
            throw new IllegalArgumentException("ID must be positive");
        }
        return userRepository.findById(id);
    }
}
```

### 2. 매개변수 및 반환값 문서화
```java
/**
 * 사용자 목록을 필터링하고 페이징하여 반환합니다.
 *
 * @param filter 검색 조건 (null 허용)
 * @param page 페이지 번호 (0부터 시작)
 * @param size 페이지당 항목 수 (1-100)
 * @return 필터링 및 페이징된 사용자 목록
 * @throws IllegalArgumentException page가 음수이거나 size가 범위를 벗어난 경우
 */
public Page<User> getUsers(UserFilter filter, int page, int size) {
    // Implementation
}
```

### 3. 예제 코드 포함
```java
/**
 * 비밀번호를 안전하게 해시합니다.
 * <p>
 * BCrypt 알고리즘을 사용하여 비밀번호를 해시합니다.
 * Salt는 자동으로 생성되며 결과에 포함됩니다.
 * </p>
 *
 * <pre>{@code
 * UserService service = new UserService();
 * String hashed = service.hashPassword("myPassword123");
 * boolean valid = service.verifyPassword("myPassword123", hashed);
 * }</pre>
 *
 * @param password 해시할 비밀번호
 * @return 해시된 비밀번호 문자열
 * @see #verifyPassword(String, String)
 */
public String hashPassword(String password) {
    return encoder.encode(password);
}
```

### 4. 제네릭 문서화
```java
/**
 * 제네릭 리포지토리 인터페이스입니다.
 *
 * @param <T> 엔티티 타입
 * @param <ID> 엔티티 ID 타입
 */
public interface Repository<T, ID> {
    /**
     * ID로 엔티티를 조회합니다.
     *
     * @param id 엔티티 ID
     * @return 엔티티가 존재하면 해당 엔티티, 없으면 빈 Optional
     */
    Optional<T> findById(ID id);
}
```

### 5. Deprecated 마킹
```java
/**
 * 사용자 이름으로 조회합니다.
 *
 * @deprecated 대신 {@link #findByEmail(String)}을 사용하세요.
 *             이 메서드는 버전 2.0에서 제거됩니다.
 * @param name 사용자 이름
 * @return 사용자 정보
 */
@Deprecated(since = "1.5", forRemoval = true)
public User findByName(String name) {
    // Legacy implementation
}
```

## References

- [How to Write Doc Comments](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html)
- [JavaDoc Tags](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/javadoc.html)
