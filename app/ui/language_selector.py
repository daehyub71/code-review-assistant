"""
Language Selector Widget - 프로그래밍 언어 선택 위젯
"""

from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel
from PySide6.QtCore import Signal
from typing import Optional
import logging

from app.models.language import Language, LanguageConfig

logger = logging.getLogger(__name__)


class LanguageSelectorWidget(QWidget):
    """언어 선택 위젯

    QComboBox를 사용하여 프로그래밍 언어를 선택합니다.
    한글 표시명을 사용하며, Language enum을 반환합니다.

    Signals:
        language_changed: 언어가 변경될 때 발생 (Language enum 전달)

    Examples:
        >>> selector = LanguageSelectorWidget()
        >>> selector.language_changed.connect(on_language_changed)
        >>> language = selector.get_selected_language()
        >>> print(language)  # Language.PYTHON
    """

    # Signal: 언어 변경 시 발생
    language_changed = Signal(Language)

    def __init__(self, parent: Optional[QWidget] = None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self._init_ui()
        logger.info("LanguageSelectorWidget initialized")

    def _init_ui(self):
        """UI 초기화"""
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        label = QLabel("프로그래밍 언어:")
        layout.addWidget(label)

        # ComboBox
        self.combo_box = QComboBox()
        self.combo_box.setMinimumWidth(200)

        # 4개 언어 추가 (표시명: 한글, 데이터: Language enum)
        self._language_items = [
            ("C#", Language.CSHARP),
            ("Java", Language.JAVA),
            ("Python", Language.PYTHON),
            ("Vue.js", Language.VUE),
        ]

        for display_name, language in self._language_items:
            self.combo_box.addItem(display_name, language)

        # Signal 연결
        self.combo_box.currentIndexChanged.connect(self._on_selection_changed)

        layout.addWidget(self.combo_box)

        self.setLayout(layout)

    def _on_selection_changed(self, index: int):
        """ComboBox 선택 변경 이벤트 핸들러

        Args:
            index: 선택된 인덱스
        """
        if index >= 0:
            language = self.combo_box.itemData(index)
            logger.info(f"Language changed to: {language.value}")
            self.language_changed.emit(language)

    def get_selected_language(self) -> Language:
        """현재 선택된 언어 반환

        Returns:
            선택된 Language enum

        Examples:
            >>> selector = LanguageSelectorWidget()
            >>> language = selector.get_selected_language()
            >>> print(language.value)  # "csharp"
        """
        index = self.combo_box.currentIndex()
        if index < 0:
            # 기본값: Python
            return Language.PYTHON

        language = self.combo_box.itemData(index)
        return language

    def set_selected_language(self, language: Language):
        """언어 선택 설정

        Args:
            language: 설정할 Language enum

        Examples:
            >>> selector = LanguageSelectorWidget()
            >>> selector.set_selected_language(Language.JAVA)
            >>> print(selector.get_selected_language())  # Language.JAVA
        """
        for index, (_, lang) in enumerate(self._language_items):
            if lang == language:
                self.combo_box.setCurrentIndex(index)
                logger.debug(f"Language set to: {language.value}")
                return

        logger.warning(f"Language not found in selector: {language.value}")

    def get_display_name(self) -> str:
        """현재 선택된 언어의 표시명 반환

        Returns:
            선택된 언어의 표시명 (예: "Python")

        Examples:
            >>> selector = LanguageSelectorWidget()
            >>> selector.set_selected_language(Language.PYTHON)
            >>> print(selector.get_display_name())  # "Python"
        """
        return self.combo_box.currentText()

    def set_enabled(self, enabled: bool):
        """위젯 활성화/비활성화

        Args:
            enabled: True면 활성화, False면 비활성화

        Examples:
            >>> selector = LanguageSelectorWidget()
            >>> selector.set_enabled(False)  # 비활성화
        """
        self.combo_box.setEnabled(enabled)
        logger.debug(f"LanguageSelector enabled: {enabled}")
