# 리소스 관리 - Java

## What to Check

- **AutoCloseable 미사용**
  - try-with-resources 미사용
  - finally 블록에서 수동 close()
  - 리소스 누수 가능성

- **Connection Pool 미사용**
  - 매번 새 연결 생성
  - 연결 재사용 안 함

## Best Practices

### 1. try-with-resources
```java
// Bad
Connection conn = null;
PreparedStatement stmt = null;
try {
    conn = dataSource.getConnection();
    stmt = conn.prepareStatement(sql);
    stmt.executeQuery();
} finally {
    if (stmt != null) stmt.close();
    if (conn != null) conn.close();
}

// Good
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {
    stmt.executeQuery();
}  // 자동 close
```

### 2. AutoCloseable 구현
```java
public class DatabaseConnection implements AutoCloseable {
    private final Connection connection;

    public DatabaseConnection(String url) throws SQLException {
        this.connection = DriverManager.getConnection(url);
    }

    @Override
    public void close() throws SQLException {
        if (connection != null && !connection.isClosed()) {
            connection.close();
        }
    }
}

// 사용
try (DatabaseConnection db = new DatabaseConnection(url)) {
    // use connection
}
```

### 3. Connection Pool 사용
```java
// application.properties
spring.datasource.hikari.maximum-pool-size=10
spring.datasource.hikari.minimum-idle=5

// 사용
@Autowired
private DataSource dataSource;  // HikariCP

public void query() {
    try (Connection conn = dataSource.getConnection()) {
        // 풀에서 연결 가져옴, 사용 후 반환
    }
}
```

## References

- [try-with-resources](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)
- [AutoCloseable Interface](https://docs.oracle.com/javase/8/docs/api/java/lang/AutoCloseable.html)
