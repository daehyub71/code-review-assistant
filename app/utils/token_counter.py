"""
Token Counter - UI용 토큰 카운팅 유틸리티 (Debounce 지원)
"""

import threading
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class DebouncedTokenCounter:
    """Debounce 기능이 있는 토큰 카운터

    UI에서 사용자가 텍스트를 입력할 때마다 즉시 토큰을 카운팅하는 대신,
    일정 시간(예: 500ms) 동안 입력이 없을 때만 카운팅을 수행합니다.

    Examples:
        >>> def on_count_complete(count: int):
        ...     print(f"Token count: {count}")
        ...
        >>> counter = DebouncedTokenCounter(
        ...     count_func=lambda text: len(text.split()),
        ...     callback=on_count_complete,
        ...     delay_ms=500
        ... )
        >>> counter.count("Hello world")  # 500ms 후에 on_count_complete(2) 호출
        >>> counter.count("Hello world again")  # 이전 타이머 취소, 새로운 500ms 타이머 시작
    """

    def __init__(
        self,
        count_func: Callable[[str], int],
        callback: Callable[[int], None],
        delay_ms: int = 500
    ):
        """초기화

        Args:
            count_func: 토큰 카운팅 함수 (text -> token_count)
            callback: 카운팅 완료 시 호출될 콜백 함수 (token_count -> None)
            delay_ms: Debounce 지연 시간 (밀리초, 기본값: 500ms)
        """
        self.count_func = count_func
        self.callback = callback
        self.delay_seconds = delay_ms / 1000.0
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

        logger.debug(f"DebouncedTokenCounter initialized with delay: {delay_ms}ms")

    def count(self, text: str) -> None:
        """텍스트 토큰 카운팅 (Debounced)

        이 메서드를 호출하면 기존 타이머를 취소하고 새로운 타이머를 시작합니다.
        delay_ms 시간 동안 추가 호출이 없으면 count_func를 실행하고 callback을 호출합니다.

        Args:
            text: 카운팅할 텍스트

        Examples:
            >>> counter.count("Hello")
            >>> time.sleep(0.6)  # 500ms 후 카운팅 완료
        """
        with self._lock:
            # 기존 타이머 취소
            if self._timer is not None:
                self._timer.cancel()
                logger.debug("Cancelled previous timer")

            # 새로운 타이머 시작
            self._timer = threading.Timer(
                self.delay_seconds,
                self._execute_count,
                args=(text,)
            )
            self._timer.start()
            logger.debug(f"Started new timer for text (length={len(text)})")

    def _execute_count(self, text: str) -> None:
        """실제 토큰 카운팅 실행 (내부 메서드)

        Args:
            text: 카운팅할 텍스트
        """
        try:
            count = self.count_func(text)
            logger.info(f"Token count completed: {count} tokens")
            self.callback(count)
        except Exception as e:
            logger.error(f"Error during token counting: {e}")

    def cancel(self) -> None:
        """진행 중인 타이머 취소

        Examples:
            >>> counter.count("Hello")
            >>> counter.cancel()  # 카운팅 취소
        """
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
                logger.debug("Timer cancelled by user")

    def is_pending(self) -> bool:
        """카운팅 대기 중인지 확인

        Returns:
            타이머가 활성 상태면 True

        Examples:
            >>> counter.count("Hello")
            >>> print(counter.is_pending())
            True
            >>> time.sleep(0.6)
            >>> print(counter.is_pending())
            False
        """
        with self._lock:
            return self._timer is not None and self._timer.is_alive()


class SimpleTokenCounter:
    """Simple 토큰 카운터 (Debounce 없음)

    즉시 토큰 카운팅을 수행하는 간단한 카운터입니다.
    UI가 아닌 배치 처리나 테스트에 사용합니다.

    Examples:
        >>> counter = SimpleTokenCounter(count_func=lambda text: len(text.split()))
        >>> count = counter.count("Hello world")
        >>> print(count)
        2
    """

    def __init__(self, count_func: Callable[[str], int]):
        """초기화

        Args:
            count_func: 토큰 카운팅 함수 (text -> token_count)
        """
        self.count_func = count_func

    def count(self, text: str) -> int:
        """텍스트 토큰 카운팅 (즉시 실행)

        Args:
            text: 카운팅할 텍스트

        Returns:
            토큰 수

        Examples:
            >>> counter = SimpleTokenCounter(lambda text: len(text.split()))
            >>> count = counter.count("Hello world")
            >>> print(count)
            2
        """
        try:
            count = self.count_func(text)
            logger.debug(f"Token count: {count}")
            return count
        except Exception as e:
            logger.error(f"Error during token counting: {e}")
            return 0
