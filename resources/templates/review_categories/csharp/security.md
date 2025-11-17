# 보안 모범 사례 - C#

## What to Check

- **SQL Injection 취약점**
  - 문자열 연결로 SQL 쿼리 생성
  - 매개변수화된 쿼리 미사용
  - ORM (Entity Framework) 미사용 시 안전하지 않은 쿼리

- **크로스 사이트 스크립팅 (XSS)**
  - 사용자 입력의 HTML 인코딩 누락
  - Raw HTML 출력
  - JavaScript 코드에 사용자 입력 직접 삽입

- **민감 정보 노출**
  - 하드코딩된 비밀번호, API 키
  - 평문 저장된 민감 데이터
  - 예외 메시지에 민감 정보 포함

- **입력 검증 누락**
  - 사용자 입력의 검증/정제 없음
  - 파일 업로드 시 확장자/크기 검증 누락
  - 경로 조작 (Path Traversal) 가능성

## Best Practices

### 1. 매개변수화된 쿼리 사용
```csharp
// Bad - SQL Injection 취약
public User GetUser(string username)
{
    var query = "SELECT * FROM Users WHERE Username = '" + username + "'";
    // username이 "admin' OR '1'='1" 이면?
    return ExecuteQuery(query);
}

// Good - 매개변수화된 쿼리
public User GetUser(string username)
{
    var query = "SELECT * FROM Users WHERE Username = @Username";
    var parameters = new SqlParameter("@Username", username);
    return ExecuteQuery(query, parameters);
}

// Best - Entity Framework 사용
public User GetUser(string username)
{
    return _context.Users
        .FirstOrDefault(u => u.Username == username);
}
```

### 2. 입력 검증 및 정제
```csharp
// Bad - 검증 없음
public IActionResult UpdateProfile(string email)
{
    _user.Email = email;  // 임의 입력 허용
    return Ok();
}

// Good - 입력 검증
public IActionResult UpdateProfile(string email)
{
    // Email 형식 검증
    if (!new EmailAddressAttribute().IsValid(email))
    {
        return BadRequest("Invalid email format");
    }

    // 길이 제한
    if (email.Length > 256)
    {
        return BadRequest("Email too long");
    }

    _user.Email = email;
    return Ok();
}

// Better - Data Annotations 사용
public class UpdateProfileRequest
{
    [Required]
    [EmailAddress]
    [MaxLength(256)]
    public string Email { get; set; }
}

public IActionResult UpdateProfile([FromBody] UpdateProfileRequest request)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState);

    _user.Email = request.Email;
    return Ok();
}
```

### 3. 민감 정보 암호화
```csharp
// Bad - 평문 저장
public class User
{
    public string Password { get; set; }  // ❌
    public string CreditCard { get; set; }  // ❌
}

// Good - 해시/암호화
using System.Security.Cryptography;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;

public class UserService
{
    // 비밀번호 해싱 (PBKDF2)
    public string HashPassword(string password)
    {
        byte[] salt = RandomNumberGenerator.GetBytes(128 / 8);

        string hashed = Convert.ToBase64String(KeyDerivation.Pbkdf2(
            password: password,
            salt: salt,
            prf: KeyDerivationPrf.HMACSHA256,
            iterationCount: 100000,
            numBytesRequested: 256 / 8
        ));

        return $"{Convert.ToBase64String(salt)}:{hashed}";
    }

    // 데이터 암호화 (AES)
    public string EncryptData(string plainText, byte[] key, byte[] iv)
    {
        using var aes = Aes.Create();
        aes.Key = key;
        aes.IV = iv;

        using var encryptor = aes.CreateEncryptor();
        using var ms = new MemoryStream();
        using var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write);
        using var sw = new StreamWriter(cs);

        sw.Write(plainText);
        sw.Close();

        return Convert.ToBase64String(ms.ToArray());
    }
}
```

### 4. XSS 방지 (HTML 인코딩)
```csharp
// Bad - Raw HTML 출력
@{
    var userInput = Model.Comment;
}
<div>@Html.Raw(userInput)</div>  // ❌ XSS 취약

// Good - 자동 인코딩
<div>@Model.Comment</div>  // ✅ Razor가 자동 인코딩

// 또는 명시적 인코딩
@using System.Web;
<div>@HttpUtility.HtmlEncode(Model.Comment)</div>
```

### 5. 경로 조작 방지
```csharp
// Bad - Path Traversal 취약
public IActionResult GetFile(string filename)
{
    var path = Path.Combine(_uploadPath, filename);
    // filename이 "../../../etc/passwd" 이면?
    return File(path, "application/octet-stream");
}

// Good - 경로 검증
public IActionResult GetFile(string filename)
{
    // 파일명만 추출 (경로 제거)
    var safeFilename = Path.GetFileName(filename);

    // 위험한 문자 제거
    safeFilename = Regex.Replace(safeFilename, @"[^\w\.]", "");

    var path = Path.Combine(_uploadPath, safeFilename);

    // 실제 경로가 업로드 디렉토리 내부인지 확인
    var fullPath = Path.GetFullPath(path);
    var uploadFullPath = Path.GetFullPath(_uploadPath);

    if (!fullPath.StartsWith(uploadFullPath))
    {
        return BadRequest("Invalid file path");
    }

    return File(fullPath, "application/octet-stream");
}
```

### 6. 보안 헤더 설정
```csharp
// Startup.cs / Program.cs
app.Use(async (context, next) =>
{
    // XSS 보호
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");

    // HTTPS 강제
    context.Response.Headers.Add(
        "Strict-Transport-Security",
        "max-age=31536000; includeSubDomains"
    );

    // CSP (Content Security Policy)
    context.Response.Headers.Add(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self'"
    );

    await next();
});
```

## Example

**Before**:
```csharp
public class UserController : Controller
{
    private readonly string _connString = "Server=localhost;Database=MyDB;User=sa;Password=admin123;";

    public IActionResult Login(string username, string password)
    {
        // SQL Injection 취약
        var query = $"SELECT * FROM Users WHERE Username='{username}' AND Password='{password}'";
        var user = ExecuteQuery(query);

        if (user != null)
        {
            // 세션에 민감 정보 저장
            Session["UserPassword"] = password;
            return Ok("Login successful");
        }

        return Unauthorized("Login failed");
    }

    public IActionResult DownloadFile(string path)
    {
        // Path Traversal 취약
        var fullPath = "/uploads/" + path;
        return File(fullPath, "application/octet-stream");
    }

    public IActionResult ShowComment(int id)
    {
        var comment = _db.Comments.Find(id);
        // XSS 취약
        return Content(comment.Text, "text/html");
    }
}
```

**After**:
```csharp
public class UserController : Controller
{
    private readonly IConfiguration _config;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UserController> _logger;

    public UserController(
        IConfiguration config,
        IPasswordHasher<User> passwordHasher,
        ApplicationDbContext context,
        ILogger<UserController> logger)
    {
        _config = config;
        _passwordHasher = passwordHasher;
        _context = context;
        _logger = logger;
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Login(
        [FromBody] LoginRequest request)
    {
        // 입력 검증
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        // Entity Framework 사용 (SQL Injection 방지)
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Username == request.Username);

        if (user == null)
        {
            _logger.LogWarning("Login attempt for non-existent user: {Username}",
                request.Username);
            return Unauthorized("Invalid credentials");
        }

        // 비밀번호 해시 비교
        var result = _passwordHasher.VerifyHashedPassword(
            user,
            user.PasswordHash,
            request.Password
        );

        if (result == PasswordVerificationResult.Failed)
        {
            _logger.LogWarning("Failed login attempt for user: {UserId}",
                user.Id);
            return Unauthorized("Invalid credentials");
        }

        // JWT 토큰 생성 (세션에 민감 정보 저장 안 함)
        var token = GenerateJwtToken(user);

        return Ok(new { Token = token });
    }

    [HttpGet]
    public IActionResult DownloadFile(string filename)
    {
        // 파일명 정제
        var safeFilename = Path.GetFileName(filename);
        safeFilename = Regex.Replace(safeFilename, @"[^\w\.-]", "");

        var uploadPath = _config["UploadPath"];
        var fullPath = Path.GetFullPath(
            Path.Combine(uploadPath, safeFilename)
        );

        // 경로 검증
        if (!fullPath.StartsWith(Path.GetFullPath(uploadPath)))
        {
            _logger.LogWarning(
                "Path traversal attempt: {Filename}",
                filename
            );
            return BadRequest("Invalid file path");
        }

        if (!System.IO.File.Exists(fullPath))
            return NotFound();

        return PhysicalFile(fullPath, "application/octet-stream");
    }

    [HttpGet]
    public async Task<IActionResult> ShowComment(int id)
    {
        var comment = await _context.Comments.FindAsync(id);

        if (comment == null)
            return NotFound();

        // Razor View가 자동으로 HTML 인코딩 수행
        return View(comment);
    }
}

public class LoginRequest
{
    [Required]
    [StringLength(50, MinimumLength = 3)]
    public string Username { get; set; }

    [Required]
    [StringLength(100, MinimumLength = 8)]
    public string Password { get; set; }
}
```

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SQL Injection Prevention](https://learn.microsoft.com/en-us/sql/relational-databases/security/sql-injection)
- [Cross-Site Scripting (XSS)](https://learn.microsoft.com/en-us/aspnet/core/security/cross-site-scripting)
- [Data Protection in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/)
- [Security Best Practices](https://learn.microsoft.com/en-us/aspnet/core/security/)
