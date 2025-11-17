# 코드 문서화 - C#

## What to Check

- **XML 문서 주석 누락**
  - Public API에 /// 주석 없음
  - 메서드 매개변수/반환값 설명 누락
  - 예외 발생 조건 미문서화

- **불명확한 주석**
  - What만 설명하고 Why/How 누락
  - 오래된 주석 (코드와 불일치)
  - 불필요한 주석 (자명한 코드)

- **문서화 부족**
  - 복잡한 알고리즘 설명 없음
  - 비즈니스 로직 문서화 누락
  - API 사용 예제 없음

## Best Practices

### 1. XML 문서 주석 사용
```csharp
// Bad - 주석 없음
public class UserService
{
    public User GetUser(int id)
    {
        return _repository.FindById(id);
    }
}

// Good - XML 문서 주석
/// <summary>
/// 사용자 관리 서비스를 제공합니다.
/// </summary>
public class UserService
{
    /// <summary>
    /// 지정된 ID의 사용자를 조회합니다.
    /// </summary>
    /// <param name="id">조회할 사용자 ID</param>
    /// <returns>사용자 정보 또는 null (존재하지 않는 경우)</returns>
    /// <exception cref="ArgumentException">
    /// id가 0 이하인 경우 발생합니다.
    /// </exception>
    public User GetUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("ID must be positive", nameof(id));

        return _repository.FindById(id);
    }
}
```

### 2. 매개변수 및 반환값 문서화
```csharp
/// <summary>
/// 사용자 목록을 필터링하고 페이징하여 반환합니다.
/// </summary>
/// <param name="filter">검색 조건 (null 허용)</param>
/// <param name="pageNumber">페이지 번호 (1부터 시작)</param>
/// <param name="pageSize">페이지당 항목 수 (1-100)</param>
/// <returns>
/// 필터링 및 페이징된 사용자 목록.
/// 빈 목록은 반환하지만 null은 반환하지 않습니다.
/// </returns>
/// <exception cref="ArgumentOutOfRangeException">
/// pageNumber가 1 미만이거나 pageSize가 1-100 범위를 벗어난 경우
/// </exception>
public List<User> GetUsers(
    UserFilter? filter,
    int pageNumber,
    int pageSize)
{
    // Implementation
}
```

### 3. 예제 코드 포함
```csharp
/// <summary>
/// 비밀번호를 안전하게 해시합니다.
/// </summary>
/// <remarks>
/// PBKDF2 알고리즘과 HMACSHA256을 사용하여 비밀번호를 해시합니다.
/// Salt는 자동으로 생성되며 결과 문자열에 포함됩니다.
/// </remarks>
/// <example>
/// <code>
/// var hasher = new PasswordHasher();
/// string hashedPassword = hasher.HashPassword("MyPassword123");
/// bool isValid = hasher.VerifyPassword("MyPassword123", hashedPassword);
/// </code>
/// </example>
/// <param name="password">해시할 비밀번호</param>
/// <returns>Salt와 해시를 포함한 Base64 문자열</returns>
public string HashPassword(string password)
{
    // Implementation
}
```

### 4. 복잡한 로직 설명
```csharp
/// <summary>
/// Luhn 알고리즘을 사용하여 신용카드 번호의 유효성을 검증합니다.
/// </summary>
/// <remarks>
/// 알고리즘 단계:
/// 1. 오른쪽에서 왼쪽으로, 두 번째 자리마다 2를 곱합니다
/// 2. 곱한 결과가 10 이상이면 각 자릿수를 더합니다 (18 -> 1+8=9)
/// 3. 모든 숫자의 합이 10으로 나누어떨어지면 유효합니다
/// </remarks>
public bool ValidateCreditCard(string cardNumber)
{
    // 공백 및 하이픈 제거
    cardNumber = Regex.Replace(cardNumber, @"[\s-]", "");

    // 숫자만 포함되어 있는지 확인
    if (!Regex.IsMatch(cardNumber, @"^\d+$"))
        return false;

    int sum = 0;
    bool alternate = false;

    // 오른쪽부터 순회
    for (int i = cardNumber.Length - 1; i >= 0; i--)
    {
        int digit = cardNumber[i] - '0';

        if (alternate)
        {
            digit *= 2;
            if (digit > 9)
                digit -= 9;  // 또는 digit = digit / 10 + digit % 10
        }

        sum += digit;
        alternate = !alternate;
    }

    return sum % 10 == 0;
}
```

### 5. Nullable 및 제네릭 문서화
```csharp
/// <summary>
/// 제네릭 리포지토리 인터페이스입니다.
/// </summary>
/// <typeparam name="T">
/// 엔티티 타입. IEntity 인터페이스를 구현해야 합니다.
/// </typeparam>
public interface IRepository<T> where T : IEntity
{
    /// <summary>
    /// ID로 엔티티를 조회합니다.
    /// </summary>
    /// <param name="id">조회할 엔티티 ID</param>
    /// <returns>
    /// 엔티티가 존재하면 해당 엔티티, 없으면 null
    /// </returns>
    Task<T?> FindByIdAsync(int id);

    /// <summary>
    /// 모든 엔티티를 조회합니다.
    /// </summary>
    /// <returns>
    /// 엔티티 목록. 빈 목록일 수 있지만 null은 아닙니다.
    /// </returns>
    Task<List<T>> GetAllAsync();
}
```

### 6. TODO/FIXME 주석
```csharp
public class OrderService
{
    // TODO: 성능 개선 필요 - N+1 쿼리 문제 (2024-01-15, 김개발)
    public List<Order> GetOrdersWithItems()
    {
        // Current implementation
    }

    // FIXME: 동시성 문제 - 여러 스레드에서 접근 시 데이터 손실 가능
    // Issue #1234 참조
    private static int _orderCount = 0;

    // HACK: 임시 해결책 - API 버전 2.0에서 제거 예정
    private void LegacyDataConversion(Order order)
    {
        // Workaround
    }
}
```

## Example

**Before**:
```csharp
public class UserService
{
    // Get user
    public User Get(int id)
    {
        return _repo.Find(id);
    }

    // Process user data
    public void Process(User u)
    {
        // Validate
        if (u.Age < 18)
            throw new Exception("Too young");

        // Calculate discount
        var discount = u.Age > 65 ? 0.2 : 0.1;
        u.Discount = discount;

        // Save
        _repo.Save(u);
    }

    // Complex calculation
    public double Calc(double x, double y, int type)
    {
        if (type == 1)
            return x * y * 1.1;
        else if (type == 2)
            return (x + y) * 0.9;
        else
            return x - y;
    }
}
```

**After**:
```csharp
/// <summary>
/// 사용자 관리 비즈니스 로직을 제공합니다.
/// </summary>
/// <remarks>
/// 이 서비스는 사용자 조회, 수정, 할인율 계산 등의
/// 비즈니스 규칙을 캡슐화합니다.
/// </remarks>
public class UserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    /// <summary>
    /// UserService의 새 인스턴스를 생성합니다.
    /// </summary>
    /// <param name="repository">사용자 데이터 저장소</param>
    /// <param name="logger">로깅 인스턴스</param>
    public UserService(
        IUserRepository repository,
        ILogger<UserService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    /// <summary>
    /// 지정된 ID의 사용자를 조회합니다.
    /// </summary>
    /// <param name="id">조회할 사용자 ID</param>
    /// <returns>사용자 정보 또는 null</returns>
    /// <exception cref="ArgumentException">
    /// id가 0 이하인 경우
    /// </exception>
    public User? GetUser(int id)
    {
        if (id <= 0)
        {
            throw new ArgumentException(
                "User ID must be positive",
                nameof(id)
            );
        }

        return _repository.FindById(id);
    }

    /// <summary>
    /// 사용자 정보를 검증하고 할인율을 계산합니다.
    /// </summary>
    /// <param name="user">처리할 사용자 정보</param>
    /// <exception cref="ArgumentNullException">
    /// user가 null인 경우
    /// </exception>
    /// <exception cref="InvalidOperationException">
    /// 사용자가 최소 연령(18세) 미만인 경우
    /// </exception>
    /// <remarks>
    /// 할인율 정책:
    /// - 65세 초과: 20% 할인 (경로 우대)
    /// - 18-65세: 10% 기본 할인
    /// </remarks>
    public void ProcessUser(User user)
    {
        ArgumentNullException.ThrowIfNull(user);

        // 최소 연령 검증
        const int MinimumAge = 18;
        if (user.Age < MinimumAge)
        {
            throw new InvalidOperationException(
                $"User must be at least {MinimumAge} years old"
            );
        }

        // 할인율 계산 (비즈니스 규칙)
        const double SeniorDiscountRate = 0.2;  // 20%
        const double StandardDiscountRate = 0.1;  // 10%
        const int SeniorAge = 65;

        user.DiscountRate = user.Age > SeniorAge
            ? SeniorDiscountRate
            : StandardDiscountRate;

        _logger.LogInformation(
            "Applied {DiscountRate}% discount for user {UserId} (age: {Age})",
            user.DiscountRate * 100,
            user.Id,
            user.Age
        );

        _repository.Save(user);
    }

    /// <summary>
    /// 주문 금액을 계산합니다.
    /// </summary>
    /// <param name="basePrice">기본 가격</param>
    /// <param name="quantity">수량</param>
    /// <param name="orderType">주문 유형</param>
    /// <returns>최종 계산된 금액</returns>
    /// <exception cref="ArgumentException">
    /// 알 수 없는 orderType인 경우
    /// </exception>
    /// <remarks>
    /// 주문 유형별 계산 방식:
    /// - Premium (1): (기본가격 * 수량) * 1.1 (10% 프리미엄)
    /// - Bulk (2): (기본가격 + 수량) * 0.9 (10% 대량 할인)
    /// - Standard (기타): 기본가격 - 수량 (수량 차감)
    /// </remarks>
    public double CalculateOrderAmount(
        double basePrice,
        double quantity,
        OrderType orderType)
    {
        return orderType switch
        {
            OrderType.Premium =>
                basePrice * quantity * 1.1,  // 10% 프리미엄

            OrderType.Bulk =>
                (basePrice + quantity) * 0.9,  // 10% 대량 할인

            OrderType.Standard =>
                basePrice - quantity,  // 수량 차감

            _ => throw new ArgumentException(
                $"Unknown order type: {orderType}",
                nameof(orderType)
            )
        };
    }
}

/// <summary>
/// 주문 유형을 정의합니다.
/// </summary>
public enum OrderType
{
    /// <summary>프리미엄 주문 (10% 추가)</summary>
    Premium = 1,

    /// <summary>대량 주문 (10% 할인)</summary>
    Bulk = 2,

    /// <summary>표준 주문</summary>
    Standard = 3
}
```

## References

- [XML Documentation Comments](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/)
- [Recommended XML Tags](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/recommended-tags)
- [C# Coding Conventions - Comments](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions#commenting-conventions)
- [Documentation Comments Best Practices](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/documentation-comments)
