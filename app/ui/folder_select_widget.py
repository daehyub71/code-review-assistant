"""
Folder Select Widget - 폴더 선택 위젯
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QListWidget
)
from PySide6.QtCore import Signal
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class FolderSelectWidget(QWidget):
    """폴더 선택 위젯

    폴더 선택 다이얼로그를 통해 폴더를 선택하고 내부 파일 목록을 표시합니다.
    파일 개수 제한 (기본 100개)을 지원합니다.

    Signals:
        folder_selected: 폴더가 선택될 때 발생 (folder_path: str)
        files_found: 파일이 발견될 때 발생 (file_paths: List[str])

    Examples:
        >>> widget = FolderSelectWidget(max_files=100)
        >>> widget.folder_selected.connect(on_folder_selected)
    """

    # Signals
    folder_selected = Signal(str)
    files_found = Signal(list)

    def __init__(
        self,
        max_files: int = 100,
        file_extension: str = "*.py",
        parent: Optional[QWidget] = None
    ):
        """초기화

        Args:
            max_files: 최대 파일 개수 (기본값: 100)
            file_extension: 파일 확장자 필터 (기본값: "*.py")
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.max_files = max_files
        self.file_extension = file_extension
        self.selected_folder_path: Optional[str] = None
        self.found_files: List[str] = []
        self._init_ui()
        logger.info(f"FolderSelectWidget initialized with max files: {max_files}")

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Button layout
        button_layout = QHBoxLayout()

        # Select folder button
        self.select_button = QPushButton("폴더 선택")
        self.select_button.clicked.connect(self._on_select_folder)
        button_layout.addWidget(self.select_button)

        # Clear button
        self.clear_button = QPushButton("초기화")
        self.clear_button.clicked.connect(self._on_clear)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Folder info label
        self.folder_info_label = QLabel("선택된 폴더 없음")
        self.folder_info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self.folder_info_label)

        # File count label
        self.file_count_label = QLabel("")
        self.file_count_label.setStyleSheet("color: #9ca3af; font-size: 10px;")
        layout.addWidget(self.file_count_label)

        # File list
        self.file_list_widget = QListWidget()
        self.file_list_widget.setMaximumHeight(150)
        layout.addWidget(self.file_list_widget)

        # Limit label
        limit_label = QLabel(f"최대 파일 개수: {self.max_files}개 ({self.file_extension})")
        limit_label.setStyleSheet("color: #9ca3af; font-size: 10px;")
        layout.addWidget(limit_label)

        self.setLayout(layout)

    def _on_select_folder(self):
        """폴더 선택 버튼 클릭 이벤트"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "폴더 선택",
            ""
        )

        if not folder_path:
            return

        # 폴더 내 파일 검색
        files = self._find_files_in_folder(folder_path)

        if not files:
            QMessageBox.warning(
                self,
                "파일 없음",
                f"선택한 폴더에 {self.file_extension} 파일이 없습니다."
            )
            logger.warning(f"No files found in folder: {folder_path}")
            return

        if len(files) > self.max_files:
            QMessageBox.warning(
                self,
                "파일 개수 초과",
                f"파일 개수({len(files)}개)가 최대 개수({self.max_files}개)를 초과합니다."
            )
            logger.warning(f"File count exceeded: {len(files)} > {self.max_files}")
            return

        self.selected_folder_path = folder_path
        self.found_files = files
        self._update_folder_info(folder_path, files)
        self.clear_button.setEnabled(True)

        self.folder_selected.emit(folder_path)
        self.files_found.emit(files)

        logger.info(f"Folder selected: {folder_path} ({len(files)} files)")

    def _find_files_in_folder(self, folder_path: str) -> List[str]:
        """폴더 내 파일 검색

        Args:
            folder_path: 폴더 경로

        Returns:
            파일 경로 리스트
        """
        folder = Path(folder_path)
        files = []

        # Recursive search
        for file_path in folder.rglob(self.file_extension):
            if file_path.is_file():
                files.append(str(file_path))

        return sorted(files)

    def _on_clear(self):
        """초기화 버튼 클릭 이벤트"""
        self.selected_folder_path = None
        self.found_files = []
        self.folder_info_label.setText("선택된 폴더 없음")
        self.folder_info_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self.file_count_label.setText("")
        self.file_list_widget.clear()
        self.clear_button.setEnabled(False)
        logger.info("Folder selection cleared")

    def _update_folder_info(self, folder_path: str, files: List[str]):
        """폴더 정보 업데이트

        Args:
            folder_path: 폴더 경로
            files: 파일 경로 리스트
        """
        folder_name = Path(folder_path).name
        file_count = len(files)

        # Folder info
        info_text = f"📁 {folder_name}"
        self.folder_info_label.setText(info_text)
        self.folder_info_label.setStyleSheet("color: #059669; font-size: 11px; font-weight: bold;")

        # File count
        count_text = f"발견된 파일: {file_count}개"
        self.file_count_label.setText(count_text)

        # File list
        self.file_list_widget.clear()
        for file_path in files:
            # Show relative path from folder
            relative_path = Path(file_path).relative_to(folder_path)
            self.file_list_widget.addItem(str(relative_path))

    def get_selected_folder(self) -> Optional[str]:
        """선택된 폴더 경로 가져오기

        Returns:
            선택된 폴더 경로 (없으면 None)

        Examples:
            >>> widget = FolderSelectWidget()
            >>> folder_path = widget.get_selected_folder()
        """
        return self.selected_folder_path

    def get_found_files(self) -> List[str]:
        """발견된 파일 목록 가져오기

        Returns:
            파일 경로 리스트

        Examples:
            >>> widget = FolderSelectWidget()
            >>> files = widget.get_found_files()
        """
        return self.found_files.copy()

    def set_max_files(self, max_files: int):
        """최대 파일 개수 설정

        Args:
            max_files: 최대 파일 개수

        Examples:
            >>> widget = FolderSelectWidget()
            >>> widget.set_max_files(200)
        """
        self.max_files = max_files
        logger.info(f"Max files set to: {max_files}")

    def set_file_extension(self, extension: str):
        """파일 확장자 필터 설정

        Args:
            extension: 파일 확장자 (예: "*.py", "*.java")

        Examples:
            >>> widget = FolderSelectWidget()
            >>> widget.set_file_extension("*.java")
        """
        self.file_extension = extension
        logger.info(f"File extension filter set to: {extension}")

    def get_file_count(self) -> int:
        """발견된 파일 개수 반환

        Returns:
            파일 개수

        Examples:
            >>> widget = FolderSelectWidget()
            >>> count = widget.get_file_count()
        """
        return len(self.found_files)
