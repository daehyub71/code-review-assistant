"""Review category definitions for code analysis."""
from enum import Enum
from typing import Dict


class ReviewCategory(Enum):
    """8 standardized code review categories.

    These categories are consistent across all supported languages,
    but their implementation details vary per language.
    """

    # 1. Null/Undefined Safety
    NULL_SAFETY = "null_reference"

    # 2. Exception/Error Handling
    EXCEPTION_HANDLING = "exception_handling"

    # 3. Resource Management
    RESOURCE_MANAGEMENT = "resource_management"

    # 4. Performance Optimization
    PERFORMANCE = "performance"

    # 5. Security Best Practices
    SECURITY = "security"

    # 6. Naming Conventions
    NAMING_CONVENTION = "naming_convention"

    # 7. Code Documentation
    CODE_DOCUMENTATION = "code_documentation"

    # 8. Configuration Management
    HARDCODING_TO_CONFIG = "hardcoding_to_config"

    @property
    def display_name(self) -> str:
        """Get human-readable display name for the category."""
        return CATEGORY_DISPLAY_NAMES[self]

    @property
    def description(self) -> str:
        """Get detailed description of the category."""
        return CATEGORY_DESCRIPTIONS[self]

    @property
    def template_filename(self) -> str:
        """Get template filename for this category (without .md extension)."""
        return self.value


# Display names for UI (Korean)
CATEGORY_DISPLAY_NAMES: Dict[ReviewCategory, str] = {
    ReviewCategory.NULL_SAFETY: "Null/Undefined 안전성",
    ReviewCategory.EXCEPTION_HANDLING: "예외/에러 처리",
    ReviewCategory.RESOURCE_MANAGEMENT: "리소스 관리",
    ReviewCategory.PERFORMANCE: "성능 최적화",
    ReviewCategory.SECURITY: "보안 모범 사례",
    ReviewCategory.NAMING_CONVENTION: "네이밍 규칙",
    ReviewCategory.CODE_DOCUMENTATION: "코드 문서화",
    ReviewCategory.HARDCODING_TO_CONFIG: "설정 관리",
}

# Detailed descriptions for each category
CATEGORY_DESCRIPTIONS: Dict[ReviewCategory, str] = {
    ReviewCategory.NULL_SAFETY: (
        "Null 참조 오류를 방지하고 안전한 코드를 작성하는 패턴을 검토합니다. "
        "언어별로 null-conditional operator, Optional<T>, type hints 등을 확인합니다."
    ),
    ReviewCategory.EXCEPTION_HANDLING: (
        "예외 처리가 적절하게 구현되었는지 검토합니다. "
        "try-catch 패턴, 특정 예외 타입 처리, 예외 전파 등을 확인합니다."
    ),
    ReviewCategory.RESOURCE_MANAGEMENT: (
        "파일, 데이터베이스 연결, 네트워크 리소스 등이 올바르게 관리되는지 검토합니다. "
        "using 문, try-with-resources, context manager 등을 확인합니다."
    ),
    ReviewCategory.PERFORMANCE: (
        "코드의 성능을 개선할 수 있는 부분을 검토합니다. "
        "LINQ, Stream API, comprehension, computed properties 등 언어별 최적화 패턴을 확인합니다."
    ),
    ReviewCategory.SECURITY: (
        "보안 취약점을 검토합니다. "
        "SQL Injection, XSS, 입력 검증, 인증/인가 등을 확인합니다."
    ),
    ReviewCategory.NAMING_CONVENTION: (
        "언어별 네이밍 규칙을 준수하는지 검토합니다. "
        "PascalCase, camelCase, snake_case 등 언어 표준을 확인합니다."
    ),
    ReviewCategory.CODE_DOCUMENTATION: (
        "코드 문서화가 충분한지 검토합니다. "
        "XML 주석, JavaDoc, docstring, JSDoc 등 언어별 문서화 표준을 확인합니다."
    ),
    ReviewCategory.HARDCODING_TO_CONFIG: (
        "하드코딩된 값을 설정 파일로 분리해야 하는지 검토합니다. "
        "appsettings.json, .properties, .env 파일 등을 활용하는 패턴을 확인합니다."
    ),
}


def get_all_categories() -> list[ReviewCategory]:
    """Get list of all review categories.

    Returns:
        List of all ReviewCategory enum values
    """
    return list(ReviewCategory)


def get_category_by_value(value: str) -> ReviewCategory:
    """Get ReviewCategory by its string value.

    Args:
        value: Category value (e.g., "null_reference")

    Returns:
        ReviewCategory enum

    Raises:
        ValueError: If value doesn't match any category
    """
    for category in ReviewCategory:
        if category.value == value:
            return category
    raise ValueError(f"Unknown review category: {value}")
