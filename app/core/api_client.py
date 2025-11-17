"""
API Client - LLM API 클라이언트

OpenAI 및 Anthropic API를 사용하여 코드 리뷰를 수행합니다.
QThread 기반 비동기 처리로 UI 블로킹을 방지합니다.
"""

from PySide6.QtCore import QThread, Signal
from typing import Optional, Callable
import logging
from dataclasses import dataclass

from openai import OpenAI, APIError as OpenAIAPIError
from anthropic import Anthropic, APIError as AnthropicAPIError

from app.config import get_settings
from app.models.language import Language

logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """코드 분석 요청

    Attributes:
        code: 분석할 코드
        language: 프로그래밍 언어
        prompt: 시스템 프롬프트
        provider: LLM 제공자 ("openai" or "anthropic")
        model: 모델 이름 (옵션, 기본값은 설정에서 가져옴)
    """

    code: str
    language: Language
    prompt: str
    provider: str = "openai"
    model: Optional[str] = None


@dataclass
class AnalysisResponse:
    """코드 분석 응답

    Attributes:
        content: 리뷰 결과 (마크다운)
        input_tokens: 입력 토큰 수
        output_tokens: 출력 토큰 수
        model: 사용된 모델 이름
        provider: LLM 제공자
    """

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str


class AnalysisWorker(QThread):
    """코드 분석 워커 스레드

    별도 스레드에서 LLM API 호출을 수행하여 UI 블로킹을 방지합니다.

    Signals:
        chunk_received: 스트리밍 청크 수신 시 발생 (chunk: str)
        finished_success: 분석 완료 시 발생 (response: AnalysisResponse)
        finished_error: 에러 발생 시 발생 (error_message: str)

    Examples:
        >>> worker = AnalysisWorker(request)
        >>> worker.chunk_received.connect(on_chunk)
        >>> worker.finished_success.connect(on_success)
        >>> worker.finished_error.connect(on_error)
        >>> worker.start()
    """

    # Signals
    chunk_received = Signal(str)  # 스트리밍 청크
    finished_success = Signal(AnalysisResponse)  # 성공
    finished_error = Signal(str)  # 에러

    def __init__(self, request: AnalysisRequest, parent=None):
        """초기화

        Args:
            request: 분석 요청
            parent: 부모 QObject
        """
        super().__init__(parent)
        self.request = request
        self.settings = get_settings()
        logger.info(f"AnalysisWorker created for {request.provider}")

    def run(self):
        """워커 실행 (QThread 메인 루프)"""
        try:
            if self.request.provider == "openai":
                response = self._analyze_with_openai()
            elif self.request.provider == "anthropic":
                response = self._analyze_with_anthropic()
            else:
                raise ValueError(f"Unknown provider: {self.request.provider}")

            self.finished_success.emit(response)
            logger.info("Analysis completed successfully")

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.finished_error.emit(error_msg)

    def _analyze_with_openai(self) -> AnalysisResponse:
        """OpenAI API로 코드 분석

        Returns:
            AnalysisResponse

        Raises:
            OpenAIAPIError: API 호출 실패
        """
        if not self.settings.has_openai_key():
            raise ValueError("OpenAI API key not configured")

        # 클라이언트 초기화
        client = OpenAI(api_key=self.settings.openai_api_key)

        # 모델 결정
        model = self.request.model or self.settings.openai_model

        logger.info(f"Starting OpenAI analysis with model: {model}")

        # 스트리밍 요청
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.request.prompt},
                {
                    "role": "user",
                    "content": f"다음 {self.request.language.value} 코드를 리뷰해주세요:\n\n```{self.request.language.value}\n{self.request.code}\n```",
                },
            ],
            stream=True,
            temperature=0.7,
        )

        # 스트리밍 응답 처리
        full_content = ""
        input_tokens = 0
        output_tokens = 0

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                self.chunk_received.emit(content)

            # 토큰 사용량 (마지막 청크에 포함)
            if hasattr(chunk, "usage") and chunk.usage:
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens

        # 토큰 사용량이 스트림에 없으면 추정 (tiktoken 사용)
        if input_tokens == 0 or output_tokens == 0:
            from app.core.cost_calculator import CostCalculator

            calculator = CostCalculator()
            input_tokens = calculator.count_tokens(
                self.request.prompt + self.request.code, model
            )
            output_tokens = calculator.count_tokens(full_content, model)

        return AnalysisResponse(
            content=full_content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            provider="openai",
        )

    def _analyze_with_anthropic(self) -> AnalysisResponse:
        """Anthropic API로 코드 분석

        Returns:
            AnalysisResponse

        Raises:
            AnthropicAPIError: API 호출 실패
        """
        if not self.settings.has_anthropic_key():
            raise ValueError("Anthropic API key not configured")

        # 클라이언트 초기화
        client = Anthropic(api_key=self.settings.anthropic_api_key)

        # 모델 결정
        model = self.request.model or self.settings.anthropic_model

        logger.info(f"Starting Anthropic analysis with model: {model}")

        # 스트리밍 요청
        full_content = ""
        input_tokens = 0
        output_tokens = 0

        with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=self.request.prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"다음 {self.request.language.value} 코드를 리뷰해주세요:\n\n```{self.request.language.value}\n{self.request.code}\n```",
                }
            ],
            temperature=0.7,
        ) as stream:
            for text in stream.text_stream:
                full_content += text
                self.chunk_received.emit(text)

            # 최종 메시지에서 토큰 사용량 가져오기
            final_message = stream.get_final_message()
            input_tokens = final_message.usage.input_tokens
            output_tokens = final_message.usage.output_tokens

        return AnalysisResponse(
            content=full_content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            provider="anthropic",
        )


class APIClient:
    """LLM API 클라이언트

    OpenAI 및 Anthropic API를 사용하여 코드 리뷰를 수행합니다.
    QThread 기반 비동기 처리를 지원합니다.

    Examples:
        >>> client = APIClient()
        >>> request = AnalysisRequest(
        ...     code="print('hello')",
        ...     language=Language.PYTHON,
        ...     prompt="Review this code",
        ...     provider="openai"
        ... )
        >>> worker = client.analyze_async(request)
        >>> worker.chunk_received.connect(on_chunk)
        >>> worker.finished_success.connect(on_success)
        >>> worker.start()
    """

    def __init__(self):
        """초기화"""
        self.settings = get_settings()
        logger.info("APIClient initialized")

    def analyze_async(self, request: AnalysisRequest) -> AnalysisWorker:
        """비동기 코드 분석 (QThread 사용)

        Args:
            request: 분석 요청

        Returns:
            AnalysisWorker 인스턴스 (start() 호출 필요)

        Examples:
            >>> client = APIClient()
            >>> worker = client.analyze_async(request)
            >>> worker.chunk_received.connect(lambda chunk: print(chunk))
            >>> worker.start()
        """
        worker = AnalysisWorker(request)
        logger.debug(f"Created worker for {request.provider} analysis")
        return worker

    def analyze_sync(self, request: AnalysisRequest) -> AnalysisResponse:
        """동기 코드 분석 (테스트용, UI 스레드 블로킹)

        WARNING: UI에서 직접 호출하면 블로킹됩니다. 테스트 전용입니다.

        Args:
            request: 분석 요청

        Returns:
            AnalysisResponse

        Examples:
            >>> client = APIClient()
            >>> response = client.analyze_sync(request)  # 블로킹!
            >>> print(response.content)
        """
        logger.warning("Synchronous analysis called - will block UI!")

        worker = AnalysisWorker(request)
        worker.run()  # 동기 실행 (start() 대신 run() 직접 호출)

        # 에러 체크
        if hasattr(worker, "_error"):
            raise RuntimeError(worker._error)

        return worker._response

    def get_available_providers(self) -> list[str]:
        """사용 가능한 LLM 제공자 목록

        Returns:
            List of providers: ["openai", "anthropic"]
        """
        return self.settings.get_available_providers()

    def validate_provider(self, provider: str) -> bool:
        """제공자 유효성 검증

        Args:
            provider: "openai" or "anthropic"

        Returns:
            True if provider is available
        """
        return provider in self.get_available_providers()


# 모듈 레벨 export
__all__ = [
    "APIClient",
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisWorker",
]
