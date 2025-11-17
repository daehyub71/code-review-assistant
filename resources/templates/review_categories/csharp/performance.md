# 성능 최적화 - C#

## What to Check

- **비효율적인 컬렉션 사용**
  - List에서 반복적인 Contains() 호출
  - HashSet/Dictionary 미사용
  - LINQ 체이닝 과다로 인한 다중 순회

- **불필요한 객체 생성**
  - string concatenation에서 + 연산자 반복 사용
  - StringBuilder 미사용
  - 루프 내 불필요한 객체 할당

- **동기 I/O 사용**
  - File.ReadAllText() 등 동기 메서드
  - async/await 미적용
  - Task.Result, Task.Wait() 사용으로 데드락 위험

## Best Practices

### 1. 적절한 컬렉션 선택
```csharp
// Bad - O(n) 탐색
var userIds = new List<int> { 1, 2, 3, ... };
if (userIds.Contains(targetId))  // 매번 전체 순회
{
    // ...
}

// Good - O(1) 탐색
var userIds = new HashSet<int> { 1, 2, 3, ... };
if (userIds.Contains(targetId))  // 즉시 찾기
{
    // ...
}
```

### 2. StringBuilder 사용
```csharp
// Bad - 매번 새 string 객체 생성
string result = "";
for (int i = 0; i < 1000; i++)
{
    result += i.ToString() + ",";  // 1000개 객체 생성
}

// Good - 단일 버퍼 사용
var sb = new StringBuilder();
for (int i = 0; i < 1000; i++)
{
    sb.Append(i).Append(',');
}
string result = sb.ToString();
```

### 3. LINQ 최적화
```csharp
// Bad - 여러 번 순회
var users = GetUsers()
    .Where(u => u.IsActive)
    .ToList()  // 첫 번째 순회
    .Where(u => u.Age > 18)
    .ToList();  // 두 번째 순회

// Good - 단일 순회
var users = GetUsers()
    .Where(u => u.IsActive && u.Age > 18)
    .ToList();  // 한 번만 순회

// 또는 지연 평가 활용
var query = GetUsers()
    .Where(u => u.IsActive && u.Age > 18);
// 실제 사용 시점에만 실행됨
```

### 4. 비동기 I/O 사용
```csharp
// Bad - UI 스레드 블로킹
public void LoadData()
{
    var data = File.ReadAllText(path);  // 동기 I/O
    ProcessData(data);
}

// Good - 비동기 I/O
public async Task LoadDataAsync()
{
    var data = await File.ReadAllTextAsync(path);
    await ProcessDataAsync(data);
}
```

### 5. Span<T> / Memory<T> 활용
```csharp
// Bad - 부분 문자열마다 새 string 생성
string input = "user:john,age:30,city:NYC";
string[] parts = input.Split(',');
foreach (var part in parts)
{
    var keyValue = part.Split(':');  // 추가 할당
}

// Good - Span으로 할당 없이 처리
ReadOnlySpan<char> input = "user:john,age:30,city:NYC";
while (true)
{
    int commaIndex = input.IndexOf(',');
    var segment = commaIndex >= 0
        ? input.Slice(0, commaIndex)
        : input;

    int colonIndex = segment.IndexOf(':');
    var key = segment.Slice(0, colonIndex);
    var value = segment.Slice(colonIndex + 1);

    // key, value 사용 (할당 없음)

    if (commaIndex < 0) break;
    input = input.Slice(commaIndex + 1);
}
```

### 6. ValueTask 사용 (자주 동기 완료되는 경우)
```csharp
// Bad - 캐시 히트 시에도 Task 할당
public async Task<User> GetUserAsync(int id)
{
    if (_cache.TryGetValue(id, out var user))
        return user;  // Task 할당

    return await _repository.GetUserAsync(id);
}

// Good - 캐시 히트 시 할당 없음
public ValueTask<User> GetUserAsync(int id)
{
    if (_cache.TryGetValue(id, out var user))
        return new ValueTask<User>(user);  // 할당 없음

    return new ValueTask<User>(_repository.GetUserAsync(id));
}
```

## Example

**Before**:
```csharp
public class DataProcessor
{
    public List<string> ProcessUsers(List<User> users)
    {
        var result = new List<string>();

        // 비효율적인 필터링
        var activeUsers = users.Where(u => u.IsActive).ToList();
        var adultUsers = activeUsers.Where(u => u.Age >= 18).ToList();

        foreach (var user in adultUsers)
        {
            // string concatenation
            string info = "";
            info += "Name: " + user.Name;
            info += ", Age: " + user.Age;
            info += ", Email: " + user.Email;
            result.Add(info);
        }

        return result;
    }

    public string GenerateReport(int[] data)
    {
        string report = "";  // 비효율적
        for (int i = 0; i < data.Length; i++)
        {
            report += $"Item {i}: {data[i]}\n";
        }
        return report;
    }

    public void SaveData(string path, string content)
    {
        File.WriteAllText(path, content);  // 동기 I/O
    }
}
```

**After**:
```csharp
public class DataProcessor
{
    public List<string> ProcessUsers(List<User> users)
    {
        // 단일 LINQ 쿼리로 최적화
        return users
            .Where(u => u.IsActive && u.Age >= 18)
            .Select(u => $"Name: {u.Name}, Age: {u.Age}, Email: {u.Email}")
            .ToList();
    }

    public string GenerateReport(int[] data)
    {
        // StringBuilder 사용
        var sb = new StringBuilder(capacity: data.Length * 20);

        for (int i = 0; i < data.Length; i++)
        {
            sb.Append("Item ")
              .Append(i)
              .Append(": ")
              .Append(data[i])
              .AppendLine();
        }

        return sb.ToString();
    }

    // 비동기 I/O 사용
    public async Task SaveDataAsync(string path, string content)
    {
        await File.WriteAllTextAsync(path, content);
    }

    // Span 활용 예제
    public int CountWords(ReadOnlySpan<char> text)
    {
        int count = 0;
        int pos = 0;

        while (pos < text.Length)
        {
            // 공백 건너뛰기
            while (pos < text.Length && char.IsWhiteSpace(text[pos]))
                pos++;

            if (pos < text.Length)
            {
                count++;

                // 단어 건너뛰기
                while (pos < text.Length && !char.IsWhiteSpace(text[pos]))
                    pos++;
            }
        }

        return count;  // 할당 없이 처리 완료
    }
}
```

## References

- [Performance Tips](https://learn.microsoft.com/en-us/dotnet/framework/performance/performance-tips)
- [String vs StringBuilder](https://learn.microsoft.com/en-us/dotnet/api/system.text.stringbuilder)
- [LINQ Performance](https://learn.microsoft.com/en-us/dotnet/standard/linq/performance)
- [Span<T> and Memory<T>](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/)
- [ValueTask<T>](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1)
