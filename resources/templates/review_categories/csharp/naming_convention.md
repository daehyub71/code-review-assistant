# 네이밍 규칙 - C#

## What to Check

- **일관되지 않은 케이스**
  - PascalCase, camelCase 혼용
  - 약어 대소문자 불일치 (ID vs Id)
  - 상수/필드 명명 규칙 미준수

- **의미 없는 이름**
  - 단일 문자 변수 (i, j, k 제외 루프 변수)
  - 축약어 과다 사용 (mgr, svc, rpo)
  - 불명확한 이름 (data, info, temp)

- **Hungarian Notation 사용**
  - strName, intAge 등 타입 접두사
  - 현대 C#에서 불필요 (타입 추론)

## Best Practices

### 1. 클래스 및 메서드: PascalCase
```csharp
// Bad
public class userService { }
public class User_Repository { }

// Good
public class UserService { }
public class UserRepository { }
```

### 2. 변수 및 매개변수: camelCase
```csharp
// Bad
public void ProcessUser(string UserName, int UserAge)
{
    string FirstName = GetFirstName(UserName);
}

// Good
public void ProcessUser(string userName, int userAge)
{
    string firstName = GetFirstName(userName);
}
```

### 3. Private 필드: _camelCase (언더스코어 접두사)
```csharp
// Bad
public class UserService
{
    private string connectionString;
    private ILogger logger;
}

// Good
public class UserService
{
    private readonly string _connectionString;
    private readonly ILogger _logger;
}
```

### 4. 인터페이스: I + PascalCase
```csharp
// Bad
public interface UserRepository { }
public interface IuserService { }

// Good
public interface IUserRepository { }
public interface IUserService { }
```

### 5. 상수: PascalCase (ALL_CAPS 사용 안 함)
```csharp
// Bad (C++ 스타일)
public const int MAX_RETRY_COUNT = 3;
public const string DEFAULT_CONNECTION_STRING = "...";

// Good (C# 스타일)
public const int MaxRetryCount = 3;
public const string DefaultConnectionString = "...";
```

### 6. Boolean: Is/Has/Can 접두사
```csharp
// Bad
public bool Active { get; set; }
public bool Authenticated { get; set; }
public bool Delete() { }

// Good
public bool IsActive { get; set; }
public bool IsAuthenticated { get; set; }
public bool CanDelete() { }
```

### 7. 약어 규칙
```csharp
// Bad - 일관되지 않음
public class HTMLUI { }
public string UserID { get; set; }
public int XMLParser { get; set; }

// Good - 2글자 약어는 대문자, 3글자 이상은 PascalCase
public class HtmlUI { }
public string UserId { get; set; }  // 2글자: Id
public class XmlParser { }          // 3글자 이상: Xml
public class IOStream { }           // 2글자: IO
```

### 8. 의미 있는 이름 사용
```csharp
// Bad
public void Process(int x, string s)
{
    var temp = x * 2;
    var data = Get(s);
}

// Good
public void ProcessUserOrder(int orderId, string userName)
{
    var doubledQuantity = orderId * 2;
    var userData = GetUserData(userName);
}
```

### 9. Async 메서드: Async 접미사
```csharp
// Bad
public async Task<User> GetUser(int id) { }
public async Task SaveChanges() { }

// Good
public async Task<User> GetUserAsync(int id) { }
public async Task SaveChangesAsync() { }
```

### 10. 네임스페이스: 회사명.제품명.기능
```csharp
// Bad
namespace Utils { }
namespace Helpers { }

// Good
namespace CompanyName.ProductName.Core { }
namespace CompanyName.ProductName.Services { }
namespace CompanyName.ProductName.Data.Repositories { }
```

## Example

**Before**:
```csharp
namespace myapp
{
    public class user_service
    {
        // Hungarian Notation
        private string strConnectionString;
        private int nRetryCount;

        // 일관되지 않은 케이스
        public string UserID { get; set; }
        public bool active { get; set; }

        // 의미 없는 이름
        public void Process(string s, int x)
        {
            var temp = s.Split(',');
            var data = x * 2;

            for (int i = 0; i < temp.Length; i++)
            {
                var item = temp[i];
                // process
            }
        }

        // Async 접미사 누락
        public async Task<user> GetUser(int id)
        {
            return await _repository.Find(id);
        }
    }

    // 인터페이스 I 접두사 누락
    public interface UserRepository { }
}
```

**After**:
```csharp
namespace CompanyName.UserManagement.Services
{
    public class UserService
    {
        // Private 필드: _camelCase
        private readonly string _connectionString;
        private readonly int _retryCount;
        private readonly IUserRepository _repository;
        private readonly ILogger<UserService> _logger;

        // 프로퍼티: PascalCase
        public string UserId { get; set; }
        public bool IsActive { get; set; }

        public UserService(
            string connectionString,
            IUserRepository repository,
            ILogger<UserService> logger)
        {
            _connectionString = connectionString;
            _repository = repository;
            _logger = logger;
            _retryCount = MaxRetryCount;
        }

        // 상수: PascalCase
        private const int MaxRetryCount = 3;
        private const string DefaultUserRole = "Guest";

        // 의미 있는 이름 사용
        public void ProcessUserData(string csvData, int multiplier)
        {
            var userRecords = csvData.Split(',');
            var calculatedValue = multiplier * 2;

            foreach (var record in userRecords)
            {
                var trimmedRecord = record.Trim();
                ProcessRecord(trimmedRecord);
            }
        }

        // Async 메서드: Async 접미사
        public async Task<User> GetUserAsync(int userId)
        {
            ArgumentNullException.ThrowIfNull(userId);

            _logger.LogInformation(
                "Fetching user with ID: {UserId}",
                userId
            );

            return await _repository.FindByIdAsync(userId);
        }

        // Boolean 메서드: Can 접두사
        public bool CanDeleteUser(User user)
        {
            return user.IsActive && !user.HasPendingOrders;
        }
    }

    // 인터페이스: I 접두사
    public interface IUserRepository
    {
        Task<User> FindByIdAsync(int userId);
        Task<bool> ExistsAsync(int userId);
    }

    // DTO: 명확한 이름
    public class UserRegistrationRequest
    {
        public string Email { get; set; }
        public string Password { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
    }
}
```

## C# 네이밍 규칙 요약표

| 타입 | 규칙 | 예시 |
|------|------|------|
| 클래스 | PascalCase | `UserService`, `OrderManager` |
| 인터페이스 | I + PascalCase | `IUserRepository`, `ILogger` |
| 메서드 | PascalCase | `GetUser()`, `ProcessData()` |
| Async 메서드 | PascalCase + Async | `GetUserAsync()`, `SaveAsync()` |
| 프로퍼티 | PascalCase | `UserId`, `IsActive` |
| Public 필드 | PascalCase | `MaxValue` (드물게 사용) |
| Private 필드 | _camelCase | `_connectionString`, `_logger` |
| 로컬 변수 | camelCase | `userName`, `totalCount` |
| 매개변수 | camelCase | `userId`, `orderDate` |
| 상수 | PascalCase | `MaxRetryCount`, `DefaultTimeout` |
| 네임스페이스 | PascalCase | `CompanyName.ProductName.Feature` |

## References

- [C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [.NET Naming Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/naming-guidelines)
- [Framework Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/)
- [C# Identifier Naming Rules](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names)
