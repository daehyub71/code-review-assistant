"""
Editor Dialog - 코드 에디터 팝업 다이얼로그

코드 에디터를 큰 창으로 띄워서 편집할 수 있게 합니다.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from typing import Optional
import logging

from app.ui.before_after_editor import BeforeAfterEditorWidget

logger = logging.getLogger(__name__)


class EditorDialog(QDialog):
    """코드 에디터 팝업 다이얼로그

    BeforeAfterEditorWidget을 큰 창으로 띄워서 편집합니다.

    Examples:
        >>> dialog = EditorDialog(parent)
        >>> dialog.set_before_text("print('hello')")
        >>> if dialog.exec() == QDialog.Accepted:
        ...     before_text = dialog.get_before_text()
        ...     after_text = dialog.get_after_text()
    """

    def __init__(self, parent: Optional[QDialog] = None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self._init_ui()
        logger.info("EditorDialog initialized")

    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("코드 에디터 (확대)")
        self.setMinimumSize(1200, 800)

        # Main layout
        layout = QVBoxLayout()

        # Before/After Editor
        self.editor = BeforeAfterEditorWidget()
        layout.addWidget(self.editor, stretch=1)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 버튼 공통 스타일
        button_style = """
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2563EB;
                color: white;
                border-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """

        # 확인 버튼
        self.ok_button = QPushButton("확인")
        self.ok_button.setStyleSheet(button_style)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        # 취소 버튼
        self.cancel_button = QPushButton("취소")
        self.cancel_button.setStyleSheet(button_style)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def set_before_text(self, text: str):
        """Before 텍스트 설정

        Args:
            text: 설정할 텍스트
        """
        self.editor.set_before_text(text)

    def set_after_text(self, text: str):
        """After 텍스트 설정

        Args:
            text: 설정할 텍스트
        """
        self.editor.set_after_text(text)

    def get_before_text(self) -> str:
        """Before 텍스트 가져오기

        Returns:
            Before 에디터의 텍스트
        """
        return self.editor.get_before_text()

    def get_after_text(self) -> str:
        """After 텍스트 가져오기

        Returns:
            After 에디터의 텍스트
        """
        return self.editor.get_after_text()
