"""
Main Window - 코드 리뷰 어시스턴트 메인 윈도우
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSplitter, QGroupBox, QCheckBox,
    QLabel, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Optional
import logging

from app.ui.language_selector import LanguageSelectorWidget
from app.ui.cost_monitor import CostMonitorWidget
from app.ui.before_after_editor import BeforeAfterEditorWidget
from app.ui.result_panel import ResultPanelWidget
from app.ui.file_upload_widget import FileUploadWidget
from app.ui.folder_select_widget import FolderSelectWidget
from app.models.language import Language
from app.models.review_category import ReviewCategory

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """코드 리뷰 어시스턴트 메인 윈도우
    
    모든 UI 컴포넌트를 통합하고 사용자 인터랙션을 관리합니다.
    
    Signals:
        analysis_requested: 분석 요청 시 발생 (언어, 카테고리, 코드)
    """
    
    # Signals
    analysis_requested = Signal(Language, list, str)  # language, categories, code
    
    def __init__(self):
        """초기화"""
        super().__init__()
        
        self.current_language = Language.PYTHON  # 기본 언어
        
        self._init_ui()
        self._connect_signals()
        
        logger.info("MainWindow initialized")
    
    def _init_ui(self):
        """UI 초기화"""
        # Window 설정
        self.setWindowTitle("Code Review Assistant")
        self.setMinimumSize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)
        
        # === Top: Language Selector ===
        self.language_selector = LanguageSelectorWidget()
        main_layout.addWidget(self.language_selector)
        
        # === Middle: Content Area (Splitter) ===
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(3)
        
        # Left Panel: Code Editor + File Upload
        left_panel = self._create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right Panel: Result Panel
        right_panel = self._create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Splitter 비율: 50:50
        content_splitter.setSizes([700, 700])
        
        main_layout.addWidget(content_splitter, stretch=1)
        
        # === Bottom: Category Selection + Analyze Button ===
        category_layout = self._create_category_section()
        main_layout.addLayout(category_layout)
        
        # === Status Bar: Cost Monitor ===
        self.cost_monitor = CostMonitorWidget()
        status_bar = QStatusBar()
        status_bar.addPermanentWidget(self.cost_monitor)
        self.setStatusBar(status_bar)
    
    def _create_left_panel(self) -> QWidget:
        """왼쪽 패널 생성 (코드 에디터 + 파일 업로드)"""
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_widget.setLayout(left_layout)
        
        # File/Folder Upload
        upload_group = QGroupBox("파일 선택")
        upload_layout = QHBoxLayout()
        
        self.file_upload_widget = FileUploadWidget()
        upload_layout.addWidget(self.file_upload_widget)
        
        self.folder_select_widget = FolderSelectWidget()
        upload_layout.addWidget(self.folder_select_widget)
        
        upload_group.setLayout(upload_layout)
        left_layout.addWidget(upload_group)
        
        # Before/After Editor
        editor_group = QGroupBox("코드 에디터")
        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        self.before_after_editor = BeforeAfterEditorWidget()
        editor_layout.addWidget(self.before_after_editor)
        
        editor_group.setLayout(editor_layout)
        left_layout.addWidget(editor_group, stretch=1)
        
        return left_widget
    
    def _create_right_panel(self) -> QWidget:
        """오른쪽 패널 생성 (결과 패널)"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_widget.setLayout(right_layout)
        
        # Result Panel
        result_group = QGroupBox("분석 결과")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(5, 5, 5, 5)
        
        self.result_panel = ResultPanelWidget()
        result_layout.addWidget(self.result_panel)
        
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)
        
        return right_widget
    
    def _create_category_section(self) -> QHBoxLayout:
        """카테고리 선택 섹션 생성"""
        layout = QHBoxLayout()
        
        # Category Group Box
        category_group = QGroupBox("검토 카테고리 (최소 1개 선택)")
        category_layout = QHBoxLayout()
        
        # 8개 카테고리 체크박스
        self.category_checkboxes = {}
        
        for category in ReviewCategory:
            checkbox = QCheckBox(category.display_name)
            checkbox.setChecked(True)  # 기본적으로 모두 선택
            self.category_checkboxes[category] = checkbox
            category_layout.addWidget(checkbox)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group, stretch=1)
        
        # Analyze Button
        self.analyze_button = QPushButton("분석하기")
        self.analyze_button.setMinimumSize(150, 60)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        layout.addWidget(self.analyze_button)
        
        return layout
    
    def _connect_signals(self):
        """Signal 연결"""
        # Language selector
        self.language_selector.language_changed.connect(self._on_language_changed)
        
        # File upload
        self.file_upload_widget.file_selected.connect(self._on_file_selected)
        
        # Folder select
        self.folder_select_widget.folder_selected.connect(self._on_folder_selected)
        
        # Before/After editor text changed
        self.before_after_editor.before_text_changed.connect(self._on_code_changed)
        
        # Analyze button
        self.analyze_button.clicked.connect(self._on_analyze_clicked)
        
        # Result panel
        self.result_panel.report_saved.connect(self._on_report_saved)
    
    def _on_language_changed(self, language: Language):
        """언어 변경 이벤트"""
        self.current_language = language
        logger.info(f"Language changed to: {language.value}")
        
        # 폴더 선택 위젯의 파일 확장자 업데이트
        # TODO: Language에서 파일 확장자를 가져와서 설정
        # 예: self.folder_select_widget.set_file_extension(language.get_extension())
    
    def _on_file_selected(self, file_path: str):
        """파일 선택 이벤트"""
        logger.info(f"File selected: {file_path}")
        
        # 파일 내용 읽어서 Before 에디터에 표시
        content = self.file_upload_widget.read_file_content()
        if content:
            self.before_after_editor.set_before_text(content)
            logger.debug(f"Loaded {len(content)} characters from file")
    
    def _on_folder_selected(self, folder_path: str):
        """폴더 선택 이벤트"""
        logger.info(f"Folder selected: {folder_path}")
        
        # TODO: 배치 분석 구현 (Day 13)
        # 현재는 첫 번째 파일만 로드
        files = self.folder_select_widget.get_found_files()
        if files:
            first_file = files[0]
            try:
                from pathlib import Path
                content = Path(first_file).read_text(encoding='utf-8')
                self.before_after_editor.set_before_text(content)
                logger.debug(f"Loaded first file from folder: {first_file}")
            except Exception as e:
                logger.error(f"Failed to read file: {e}")
    
    def _on_code_changed(self, text: str):
        """코드 변경 이벤트 (토큰 카운팅용)"""
        # TODO: Day 11에서 실시간 토큰 카운팅 구현
        # 현재는 로그만 남김
        logger.debug(f"Code changed: {len(text)} characters")
    
    def _on_analyze_clicked(self):
        """분석하기 버튼 클릭 이벤트"""
        logger.info("Analyze button clicked")
        
        # 선택된 카테고리 확인
        selected_categories = self._get_selected_categories()
        
        if not selected_categories:
            QMessageBox.warning(
                self,
                "카테고리 미선택",
                "최소 1개 이상의 검토 카테고리를 선택해주세요."
            )
            return
        
        # Before 코드 확인
        code = self.before_after_editor.get_before_text()
        
        if not code.strip():
            QMessageBox.warning(
                self,
                "코드 없음",
                "분석할 코드를 입력하거나 파일을 업로드해주세요."
            )
            return
        
        # 분석 요청 Signal 발생
        self.analysis_requested.emit(self.current_language, selected_categories, code)
        
        logger.info(
            f"Analysis requested: {self.current_language.value}, "
            f"{len(selected_categories)} categories, "
            f"{len(code)} characters"
        )
        
        # TODO: Day 11에서 API 호출 구현
        # 현재는 더미 결과 표시
        self._show_dummy_result()
    
    def _get_selected_categories(self) -> List[ReviewCategory]:
        """선택된 카테고리 반환"""
        selected = []
        for category, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked():
                selected.append(category)
        return selected
    
    def _show_dummy_result(self):
        """더미 결과 표시 (테스트용)"""
        dummy_markdown = f"""# Code Review Result

## Programming Language: {self.current_language.value.upper()}

## Selected Categories
{chr(10).join(f"- {cat.display_name}" for cat in self._get_selected_categories())}

## Analysis
This is a dummy result for testing purposes.
The actual analysis will be implemented in Day 11 (API Client).

### Example Issue

**Before:**
```{self.current_language.value}
def get_user(user_id):
    return db.query(User).get(user_id)
```

**After:**
```{self.current_language.value}
def get_user(user_id: int) -> Optional[User]:
    try:
        return db.query(User).get(user_id)
    except Exception as e:
        logger.error(f"Failed to get user: {{e}}")
        return None
```

## Summary
- Total issues found: 3
- Critical: 1
- Warning: 2
"""
        
        self.result_panel.set_markdown(dummy_markdown)
        logger.debug("Dummy result displayed")
    
    def _on_report_saved(self, file_path: str):
        """리포트 저장 완료 이벤트"""
        logger.info(f"Report saved: {file_path}")
        # TODO: 히스토리 DB에 저장 (Day 12)
    
    def set_analyze_enabled(self, enabled: bool):
        """분석 버튼 활성화/비활성화
        
        Args:
            enabled: True면 활성화, False면 비활성화
        """
        self.analyze_button.setEnabled(enabled)
    
    def clear_all(self):
        """모든 입력/결과 초기화"""
        self.before_after_editor.clear()
        self.result_panel.clear()
        self.cost_monitor.reset()
        logger.info("All cleared")
    
    def get_current_language(self) -> Language:
        """현재 선택된 언어 반환"""
        return self.current_language
    
    def get_selected_categories(self) -> List[ReviewCategory]:
        """선택된 카테고리 반환"""
        return self._get_selected_categories()
