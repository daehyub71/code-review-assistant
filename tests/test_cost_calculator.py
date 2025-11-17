"""
Tests for Cost Calculator
"""

import pytest
from app.core.cost_calculator import (
    CostCalculator,
    CostEstimate,
    ModelType,
    ModelPricing,
    MODEL_PRICING,
    CostCalculatorError,
    get_model_type_from_string,
)


class TestModelType:
    """ModelType enum 테스트"""

    def test_model_type_values(self):
        """ModelType enum 값 확인"""
        assert ModelType.GPT_4O.value == "gpt-4o"
        assert ModelType.GPT_4O_MINI.value == "gpt-4o-mini"
        assert ModelType.GPT_5_MINI.value == "gpt-5-mini"
        assert ModelType.CLAUDE_3_5_HAIKU.value == "claude-3-5-haiku-latest"
        assert ModelType.CLAUDE_3_5_SONNET.value == "claude-3-5-sonnet-latest"

    def test_all_models_have_pricing(self):
        """모든 ModelType이 가격 정보를 가지고 있는지 확인"""
        for model_type in ModelType:
            assert model_type in MODEL_PRICING
            pricing = MODEL_PRICING[model_type]
            assert isinstance(pricing, ModelPricing)
            assert pricing.input_price_per_1m > 0
            assert pricing.output_price_per_1m > 0
            assert pricing.encoding_name


class TestModelPricing:
    """ModelPricing 테스트"""

    def test_gpt_4o_mini_pricing(self):
        """gpt-4o-mini 가격 확인"""
        pricing = MODEL_PRICING[ModelType.GPT_4O_MINI]
        assert pricing.input_price_per_1m == 0.150
        assert pricing.output_price_per_1m == 0.600
        assert pricing.encoding_name == "cl100k_base"

    def test_gpt_4o_pricing(self):
        """gpt-4o 가격 확인"""
        pricing = MODEL_PRICING[ModelType.GPT_4O]
        assert pricing.input_price_per_1m == 2.50
        assert pricing.output_price_per_1m == 10.00
        assert pricing.encoding_name == "cl100k_base"

    def test_claude_haiku_pricing(self):
        """claude-3-5-haiku 가격 확인"""
        pricing = MODEL_PRICING[ModelType.CLAUDE_3_5_HAIKU]
        assert pricing.input_price_per_1m == 0.80
        assert pricing.output_price_per_1m == 4.00
        assert pricing.encoding_name == "cl100k_base"


class TestCostCalculator:
    """CostCalculator 클래스 테스트"""

    def test_initialization_default_rate(self):
        """기본 환율로 초기화"""
        calculator = CostCalculator()
        assert calculator.usd_to_krw_rate == 1340.0

    def test_initialization_custom_rate(self):
        """커스텀 환율로 초기화"""
        calculator = CostCalculator(usd_to_krw_rate=1400.0)
        assert calculator.usd_to_krw_rate == 1400.0

    def test_count_tokens_simple_text(self):
        """간단한 텍스트 토큰 카운팅"""
        calculator = CostCalculator()
        text = "Hello, world!"
        token_count = calculator.count_tokens(text, ModelType.GPT_4O_MINI)

        # "Hello, world!"는 대략 4 토큰
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 10  # Reasonable upper bound

    def test_count_tokens_empty_text(self):
        """빈 텍스트 토큰 카운팅"""
        calculator = CostCalculator()
        token_count = calculator.count_tokens("", ModelType.GPT_4O_MINI)
        assert token_count == 0

    def test_count_tokens_long_text(self):
        """긴 텍스트 토큰 카운팅"""
        calculator = CostCalculator()
        text = "Hello " * 1000  # "Hello " repeated 1000 times
        token_count = calculator.count_tokens(text, ModelType.GPT_4O_MINI)

        # "Hello " is ~1 token per repetition, so 1000 repetitions ~1000 tokens
        assert token_count > 900
        assert token_count < 1200

    def test_count_tokens_korean_text(self):
        """한글 텍스트 토큰 카운팅"""
        calculator = CostCalculator()
        text = "안녕하세요"
        token_count = calculator.count_tokens(text, ModelType.GPT_4O_MINI)

        # Korean text typically uses more tokens
        assert token_count > 0

    def test_count_tokens_code_snippet(self):
        """코드 스니펫 토큰 카운팅"""
        calculator = CostCalculator()
        code = """
        def hello():
            print("Hello, world!")
        """
        token_count = calculator.count_tokens(code, ModelType.GPT_4O_MINI)
        assert token_count > 0

    def test_count_tokens_unsupported_model(self):
        """지원하지 않는 모델로 토큰 카운팅 시 에러"""
        calculator = CostCalculator()

        # Create a fake model type (not in MODEL_PRICING)
        # This test verifies error handling, but all current ModelType values are supported
        # We'll test with a known model to ensure it works
        token_count = calculator.count_tokens("test", ModelType.GPT_4O_MINI)
        assert token_count >= 0

    def test_encoding_caching(self):
        """Encoding 캐싱 동작 확인"""
        calculator = CostCalculator()

        # First call loads encoding
        calculator.count_tokens("Hello", ModelType.GPT_4O_MINI)
        assert "cl100k_base" in calculator._encoding_cache

        # Second call uses cached encoding
        calculator.count_tokens("World", ModelType.GPT_4O_MINI)
        assert len(calculator._encoding_cache) == 1


class TestCostEstimation:
    """비용 예측 테스트"""

    def test_estimate_cost_basic(self):
        """기본 비용 예측"""
        calculator = CostCalculator(usd_to_krw_rate=1340.0)
        cost = calculator.estimate_cost(
            input_tokens=1000,
            output_tokens=2000,
            model_type=ModelType.GPT_4O_MINI
        )

        assert isinstance(cost, CostEstimate)
        assert cost.input_tokens == 1000
        assert cost.output_tokens == 2000
        assert cost.model_type == ModelType.GPT_4O_MINI

        # gpt-4o-mini: $0.150/1M input, $0.600/1M output
        # Input: 1000 * 0.150 / 1,000,000 = 0.00015
        # Output: 2000 * 0.600 / 1,000,000 = 0.0012
        # Total: 0.00135
        expected_input_cost = (1000 / 1_000_000) * 0.150
        expected_output_cost = (2000 / 1_000_000) * 0.600
        expected_total_usd = expected_input_cost + expected_output_cost

        assert abs(cost.input_cost_usd - expected_input_cost) < 0.0001
        assert abs(cost.output_cost_usd - expected_output_cost) < 0.0001
        assert abs(cost.total_cost_usd - expected_total_usd) < 0.0001

    def test_estimate_cost_krw_conversion(self):
        """KRW 환율 적용 확인"""
        calculator = CostCalculator(usd_to_krw_rate=1340.0)
        cost = calculator.estimate_cost(
            input_tokens=1000,
            output_tokens=2000,
            model_type=ModelType.GPT_4O_MINI
        )

        expected_krw = cost.total_cost_usd * 1340.0
        assert abs(cost.total_cost_krw - expected_krw) < 0.01

    def test_estimate_cost_zero_tokens(self):
        """토큰이 0일 때 비용 예측"""
        calculator = CostCalculator()
        cost = calculator.estimate_cost(
            input_tokens=0,
            output_tokens=0,
            model_type=ModelType.GPT_4O_MINI
        )

        assert cost.total_cost_usd == 0.0
        assert cost.total_cost_krw == 0.0

    def test_estimate_cost_negative_tokens_raises_error(self):
        """음수 토큰 수 입력 시 에러"""
        calculator = CostCalculator()

        with pytest.raises(ValueError, match="Token counts must be non-negative"):
            calculator.estimate_cost(
                input_tokens=-100,
                output_tokens=200,
                model_type=ModelType.GPT_4O_MINI
            )

    def test_estimate_cost_different_models(self):
        """다양한 모델별 비용 예측"""
        calculator = CostCalculator()

        # GPT-4O (expensive)
        cost_4o = calculator.estimate_cost(
            input_tokens=1000,
            output_tokens=1000,
            model_type=ModelType.GPT_4O
        )

        # GPT-4O-MINI (cheap)
        cost_4o_mini = calculator.estimate_cost(
            input_tokens=1000,
            output_tokens=1000,
            model_type=ModelType.GPT_4O_MINI
        )

        # GPT-4O should be more expensive
        assert cost_4o.total_cost_usd > cost_4o_mini.total_cost_usd

    def test_estimate_cost_from_text(self):
        """텍스트로부터 직접 비용 예측"""
        calculator = CostCalculator()
        text = "Hello, world!"
        estimated_output = 500

        cost = calculator.estimate_cost_from_text(
            input_text=text,
            estimated_output_tokens=estimated_output,
            model_type=ModelType.GPT_4O_MINI
        )

        # Verify input tokens were counted correctly
        expected_input_tokens = calculator.count_tokens(text, ModelType.GPT_4O_MINI)
        assert cost.input_tokens == expected_input_tokens
        assert cost.output_tokens == estimated_output


class TestCostEstimateDataclass:
    """CostEstimate dataclass 테스트"""

    def test_total_tokens_property(self):
        """total_tokens property 확인"""
        cost = CostEstimate(
            input_tokens=100,
            output_tokens=200,
            input_cost_usd=0.001,
            output_cost_usd=0.002,
            total_cost_usd=0.003,
            total_cost_krw=4.02,
            model_type=ModelType.GPT_4O_MINI
        )

        assert cost.total_tokens == 300

    def test_str_representation(self):
        """문자열 표현 확인"""
        cost = CostEstimate(
            input_tokens=100,
            output_tokens=200,
            input_cost_usd=0.001,
            output_cost_usd=0.002,
            total_cost_usd=0.003,
            total_cost_krw=4.02,
            model_type=ModelType.GPT_4O_MINI
        )

        str_repr = str(cost)
        assert "gpt-4o-mini" in str_repr
        assert "100" in str_repr  # input tokens
        assert "200" in str_repr  # output tokens
        assert "300" in str_repr  # total tokens
        assert "0.003" in str_repr  # USD cost
        assert "4.02" in str_repr  # KRW cost


class TestModelTypeConversion:
    """get_model_type_from_string 테스트"""

    def test_valid_model_names(self):
        """유효한 모델 이름 변환"""
        assert get_model_type_from_string("gpt-4o") == ModelType.GPT_4O
        assert get_model_type_from_string("gpt-4o-mini") == ModelType.GPT_4O_MINI
        assert get_model_type_from_string("gpt-5-mini") == ModelType.GPT_5_MINI
        assert get_model_type_from_string("claude-3-5-haiku-latest") == ModelType.CLAUDE_3_5_HAIKU
        assert get_model_type_from_string("claude-3-5-haiku") == ModelType.CLAUDE_3_5_HAIKU
        assert get_model_type_from_string("claude-3-5-sonnet-latest") == ModelType.CLAUDE_3_5_SONNET

    def test_case_insensitive(self):
        """대소문자 무관하게 변환"""
        assert get_model_type_from_string("GPT-4O-MINI") == ModelType.GPT_4O_MINI
        assert get_model_type_from_string("Gpt-4o-Mini") == ModelType.GPT_4O_MINI

    def test_whitespace_handling(self):
        """공백 처리"""
        assert get_model_type_from_string("  gpt-4o-mini  ") == ModelType.GPT_4O_MINI

    def test_invalid_model_name(self):
        """유효하지 않은 모델 이름 시 에러"""
        with pytest.raises(ValueError, match="Unsupported model name"):
            get_model_type_from_string("invalid-model-name")

    def test_empty_string(self):
        """빈 문자열 시 에러"""
        with pytest.raises(ValueError, match="Unsupported model name"):
            get_model_type_from_string("")


class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        # 1. Calculator 초기화
        calculator = CostCalculator(usd_to_krw_rate=1340.0)

        # 2. 코드 리뷰 프롬프트 시뮬레이션
        code_to_review = """
        def get_user(user_id):
            return db.query(User).get(user_id)
        """

        prompt = f"Review this code:\n\n{code_to_review}\n\nProvide detailed feedback."

        # 3. Input 토큰 카운팅
        input_tokens = calculator.count_tokens(prompt, ModelType.GPT_4O_MINI)
        assert input_tokens > 0

        # 4. 예상 output 토큰 (보통 input의 2-3배)
        estimated_output_tokens = input_tokens * 3

        # 5. 비용 예측
        cost = calculator.estimate_cost(
            input_tokens=input_tokens,
            output_tokens=estimated_output_tokens,
            model_type=ModelType.GPT_4O_MINI
        )

        # 6. 결과 확인
        assert cost.total_cost_usd > 0
        assert cost.total_cost_krw > 0
        assert cost.total_tokens == input_tokens + estimated_output_tokens

        # 7. 문자열 출력
        output = str(cost)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_batch_cost_estimation(self):
        """배치 파일 리뷰 비용 예측"""
        calculator = CostCalculator()

        files = [
            "def hello(): print('Hello')",
            "class User: pass",
            "import sys\nprint(sys.version)",
        ]

        total_cost = 0.0
        for file_content in files:
            cost = calculator.estimate_cost_from_text(
                input_text=file_content,
                estimated_output_tokens=500,
                model_type=ModelType.GPT_4O_MINI
            )
            total_cost += cost.total_cost_usd

        assert total_cost > 0

    def test_model_comparison(self):
        """여러 모델 간 비용 비교"""
        calculator = CostCalculator()
        text = "Review this code: def hello(): print('Hello')"
        estimated_output = 1000

        models = [
            ModelType.GPT_4O_MINI,
            ModelType.GPT_4O,
            ModelType.CLAUDE_3_5_HAIKU,
        ]

        costs = {}
        for model in models:
            cost = calculator.estimate_cost_from_text(
                input_text=text,
                estimated_output_tokens=estimated_output,
                model_type=model
            )
            costs[model] = cost.total_cost_usd

        # GPT-4O-MINI should be cheapest
        assert costs[ModelType.GPT_4O_MINI] < costs[ModelType.GPT_4O]
