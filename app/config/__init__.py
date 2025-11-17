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
            env_file: .env 파일 경로 (기본: 프로젝트 루트의 .env)
        """
        # .env 파일 경로 결정
        if env_file is None:
            # PyInstaller로 빌드된 EXE인지 확인
            if getattr(sys, 'frozen', False):
                # PyInstaller로 빌드된 경우: EXE가 있는 폴더에서 .env 찾기
                exe_dir = Path(sys.executable).parent
                env_file = exe_dir / ".env"
                logger.info(f"Running as PyInstaller EXE, looking for .env in: {exe_dir}")
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

        # 환경 변수 로딩
        self._load_settings()

        # 필수 설정 검증
        self._validate_required_settings()

        logger.info("Settings initialized successfully")

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
