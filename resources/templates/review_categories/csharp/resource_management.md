# 리소스 관리 - C#

## What to Check

- **IDisposable 미구현/미사용**
  - 파일, 데이터베이스 연결, 네트워크 스트림 등 비관리 리소스
  - using 문 미사용으로 리소스 누수 가능성
  - Dispose() 명시적 호출 누락

- **메모리 누수 위험**
  - 이벤트 핸들러 등록 후 해제 누락
  - 정적 컬렉션에 객체 무한 추가
  - 대용량 객체의 생명주기 관리 미흡

- **비동기 리소스 처리**
  - IAsyncDisposable 미사용
  - await using 미사용
  - 비동기 스트림 정리 누락

## Best Practices

### 1. using 선언으로 자동 정리 (C# 8.0+)
```csharp
// Bad
FileStream file = new FileStream(path, FileMode.Open);
try
{
    // use file
}
finally
{
    file.Dispose();
}

// Good (C# 8.0+)
using var file = new FileStream(path, FileMode.Open);
// use file
// 스코프 종료 시 자동 Dispose
```

### 2. IDisposable 패턴 구현
```csharp
public class DatabaseConnection : IDisposable
{
    private SqlConnection _connection;
    private bool _disposed = false;

    public DatabaseConnection(string connectionString)
    {
        _connection = new SqlConnection(connectionString);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // 관리 리소스 해제
                _connection?.Dispose();
            }

            // 비관리 리소스 해제 (필요한 경우)
            _disposed = true;
        }
    }

    public void Dispose()
    {
        Dispose(disposing: true);
        GC.SuppressFinalize(this);
    }
}
```

### 3. IAsyncDisposable 구현 (비동기 정리)
```csharp
public class AsyncDatabaseConnection : IAsyncDisposable
{
    private SqlConnection _connection;

    public async ValueTask DisposeAsync()
    {
        if (_connection != null)
        {
            await _connection.CloseAsync();
            await _connection.DisposeAsync();
        }

        GC.SuppressFinalize(this);
    }
}

// 사용
await using var connection = new AsyncDatabaseConnection(connectionString);
// use connection
```

### 4. 이벤트 핸들러 정리
```csharp
public class EventSubscriber : IDisposable
{
    private readonly EventPublisher _publisher;

    public EventSubscriber(EventPublisher publisher)
    {
        _publisher = publisher;
        _publisher.DataReceived += OnDataReceived;
    }

    private void OnDataReceived(object sender, DataEventArgs e)
    {
        // Handle event
    }

    public void Dispose()
    {
        // 이벤트 핸들러 해제로 메모리 누수 방지
        _publisher.DataReceived -= OnDataReceived;
    }
}
```

### 5. 여러 리소스 관리
```csharp
// Bad
using (var conn = new SqlConnection(connectionString))
{
    using (var cmd = new SqlCommand(query, conn))
    {
        using (var reader = cmd.ExecuteReader())
        {
            // nested using
        }
    }
}

// Good (C# 8.0+)
using var conn = new SqlConnection(connectionString);
using var cmd = new SqlCommand(query, conn);
using var reader = cmd.ExecuteReader();
// 모든 리소스가 스코프 종료 시 역순으로 정리됨
```

## Example

**Before**:
```csharp
public class FileProcessor
{
    public void ProcessLargeFile(string inputPath, string outputPath)
    {
        // 리소스 정리 없음
        var reader = new StreamReader(inputPath);
        var writer = new StreamWriter(outputPath);

        string line;
        while ((line = reader.ReadLine()) != null)
        {
            writer.WriteLine(line.ToUpper());
        }

        // Dispose 호출 누락 - 리소스 누수
    }

    public void SaveToDatabase(Data data)
    {
        var connection = new SqlConnection(connectionString);
        connection.Open();

        var command = new SqlCommand(query, connection);
        command.ExecuteNonQuery();

        // 예외 발생 시 정리 안됨
        connection.Close();
    }
}

public class CacheManager
{
    private static List<byte[]> _cache = new List<byte[]>();

    public void AddToCache(byte[] data)
    {
        _cache.Add(data);  // 정적 컬렉션 - 메모리 누수 위험
    }
}
```

**After**:
```csharp
public class FileProcessor
{
    public async Task ProcessLargeFileAsync(string inputPath, string outputPath)
    {
        // using 선언으로 자동 정리
        await using var reader = new StreamReader(inputPath);
        await using var writer = new StreamWriter(outputPath);

        string? line;
        while ((line = await reader.ReadLineAsync()) != null)
        {
            await writer.WriteLineAsync(line.ToUpper());
        }
        // 스코프 종료 시 reader, writer 자동 정리
    }

    public async Task SaveToDatabaseAsync(Data data)
    {
        await using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = new SqlCommand(_query, connection);
        await command.ExecuteNonQueryAsync();

        // 예외 발생해도 자동 정리됨
    }
}

public class CacheManager : IDisposable
{
    private readonly Dictionary<string, WeakReference<byte[]>> _cache = new();
    private readonly int _maxCacheSize = 100;

    public void AddToCache(string key, byte[] data)
    {
        // 캐시 크기 제한
        if (_cache.Count >= _maxCacheSize)
        {
            CleanupOldEntries();
        }

        _cache[key] = new WeakReference<byte[]>(data);
    }

    private void CleanupOldEntries()
    {
        var keysToRemove = _cache
            .Where(kvp => !kvp.Value.TryGetTarget(out _))
            .Select(kvp => kvp.Key)
            .ToList();

        foreach (var key in keysToRemove)
        {
            _cache.Remove(key);
        }
    }

    public void Dispose()
    {
        _cache.Clear();
        GC.SuppressFinalize(this);
    }
}
```

## References

- [IDisposable Interface](https://learn.microsoft.com/en-us/dotnet/api/system.idisposable)
- [Implement a Dispose method](https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose)
- [using statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)
- [IAsyncDisposable Interface](https://learn.microsoft.com/en-us/dotnet/api/system.iasyncdisposable)
- [Memory Management in .NET](https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/)
