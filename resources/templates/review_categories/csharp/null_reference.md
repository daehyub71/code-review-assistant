# Null/Undefined 안전성 - C#

## What to Check

- **Null Reference Exception 발생 가능성**
  - 메서드 매개변수에 null 검사 누락
  - 프로퍼티 접근 시 null 체크 없음
  - 컬렉션/배열 요소 접근 전 null 확인 누락

- **Nullable Reference Types 미사용**
  - C# 8.0+ nullable reference types 활성화 여부
  - `string?` vs `string` 구분 없음
  - `#nullable enable` 지시문 누락

- **안전하지 않은 패턴**
  - `!` null-forgiving 연산자 과도한 사용
  - null 반환 메서드의 반환값 미체크
  - LINQ 쿼리 결과의 null 가능성 무시

## Best Practices

### 1. Null-Conditional Operator (?.) 사용
```csharp
// Bad
if (user != null && user.Profile != null)
{
    Console.WriteLine(user.Profile.Name);
}

// Good
Console.WriteLine(user?.Profile?.Name ?? "Unknown");
```

### 2. Nullable Reference Types 활성화
```csharp
// .csproj에 추가
<Nullable>enable</Nullable>

// 코드에서 명시적 선언
#nullable enable

string name;        // Non-nullable
string? nickname;   // Nullable
```

### 3. Null Coalescing Operator (??) 활용
```csharp
// Bad
string displayName;
if (user.Name != null)
    displayName = user.Name;
else
    displayName = "Guest";

// Good
string displayName = user.Name ?? "Guest";
```

### 4. Required 키워드 사용 (C# 11+)
```csharp
public class User
{
    public required string Name { get; init; }
    public required string Email { get; init; }
}

// 컴파일 타임 보장
var user = new User
{
    Name = "John",
    Email = "john@example.com"
};
```

### 5. ArgumentNullException.ThrowIfNull 사용 (C# 11+)
```csharp
// Bad
public void ProcessUser(User user)
{
    if (user == null)
        throw new ArgumentNullException(nameof(user));
    // ...
}

// Good
public void ProcessUser(User user)
{
    ArgumentNullException.ThrowIfNull(user);
    // ...
}
```

## Example

**Before**:
```csharp
public class UserService
{
    public string GetUserDisplayName(User user)
    {
        // Null check 없음 - NullReferenceException 위험
        return user.Profile.Name;
    }

    public List<string> GetUserEmails(List<User> users)
    {
        // users가 null이거나 요소가 null일 수 있음
        return users.Select(u => u.Email).ToList();
    }
}
```

**After**:
```csharp
#nullable enable

public class UserService
{
    // Nullable reference types 명시
    public string GetUserDisplayName(User? user)
    {
        // Null-conditional + Null-coalescing 사용
        return user?.Profile?.Name ?? "Unknown User";
    }

    public List<string> GetUserEmails(List<User>? users)
    {
        // 입력 검증
        ArgumentNullException.ThrowIfNull(users);

        // Null 필터링 + 안전한 접근
        return users
            .Where(u => u?.Email != null)
            .Select(u => u.Email!)  // 이미 필터링했으므로 안전
            .ToList();
    }
}
```

## References

- [Nullable Reference Types (Microsoft Docs)](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)
- [Null-conditional operators ?. and ?[]](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/member-access-operators#null-conditional-operators--and-)
- [?? and ??= operators](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/null-coalescing-operator)
- [C# Coding Conventions - Null Checks](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
