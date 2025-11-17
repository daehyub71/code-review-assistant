# 예외/에러 처리 - Java

## What to Check

- **일반적인 Exception 캐치**
  - catch (Exception e) 과도한 사용
  - 예외 삼키기 (빈 catch 블록)
  - 예외 정보 손실

- **Checked vs Unchecked Exception**
  - 부적절한 예외 타입 선택
  - 비즈니스 로직 예외를 checked로 처리
  - RuntimeException 남용

## Best Practices

### 1. 구체적인 예외 타입 캐치
```java
// Bad
try {
    String content = Files.readString(Path.of(filePath));
} catch (Exception e) {  // 너무 광범위
    System.out.println("Error");
}

// Good
try {
    String content = Files.readString(Path.of(filePath));
} catch (NoSuchFileException e) {
    log.error("File not found: {}", filePath);
} catch (AccessDeniedException e) {
    log.error("Access denied: {}", filePath);
} catch (IOException e) {
    log.error("IO error reading file: {}", filePath, e);
}
```

### 2. try-with-resources 사용
```java
// Bad
BufferedReader reader = null;
try {
    reader = new BufferedReader(new FileReader(path));
    return reader.readLine();
} catch (IOException e) {
    throw new RuntimeException(e);
} finally {
    if (reader != null) {
        try {
            reader.close();
        } catch (IOException e) {
            // ignore
        }
    }
}

// Good
try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
    return reader.readLine();
} catch (IOException e) {
    throw new DataAccessException("Failed to read file: " + path, e);
}
```

### 3. Custom Exception 정의
```java
public class UserNotFoundException extends RuntimeException {
    private final Long userId;

    public UserNotFoundException(Long userId) {
        super("User not found: " + userId);
        this.userId = userId;
    }

    public Long getUserId() {
        return userId;
    }
}

// 사용
public User getUser(Long id) {
    return userRepository.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

### 4. 예외 체이닝
```java
// Bad
try {
    externalApi.fetchData();
} catch (ApiException e) {
    throw new ServiceException("Failed to fetch data");  // 원본 예외 손실
}

// Good
try {
    externalApi.fetchData();
} catch (ApiException e) {
    throw new ServiceException("Failed to fetch data", e);  // 원본 예외 보존
}
```

## Example

**Before**:
```java
public class DataProcessor {
    public void processFile(String path) {
        try {
            String content = Files.readString(Path.of(path));
            Data data = objectMapper.readValue(content, Data.class);
            saveToDatabase(data);
        } catch (Exception e) {  // 너무 광범위
            System.out.println(e.getMessage());
        }
    }
}
```

**After**:
```java
public class DataProcessor {
    private final ObjectMapper objectMapper;
    private final DataRepository repository;
    private final Logger log = LoggerFactory.getLogger(DataProcessor.class);

    public void processFile(String path) throws DataProcessingException {
        try {
            String content = Files.readString(Path.of(path));

            Data data = parseJson(content);
            saveToDatabase(data);

            log.info("Successfully processed file: {}", path);
        } catch (NoSuchFileException e) {
            log.error("File not found: {}", path);
            throw new DataProcessingException("File not found: " + path, e);
        } catch (JsonProcessingException e) {
            log.error("Invalid JSON in file: {}", path);
            throw new DataProcessingException("Invalid data format", e);
        } catch (IOException e) {
            log.error("IO error processing file: {}", path, e);
            throw new DataProcessingException("Failed to read file", e);
        }
    }

    private Data parseJson(String content) throws JsonProcessingException {
        Data data = objectMapper.readValue(content, Data.class);
        if (data == null) {
            throw new IllegalStateException("Parsed data is null");
        }
        return data;
    }

    private void saveToDatabase(Data data) {
        try {
            repository.save(data);
        } catch (DataAccessException e) {
            log.error("Database error saving data", e);
            throw new DataProcessingException("Failed to save data", e);
        }
    }
}

public class DataProcessingException extends RuntimeException {
    public DataProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## References

- [Exceptions (Oracle Tutorial)](https://docs.oracle.com/javase/tutorial/essential/exceptions/)
- [try-with-resources](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)
- [Effective Java - Item 69-77 (Exceptions)](https://www.oreilly.com/library/view/effective-java/9780134686097/)
