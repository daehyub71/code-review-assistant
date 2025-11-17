# 설정 관리 - Java

## What to Check

- **하드코딩된 값**
  - 소스 코드에 연결 문자열
  - 하드코딩된 API 키
  - 환경별 값이 코드에 포함

- **Magic Number/String**
  - 의미 불명확한 숫자
  - 반복되는 문자열 리터럴

## Best Practices

### 1. application.properties / application.yml 사용
```java
// Bad - 하드코딩
public class EmailService {
    private String smtpServer = "smtp.gmail.com";
    private int smtpPort = 587;
    private String apiKey = "secret-key-123";  // ❌
}

// Good - application.yml
// application.yml:
email:
  smtp:
    server: smtp.gmail.com
    port: 587
  from: noreply@company.com

// Java:
@ConfigurationProperties(prefix = "email")
@Data
public class EmailProperties {
    private Smtp smtp;
    private String from;

    @Data
    public static class Smtp {
        private String server;
        private int port;
    }
}

@Service
public class EmailService {
    private final EmailProperties properties;

    public EmailService(EmailProperties properties) {
        this.properties = properties;
    }
}
```

### 2. @Value 애노테이션
```java
@Service
public class ApiClient {
    @Value("${api.base-url}")
    private String baseUrl;

    @Value("${api.timeout:30}")  // 기본값 30
    private int timeout;

    @Value("${api.retry-count:3}")
    private int retryCount;
}
```

### 3. 환경별 설정 분리
```yaml
# application.yml (공통)
server:
  port: 8080

# application-dev.yml (개발)
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb_dev

# application-prod.yml (운영)
spring:
  datasource:
    url: jdbc:mysql://prod-server:3306/mydb
```

### 4. 환경 변수 사용
```yaml
# application.yml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
```

```bash
# Docker
docker run -e DB_URL=jdbc:mysql://db:3306/mydb \
           -e DB_USERNAME=user \
           -e DB_PASSWORD=pass \
           myapp
```

### 5. 상수 정의
```java
// Bad - Magic Number
public class OrderService {
    public BigDecimal calculateDiscount(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.valueOf(100)) > 0) {
            return amount.multiply(BigDecimal.valueOf(0.1));
        }
        return BigDecimal.ZERO;
    }
}

// Good - 상수 정의
public class OrderService {
    private static final BigDecimal PREMIUM_THRESHOLD = BigDecimal.valueOf(100);
    private static final BigDecimal PREMIUM_DISCOUNT_RATE = BigDecimal.valueOf(0.1);

    public BigDecimal calculateDiscount(BigDecimal amount) {
        if (amount.compareTo(PREMIUM_THRESHOLD) > 0) {
            return amount.multiply(PREMIUM_DISCOUNT_RATE);
        }
        return BigDecimal.ZERO;
    }
}
```

### 6. @ConfigurationProperties 활용
```java
@ConfigurationProperties(prefix = "app.cache")
@Data
@Component
public class CacheProperties {
    private int ttl = 3600;  // 기본값
    private int maxSize = 1000;
    private boolean enabled = true;
}

@Service
public class CacheService {
    private final CacheProperties properties;

    public CacheService(CacheProperties properties) {
        this.properties = properties;
    }

    public void cache() {
        int ttl = properties.getTtl();
        // ...
    }
}
```

## Example

**Before**:
```java
public class UserService {
    private String dbUrl = "jdbc:mysql://localhost:3306/mydb";
    private String dbUser = "root";
    private String dbPassword = "password123";  // ❌

    public void sendEmail(String to) {
        String smtpServer = "smtp.gmail.com";
        int smtpPort = 587;
        String apiKey = "sk-1234567890";  // ❌
    }

    public BigDecimal calculateFee(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.valueOf(1000)) > 0) {
            return amount.multiply(BigDecimal.valueOf(0.02));
        }
        return BigDecimal.ZERO;
    }
}
```

**After**:
```yaml
# application.yml
spring:
  datasource:
    url: ${DB_URL:jdbc:mysql://localhost:3306/mydb}
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD}

email:
  smtp:
    server: smtp.gmail.com
    port: 587
  api-key: ${EMAIL_API_KEY}

fee:
  premium-threshold: 1000
  premium-rate: 0.02
```

```java
@ConfigurationProperties(prefix = "email")
@Data
@Component
public class EmailProperties {
    private Smtp smtp;
    private String apiKey;

    @Data
    public static class Smtp {
        private String server;
        private int port;
    }
}

@ConfigurationProperties(prefix = "fee")
@Data
@Component
public class FeeProperties {
    private BigDecimal premiumThreshold;
    private BigDecimal premiumRate;
}

@Service
public class UserService {
    private final DataSource dataSource;
    private final EmailProperties emailProperties;
    private final FeeProperties feeProperties;

    public UserService(
        DataSource dataSource,
        EmailProperties emailProperties,
        FeeProperties feeProperties
    ) {
        this.dataSource = dataSource;
        this.emailProperties = emailProperties;
        this.feeProperties = feeProperties;
    }

    public void sendEmail(String to) {
        String server = emailProperties.getSmtp().getServer();
        int port = emailProperties.getSmtp().getPort();
        String apiKey = emailProperties.getApiKey();
        // ...
    }

    public BigDecimal calculateFee(BigDecimal amount) {
        if (amount.compareTo(feeProperties.getPremiumThreshold()) > 0) {
            return amount.multiply(feeProperties.getPremiumRate());
        }
        return BigDecimal.ZERO;
    }
}
```

## References

- [Externalized Configuration](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)
- [@ConfigurationProperties](https://docs.spring.io/spring-boot/docs/current/reference/html/configuration-metadata.html)
- [Environment Variables](https://www.baeldung.com/spring-boot-properties-env-variables)
