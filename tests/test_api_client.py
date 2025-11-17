"""
Tests for API Client - LLM API 클라이언트 테스트
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QThread

from app.config import Settings, get_settings
from app.core.api_client import (
    APIClient,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisWorker,
)
from app.models.language import Language


class TestSettings:
    """Settings 클래스 테스트"""

    def test_init_with_env_file(self, tmp_path):
        """환경 변수 파일에서 설정 로딩"""
        # .env 파일 생성
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OPENAI_API_KEY=sk-test123\n"
            "OPENAI_MODEL=gpt-4o-mini\n"
            "USD_TO_KRW_RATE=1350\n"
        )

        # 환경 변수 격리 (기존 .env 영향 제거)
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(env_file=env_file)

            assert settings.openai_api_key == "sk-test123"
            assert settings.openai_model == "gpt-4o-mini"
            assert settings.usd_to_krw_rate == 1350.0

    def test_init_without_env_file(self):
        """환경 변수 없이 초기화 - 기본값 사용"""
        # 임시로 환경 변수 설정
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-test", "USD_TO_KRW_RATE": "1340"},
            clear=True,
        ):
            settings = Settings(env_file=Path("/nonexistent/.env"))

            assert settings.openai_api_key == "sk-test"
            assert settings.openai_model == "gpt-4o-mini"  # 기본값

    def test_validation_no_api_keys(self):
        """API 키 없이 초기화 - 에러"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="At least one API key required"):
                Settings(env_file=Path("/nonexistent/.env"))

    def test_validation_invalid_usd_rate(self):
        """잘못된 환율 - 에러"""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-test", "USD_TO_KRW_RATE": "-100"},
            clear=True,
        ):
            with pytest.raises(ValueError, match="Invalid USD_TO_KRW_RATE"):
                Settings(env_file=Path("/nonexistent/.env"))

    def test_has_openai_key(self):
        """OpenAI 키 존재 여부 확인"""
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True
        ):
            settings = Settings(env_file=Path("/nonexistent/.env"))
            assert settings.has_openai_key() is True

    def test_has_anthropic_key(self):
        """Anthropic 키 존재 여부 확인"""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-test1", "ANTHROPIC_API_KEY": "sk-ant-test"},
            clear=True,
        ):
            settings = Settings(env_file=Path("/nonexistent/.env"))
            assert settings.has_anthropic_key() is True

    def test_get_available_providers(self):
        """사용 가능한 제공자 목록"""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "sk-test1", "ANTHROPIC_API_KEY": "sk-ant-test"},
            clear=True,
        ):
            settings = Settings(env_file=Path("/nonexistent/.env"))
            providers = settings.get_available_providers()

            assert "openai" in providers
            assert "anthropic" in providers

    def test_repr_masks_api_keys(self):
        """API 키 마스킹 확인"""
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "sk-secretkey123"}, clear=True
        ):
            settings = Settings(env_file=Path("/nonexistent/.env"))
            repr_str = repr(settings)

            assert "sk-secretkey123" not in repr_str
            assert "***" in repr_str


class TestAnalysisRequest:
    """AnalysisRequest 데이터클래스 테스트"""

    def test_create_request(self):
        """분석 요청 생성"""
        request = AnalysisRequest(
            code="print('hello')",
            language=Language.PYTHON,
            prompt="Review this code",
            provider="openai",
        )

        assert request.code == "print('hello')"
        assert request.language == Language.PYTHON
        assert request.provider == "openai"

    def test_default_provider(self):
        """기본 제공자는 openai"""
        request = AnalysisRequest(
            code="test", language=Language.PYTHON, prompt="test"
        )

        assert request.provider == "openai"


class TestAPIClient:
    """APIClient 클래스 테스트"""

    @pytest.fixture
    def mock_settings(self):
        """Mock Settings 픽스처"""
        with patch("app.core.api_client.get_settings") as mock:
            settings = Mock()
            settings.openai_api_key = "sk-test"
            settings.openai_model = "gpt-4o-mini"
            settings.anthropic_api_key = "sk-ant-test"
            settings.anthropic_model = "claude-3-5-haiku-latest"
            settings.has_openai_key.return_value = True
            settings.has_anthropic_key.return_value = True
            settings.get_available_providers.return_value = ["openai", "anthropic"]
            mock.return_value = settings
            yield settings

    def test_init(self, mock_settings):
        """APIClient 초기화"""
        client = APIClient()
        assert client.settings == mock_settings

    def test_analyze_async_returns_worker(self, mock_settings):
        """비동기 분석은 AnalysisWorker 반환"""
        client = APIClient()
        request = AnalysisRequest(
            code="test", language=Language.PYTHON, prompt="test"
        )

        worker = client.analyze_async(request)

        assert isinstance(worker, AnalysisWorker)
        assert worker.request == request

    def test_get_available_providers(self, mock_settings):
        """사용 가능한 제공자 목록"""
        client = APIClient()
        providers = client.get_available_providers()

        assert providers == ["openai", "anthropic"]

    def test_validate_provider_valid(self, mock_settings):
        """유효한 제공자 검증"""
        client = APIClient()

        assert client.validate_provider("openai") is True
        assert client.validate_provider("anthropic") is True

    def test_validate_provider_invalid(self, mock_settings):
        """유효하지 않은 제공자 검증"""
        client = APIClient()

        assert client.validate_provider("invalid") is False


class TestAnalysisWorker:
    """AnalysisWorker 스레드 테스트"""

    @pytest.fixture
    def mock_settings(self):
        """Mock Settings 픽스처"""
        with patch("app.core.api_client.get_settings") as mock:
            settings = Mock()
            settings.openai_api_key = "sk-test"
            settings.openai_model = "gpt-4o-mini"
            settings.has_openai_key.return_value = True
            mock.return_value = settings
            yield settings

    def test_worker_initialization(self, mock_settings):
        """워커 초기화"""
        request = AnalysisRequest(
            code="test", language=Language.PYTHON, prompt="test", provider="openai"
        )

        worker = AnalysisWorker(request)

        assert worker.request == request
        assert isinstance(worker, QThread)

    @patch("app.core.api_client.OpenAI")
    def test_openai_analysis_success(self, mock_openai_class, mock_settings, qtbot):
        """OpenAI 분석 성공"""
        # Mock OpenAI 클라이언트
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock 스트리밍 응답
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock(delta=Mock(content="Hello "))]
        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock(delta=Mock(content="World"))]
        mock_chunk2.usage = Mock(prompt_tokens=10, completion_tokens=5)

        mock_client.chat.completions.create.return_value = iter(
            [mock_chunk1, mock_chunk2]
        )

        # 워커 생성 및 실행
        request = AnalysisRequest(
            code="test", language=Language.PYTHON, prompt="test", provider="openai"
        )
        worker = AnalysisWorker(request)

        # Signal 연결
        chunks = []
        worker.chunk_received.connect(lambda chunk: chunks.append(chunk))

        # 동기 실행 (테스트용)
        worker.run()

        # 검증
        assert chunks == ["Hello ", "World"]

    @patch("app.core.api_client.Anthropic")
    def test_anthropic_analysis_success(
        self, mock_anthropic_class, mock_settings, qtbot
    ):
        """Anthropic 분석 성공"""
        # Mock Anthropic 클라이언트
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Mock 스트리밍 컨텍스트
        mock_stream = MagicMock()
        mock_stream.__enter__.return_value = mock_stream
        mock_stream.__exit__.return_value = None
        mock_stream.text_stream = ["Hello ", "Anthropic"]
        mock_stream.get_final_message.return_value = Mock(
            usage=Mock(input_tokens=10, output_tokens=5)
        )

        mock_client.messages.stream.return_value = mock_stream

        # Anthropic 키 설정
        mock_settings.has_anthropic_key.return_value = True
        mock_settings.anthropic_api_key = "sk-ant-test"
        mock_settings.anthropic_model = "claude-3-5-haiku-latest"

        # 워커 생성 및 실행
        request = AnalysisRequest(
            code="test",
            language=Language.PYTHON,
            prompt="test",
            provider="anthropic",
        )
        worker = AnalysisWorker(request)

        # Signal 연결
        chunks = []
        worker.chunk_received.connect(lambda chunk: chunks.append(chunk))

        # 동기 실행
        worker.run()

        # 검증
        assert chunks == ["Hello ", "Anthropic"]

    def test_invalid_provider_error(self, mock_settings, qtbot):
        """잘못된 제공자 - 에러"""
        request = AnalysisRequest(
            code="test", language=Language.PYTHON, prompt="test", provider="invalid"
        )
        worker = AnalysisWorker(request)

        # Signal 연결
        errors = []
        worker.finished_error.connect(lambda error: errors.append(error))

        # 실행
        worker.run()

        # 에러 메시지 확인
        assert len(errors) == 1
        assert "Unknown provider" in errors[0]


class TestIntegration:
    """통합 테스트"""

    @pytest.fixture
    def test_env_file(self, tmp_path):
        """테스트용 .env 파일"""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "OPENAI_API_KEY=sk-test-integration\n"
            "OPENAI_MODEL=gpt-4o-mini\n"
            "USD_TO_KRW_RATE=1340\n"
        )
        return env_file

    @patch("app.core.api_client.OpenAI")
    def test_full_workflow(self, mock_openai_class, test_env_file, qtbot):
        """전체 워크플로우 테스트"""
        # Settings 초기화
        with patch("app.config.Settings.__init__", return_value=None):
            with patch("app.core.api_client.get_settings") as mock_get_settings:
                # Mock Settings
                settings = Mock()
                settings.openai_api_key = "sk-test"
                settings.openai_model = "gpt-4o-mini"
                settings.has_openai_key.return_value = True
                settings.get_available_providers.return_value = ["openai"]
                mock_get_settings.return_value = settings

                # Mock OpenAI 응답
                mock_client = Mock()
                mock_openai_class.return_value = mock_client

                mock_chunk = Mock()
                mock_chunk.choices = [Mock(delta=Mock(content="Review result"))]
                mock_chunk.usage = Mock(prompt_tokens=10, completion_tokens=5)
                mock_client.chat.completions.create.return_value = iter([mock_chunk])

                # APIClient 생성
                client = APIClient()

                # 분석 요청
                request = AnalysisRequest(
                    code="def hello(): pass",
                    language=Language.PYTHON,
                    prompt="Review this Python code",
                    provider="openai",
                )

                # 워커 생성
                worker = client.analyze_async(request)

                # Signal 수집
                chunks = []
                worker.chunk_received.connect(lambda chunk: chunks.append(chunk))

                # 실행
                worker.run()

                # 검증
                assert "Review result" in chunks
