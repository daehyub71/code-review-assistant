"""
Batch Analyzer - 배치 분석기

여러 파일을 순차적으로 분석하여 통합 리포트를 생성합니다.
QThread 기반 비동기 처리로 UI 블로킹을 방지합니다.
"""

from PySide6.QtCore import QThread, Signal
from pathlib import Path
from typing import List, Optional
import logging
from dataclasses import dataclass

from app.models.language import Language
from app.models.review_category import ReviewCategory
from app.core.api_client import APIClient, AnalysisRequest, AnalysisResponse
from app.core.prompt_builder import PromptBuilder
from app.core.integrated_report_generator import IntegratedReportGenerator, FileAnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class BatchAnalysisProgress:
    """배치 분석 진행 상황

    Attributes:
        current_file: 현재 분석 중인 파일명
        current_index: 현재 파일 인덱스 (0-based)
        total_files: 전체 파일 개수
        progress_percent: 진행률 (0-100)
    """
    current_file: str
    current_index: int
    total_files: int
    progress_percent: float


@dataclass
class BatchAnalysisResult:
    """배치 분석 결과

    Attributes:
        file_results: 파일별 분석 결과 리스트
        integrated_report_path: 통합 리포트 저장 경로
        total_input_tokens: 총 입력 토큰 수
        total_output_tokens: 총 출력 토큰 수
        total_cost_usd: 총 비용 (USD)
        total_cost_krw: 총 비용 (KRW)
    """
    file_results: List[FileAnalysisResult]
    integrated_report_path: Optional[Path]
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_cost_krw: float


class BatchAnalyzerWorker(QThread):
    """배치 분석 워커 스레드

    여러 파일을 순차적으로 분석하여 통합 리포트를 생성합니다.

    Signals:
        progress_updated: 진행 상황 업데이트 (BatchAnalysisProgress)
        file_completed: 파일 분석 완료 (file_path: str, result: str)
        finished_success: 전체 분석 완료 (BatchAnalysisResult)
        finished_error: 오류 발생 (error_message: str)

    Examples:
        >>> worker = BatchAnalyzerWorker(
        ...     file_paths=["/path/to/file1.py", "/path/to/file2.py"],
        ...     language=Language.PYTHON,
        ...     categories=[ReviewCategory.NULL_SAFETY],
        ...     provider="openai"
        ... )
        >>> worker.progress_updated.connect(on_progress)
        >>> worker.file_completed.connect(on_file_done)
        >>> worker.finished_success.connect(on_success)
        >>> worker.start()
    """

    # Signals
    progress_updated = Signal(BatchAnalysisProgress)
    file_completed = Signal(str, str)  # file_path, result
    finished_success = Signal(BatchAnalysisResult)
    finished_error = Signal(str)

    def __init__(
        self,
        file_paths: List[str],
        language: Language,
        categories: List[ReviewCategory],
        provider: str = "openai",
        model: Optional[str] = None,
        parent=None
    ):
        """초기화

        Args:
            file_paths: 분석할 파일 경로 리스트
            language: 프로그래밍 언어
            categories: 검토 카테고리 리스트
            provider: LLM 제공자 ("openai" or "anthropic")
            model: 모델 이름 (옵션)
            parent: 부모 QObject
        """
        super().__init__(parent)
        self.file_paths = file_paths
        self.language = language
        self.categories = categories
        self.provider = provider
        self.model = model

        self.api_client = APIClient()
        self.prompt_builder = PromptBuilder()
        self.report_generator = IntegratedReportGenerator()

        self._is_cancelled = False

        logger.info(f"BatchAnalyzerWorker created for {len(file_paths)} files")

    def cancel(self):
        """분석 취소"""
        self._is_cancelled = True
        logger.info("Batch analysis cancelled")

    def run(self):
        """워커 실행 (QThread 메인 루프)"""
        try:
            file_results: List[FileAnalysisResult] = []
            total_input_tokens = 0
            total_output_tokens = 0
            total_cost_usd = 0.0
            total_cost_krw = 0.0

            total_files = len(self.file_paths)

            # 시스템 프롬프트 생성 (모든 파일에 공통으로 사용)
            prompt = self.prompt_builder.build_system_prompt(
                language=self.language,
                categories=self.categories
            )

            for index, file_path in enumerate(self.file_paths):
                if self._is_cancelled:
                    logger.info("Batch analysis stopped by user")
                    return

                # 진행 상황 업데이트
                progress = BatchAnalysisProgress(
                    current_file=Path(file_path).name,
                    current_index=index,
                    total_files=total_files,
                    progress_percent=(index / total_files) * 100
                )
                self.progress_updated.emit(progress)

                logger.info(f"Analyzing file {index + 1}/{total_files}: {file_path}")

                try:
                    # 파일 읽기
                    code = Path(file_path).read_text(encoding='utf-8')

                    # API 분석 요청
                    request = AnalysisRequest(
                        code=code,
                        language=self.language,
                        prompt=prompt,
                        provider=self.provider,
                        model=self.model
                    )

                    # 동기 분석 (배치 처리는 순차 실행)
                    from app.core.api_client import AnalysisWorker
                    worker = AnalysisWorker(request)

                    response: Optional[AnalysisResponse] = None
                    error_message: Optional[str] = None

                    def on_success(resp: AnalysisResponse):
                        nonlocal response
                        response = resp

                    def on_error(msg: str):
                        nonlocal error_message
                        error_message = msg

                    worker.finished_success.connect(on_success)
                    worker.finished_error.connect(on_error)

                    # 동기 실행
                    worker.run()

                    if error_message:
                        raise RuntimeError(error_message)

                    if not response:
                        raise RuntimeError("No response from API")

                    # 결과 저장
                    file_result = FileAnalysisResult(
                        file_path=file_path,
                        code=code,
                        review_result=response.content,
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens
                    )
                    file_results.append(file_result)

                    # 토큰 및 비용 누적
                    total_input_tokens += response.input_tokens
                    total_output_tokens += response.output_tokens

                    # 비용 계산 (개별 파일 - 나중에 CostCalculator 사용)
                    from app.core.cost_calculator import CostCalculator, ModelType
                    calculator = CostCalculator()
                    model_type = ModelType.from_string(response.model)
                    cost_estimate = calculator.estimate_cost(
                        input_tokens=response.input_tokens,
                        output_tokens=response.output_tokens,
                        model_type=model_type
                    )
                    total_cost_usd += cost_estimate.total_cost_usd
                    total_cost_krw += cost_estimate.total_cost_krw

                    # 파일 완료 시그널
                    self.file_completed.emit(file_path, response.content)

                    logger.info(
                        f"File analysis completed: {file_path} "
                        f"({response.input_tokens} input, {response.output_tokens} output tokens)"
                    )

                except Exception as e:
                    error_msg = f"Failed to analyze {file_path}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    # 오류 발생 시 해당 파일만 스킵 (나머지 진행)
                    file_results.append(FileAnalysisResult(
                        file_path=file_path,
                        code="",
                        review_result=f"# Error\n\n{error_msg}",
                        input_tokens=0,
                        output_tokens=0
                    ))

            # 100% 완료 시그널
            final_progress = BatchAnalysisProgress(
                current_file="완료",
                current_index=total_files,
                total_files=total_files,
                progress_percent=100.0
            )
            self.progress_updated.emit(final_progress)

            # 통합 리포트 생성
            integrated_report_path = None
            if file_results:
                try:
                    integrated_report = self.report_generator.generate_integrated_report(
                        language=self.language,
                        file_results=file_results,
                        categories=self.categories,
                        model=self.model or "unknown"
                    )
                    integrated_report_path = self.report_generator.save_integrated_report(
                        report=integrated_report,
                        language=self.language
                    )
                    logger.info(f"Integrated report saved: {integrated_report_path}")
                except Exception as e:
                    logger.error(f"Failed to save integrated report: {e}", exc_info=True)

            # 최종 결과
            result = BatchAnalysisResult(
                file_results=file_results,
                integrated_report_path=integrated_report_path,
                total_input_tokens=total_input_tokens,
                total_output_tokens=total_output_tokens,
                total_cost_usd=total_cost_usd,
                total_cost_krw=total_cost_krw
            )

            self.finished_success.emit(result)
            logger.info(
                f"Batch analysis completed: {len(file_results)} files, "
                f"{total_input_tokens} input tokens, "
                f"{total_output_tokens} output tokens, "
                f"${total_cost_usd:.6f}"
            )

        except Exception as e:
            error_msg = f"Batch analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.finished_error.emit(error_msg)


class BatchAnalyzer:
    """배치 분석기

    여러 파일을 순차적으로 분석하여 통합 리포트를 생성합니다.

    Examples:
        >>> analyzer = BatchAnalyzer()
        >>> worker = analyzer.analyze_folder_async(
        ...     file_paths=["/path/to/file1.py", "/path/to/file2.py"],
        ...     language=Language.PYTHON,
        ...     categories=[ReviewCategory.NULL_SAFETY]
        ... )
        >>> worker.progress_updated.connect(on_progress)
        >>> worker.finished_success.connect(on_success)
        >>> worker.start()
    """

    def __init__(self):
        """초기화"""
        logger.info("BatchAnalyzer initialized")

    def analyze_folder_async(
        self,
        file_paths: List[str],
        language: Language,
        categories: List[ReviewCategory],
        provider: str = "openai",
        model: Optional[str] = None
    ) -> BatchAnalyzerWorker:
        """비동기 배치 파일 분석

        Args:
            file_paths: 분석할 파일 경로 리스트
            language: 프로그래밍 언어
            categories: 검토 카테고리 리스트
            provider: LLM 제공자
            model: 모델 이름 (옵션)

        Returns:
            BatchAnalyzerWorker 인스턴스 (start() 호출 필요)

        Examples:
            >>> analyzer = BatchAnalyzer()
            >>> worker = analyzer.analyze_folder_async(
            ...     file_paths=["/path/file1.py", "/path/file2.py"],
            ...     language=Language.PYTHON,
            ...     categories=[ReviewCategory.NULL_SAFETY],
            ...     provider="openai"
            ... )
            >>> worker.progress_updated.connect(lambda p: print(f"{p.progress_percent}%"))
            >>> worker.start()
        """
        worker = BatchAnalyzerWorker(
            file_paths=file_paths,
            language=language,
            categories=categories,
            provider=provider,
            model=model
        )
        logger.debug(f"Created batch worker for {len(file_paths)} files")
        return worker


# 모듈 레벨 export
__all__ = [
    "BatchAnalyzer",
    "BatchAnalyzerWorker",
    "BatchAnalysisProgress",
    "BatchAnalysisResult",
]
