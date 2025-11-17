"""
Integrated Report Generator - 통합 리포트 생성기

여러 파일의 배치 분석 결과를 하나의 통합 리포트로 생성합니다.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.models.language import Language
from app.models.review_category import ReviewCategory

logger = logging.getLogger(__name__)


class FileAnalysisResult:
    """단일 파일 분석 결과

    Attributes:
        file_path: 파일 경로
        code: 코드 내용
        review_result: 리뷰 결과
        input_tokens: 입력 토큰 수
        output_tokens: 출력 토큰 수
    """

    def __init__(
        self,
        file_path: str,
        code: str,
        review_result: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ):
        self.file_path = file_path
        self.code = code
        self.review_result = review_result
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class IntegratedReportGenerator:
    """통합 리포트 생성기

    여러 파일의 분석 결과를 하나의 통합 리포트로 생성합니다.

    Examples:
        >>> generator = IntegratedReportGenerator()
        >>> results = [
        ...     FileAnalysisResult("file1.py", "code1", "review1", 100, 200),
        ...     FileAnalysisResult("file2.py", "code2", "review2", 150, 250),
        ... ]
        >>> report = generator.generate_integrated_report(
        ...     results=results,
        ...     language=Language.PYTHON,
        ...     model="gpt-4o-mini"
        ... )
    """

    def __init__(self, reports_dir: Optional[Path] = None):
        """초기화

        Args:
            reports_dir: 리포트 저장 디렉토리
        """
        if reports_dir is None:
            project_root = Path(__file__).parent.parent.parent
            reports_dir = project_root / "reports"

        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"IntegratedReportGenerator initialized")

    def generate_integrated_report(
        self,
        results: List[FileAnalysisResult],
        language: Language,
        categories: List[ReviewCategory],
        model: str,
        cost_usd: float = 0.0,
        cost_krw: float = 0.0,
    ) -> str:
        """통합 리포트 생성

        Args:
            results: 파일별 분석 결과 리스트
            language: 프로그래밍 언어
            categories: 리뷰 카테고리
            model: 사용된 모델
            cost_usd: 총 비용 (USD)
            cost_krw: 총 비용 (KRW)

        Returns:
            통합 마크다운 리포트

        Examples:
            >>> generator = IntegratedReportGenerator()
            >>> results = [FileAnalysisResult(...), ...]
            >>> report = generator.generate_integrated_report(results, ...)
        """
        timestamp = datetime.now()

        # 헤더
        header = self._generate_header(
            timestamp, language, model, categories, len(results)
        )

        # 요약 통계
        summary = self._generate_summary(results, cost_usd, cost_krw)

        # 파일별 리뷰 결과
        file_reviews = self._generate_file_reviews(results, language)

        # 전체 분석 요약
        overall_summary = self._generate_overall_summary(results)

        # 푸터
        footer = self._generate_footer(timestamp)

        # 전체 리포트 조합
        report = f"{header}\n\n{summary}\n\n{file_reviews}\n\n{overall_summary}\n\n{footer}"

        logger.info(f"Integrated report generated for {len(results)} files")

        return report

    def _generate_header(
        self,
        timestamp: datetime,
        language: Language,
        model: str,
        categories: List[ReviewCategory],
        file_count: int,
    ) -> str:
        """헤더 생성"""
        category_names = ", ".join([cat.value for cat in categories])

        header = f"""# 통합 코드 리뷰 리포트

**생성 일시**: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}  
**프로그래밍 언어**: {language.value}  
**분석 모델**: {model}  
**리뷰 카테고리**: {category_names}  
**분석 파일 수**: {file_count}개

---
"""
        return header

    def _generate_summary(
        self, results: List[FileAnalysisResult], cost_usd: float, cost_krw: float
    ) -> str:
        """요약 통계 생성"""
        total_input_tokens = sum(r.input_tokens for r in results)
        total_output_tokens = sum(r.output_tokens for r in results)
        total_tokens = total_input_tokens + total_output_tokens

        summary = f"""## 📊 요약 통계

| 항목 | 값 |
|------|-----|
| 분석 파일 수 | {len(results)}개 |
| 총 Input Tokens | {total_input_tokens:,} |
| 총 Output Tokens | {total_output_tokens:,} |
| 총 Tokens | {total_tokens:,} |
| 총 비용 (USD) | ${cost_usd:.6f} |
| 총 비용 (KRW) | ₩{cost_krw:.2f} |
| 파일당 평균 비용 (USD) | ${cost_usd / len(results):.6f} |

---
"""
        return summary

    def _generate_file_reviews(
        self, results: List[FileAnalysisResult], language: Language
    ) -> str:
        """파일별 리뷰 결과 생성"""
        section = "## 📁 파일별 리뷰 결과\n\n"

        for idx, result in enumerate(results, 1):
            file_name = Path(result.file_path).name

            section += f"""### {idx}. {file_name}

**파일 경로**: `{result.file_path}`  
**Input Tokens**: {result.input_tokens:,} | **Output Tokens**: {result.output_tokens:,}

#### 코드

```{language.value}
{result.code}
```

#### 리뷰 결과

{result.review_result}

---

"""

        return section

    def _generate_overall_summary(self, results: List[FileAnalysisResult]) -> str:
        """전체 분석 요약 생성"""
        summary = f"""## 🔍 전체 분석 요약

총 **{len(results)}개의 파일**을 분석했습니다.

### 주요 개선 사항

위의 각 파일별 리뷰 결과를 참고하여 코드 품질을 개선하시기 바랍니다.

### 다음 단계

1. 각 파일의 리뷰 결과를 확인합니다
2. 우선순위가 높은 개선 사항부터 적용합니다
3. 코드 수정 후 재검토를 진행합니다

---
"""
        return summary

    def _generate_footer(self, timestamp: datetime) -> str:
        """푸터 생성"""
        footer = f"""---

*Integrated Report generated by Code Review Assistant*  
*{timestamp.strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return footer

    def save_integrated_report(
        self, report: str, filename: Optional[str] = None, language: Optional[Language] = None
    ) -> Path:
        """통합 리포트 저장

        Args:
            report: 마크다운 리포트
            filename: 파일명 (옵션)
            language: 언어 (파일명에 포함)

        Returns:
            저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lang_prefix = language.value if language else "unknown"
            filename = f"{lang_prefix}_integrated_{timestamp}.md"

        if not filename.endswith(".md"):
            filename += ".md"

        file_path = self.reports_dir / filename
        file_path.write_text(report, encoding="utf-8")

        logger.info(f"Integrated report saved to: {file_path}")

        return file_path


# 모듈 레벨 export
__all__ = ["IntegratedReportGenerator", "FileAnalysisResult"]
