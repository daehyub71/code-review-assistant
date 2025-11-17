"""
Diagram Converter - Mermaid 다이어그램 변환기

코드 분석 결과를 Mermaid 다이어그램으로 변환합니다.
"""

from typing import List, Optional
import logging

from app.models.language import Language
from app.models.review_category import ReviewCategory

logger = logging.getLogger(__name__)


class DiagramConverter:
    """Mermaid 다이어그램 변환기

    코드 분석 결과를 Mermaid 다이어그램 문법으로 변환합니다.

    Examples:
        >>> converter = DiagramConverter()
        >>> diagram = converter.generate_review_summary_diagram(
        ...     categories=[ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY],
        ...     scores={"null_safety": 8, "security": 6}
        ... )
        >>> print(diagram)
    """

    def generate_review_summary_diagram(
        self,
        categories: List[ReviewCategory],
        scores: Optional[dict] = None,
    ) -> str:
        """리뷰 요약 다이어그램 생성 (파이 차트)

        Args:
            categories: 리뷰 카테고리 리스트
            scores: 카테고리별 점수 (옵션)

        Returns:
            Mermaid 파이 차트 코드

        Examples:
            >>> converter = DiagramConverter()
            >>> diagram = converter.generate_review_summary_diagram(
            ...     categories=[ReviewCategory.NULL_SAFETY],
            ...     scores={"null_safety": 10}
            ... )
        """
        if scores is None:
            # 균등 분포
            scores = {cat.value: 10 for cat in categories}

        diagram = "```mermaid\npie title Review Categories\n"

        for category in categories:
            score = scores.get(category.value, 0)
            diagram += f'    "{category.value}" : {score}\n'

        diagram += "```\n"

        logger.debug(f"Generated pie chart diagram with {len(categories)} categories")

        return diagram

    def generate_file_structure_diagram(
        self, file_paths: List[str], base_dir: Optional[str] = None
    ) -> str:
        """파일 구조 다이어그램 생성 (플로우차트)

        Args:
            file_paths: 파일 경로 리스트
            base_dir: 기준 디렉토리 (상대 경로 표시용)

        Returns:
            Mermaid 플로우차트 코드

        Examples:
            >>> converter = DiagramConverter()
            >>> diagram = converter.generate_file_structure_diagram(
            ...     file_paths=["src/main.py", "src/utils.py"],
            ...     base_dir="src"
            ... )
        """
        diagram = "```mermaid\ngraph TD\n"
        diagram += "    Root[Project]\n"

        for idx, file_path in enumerate(file_paths, 1):
            file_id = f"File{idx}"
            file_name = file_path.split("/")[-1] if "/" in file_path else file_path
            diagram += f"    Root --> {file_id}[{file_name}]\n"

        diagram += "```\n"

        logger.debug(f"Generated file structure diagram with {len(file_paths)} files")

        return diagram

    def generate_analysis_flow_diagram(
        self, language: Language, categories: List[ReviewCategory]
    ) -> str:
        """분석 프로세스 플로우 다이어그램 생성

        Args:
            language: 프로그래밍 언어
            categories: 리뷰 카테고리

        Returns:
            Mermaid 플로우차트 코드

        Examples:
            >>> converter = DiagramConverter()
            >>> diagram = converter.generate_analysis_flow_diagram(
            ...     language=Language.PYTHON,
            ...     categories=[ReviewCategory.NULL_SAFETY]
            ... )
        """
        diagram = "```mermaid\ngraph LR\n"
        diagram += f"    A[Code Input] --> B[Language: {language.value}]\n"
        diagram += "    B --> C[Category Selection]\n"

        for idx, category in enumerate(categories, 1):
            cat_id = f"Cat{idx}"
            diagram += f"    C --> {cat_id}[{category.value}]\n"

        diagram += "    C --> D[LLM Analysis]\n"
        diagram += "    D --> E[Report Generation]\n"

        diagram += "```\n"

        logger.debug(f"Generated analysis flow diagram")

        return diagram

    def generate_cost_breakdown_diagram(
        self, input_tokens: int, output_tokens: int
    ) -> str:
        """비용 분해 다이어그램 생성 (파이 차트)

        Args:
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수

        Returns:
            Mermaid 파이 차트 코드

        Examples:
            >>> converter = DiagramConverter()
            >>> diagram = converter.generate_cost_breakdown_diagram(100, 200)
        """
        diagram = "```mermaid\npie title Token Distribution\n"
        diagram += f'    "Input Tokens" : {input_tokens}\n'
        diagram += f'    "Output Tokens" : {output_tokens}\n'
        diagram += "```\n"

        logger.debug(f"Generated cost breakdown diagram")

        return diagram

    def generate_timeline_diagram(
        self, events: List[tuple[str, str]]
    ) -> str:
        """타임라인 다이어그램 생성

        Args:
            events: (날짜, 이벤트) 튜플 리스트

        Returns:
            Mermaid 타임라인 코드

        Examples:
            >>> converter = DiagramConverter()
            >>> events = [("2024-01-01", "Project Start"), ("2024-01-15", "First Review")]
            >>> diagram = converter.generate_timeline_diagram(events)
        """
        diagram = "```mermaid\ntimeline\n"
        diagram += "    title Analysis History\n"

        for date, event in events:
            diagram += f"    {date} : {event}\n"

        diagram += "```\n"

        logger.debug(f"Generated timeline diagram with {len(events)} events")

        return diagram


# 모듈 레벨 export
__all__ = ["DiagramConverter"]
