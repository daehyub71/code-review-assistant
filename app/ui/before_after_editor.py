"""
Before/After Editor Widget - 코드 리뷰 전후 비교 에디터
"""

from PySide6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSplitter, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor, QFont
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BeforeAfterEditorWidget(QWidget):
    """Before/After 코드 비교 에디터 위젯

    두 개의 QTextEdit을 사용하여 리뷰 전/후 코드를 비교합니다.
    스크롤 동기화, 복사 버튼 등의 기능을 제공합니다.

    Signals:
        before_text_changed: Before 텍스트가 변경될 때 발생
        after_text_changed: After 텍스트가 변경될 때 발생

    Examples:
        >>> editor = BeforeAfterEditorWidget()
        >>> editor.set_before_text("def hello():\n    print('old')")
        >>> editor.set_after_text("def hello():\n    print('new')")
    """

    # Signals
    before_text_changed = Signal(str)
    after_text_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self._sync_scroll_enabled = False
        self._init_ui()
        logger.info("BeforeAfterEditorWidget initialized")

    def _init_ui(self):
        """UI 초기화"""
        # Main layout
        main_layout = QVBoxLayout()

        # Top controls
        controls_layout = QHBoxLayout()

        # 스크롤 동기화 체크박스
        self.sync_scroll_checkbox = QCheckBox("스크롤 동기화")
        self.sync_scroll_checkbox.stateChanged.connect(self._on_sync_scroll_changed)
        controls_layout.addWidget(self.sync_scroll_checkbox)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Splitter for Before/After editors
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Before panel
        before_panel = self._create_editor_panel(
            "Before (원본 코드)",
            is_before=True
        )
        splitter.addWidget(before_panel)

        # After panel
        after_panel = self._create_editor_panel(
            "After (개선된 코드)",
            is_before=False
        )
        splitter.addWidget(after_panel)

        # Set equal sizes
        splitter.setSizes([500, 500])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def _create_editor_panel(self, title: str, is_before: bool) -> QWidget:
        """에디터 패널 생성

        Args:
            title: 패널 제목
            is_before: Before 에디터 여부

        Returns:
            QWidget: 생성된 패널
        """
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Title and Copy button
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #1E3A5F; background-color: transparent;")
        header_layout.addWidget(title_label)

        copy_button = QPushButton("복사")
        copy_button.setMaximumWidth(60)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2563EB;
                color: white;
                border-color: #2563EB;
            }
        """)
        if is_before:
            copy_button.clicked.connect(self._copy_before_text)
        else:
            copy_button.clicked.connect(self._copy_after_text)
        header_layout.addWidget(copy_button)

        layout.addLayout(header_layout)

        # Text editor
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Courier New", 10))
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # UI 색상 테마 적용 (개선된 디자인)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #DBEAFE;
                selection-color: #1E3A5F;
                font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            }
            QTextEdit:focus {
                border: 2px solid #2563EB;
                padding: 7px;
            }
        """)

        if is_before:
            self.before_editor = text_edit
            text_edit.textChanged.connect(self._on_before_text_changed)
            text_edit.verticalScrollBar().valueChanged.connect(
                lambda value: self._on_scroll_changed(value, is_before=True)
            )
        else:
            self.after_editor = text_edit
            text_edit.textChanged.connect(self._on_after_text_changed)
            text_edit.verticalScrollBar().valueChanged.connect(
                lambda value: self._on_scroll_changed(value, is_before=False)
            )

        layout.addWidget(text_edit)

        panel.setLayout(layout)
        return panel

    def _on_before_text_changed(self):
        """Before 텍스트 변경 이벤트"""
        text = self.before_editor.toPlainText()
        self.before_text_changed.emit(text)
        logger.debug(f"Before text changed: {len(text)} characters")

    def _on_after_text_changed(self):
        """After 텍스트 변경 이벤트"""
        text = self.after_editor.toPlainText()
        self.after_text_changed.emit(text)
        logger.debug(f"After text changed: {len(text)} characters")

    def _on_sync_scroll_changed(self, state: int):
        """스크롤 동기화 체크박스 변경 이벤트

        Args:
            state: 체크박스 상태
        """
        self._sync_scroll_enabled = (state == Qt.CheckState.Checked.value)
        logger.info(f"Scroll sync enabled: {self._sync_scroll_enabled}")

    def _on_scroll_changed(self, value: int, is_before: bool):
        """스크롤 변경 이벤트

        Args:
            value: 스크롤 값
            is_before: Before 에디터에서 발생한 이벤트인지 여부
        """
        if not self._sync_scroll_enabled:
            return

        # 다른 에디터의 스크롤도 동기화
        if is_before:
            target_scrollbar = self.after_editor.verticalScrollBar()
        else:
            target_scrollbar = self.before_editor.verticalScrollBar()

        # 무한 루프 방지를 위해 시그널 일시적으로 차단
        target_scrollbar.blockSignals(True)
        target_scrollbar.setValue(value)
        target_scrollbar.blockSignals(False)

    def _copy_before_text(self):
        """Before 텍스트 클립보드에 복사"""
        text = self.before_editor.toPlainText()
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        logger.info("Before text copied to clipboard")

    def _copy_after_text(self):
        """After 텍스트 클립보드에 복사"""
        text = self.after_editor.toPlainText()
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        logger.info("After text copied to clipboard")

    def set_before_text(self, text: str):
        """Before 텍스트 설정

        Args:
            text: 설정할 텍스트

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> editor.set_before_text("def hello():\n    print('old')")
        """
        self.before_editor.setPlainText(text)
        logger.debug(f"Before text set: {len(text)} characters")

    def set_after_text(self, text: str):
        """After 텍스트 설정

        Args:
            text: 설정할 텍스트

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> editor.set_after_text("def hello():\n    print('new')")
        """
        self.after_editor.setPlainText(text)
        logger.debug(f"After text set: {len(text)} characters")

    def get_before_text(self) -> str:
        """Before 텍스트 가져오기

        Returns:
            Before 에디터의 텍스트

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> text = editor.get_before_text()
        """
        return self.before_editor.toPlainText()

    def get_after_text(self) -> str:
        """After 텍스트 가져오기

        Returns:
            After 에디터의 텍스트

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> text = editor.get_after_text()
        """
        return self.after_editor.toPlainText()

    def clear(self):
        """Both editors clear

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> editor.clear()
        """
        self.before_editor.clear()
        self.after_editor.clear()
        logger.info("Both editors cleared")

    def set_read_only(self, before_readonly: bool, after_readonly: bool):
        """에디터 읽기 전용 설정

        Args:
            before_readonly: Before 에디터 읽기 전용 여부
            after_readonly: After 에디터 읽기 전용 여부

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> editor.set_read_only(True, False)
        """
        self.before_editor.setReadOnly(before_readonly)
        self.after_editor.setReadOnly(after_readonly)
        logger.debug(f"Read-only set: before={before_readonly}, after={after_readonly}")

    def enable_sync_scroll(self, enabled: bool):
        """스크롤 동기화 활성화/비활성화

        Args:
            enabled: 활성화 여부

        Examples:
            >>> editor = BeforeAfterEditorWidget()
            >>> editor.enable_sync_scroll(True)
        """
        self.sync_scroll_checkbox.setChecked(enabled)
