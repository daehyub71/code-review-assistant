# 설정 관리 - C#

## What to Check

- **하드코딩된 값**
  - 소스 코드에 직접 작성된 연결 문자열
  - 하드코딩된 API 키, 비밀번호
  - 환경별로 달라지는 값이 코드에 포함

- **Magic Number/String**
  - 의미 불명확한 숫자 상수
  - 반복되는 문자열 리터럴
  - 상수화되지 않은 고정값

- **설정 파일 미사용**
  - appsettings.json 미활용
  - 환경 변수 미사용
  - User Secrets / Azure Key Vault 미사용

## Best Practices

### 1. appsettings.json 사용
```csharp
// Bad - 하드코딩
public class EmailService
{
    public void SendEmail(string to, string subject)
    {
        var smtpServer = "smtp.gmail.com";
        var smtpPort = 587;
        var fromEmail = "noreply@company.com";
        var password = "P@ssw0rd123";  // ❌ 위험!

        // Send email
    }
}

// Good - appsettings.json 사용
// appsettings.json:
{
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "FromEmail": "noreply@company.com",
    "EnableSsl": true
  }
}

// C# 코드:
public class EmailSettings
{
    public string SmtpServer { get; set; }
    public int SmtpPort { get; set; }
    public string FromEmail { get; set; }
    public bool EnableSsl { get; set; }
}

public class EmailService
{
    private readonly EmailSettings _settings;

    public EmailService(IOptions<EmailSettings> settings)
    {
        _settings = settings.Value;
    }

    public void SendEmail(string to, string subject)
    {
        var smtpServer = _settings.SmtpServer;
        var smtpPort = _settings.SmtpPort;
        // ...
    }
}
```

### 2. 환경별 설정 분리
```json
// appsettings.json (기본값)
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=MyDb;..."
  },
  "ApiSettings": {
    "BaseUrl": "https://api.example.com",
    "Timeout": 30
  }
}

// appsettings.Development.json (개발)
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=MyDb_Dev;..."
  },
  "ApiSettings": {
    "BaseUrl": "https://dev-api.example.com"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Debug"
    }
  }
}

// appsettings.Production.json (운영)
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=prod-server;Database=MyDb;..."
  },
  "ApiSettings": {
    "BaseUrl": "https://api.example.com"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

### 3. User Secrets (개발 환경)
```bash
# User Secrets 초기화
dotnet user-secrets init

# 비밀 값 설정
dotnet user-secrets set "EmailSettings:Password" "MySecretPassword"
dotnet user-secrets set "ApiKeys:OpenAI" "sk-..."
```

```csharp
// Program.cs
if (builder.Environment.IsDevelopment())
{
    builder.Configuration.AddUserSecrets<Program>();
}

// 코드에서 사용
var emailPassword = builder.Configuration["EmailSettings:Password"];
```

### 4. 환경 변수 사용
```csharp
// Program.cs
builder.Configuration.AddEnvironmentVariables();

// 환경 변수 읽기 (자동 매핑)
// EMAIL_SETTINGS__PASSWORD → EmailSettings:Password
var password = builder.Configuration["EmailSettings:Password"];

// Docker/Kubernetes 환경
public class DatabaseSettings
{
    public string ConnectionString { get; set; }
}

// appsettings.json에서 환경 변수 참조
{
  "DatabaseSettings": {
    "ConnectionString": "${DB_CONNECTION_STRING}"
  }
}
```

### 5. Magic Number/String 상수화
```csharp
// Bad - Magic Number
public class OrderService
{
    public decimal CalculateDiscount(decimal amount)
    {
        if (amount > 100)
            return amount * 0.1;  // 0.1이 무엇?
        else if (amount > 50)
            return amount * 0.05;  // 0.05가 무엇?
        return 0;
    }

    public bool IsValidAge(int age)
    {
        return age >= 18 && age <= 65;  // 18, 65가 무엇?
    }
}

// Good - 상수화
public class OrderService
{
    // 할인 정책
    private const decimal PremiumThreshold = 100m;
    private const decimal StandardThreshold = 50m;
    private const decimal PremiumDiscountRate = 0.1m;  // 10%
    private const decimal StandardDiscountRate = 0.05m;  // 5%

    // 연령 제한
    private const int MinimumAge = 18;
    private const int MaximumAge = 65;

    public decimal CalculateDiscount(decimal amount)
    {
        if (amount > PremiumThreshold)
            return amount * PremiumDiscountRate;
        else if (amount > StandardThreshold)
            return amount * StandardDiscountRate;
        return 0;
    }

    public bool IsValidAge(int age)
    {
        return age >= MinimumAge && age <= MaximumAge;
    }
}
```

### 6. Options Pattern 활용
```csharp
// appsettings.json
{
  "CacheSettings": {
    "SlidingExpiration": 600,
    "AbsoluteExpiration": 3600,
    "MaxSize": 1000
  }
}

// Settings 클래스
public class CacheSettings
{
    public const string SectionName = "CacheSettings";

    public int SlidingExpiration { get; set; }
    public int AbsoluteExpiration { get; set; }
    public int MaxSize { get; set; }
}

// Program.cs 또는 Startup.cs
builder.Services.Configure<CacheSettings>(
    builder.Configuration.GetSection(CacheSettings.SectionName)
);

// 서비스에서 사용
public class CacheService
{
    private readonly CacheSettings _settings;

    public CacheService(IOptions<CacheSettings> options)
    {
        _settings = options.Value;
    }

    public void AddToCache<T>(string key, T value)
    {
        var options = new MemoryCacheEntryOptions
        {
            SlidingExpiration = TimeSpan.FromSeconds(
                _settings.SlidingExpiration
            ),
            AbsoluteExpiration = DateTimeOffset.Now.AddSeconds(
                _settings.AbsoluteExpiration
            )
        };

        _cache.Set(key, value, options);
    }
}
```

### 7. Azure Key Vault (운영 환경)
```csharp
// Program.cs
if (builder.Environment.IsProduction())
{
    var keyVaultEndpoint = builder.Configuration["KeyVault:Endpoint"];

    builder.Configuration.AddAzureKeyVault(
        new Uri(keyVaultEndpoint),
        new DefaultAzureCredential()
    );
}

// 사용
var apiKey = builder.Configuration["ApiKeys--OpenAI"];  // Key Vault에서 자동 로드
```

## Example

**Before**:
```csharp
public class UserService
{
    public async Task<User> AuthenticateAsync(string username, string password)
    {
        // 하드코딩된 연결 문자열
        var connString = "Server=localhost;Database=UserDb;User=sa;Password=P@ss123;";

        using var conn = new SqlConnection(connString);
        await conn.OpenAsync();

        // Magic string
        var query = "SELECT * FROM Users WHERE Username=@user AND Password=@pass";
        // ...
    }

    public async Task SendWelcomeEmailAsync(string email)
    {
        // 하드코딩된 이메일 설정
        var smtpServer = "smtp.gmail.com";
        var smtpPort = 587;
        var fromEmail = "noreply@company.com";
        var password = "SecretPassword123";  // ❌ 위험!

        // Magic number
        if (email.Length > 50)
            throw new Exception("Email too long");

        // ...
    }

    public decimal CalculateFee(decimal amount)
    {
        // Magic number
        if (amount > 1000)
            return amount * 0.02;  // 0.02가 무엇?
        return amount * 0.05;  // 0.05가 무엇?
    }
}

public class ApiClient
{
    public async Task<string> GetDataAsync()
    {
        // 하드코딩된 API 엔드포인트
        var apiUrl = "https://api.example.com/v1/data";
        var apiKey = "sk-1234567890abcdef";  // ❌ 위험!

        var client = new HttpClient();
        client.DefaultRequestHeaders.Add("X-API-Key", apiKey);

        return await client.GetStringAsync(apiUrl);
    }
}
```

**After**:
```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "UserDatabase": "Server=localhost;Database=UserDb;..."
  },
  "EmailSettings": {
    "SmtpServer": "smtp.gmail.com",
    "SmtpPort": 587,
    "FromEmail": "noreply@company.com",
    "MaxEmailLength": 256
  },
  "FeeSettings": {
    "PremiumThreshold": 1000,
    "PremiumRate": 0.02,
    "StandardRate": 0.05
  },
  "ApiSettings": {
    "BaseUrl": "https://api.example.com",
    "Version": "v1"
  }
}

// appsettings.Development.json
{
  "ConnectionStrings": {
    "UserDatabase": "Server=localhost;Database=UserDb_Dev;..."
  }
}

// User Secrets (dotnet user-secrets set)
// EmailSettings:Password = "SecretPassword123"
// ApiSettings:ApiKey = "sk-1234567890abcdef"

// Settings Classes
public class EmailSettings
{
    public string SmtpServer { get; set; }
    public int SmtpPort { get; set; }
    public string FromEmail { get; set; }
    public string Password { get; set; }  // User Secrets에서 로드
    public int MaxEmailLength { get; set; }
}

public class FeeSettings
{
    public decimal PremiumThreshold { get; set; }
    public decimal PremiumRate { get; set; }
    public decimal StandardRate { get; set; }
}

public class ApiSettings
{
    public string BaseUrl { get; set; }
    public string Version { get; set; }
    public string ApiKey { get; set; }  // User Secrets에서 로드
}

// Program.cs
builder.Services.Configure<EmailSettings>(
    builder.Configuration.GetSection("EmailSettings")
);
builder.Services.Configure<FeeSettings>(
    builder.Configuration.GetSection("FeeSettings")
);
builder.Services.Configure<ApiSettings>(
    builder.Configuration.GetSection("ApiSettings")
);

// UserService.cs
public class UserService
{
    private readonly string _connectionString;
    private readonly EmailSettings _emailSettings;
    private readonly FeeSettings _feeSettings;
    private readonly ILogger<UserService> _logger;

    public UserService(
        IConfiguration configuration,
        IOptions<EmailSettings> emailSettings,
        IOptions<FeeSettings> feeSettings,
        ILogger<UserService> logger)
    {
        _connectionString = configuration.GetConnectionString("UserDatabase");
        _emailSettings = emailSettings.Value;
        _feeSettings = feeSettings.Value;
        _logger = logger;
    }

    public async Task<User> AuthenticateAsync(string username, string password)
    {
        await using var conn = new SqlConnection(_connectionString);
        await conn.OpenAsync();

        const string Query = "SELECT * FROM Users WHERE Username=@user AND Password=@pass";
        // ...
    }

    public async Task SendWelcomeEmailAsync(string email)
    {
        // 설정에서 로드
        if (email.Length > _emailSettings.MaxEmailLength)
        {
            throw new ArgumentException(
                $"Email cannot exceed {_emailSettings.MaxEmailLength} characters",
                nameof(email)
            );
        }

        var smtp = new SmtpClient(_emailSettings.SmtpServer, _emailSettings.SmtpPort)
        {
            Credentials = new NetworkCredential(
                _emailSettings.FromEmail,
                _emailSettings.Password  // User Secrets에서 로드됨
            ),
            EnableSsl = true
        };

        // Send email...
    }

    public decimal CalculateFee(decimal amount)
    {
        return amount > _feeSettings.PremiumThreshold
            ? amount * _feeSettings.PremiumRate
            : amount * _feeSettings.StandardRate;
    }
}

// ApiClient.cs
public class ApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ApiSettings _settings;

    public ApiClient(
        HttpClient httpClient,
        IOptions<ApiSettings> settings)
    {
        _httpClient = httpClient;
        _settings = settings.Value;

        _httpClient.BaseAddress = new Uri(_settings.BaseUrl);
        _httpClient.DefaultRequestHeaders.Add(
            "X-API-Key",
            _settings.ApiKey  // User Secrets에서 로드됨
        );
    }

    public async Task<string> GetDataAsync()
    {
        var endpoint = $"{_settings.Version}/data";
        return await _httpClient.GetStringAsync(endpoint);
    }
}
```

## References

- [Configuration in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)
- [Options Pattern](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options)
- [Safe Storage of App Secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets)
- [Azure Key Vault Configuration Provider](https://learn.microsoft.com/en-us/aspnet/core/security/key-vault-configuration)
- [Environment Variables](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/#environment-variables)
