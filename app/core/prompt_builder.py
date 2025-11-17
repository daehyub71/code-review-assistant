"""
Prompt Builder - 언어별 템플릿을 조합하여 코드 리뷰 프롬프트 생성
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

from app.models.language import Language
from app.models.review_category import ReviewCategory

logger = logging.getLogger(__name__)


class PromptBuilderError(Exception):
    """Prompt Builder 관련 에러"""
    pass


class PromptBuilder:
    """코드 리뷰 프롬프트 빌더

    언어별 템플릿을 로드하고 선택된 카테고리에 따라
    최종 프롬프트를 조립합니다.

    Examples:
        >>> builder = PromptBuilder()
        >>> prompt = builder.build_prompt(
        ...     language=Language.PYTHON,
        ...     categories=[ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY],
        ...     code="def get_user(id): return db.query(User).get(id)"
        ... )
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        """초기화

        Args:
            templates_dir: 템플릿 디렉토리 경로 (기본값: resources/templates/review_categories)
        """
        if templates_dir is None:
            # 프로젝트 루트/resources/templates/review_categories
            templates_dir = Path(__file__).parent.parent.parent / "resources" / "templates" / "review_categories"

        self.templates_dir = templates_dir
        self._template_cache: Dict[str, str] = {}  # 캐시

        logger.info(f"PromptBuilder initialized with templates_dir: {self.templates_dir}")

        # 템플릿 디렉토리 존재 확인
        if not self.templates_dir.exists():
            raise PromptBuilderError(f"Templates directory not found: {self.templates_dir}")

    def load_template(self, language: Language, category: ReviewCategory) -> str:
        """언어와 카테고리에 해당하는 템플릿 로드

        Args:
            language: 프로그래밍 언어
            category: 검토 카테고리

        Returns:
            템플릿 내용 (Markdown)

        Raises:
            PromptBuilderError: 템플릿 파일을 찾을 수 없거나 읽기 실패 시

        Examples:
            >>> builder = PromptBuilder()
            >>> template = builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)
            >>> print(template[:50])
            # Null/Type 안전성 - Python
        """
        # 캐시 키: "python:null_reference"
        cache_key = f"{language.value}:{category.value}"

        # 캐시에 있으면 바로 반환
        if cache_key in self._template_cache:
            logger.debug(f"Template loaded from cache: {cache_key}")
            return self._template_cache[cache_key]

        # 템플릿 파일 경로: resources/templates/review_categories/python/null_reference.md
        template_path = self.templates_dir / language.value / f"{category.value}.md"

        if not template_path.exists():
            raise PromptBuilderError(
                f"Template not found: {template_path}\n"
                f"Language: {language.value}, Category: {category.value}"
            )

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 캐시에 저장
            self._template_cache[cache_key] = content

            logger.info(f"Template loaded: {cache_key} ({len(content)} bytes)")
            return content

        except Exception as e:
            raise PromptBuilderError(f"Failed to read template {template_path}: {e}")

    def build_prompt(
        self,
        language: Language,
        categories: List[ReviewCategory],
        code: str,
        additional_instructions: Optional[str] = None
    ) -> str:
        """최종 코드 리뷰 프롬프트 생성

        Args:
            language: 프로그래밍 언어
            categories: 검토할 카테고리 리스트
            code: 리뷰할 코드
            additional_instructions: 추가 지시사항 (선택)

        Returns:
            조립된 최종 프롬프트

        Raises:
            PromptBuilderError: 템플릿 로드 실패 시
            ValueError: categories가 비어있을 때

        Examples:
            >>> builder = PromptBuilder()
            >>> prompt = builder.build_prompt(
            ...     language=Language.PYTHON,
            ...     categories=[ReviewCategory.NULL_SAFETY],
            ...     code="def get_user(id): return User.query.get(id)"
            ... )
        """
        if not categories:
            raise ValueError("At least one category must be specified")

        logger.info(f"Building prompt for {language.value} with {len(categories)} categories")

        # 시스템 프롬프트
        system_prompt = f"""You are an expert {language.value.upper()} code reviewer.
Analyze the provided code and suggest improvements based on the following review categories.

**Programming Language**: {language.value.upper()}
**Review Categories**: {', '.join(cat.display_name for cat in categories)}
"""

        # 각 카테고리별 템플릿 로드
        category_prompts = []
        for category in categories:
            try:
                template = self.load_template(language, category)
                category_prompts.append(f"## {category.display_name}\n\n{template}")
            except PromptBuilderError as e:
                logger.error(f"Failed to load template for {category.value}: {e}")
                raise

        # 프롬프트 조립
        full_prompt = f"""{system_prompt}

---

# Review Guidelines

{''.join(category_prompts)}

---

# Code to Review

```{language.value}
{code}
```

---

# Instructions

1. Analyze the code above according to the review guidelines.
2. For each category, identify issues and suggest improvements.
3. Provide "Before" and "After" code examples for each suggestion.
4. Focus on actionable, specific improvements.
"""

        if additional_instructions:
            full_prompt += f"\n\n# Additional Instructions\n\n{additional_instructions}\n"

        full_prompt += "\nPlease provide your code review in Korean (한국어)."

        logger.info(f"Prompt built successfully ({len(full_prompt)} bytes)")

        return full_prompt

    def clear_cache(self) -> None:
        """템플릿 캐시 초기화

        Examples:
            >>> builder = PromptBuilder()
            >>> builder.clear_cache()
        """
        self._template_cache.clear()
        logger.info("Template cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 반환

        Returns:
            캐시 통계 (캐시된 템플릿 수, 총 바이트 크기)

        Examples:
            >>> builder = PromptBuilder()
            >>> stats = builder.get_cache_stats()
            >>> print(stats)
            {'cached_templates': 3, 'total_bytes': 15234}
        """
        return {
            "cached_templates": len(self._template_cache),
            "total_bytes": sum(len(content) for content in self._template_cache.values())
        }
