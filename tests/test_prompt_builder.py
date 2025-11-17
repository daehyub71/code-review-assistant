"""
Prompt Builder 테스트
"""

import pytest
from pathlib import Path

from app.core.prompt_builder import PromptBuilder, PromptBuilderError
from app.models.language import Language
from app.models.review_category import ReviewCategory


class TestPromptBuilder:
    """PromptBuilder 클래스 테스트"""

    @pytest.fixture
    def builder(self):
        """PromptBuilder 인스턴스"""
        return PromptBuilder()

    def test_init_default_templates_dir(self, builder):
        """기본 템플릿 디렉토리로 초기화"""
        assert builder.templates_dir.exists()
        assert builder.templates_dir.name == "review_categories"

    def test_init_custom_templates_dir(self, tmp_path):
        """사용자 지정 템플릿 디렉토리로 초기화"""
        # 임시 디렉토리 생성
        custom_dir = tmp_path / "custom_templates"
        custom_dir.mkdir()

        builder = PromptBuilder(templates_dir=custom_dir)
        assert builder.templates_dir == custom_dir

    def test_init_nonexistent_dir_raises_error(self, tmp_path):
        """존재하지 않는 디렉토리로 초기화 시 에러"""
        nonexistent_dir = tmp_path / "nonexistent"

        with pytest.raises(PromptBuilderError, match="Templates directory not found"):
            PromptBuilder(templates_dir=nonexistent_dir)

    def test_load_template_python_null_safety(self, builder):
        """Python null_reference 템플릿 로드"""
        template = builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)

        assert len(template) > 0
        assert "Null" in template or "Type" in template
        assert "Python" in template

    def test_load_template_csharp_security(self, builder):
        """C# security 템플릿 로드"""
        template = builder.load_template(Language.CSHARP, ReviewCategory.SECURITY)

        assert len(template) > 0
        assert "보안" in template or "Security" in template

    def test_load_template_java_performance(self, builder):
        """Java performance 템플릿 로드"""
        template = builder.load_template(Language.JAVA, ReviewCategory.PERFORMANCE)

        assert len(template) > 0
        assert "성능" in template or "Performance" in template

    def test_load_template_vue_naming(self, builder):
        """Vue naming_convention 템플릿 로드"""
        template = builder.load_template(Language.VUE, ReviewCategory.NAMING_CONVENTION)

        assert len(template) > 0
        assert "네이밍" in template or "Naming" in template or "Vue" in template

    def test_load_template_caching(self, builder):
        """템플릿 캐싱 동작 확인"""
        # 첫 번째 로드
        template1 = builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)

        # 캐시 확인
        stats_before = builder.get_cache_stats()
        assert stats_before["cached_templates"] == 1

        # 두 번째 로드 (캐시에서)
        template2 = builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)

        # 같은 내용
        assert template1 == template2

        # 캐시 크기 변화 없음
        stats_after = builder.get_cache_stats()
        assert stats_after["cached_templates"] == 1

    def test_load_template_nonexistent_raises_error(self, builder):
        """존재하지 않는 템플릿 로드 시 에러"""
        # 잘못된 language 값으로 경로 생성 시도
        with pytest.raises(PromptBuilderError, match="Template not found"):
            # 존재하지 않는 조합
            template_path = builder.templates_dir / "nonexistent_lang" / "null_reference.md"
            if not template_path.exists():
                # Language enum에 없는 값은 직접 생성 불가
                # PromptBuilderError를 발생시키기 위해 임시 경로 사용
                builder.templates_dir = Path("/nonexistent")
                builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)

    def test_build_prompt_single_category(self, builder):
        """단일 카테고리로 프롬프트 생성"""
        code = "def get_user(id): return db.query(User).get(id)"
        prompt = builder.build_prompt(
            language=Language.PYTHON,
            categories=[ReviewCategory.NULL_SAFETY],
            code=code
        )

        # 프롬프트 검증
        assert len(prompt) > 0
        assert "PYTHON" in prompt
        assert code in prompt
        assert ReviewCategory.NULL_SAFETY.display_name in prompt
        assert "한국어" in prompt

    def test_build_prompt_multiple_categories(self, builder):
        """여러 카테고리로 프롬프트 생성"""
        code = "public void ProcessUser(string name) { }"
        categories = [
            ReviewCategory.NULL_SAFETY,
            ReviewCategory.NAMING_CONVENTION,
            ReviewCategory.SECURITY
        ]

        prompt = builder.build_prompt(
            language=Language.CSHARP,
            categories=categories,
            code=code
        )

        # 모든 카테고리가 포함되었는지 확인
        for category in categories:
            assert category.display_name in prompt

        assert code in prompt
        assert "CSHARP" in prompt

    def test_build_prompt_with_additional_instructions(self, builder):
        """추가 지시사항과 함께 프롬프트 생성"""
        code = "const user = getUser(id)"
        additional = "Focus on TypeScript best practices"

        prompt = builder.build_prompt(
            language=Language.VUE,
            categories=[ReviewCategory.NULL_SAFETY],
            code=code,
            additional_instructions=additional
        )

        assert additional in prompt
        assert code in prompt

    def test_build_prompt_empty_categories_raises_error(self, builder):
        """빈 카테고리 리스트로 프롬프트 생성 시 에러"""
        with pytest.raises(ValueError, match="At least one category"):
            builder.build_prompt(
                language=Language.PYTHON,
                categories=[],
                code="print('hello')"
            )

    def test_clear_cache(self, builder):
        """캐시 초기화"""
        # 템플릿 로드하여 캐시 채우기
        builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)
        builder.load_template(Language.JAVA, ReviewCategory.SECURITY)

        # 캐시 확인
        stats_before = builder.get_cache_stats()
        assert stats_before["cached_templates"] == 2

        # 캐시 초기화
        builder.clear_cache()

        # 캐시 비었는지 확인
        stats_after = builder.get_cache_stats()
        assert stats_after["cached_templates"] == 0
        assert stats_after["total_bytes"] == 0

    def test_get_cache_stats(self, builder):
        """캐시 통계 반환"""
        # 초기 상태
        stats = builder.get_cache_stats()
        assert stats["cached_templates"] == 0
        assert stats["total_bytes"] == 0

        # 템플릿 로드
        builder.load_template(Language.PYTHON, ReviewCategory.NULL_SAFETY)
        builder.load_template(Language.PYTHON, ReviewCategory.SECURITY)

        # 통계 확인
        stats = builder.get_cache_stats()
        assert stats["cached_templates"] == 2
        assert stats["total_bytes"] > 0

    def test_all_languages_have_templates(self, builder):
        """모든 언어에 대해 최소 1개 템플릿이 존재하는지 확인"""
        for language in Language:
            # 각 언어의 디렉토리가 존재하는지
            lang_dir = builder.templates_dir / language.value
            assert lang_dir.exists(), f"Template directory missing for {language.value}"

            # 최소 1개 템플릿 파일 존재
            templates = list(lang_dir.glob("*.md"))
            assert len(templates) > 0, f"No templates found for {language.value}"

    def test_all_categories_have_templates_for_each_language(self, builder):
        """모든 언어가 8개 카테고리 템플릿을 가지는지 확인"""
        for language in Language:
            for category in ReviewCategory:
                # 템플릿 파일이 존재하는지
                template_path = builder.templates_dir / language.value / f"{category.value}.md"
                assert template_path.exists(), (
                    f"Template missing: {language.value}/{category.value}.md"
                )

                # 템플릿을 로드할 수 있는지
                template = builder.load_template(language, category)
                assert len(template) > 0
