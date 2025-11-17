"""
Configuration Management - 설정 관리

.env 파일에서 환경 변수를 로딩하고 애플리케이션 설정을 관리합니다.
"""

import os
import sys
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Settings:
    """애플리케이션 설정 관리 클래스

    .env 파일에서 환경 변수를 로딩하고 검증합니다.

    Environment Variables:
        OPENAI_API_KEY: OpenAI API 키
        OPENAI_MODEL: OpenAI 모델 이름 (기본: gpt-4o-mini)
        ANTHROPIC_API_KEY: Anthropic API 키 (선택)
        ANTHROPIC_MODEL: Anthropic 모델 이름 (기본: claude-3-5-haiku-latest)
        USD_TO_KRW_RATE: USD → KRW 환율 (기본: 1340)
        DAILY_BUDGET_USD: 일일 예산 USD (선택)
        LOG_LEVEL: 로그 레벨 (기본: INFO)

    Examples:
        >>> settings = Settings()
        >>> settings.openai_api_key
        'sk-...'
        >>> settings.usd_to_krw_rate
        1340.0
    """

    def __init__(self, env_file: Optional[Path] = None):
        """초기화

        Args:
            env_file: .env 파일 경로 (기본: 플랫폼별 설정 디렉토리)
        """
        # .env 파일 경로 결정
        if env_file is None:
            # PyInstaller로 빌드된 EXE인지 확인
            if getattr(sys, 'frozen', False):
                # PyInstaller로 빌드된 경우: 플랫폼별 설정 디렉토리 사용
                config_dir = self._get_config_directory()
                config_dir.mkdir(parents=True, exist_ok=True)  # 디렉토리 생성
                env_file = config_dir / ".env"
                logger.info(f"Running as PyInstaller EXE, using config dir: {config_dir}")

                # .env 파일이 없으면 .env.example을 복사 (처음 실행 시)
                if not env_file.exists():
                    self._create_default_env_file(env_file)
            else:
                # 일반 Python 실행: 프로젝트 루트 찾기 (app/config에서 2단계 상위)
                project_root = Path(__file__).parent.parent.parent
                env_file = project_root / ".env"
                logger.info(f"Running as Python script, looking for .env in: {project_root}")

        # .env 파일 로딩
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded .env file from: {env_file}")
        else:
            logger.warning(f".env file not found at: {env_file}")
            logger.warning(f"Please create .env file with your API keys")

        # 환경 변수 로딩
        self._load_settings()

        # 필수 설정 검증
        self._validate_required_settings()

        logger.info("Settings initialized successfully")

    def _get_config_directory(self) -> Path:
        """플랫폼별 설정 디렉토리 경로 반환

        Returns:
            설정 디렉토리 경로
            - Windows: C:\\Users\\{user}\\AppData\\Local\\CodeReviewAssistant
            - macOS: ~/Library/Application Support/CodeReviewAssistant
            - Linux: ~/.config/CodeReviewAssistant
        """
        import platform

        system = platform.system()

        if system == "Windows":
            # Windows: AppData\Local\CodeReviewAssistant
            appdata_local = os.getenv("LOCALAPPDATA")
            if appdata_local:
                return Path(appdata_local) / "CodeReviewAssistant"
            else:
                # Fallback: %USERPROFILE%\AppData\Local
                return Path.home() / "AppData" / "Local" / "CodeReviewAssistant"
        elif system == "Darwin":
            # macOS: ~/Library/Application Support/CodeReviewAssistant
            return Path.home() / "Library" / "Application Support" / "CodeReviewAssistant"
        else:
            # Linux/Unix: ~/.config/CodeReviewAssistant
            return Path.home() / ".config" / "CodeReviewAssistant"

    def _create_default_env_file(self, env_file: Path):
        """기본 .env 파일 생성 (.env.example 기반)

        Args:
            env_file: 생성할 .env 파일 경로
        """
        # .env.example 템플릿
        default_content = """# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic Configuration (alternative)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-latest

# Cost Monitoring
USD_TO_KRW_RATE=1340
DAILY_BUDGET_USD=10.00

# Application Settings
LOG_LEVEL=INFO
"""

        try:
            env_file.write_text(default_content, encoding='utf-8')
            logger.info(f"Created default .env file at: {env_file}")
            logger.info(f"Please edit {env_file} and add your API keys")
        except Exception as e:
            logger.error(f"Failed to create default .env file: {e}")

    def _load_settings(self):
        """환경 변수에서 설정 로딩"""
        # OpenAI 설정
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Anthropic 설정
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")

        # 비용 모니터링 설정
        usd_rate_str = os.getenv("USD_TO_KRW_RATE", "1340")
        self.usd_to_krw_rate: float = float(usd_rate_str)

        daily_budget_str = os.getenv("DAILY_BUDGET_USD")
        self.daily_budget_usd: Optional[float] = (
            float(daily_budget_str) if daily_budget_str else None
        )

        # 로깅 설정
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def _validate_required_settings(self):
        """필수 설정 검증

        Raises:
            ValueError: 필수 설정이 누락된 경우
        """
        # OpenAI 또는 Anthropic 중 최소 하나의 API 키는 필요
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError(
                "At least one API key required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
            )

        # 환율은 양수여야 함
        if self.usd_to_krw_rate <= 0:
            raise ValueError(f"Invalid USD_TO_KRW_RATE: {self.usd_to_krw_rate}")

        logger.debug("Settings validation passed")

    def has_openai_key(self) -> bool:
        """OpenAI API 키 존재 여부

        Returns:
            True if OpenAI API key exists
        """
        return bool(self.openai_api_key)

    def has_anthropic_key(self) -> bool:
        """Anthropic API 키 존재 여부

        Returns:
            True if Anthropic API key exists
        """
        return bool(self.anthropic_api_key)

    def get_available_providers(self) -> list[str]:
        """사용 가능한 LLM 제공자 목록

        Returns:
            List of available providers: ["openai", "anthropic"]
        """
        providers = []
        if self.has_openai_key():
            providers.append("openai")
        if self.has_anthropic_key():
            providers.append("anthropic")
        return providers

    def __repr__(self) -> str:
        """문자열 표현 (API 키는 마스킹)"""
        return (
            f"Settings("
            f"openai_key={'***' if self.openai_api_key else None}, "
            f"openai_model={self.openai_model}, "
            f"anthropic_key={'***' if self.anthropic_api_key else None}, "
            f"anthropic_model={self.anthropic_model}, "
            f"usd_rate={self.usd_to_krw_rate}, "
            f"daily_budget={self.daily_budget_usd}"
            f")"
        )


# 싱글톤 인스턴스
_settings_instance: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """설정 싱글톤 인스턴스 가져오기

    Args:
        reload: True면 설정을 다시 로딩

    Returns:
        Settings 인스턴스

    Examples:
        >>> settings = get_settings()
        >>> settings.openai_model
        'gpt-4o-mini'
    """
    global _settings_instance

    if _settings_instance is None or reload:
        _settings_instance = Settings()
        logger.debug("Settings instance created/reloaded")

    return _settings_instance


# 모듈 레벨 export
__all__ = ["Settings", "get_settings"]
