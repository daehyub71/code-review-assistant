"""
File Upload Widget - 파일 선택 위젯
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class FileUploadWidget(QWidget):
    """파일 업로드 위젯

    파일 선택 다이얼로그를 통해 단일 파일을 선택합니다.
    파일 크기 제한 (기본 1MB)을 지원합니다.

    Signals:
        file_selected: 파일이 선택될 때 발생 (file_path: str)

    Examples:
        >>> widget = FileUploadWidget(max_size_mb=1.0)
        >>> widget.file_selected.connect(on_file_selected)
    """

    # Signal: 파일 선택 시 발생
    file_selected = Signal(str)

    def __init__(
        self,
        max_size_mb: float = 1.0,
        file_filter: str = "All Files (*)",
        parent: Optional[QWidget] = None
    ):
        """초기화

        Args:
            max_size_mb: 최대 파일 크기 (MB, 기본값: 1.0)
            file_filter: 파일 필터 (기본값: "All Files (*)")
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.max_size_mb = max_size_mb
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.file_filter = file_filter
        self.selected_file_path: Optional[str] = None
        self._init_ui()
        logger.info(f"FileUploadWidget initialized with max size: {max_size_mb}MB")

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Button layout
        button_layout = QHBoxLayout()

        # Select file button
        self.select_button = QPushButton("파일 선택")
        self.select_button.clicked.connect(self._on_select_file)
        button_layout.addWidget(self.select_button)

        # Clear button
        self.clear_button = QPushButton("초기화")
        self.clear_button.clicked.connect(self._on_clear)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # File info label
        self.file_info_label = QLabel("선택된 파일 없음")
        self.file_info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self.file_info_label)

        # Size limit label
        size_limit_label = QLabel(f"최대 파일 크기: {self.max_size_mb}MB")
        size_limit_label.setStyleSheet("color: #9ca3af; font-size: 10px;")
        layout.addWidget(size_limit_label)

        self.setLayout(layout)

    def _on_select_file(self):
        """파일 선택 버튼 클릭 이벤트"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "파일 선택",
            "",
            self.file_filter
        )

        if not file_path:
            return

        # 파일 크기 확인
        file_size = Path(file_path).stat().st_size

        if file_size > self.max_size_bytes:
            size_mb = file_size / (1024 * 1024)
            QMessageBox.warning(
                self,
                "파일 크기 초과",
                f"선택한 파일({size_mb:.2f}MB)이 최대 크기({self.max_size_mb}MB)를 초과합니다."
            )
            logger.warning(f"File size exceeded: {size_mb:.2f}MB > {self.max_size_mb}MB")
            return

        self.selected_file_path = file_path
        self._update_file_info(file_path, file_size)
        self.clear_button.setEnabled(True)
        self.file_selected.emit(file_path)

        logger.info(f"File selected: {file_path} ({file_size} bytes)")

    def _on_clear(self):
        """초기화 버튼 클릭 이벤트"""
        self.selected_file_path = None
        self.file_info_label.setText("선택된 파일 없음")
        self.file_info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self.clear_button.setEnabled(False)
        logger.info("File selection cleared")

    def _update_file_info(self, file_path: str, file_size: int):
        """파일 정보 업데이트

        Args:
            file_path: 파일 경로
            file_size: 파일 크기 (bytes)
        """
        file_name = Path(file_path).name
        size_mb = file_size / (1024 * 1024)

        info_text = f"📄 {file_name} ({size_mb:.2f}MB)"
        self.file_info_label.setText(info_text)
        self.file_info_label.setStyleSheet("color: #059669; font-size: 11px; font-weight: bold;")

    def get_selected_file(self) -> Optional[str]:
        """선택된 파일 경로 가져오기

        Returns:
            선택된 파일 경로 (없으면 None)

        Examples:
            >>> widget = FileUploadWidget()
            >>> file_path = widget.get_selected_file()
        """
        return self.selected_file_path

    def set_max_size(self, size_mb: float):
        """최대 파일 크기 설정

        Args:
            size_mb: 최대 크기 (MB)

        Examples:
            >>> widget = FileUploadWidget()
            >>> widget.set_max_size(2.0)  # 2MB로 변경
        """
        self.max_size_mb = size_mb
        self.max_size_bytes = int(size_mb * 1024 * 1024)
        logger.info(f"Max file size set to: {size_mb}MB")

    def set_file_filter(self, file_filter: str):
        """파일 필터 설정

        Args:
            file_filter: 파일 필터 문자열

        Examples:
            >>> widget = FileUploadWidget()
            >>> widget.set_file_filter("Python Files (*.py);;All Files (*)")
        """
        self.file_filter = file_filter
        logger.info(f"File filter set to: {file_filter}")

    def read_file_content(self) -> Optional[str]:
        """선택된 파일 내용 읽기

        Returns:
            파일 내용 (선택된 파일이 없거나 읽기 실패 시 None)

        Examples:
            >>> widget = FileUploadWidget()
            >>> content = widget.read_file_content()
        """
        if not self.selected_file_path:
            logger.warning("No file selected")
            return None

        try:
            with open(self.selected_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"File content read: {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            QMessageBox.critical(
                self,
                "파일 읽기 실패",
                f"파일을 읽을 수 없습니다: {str(e)}"
            )
            return None
