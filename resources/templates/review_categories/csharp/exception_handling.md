# 예외/에러 처리 - C#

## What to Check

- **일반적인 Exception 캐치**
  - `catch (Exception ex)` 과도한 사용
  - 특정 예외 타입 지정 없음
  - 예외 삼키기 (empty catch block)

- **예외 정보 손실**
  - `throw ex` 사용으로 스택 트레이스 손실
  - 예외 메시지에 컨텍스트 정보 누락
  - Inner exception 무시

- **리소스 정리 누락**
  - finally 블록 미사용
  - IDisposable 리소스의 명시적 Dispose 호출
  - using 문 미사용

## Best Practices

### 1. 구체적인 예외 타입 캐치
```csharp
// Bad
try
{
    var content = File.ReadAllText(path);
}
catch (Exception ex)
{
    // 너무 광범위한 예외 처리
    Console.WriteLine("Error occurred");
}

// Good
try
{
    var content = File.ReadAllText(path);
}
catch (FileNotFoundException ex)
{
    Console.WriteLine($"File not found: {path}");
}
catch (UnauthorizedAccessException ex)
{
    Console.WriteLine($"Access denied: {path}");
}
catch (IOException ex)
{
    Console.WriteLine($"IO error: {ex.Message}");
}
```

### 2. throw 단독 사용으로 스택 트레이스 보존
```csharp
// Bad - 스택 트레이스 손실
try
{
    ProcessData();
}
catch (Exception ex)
{
    LogError(ex);
    throw ex;  // ❌ 스택 트레이스가 여기서부터 시작
}

// Good - 원본 스택 트레이스 유지
try
{
    ProcessData();
}
catch (Exception ex)
{
    LogError(ex);
    throw;  // ✅ 원본 스택 트레이스 보존
}
```

### 3. 예외 래핑 시 Inner Exception 보존
```csharp
// Bad
try
{
    var data = await externalApi.GetDataAsync();
}
catch (HttpRequestException ex)
{
    throw new ApplicationException("Failed to fetch data");
}

// Good
try
{
    var data = await externalApi.GetDataAsync();
}
catch (HttpRequestException ex)
{
    throw new ApplicationException(
        "Failed to fetch data from external API",
        ex  // Inner exception 보존
    );
}
```

### 4. using 문으로 리소스 자동 정리
```csharp
// Bad
FileStream file = null;
try
{
    file = new FileStream(path, FileMode.Open);
    // process file
}
catch (IOException ex)
{
    Console.WriteLine(ex.Message);
}
finally
{
    if (file != null)
        file.Dispose();
}

// Good
try
{
    using var file = new FileStream(path, FileMode.Open);
    // process file
} // 자동으로 Dispose 호출
catch (IOException ex)
{
    Console.WriteLine(ex.Message);
}
```

### 5. Custom Exception 정의
```csharp
public class DataValidationException : Exception
{
    public string PropertyName { get; }

    public DataValidationException(string propertyName, string message)
        : base(message)
    {
        PropertyName = propertyName;
    }

    public DataValidationException(string propertyName, string message, Exception innerException)
        : base(message, innerException)
    {
        PropertyName = propertyName;
    }
}

// 사용
if (string.IsNullOrEmpty(user.Email))
{
    throw new DataValidationException(
        nameof(user.Email),
        "Email is required"
    );
}
```

## Example

**Before**:
```csharp
public class DataProcessor
{
    public void ProcessFile(string filePath)
    {
        try
        {
            var content = File.ReadAllText(filePath);
            var data = JsonSerializer.Deserialize<Data>(content);
            SaveToDatabase(data);
        }
        catch (Exception ex)  // 너무 광범위
        {
            Console.WriteLine("Error: " + ex.Message);
            throw ex;  // 스택 트레이스 손실
        }
    }

    public void SaveToDatabase(Data data)
    {
        SqlConnection conn = new SqlConnection(connectionString);
        conn.Open();
        // ... DB 작업
        conn.Close();  // 예외 발생 시 정리 안됨
    }
}
```

**After**:
```csharp
public class DataProcessor
{
    public async Task ProcessFileAsync(string filePath)
    {
        try
        {
            var content = await File.ReadAllTextAsync(filePath);
            var data = JsonSerializer.Deserialize<Data>(content)
                ?? throw new InvalidDataException("Deserialization returned null");

            await SaveToDatabaseAsync(data);
        }
        catch (FileNotFoundException ex)
        {
            _logger.LogError(ex, "File not found: {FilePath}", filePath);
            throw new DataProcessingException(
                $"Input file not found: {filePath}",
                ex
            );
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "Invalid JSON format in {FilePath}", filePath);
            throw new DataProcessingException(
                "Invalid data format",
                ex
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error processing {FilePath}", filePath);
            throw;  // 스택 트레이스 보존
        }
    }

    public async Task SaveToDatabaseAsync(Data data)
    {
        await using var conn = new SqlConnection(_connectionString);
        await conn.OpenAsync();

        try
        {
            await using var transaction = await conn.BeginTransactionAsync();
            // ... DB 작업
            await transaction.CommitAsync();
        }
        catch (SqlException ex)
        {
            _logger.LogError(ex, "Database error while saving data");
            throw new DatabaseException("Failed to save data", ex);
        }
        // conn은 자동으로 Dispose됨
    }
}

public class DataProcessingException : Exception
{
    public DataProcessingException(string message, Exception innerException)
        : base(message, innerException) { }
}
```

## References

- [Exception Handling (Microsoft Docs)](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/exceptions/)
- [Best practices for exceptions](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)
- [using statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)
- [Creating and Throwing Exceptions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/exceptions/creating-and-throwing-exceptions)
