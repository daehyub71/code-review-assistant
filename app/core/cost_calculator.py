"""
Cost Calculator - LLM API 비용 계산 및 토큰 카운팅
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple
import tiktoken
import logging

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """지원하는 LLM 모델 타입"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_5_MINI = "gpt-5-mini"  # Future model or alias for gpt-4o-mini
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-latest"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-latest"


@dataclass
class ModelPricing:
    """모델별 가격 정보 (USD per 1M tokens)"""
    input_price_per_1m: float  # Input tokens 가격 (USD)
    output_price_per_1m: float  # Output tokens 가격 (USD)
    encoding_name: str  # tiktoken encoding name


# 모델별 가격 정의 (2024년 기준)
MODEL_PRICING: Dict[ModelType, ModelPricing] = {
    ModelType.GPT_4O: ModelPricing(
        input_price_per_1m=2.50,
        output_price_per_1m=10.00,
        encoding_name="cl100k_base"
    ),
    ModelType.GPT_4O_MINI: ModelPricing(
        input_price_per_1m=0.150,
        output_price_per_1m=0.600,
        encoding_name="cl100k_base"
    ),
    ModelType.GPT_5_MINI: ModelPricing(
        input_price_per_1m=0.150,  # Same as gpt-4o-mini for now
        output_price_per_1m=0.600,
        encoding_name="cl100k_base"
    ),
    ModelType.CLAUDE_3_5_HAIKU: ModelPricing(
        input_price_per_1m=0.80,
        output_price_per_1m=4.00,
        encoding_name="cl100k_base"  # Approximation for Claude
    ),
    ModelType.CLAUDE_3_5_SONNET: ModelPricing(
        input_price_per_1m=3.00,
        output_price_per_1m=15.00,
        encoding_name="cl100k_base"  # Approximation for Claude
    ),
}


class CostCalculatorError(Exception):
    """Cost Calculator 관련 에러"""
    pass


class CostCalculator:
    """LLM API 비용 계산기

    토큰 카운팅, 비용 예측, USD/KRW 환율 적용 기능 제공.

    Examples:
        >>> calculator = CostCalculator(usd_to_krw_rate=1340)
        >>> tokens = calculator.count_tokens("Hello, world!", ModelType.GPT_4O_MINI)
        >>> cost = calculator.estimate_cost(
        ...     input_tokens=100,
        ...     output_tokens=200,
        ...     model_type=ModelType.GPT_4O_MINI
        ... )
        >>> print(f"Cost: ${cost.usd:.4f} (₩{cost.krw:.0f})")
    """

    def __init__(self, usd_to_krw_rate: float = 1340.0):
        """초기화

        Args:
            usd_to_krw_rate: USD to KRW 환율 (기본값: 1340)
        """
        self.usd_to_krw_rate = usd_to_krw_rate
        self._encoding_cache: Dict[str, tiktoken.Encoding] = {}

        logger.info(f"CostCalculator initialized with USD/KRW rate: {usd_to_krw_rate}")

    def _get_encoding(self, encoding_name: str) -> tiktoken.Encoding:
        """tiktoken encoding 객체 가져오기 (캐싱)

        Args:
            encoding_name: Encoding 이름 (e.g., "cl100k_base")

        Returns:
            tiktoken.Encoding 객체
        """
        if encoding_name not in self._encoding_cache:
            self._encoding_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
            logger.debug(f"Loaded encoding: {encoding_name}")

        return self._encoding_cache[encoding_name]

    def count_tokens(self, text: str, model_type: ModelType) -> int:
        """텍스트의 토큰 수 계산

        Args:
            text: 토큰 수를 계산할 텍스트
            model_type: 모델 타입

        Returns:
            토큰 수

        Raises:
            CostCalculatorError: 지원하지 않는 모델 타입

        Examples:
            >>> calculator = CostCalculator()
            >>> tokens = calculator.count_tokens("Hello, world!", ModelType.GPT_4O_MINI)
            >>> print(tokens)
            4
        """
        if model_type not in MODEL_PRICING:
            raise CostCalculatorError(f"Unsupported model type: {model_type}")

        pricing = MODEL_PRICING[model_type]
        encoding = self._get_encoding(pricing.encoding_name)

        tokens = encoding.encode(text)
        token_count = len(tokens)

        logger.debug(f"Token count for {model_type.value}: {token_count}")

        return token_count

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_type: ModelType
    ) -> "CostEstimate":
        """API 호출 비용 예측

        Args:
            input_tokens: Input token 수
            output_tokens: Output token 수 (예상)
            model_type: 모델 타입

        Returns:
            CostEstimate 객체 (USD, KRW 비용 포함)

        Raises:
            CostCalculatorError: 지원하지 않는 모델 타입
            ValueError: 토큰 수가 음수인 경우

        Examples:
            >>> calculator = CostCalculator(usd_to_krw_rate=1340)
            >>> cost = calculator.estimate_cost(
            ...     input_tokens=1000,
            ...     output_tokens=2000,
            ...     model_type=ModelType.GPT_4O_MINI
            ... )
            >>> print(f"${cost.usd:.4f}")
            0.0015
        """
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts must be non-negative")

        if model_type not in MODEL_PRICING:
            raise CostCalculatorError(f"Unsupported model type: {model_type}")

        pricing = MODEL_PRICING[model_type]

        # 비용 계산 (USD)
        input_cost_usd = (input_tokens / 1_000_000) * pricing.input_price_per_1m
        output_cost_usd = (output_tokens / 1_000_000) * pricing.output_price_per_1m
        total_cost_usd = input_cost_usd + output_cost_usd

        # KRW 변환
        total_cost_krw = total_cost_usd * self.usd_to_krw_rate

        logger.info(
            f"Cost estimate for {model_type.value}: "
            f"Input={input_tokens}, Output={output_tokens}, "
            f"Total=${total_cost_usd:.6f} (₩{total_cost_krw:.2f})"
        )

        return CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=input_cost_usd,
            output_cost_usd=output_cost_usd,
            total_cost_usd=total_cost_usd,
            total_cost_krw=total_cost_krw,
            model_type=model_type
        )

    def estimate_cost_from_text(
        self,
        input_text: str,
        estimated_output_tokens: int,
        model_type: ModelType
    ) -> "CostEstimate":
        """텍스트로부터 직접 비용 예측

        Args:
            input_text: Input 텍스트
            estimated_output_tokens: 예상 output token 수
            model_type: 모델 타입

        Returns:
            CostEstimate 객체

        Examples:
            >>> calculator = CostCalculator()
            >>> cost = calculator.estimate_cost_from_text(
            ...     input_text="Analyze this code...",
            ...     estimated_output_tokens=500,
            ...     model_type=ModelType.GPT_4O_MINI
            ... )
        """
        input_tokens = self.count_tokens(input_text, model_type)
        return self.estimate_cost(input_tokens, estimated_output_tokens, model_type)


@dataclass
class CostEstimate:
    """비용 예측 결과

    Attributes:
        input_tokens: Input token 수
        output_tokens: Output token 수
        input_cost_usd: Input 비용 (USD)
        output_cost_usd: Output 비용 (USD)
        total_cost_usd: 총 비용 (USD)
        total_cost_krw: 총 비용 (KRW)
        model_type: 사용된 모델 타입
    """
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    total_cost_krw: float
    model_type: ModelType

    def __str__(self) -> str:
        """사람이 읽기 쉬운 형식으로 출력"""
        return (
            f"Model: {self.model_type.value}\n"
            f"Tokens: {self.input_tokens} input + {self.output_tokens} output = {self.total_tokens} total\n"
            f"Cost: ${self.total_cost_usd:.6f} (₩{self.total_cost_krw:.2f})"
        )

    @property
    def total_tokens(self) -> int:
        """총 토큰 수"""
        return self.input_tokens + self.output_tokens


def get_model_type_from_string(model_name: str) -> ModelType:
    """문자열로부터 ModelType 추출

    Args:
        model_name: 모델 이름 (e.g., "gpt-4o-mini", "claude-3-5-haiku-latest")

    Returns:
        ModelType enum

    Raises:
        ValueError: 지원하지 않는 모델 이름

    Examples:
        >>> model = get_model_type_from_string("gpt-4o-mini")
        >>> print(model)
        ModelType.GPT_4O_MINI
    """
    # Normalize model name
    normalized = model_name.lower().strip()

    # Map string to ModelType
    model_mapping = {
        "gpt-4o": ModelType.GPT_4O,
        "gpt-4o-mini": ModelType.GPT_4O_MINI,
        "gpt-5-mini": ModelType.GPT_5_MINI,
        "claude-3-5-haiku-latest": ModelType.CLAUDE_3_5_HAIKU,
        "claude-3-5-haiku": ModelType.CLAUDE_3_5_HAIKU,
        "claude-3-5-sonnet-latest": ModelType.CLAUDE_3_5_SONNET,
        "claude-3-5-sonnet": ModelType.CLAUDE_3_5_SONNET,
    }

    if normalized in model_mapping:
        return model_mapping[normalized]

    raise ValueError(f"Unsupported model name: {model_name}")
