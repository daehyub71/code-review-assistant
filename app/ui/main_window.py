"""
Main Window - 코드 리뷰 어시스턴트 메인 윈도우
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QGroupBox, QCheckBox,
    QLabel, QStatusBar, QMessageBox, QProgressBar
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
from app.ui.editor_dialog import EditorDialog
from app.models.language import Language
from app.models.review_category import ReviewCategory
from app.core.api_client import APIClient, AnalysisRequest, AnalysisWorker, AnalysisResponse
from app.core.prompt_builder import PromptBuilder
from app.core.cost_calculator import CostCalculator, ModelType
from app.core.report_generator import ReportGenerator
from app.core.batch_analyzer import BatchAnalyzer, BatchAnalyzerWorker, BatchAnalysisProgress, BatchAnalysisResult
from app.db.report_history import ReportHistory
from app.config import get_settings

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

        # 기본 언어는 None으로 초기화 (드롭다운 초기값과 동기화)
        self.current_language = None

        # API 및 분석 컴포넌트 초기화
        self.settings = get_settings()
        self.api_client = APIClient()
        self.prompt_builder = PromptBuilder()
        self.cost_calculator = CostCalculator()
        self.report_generator = ReportGenerator()
        self.report_history = ReportHistory()
        self.batch_analyzer = BatchAnalyzer()

        # 현재 분석 중인 워커 (취소 가능하도록)
        self.current_worker: Optional[AnalysisWorker] = None
        self.current_batch_worker: Optional[BatchAnalyzerWorker] = None

        self._init_ui()
        self._connect_signals()

        # 드롭다운의 초기 선택 값으로 current_language 동기화
        self.current_language = self.language_selector.get_selected_language()
        logger.info(f"MainWindow initialized with language: {self.current_language.value}")

        logger.info("MainWindow initialized")
    
    def _init_ui(self):
        """UI 초기화"""
        # Window 설정
        self.setWindowTitle("Code Review Assistant")
        self.setMinimumSize(1400, 900)

        # 전체 UI 색상 테마 적용 (개선된 전문적인 디자인)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #E8EEF2;
            }
            QWidget {
                background-color: #E8EEF2;
                color: #1E3A5F;
            }
            QGroupBox {
                background-color: #FFFFFF;
                color: #1E3A5F;
                border: 1px solid #94A3B8;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
                font-size: 13px;
                padding: 15px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 2px 8px;
                background-color: #FFFFFF;
                color: #2563EB;
                border-radius: 3px;
            }
            QLabel {
                color: #1E3A5F;
                background-color: transparent;
            }
            QCheckBox {
                color: #1E3A5F;
                background-color: transparent;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #94A3B8;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
            QStatusBar {
                background-color: #F8FAFC;
                color: #1E3A5F;
                border-top: 1px solid #E2E8F0;
            }
        """)

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

        # === Batch Progress Section (initially hidden) ===
        batch_progress_layout = self._create_batch_progress_section()
        main_layout.addLayout(batch_progress_layout)

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

        # 헤더 (제목 + 확대 버튼)
        editor_header_layout = QHBoxLayout()
        editor_title_label = QLabel("코드 에디터")
        editor_title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #1E3A5F; background-color: transparent;")
        editor_header_layout.addWidget(editor_title_label)
        editor_header_layout.addStretch()

        # 확대 버튼
        self.expand_editor_button = QPushButton("🔍 확대")
        self.expand_editor_button.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563EB;
                color: white;
                border-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        self.expand_editor_button.clicked.connect(self._on_expand_editor_clicked)
        editor_header_layout.addWidget(self.expand_editor_button)

        editor_layout.addLayout(editor_header_layout)

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
                background-color: #2563EB;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
        """)
        layout.addWidget(self.analyze_button)

        return layout

    def _create_batch_progress_section(self) -> QHBoxLayout:
        """배치 분석 진행 상황 섹션 생성 (초기에는 숨김)"""
        layout = QHBoxLayout()

        # Batch Progress Group Box
        self.batch_progress_group = QGroupBox("배치 분석 진행 상황")
        batch_layout = QHBoxLayout()

        # Progress Bar
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setMinimum(0)
        self.batch_progress_bar.setMaximum(100)
        self.batch_progress_bar.setValue(0)
        self.batch_progress_bar.setMinimumWidth(400)
        self.batch_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                background-color: #F1F5F9;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 4px;
            }
        """)
        batch_layout.addWidget(self.batch_progress_bar, stretch=1)

        # Status Label
        self.batch_status_label = QLabel("준비 중...")
        self.batch_status_label.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.batch_status_label.setMinimumWidth(200)
        batch_layout.addWidget(self.batch_status_label)

        # Cancel Button
        self.batch_cancel_button = QPushButton("취소")
        self.batch_cancel_button.setMinimumSize(80, 30)
        self.batch_cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
        """)
        self.batch_cancel_button.clicked.connect(self._on_batch_cancel_clicked)
        batch_layout.addWidget(self.batch_cancel_button)

        self.batch_progress_group.setLayout(batch_layout)
        layout.addWidget(self.batch_progress_group)

        # 초기에는 숨김
        self.batch_progress_group.setVisible(False)

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
        """폴더 선택 이벤트 - 배치 분석 시작"""
        logger.info(f"Folder selected: {folder_path}")

        # 선택된 파일 목록 가져오기
        files = self.folder_select_widget.get_found_files()
        if not files:
            QMessageBox.warning(
                self,
                "파일 없음",
                f"선택한 폴더에서 {self.current_language.value} 파일을 찾을 수 없습니다."
            )
            return

        logger.info(f"Found {len(files)} files in folder")

        # 카테고리 선택 확인
        selected_categories = self._get_selected_categories()
        if not selected_categories:
            QMessageBox.warning(
                self,
                "카테고리 미선택",
                "최소 1개 이상의 검토 카테고리를 선택해주세요."
            )
            return

        # 배치 분석 시작 확인
        reply = QMessageBox.question(
            self,
            "배치 분석 시작",
            f"{len(files)}개의 파일을 분석하시겠습니까?\n\n"
            f"언어: {self.current_language.value}\n"
            f"카테고리: {len(selected_categories)}개\n\n"
            f"예상 소요 시간: {len(files) * 5}초 ~ {len(files) * 10}초",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # 배치 분석 시작
        self._start_batch_analysis(files, selected_categories)
    
    def _on_code_changed(self, text: str):
        """코드 변경 이벤트 (실시간 토큰 카운팅)"""
        if not text.strip():
            self.cost_monitor.reset()
            return

        try:
            # 입력 토큰 카운팅 (추정)
            model = self.settings.openai_model if self.settings.has_openai_key() else self.settings.anthropic_model
            input_tokens = self.cost_calculator.count_tokens(text, model)

            # 출력 토큰은 입력의 50%로 추정 (실제는 분석 후 확정)
            estimated_output_tokens = int(input_tokens * 0.5)

            # 비용 추정
            model_type = ModelType.from_string(model)
            cost_estimate = self.cost_calculator.estimate_cost(
                input_tokens=input_tokens,
                output_tokens=estimated_output_tokens,
                model_type=model_type
            )

            # Cost Monitor 업데이트
            self.cost_monitor.update_cost(cost_estimate)

            logger.debug(f"Code changed: {input_tokens} input tokens, estimated cost: ${cost_estimate.total_cost_usd:.6f}")
        except Exception as e:
            logger.error(f"Failed to update cost estimate: {e}")

    def _on_analyze_clicked(self):
        """분석하기 버튼 클릭 이벤트 (실제 API 호출)"""
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

        # 분석 요청 Signal 발생 (호환성 유지)
        self.analysis_requested.emit(self.current_language, selected_categories, code)

        logger.info(
            f"Analysis requested: {self.current_language.value}, "
            f"{len(selected_categories)} categories, "
            f"{len(code)} characters"
        )

        # 실제 API 호출
        self._start_analysis(code, selected_categories)
    
    def _get_selected_categories(self) -> List[ReviewCategory]:
        """선택된 카테고리 반환"""
        selected = []
        for category, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked():
                selected.append(category)
        return selected
    
    def _start_analysis(self, code: str, categories: List[ReviewCategory]):
        """실제 API 분석 시작

        Args:
            code: 분석할 코드
            categories: 검토 카테고리 리스트
        """
        try:
            # 시스템 프롬프트 생성
            prompt = self.prompt_builder.build_system_prompt(
                language=self.current_language,
                categories=categories
            )

            # 제공자 결정 (OpenAI 우선, 없으면 Anthropic)
            provider = "openai" if self.settings.has_openai_key() else "anthropic"
            model = None  # 기본 모델 사용

            # 분석 요청 생성
            request = AnalysisRequest(
                code=code,
                language=self.current_language,
                prompt=prompt,
                provider=provider,
                model=model
            )

            # 워커 생성 및 시그널 연결
            self.current_worker = self.api_client.analyze_async(request)
            self.current_worker.chunk_received.connect(self._on_analysis_chunk)
            self.current_worker.finished_success.connect(self._on_analysis_success)
            self.current_worker.finished_error.connect(self._on_analysis_error)

            # UI 상태 변경
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("분석 중...")
            self.result_panel.clear()
            self.result_panel.set_markdown("# 분석 중...\n\n코드를 분석하고 있습니다. 잠시만 기다려주세요.")

            # 워커 시작
            self.current_worker.start()

            logger.info(f"Analysis started with {provider}")

        except Exception as e:
            error_msg = f"분석 시작 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "분석 오류", error_msg)
            self.analyze_button.setEnabled(True)
            self.analyze_button.setText("분석하기")

    def _on_analysis_chunk(self, chunk: str):
        """스트리밍 청크 수신

        Args:
            chunk: LLM이 생성한 텍스트 청크
        """
        # 실시간으로 결과 패널에 추가
        self.result_panel.append_markdown(chunk)
        logger.debug(f"Received chunk: {len(chunk)} characters")

    def _on_analysis_success(self, response: AnalysisResponse):
        """분석 성공

        Args:
            response: 분석 결과
        """
        logger.info(
            f"Analysis completed: {response.input_tokens} input, "
            f"{response.output_tokens} output tokens"
        )

        # 결과 패널 업데이트 (전체 내용으로 교체)
        self.result_panel.set_markdown(response.content)

        # After 패널에 개선된 코드 자동 채우기
        try:
            improved_code = self._extract_improved_code(response.content)
            if improved_code:
                self.before_after_editor.set_after_text(improved_code)
                logger.info(f"After panel updated with improved code ({len(improved_code)} chars)")
            else:
                logger.warning("No improved code extracted, keeping After panel empty")
                # 디버깅을 위해 분석 결과의 일부를 로그에 출력
                logger.debug(f"Analysis result preview (first 500 chars): {response.content[:500]}")
        except Exception as e:
            logger.error(f"Failed to extract improved code: {e}", exc_info=True)
            # 에러 발생 시 원본 코드를 After 패널에 표시 (fallback)
            self.before_after_editor.set_after_text(self.before_after_editor.get_before_text())

        # 비용 모니터 업데이트 (실제 토큰으로)
        model_type = ModelType.from_string(response.model)
        cost_estimate = self.cost_calculator.estimate_cost(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            model_type=model_type
        )
        self.cost_monitor.update_cost(cost_estimate)

        # DB에 히스토리 저장
        try:
            record_id = self.report_history.save_analysis(
                language=self.current_language,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=cost_estimate.total_cost_usd,
                categories=self._get_selected_categories()
            )
            logger.info(f"Analysis saved to history: record_id={record_id}")
        except Exception as e:
            logger.error(f"Failed to save analysis history: {e}")

        # UI 상태 복원
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("분석하기")
        self.current_worker = None

        QMessageBox.information(
            self,
            "분석 완료",
            f"코드 분석이 완료되었습니다.\n\n"
            f"입력 토큰: {response.input_tokens:,}\n"
            f"출력 토큰: {response.output_tokens:,}\n"
            f"예상 비용: ${cost_estimate.total_cost_usd:.6f} (₩{cost_estimate.total_cost_krw:.2f})"
        )

    def _on_analysis_error(self, error_message: str):
        """분석 실패

        Args:
            error_message: 에러 메시지
        """
        logger.error(f"Analysis failed: {error_message}")

        # 에러 메시지 표시
        self.result_panel.set_markdown(f"# 분석 오류\n\n{error_message}")

        # UI 상태 복원
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("분석하기")
        self.current_worker = None

        QMessageBox.critical(
            self,
            "분석 실패",
            f"코드 분석 중 오류가 발생했습니다:\n\n{error_message}"
        )
    
    def _on_report_saved(self, file_path: str):
        """리포트 저장 완료 이벤트"""
        logger.info(f"Report saved: {file_path}")
        # TODO: 히스토리 DB에 저장 (Day 12)

    # ============================================================
    # Batch Analysis Methods
    # ============================================================

    def _start_batch_analysis(self, file_paths: List[str], categories: List[ReviewCategory]):
        """배치 분석 시작

        Args:
            file_paths: 분석할 파일 경로 목록
            categories: 선택된 카테고리 목록
        """
        try:
            # 제공자 결정
            provider = "openai" if self.settings.has_openai_key() else "anthropic"
            model = None  # 기본 모델 사용

            # 배치 워커 생성
            self.current_batch_worker = self.batch_analyzer.analyze_folder_async(
                file_paths=file_paths,
                language=self.current_language,
                categories=categories,
                provider=provider,
                model=model
            )

            # 시그널 연결
            self.current_batch_worker.progress_updated.connect(self._on_batch_progress_updated)
            self.current_batch_worker.file_completed.connect(self._on_batch_file_completed)
            self.current_batch_worker.finished_success.connect(self._on_batch_finished_success)
            self.current_batch_worker.finished_error.connect(self._on_batch_finished_error)

            # UI 상태 변경
            self.batch_progress_group.setVisible(True)
            self.batch_progress_bar.setValue(0)
            self.batch_status_label.setText(f"0 / {len(file_paths)} 파일 분석 중...")
            self.analyze_button.setEnabled(False)
            self.language_selector.set_enabled(False)
            self.file_upload_widget.set_enabled(False)
            self.folder_select_widget.set_enabled(False)

            # 워커 시작
            self.current_batch_worker.start()

            logger.info(f"Batch analysis started: {len(file_paths)} files with {provider}")

        except Exception as e:
            error_msg = f"배치 분석 시작 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(self, "배치 분석 오류", error_msg)

    def _on_batch_progress_updated(self, progress: BatchAnalysisProgress):
        """배치 분석 진행 상황 업데이트

        Args:
            progress: 진행 상황 정보
        """
        # Progress bar 업데이트
        self.batch_progress_bar.setValue(int(progress.progress_percent))

        # Status label 업데이트
        self.batch_status_label.setText(
            f"{progress.current_index} / {progress.total_files} 파일 분석 중: {progress.current_file}"
        )

        logger.debug(f"Batch progress: {progress.progress_percent:.1f}% ({progress.current_file})")

    def _on_batch_file_completed(self, file_path: str, result: str):
        """배치 분석 - 개별 파일 완료

        Args:
            file_path: 완료된 파일 경로
            result: 분석 결과 (Markdown)
        """
        logger.info(f"Batch file completed: {file_path}")

        # 결과 패널에 마지막 파일의 결과 표시 (옵션)
        # self.result_panel.set_markdown(result)

    def _on_batch_finished_success(self, result: BatchAnalysisResult):
        """배치 분석 완료

        Args:
            result: 배치 분석 결과
        """
        logger.info(
            f"Batch analysis completed: {len(result.file_results)} files, "
            f"${result.total_cost_usd:.6f}"
        )

        # UI 상태 복원
        self.batch_progress_group.setVisible(False)
        self.analyze_button.setEnabled(True)
        self.language_selector.set_enabled(True)
        self.file_upload_widget.set_enabled(True)
        self.folder_select_widget.set_enabled(True)
        self.current_batch_worker = None

        # 비용 모니터 업데이트
        model = result.file_results[0].review_result if result.file_results else "unknown"
        from app.core.cost_calculator import CostEstimate
        cost_estimate = CostEstimate(
            input_tokens=result.total_input_tokens,
            output_tokens=result.total_output_tokens,
            total_cost_usd=result.total_cost_usd,
            total_cost_krw=result.total_cost_krw
        )
        self.cost_monitor.update_cost(cost_estimate)

        # 통합 리포트 결과 패널에 표시
        if result.integrated_report_path:
            try:
                report_content = result.integrated_report_path.read_text(encoding='utf-8')
                self.result_panel.set_markdown(report_content)
            except Exception as e:
                logger.error(f"Failed to load integrated report: {e}")

        # 완료 메시지
        report_path_str = str(result.integrated_report_path) if result.integrated_report_path else "없음"
        QMessageBox.information(
            self,
            "배치 분석 완료",
            f"배치 분석이 완료되었습니다.\n\n"
            f"분석 파일: {len(result.file_results)}개\n"
            f"입력 토큰: {result.total_input_tokens:,}\n"
            f"출력 토큰: {result.total_output_tokens:,}\n"
            f"예상 비용: ${result.total_cost_usd:.6f} (₩{result.total_cost_krw:.2f})\n\n"
            f"통합 리포트: {report_path_str}"
        )

    def _on_batch_finished_error(self, error_message: str):
        """배치 분석 실패

        Args:
            error_message: 에러 메시지
        """
        logger.error(f"Batch analysis failed: {error_message}")

        # UI 상태 복원
        self.batch_progress_group.setVisible(False)
        self.analyze_button.setEnabled(True)
        self.language_selector.set_enabled(True)
        self.file_upload_widget.set_enabled(True)
        self.folder_select_widget.set_enabled(True)
        self.current_batch_worker = None

        # 에러 메시지 표시
        self.result_panel.set_markdown(f"# 배치 분석 오류\n\n{error_message}")

        QMessageBox.critical(
            self,
            "배치 분석 실패",
            f"배치 분석 중 오류가 발생했습니다:\n\n{error_message}"
        )

    def _on_batch_cancel_clicked(self):
        """배치 분석 취소 버튼 클릭"""
        if self.current_batch_worker is None:
            return

        reply = QMessageBox.question(
            self,
            "배치 분석 취소",
            "진행 중인 배치 분석을 취소하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("User requested batch analysis cancellation")
            self.current_batch_worker.cancel()

            # UI 상태 복원
            self.batch_progress_group.setVisible(False)
            self.analyze_button.setEnabled(True)
            self.language_selector.set_enabled(True)
            self.file_upload_widget.set_enabled(True)
            self.folder_select_widget.set_enabled(True)
            self.current_batch_worker = None

            QMessageBox.information(self, "취소 완료", "배치 분석이 취소되었습니다.")

    # ============================================================
    # End Batch Analysis Methods
    # ============================================================

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

    # ============================================================
    # Editor Dialog Methods
    # ============================================================

    def _on_expand_editor_clicked(self):
        """에디터 확대 버튼 클릭 이벤트"""
        logger.info("Expand editor button clicked")

        # 팝업 다이얼로그 생성
        dialog = EditorDialog(self)

        # 현재 코드를 다이얼로그에 복사
        dialog.set_before_text(self.before_after_editor.get_before_text())
        dialog.set_after_text(self.before_after_editor.get_after_text())

        # 다이얼로그 실행
        if dialog.exec():
            # 확인 버튼을 클릭한 경우 변경사항을 메인 윈도우에 반영
            self.before_after_editor.set_before_text(dialog.get_before_text())
            self.before_after_editor.set_after_text(dialog.get_after_text())
            logger.info("Editor dialog changes applied")
        else:
            logger.info("Editor dialog cancelled")

    def _detect_indentation(self, code: str, line_number: int = 0) -> str:
        """코드 블록의 들여쓰기 감지

        Args:
            code: 코드 문자열
            line_number: 감지할 라인 번호 (0이면 첫 번째 비어있지 않은 라인)

        Returns:
            들여쓰기 문자열 (공백 또는 탭)
        """
        import re

        lines = code.split('\n')

        if line_number > 0 and line_number < len(lines):
            target_line = lines[line_number]
        else:
            # 첫 번째 비어있지 않은 라인 찾기
            target_line = None
            for line in lines:
                if line.strip():
                    target_line = line
                    break

            if not target_line:
                return ""

        # 들여쓰기 추출 (공백 또는 탭)
        indent_match = re.match(r'^(\s+)', target_line)
        if indent_match:
            return indent_match.group(1)
        return ""

    def _apply_indentation(self, code: str, indent: str) -> str:
        """코드 블록에 들여쓰기 적용

        코드의 최소 들여쓰기를 감지하고, 모든 줄의 상대적 들여쓰기를 유지하면서
        기본 들여쓰기를 적용합니다.

        Args:
            code: 코드 문자열
            indent: 적용할 기본 들여쓰기 문자열

        Returns:
            들여쓰기가 적용된 코드
        """
        if not indent:
            return code

        lines = code.split('\n')

        # 1. 코드의 최소 들여쓰기 레벨 감지
        min_indent = None
        for line in lines:
            if line.strip():  # 비어있지 않은 줄만
                current_indent = len(line) - len(line.lstrip())
                if min_indent is None or current_indent < min_indent:
                    min_indent = current_indent

        if min_indent is None:
            min_indent = 0

        # 2. 각 줄의 상대적 들여쓰기를 유지하면서 기본 들여쓰기 적용
        indented_lines = []
        for line in lines:
            if line.strip():
                # 최소 들여쓰기를 제거하고 새로운 기본 들여쓰기 적용
                relative_indent = len(line) - len(line.lstrip()) - min_indent
                relative_indent_str = ' ' * relative_indent if relative_indent > 0 else ''
                stripped = line.lstrip()
                indented_lines.append(indent + relative_indent_str + stripped)
            else:
                # 빈 줄은 그대로
                indented_lines.append('')

        return '\n'.join(indented_lines)

    def _regenerate_code_with_llm(self, original_code: str, analysis_summary: str) -> Optional[str]:
        """LLM을 사용하여 개선사항이 적용된 전체 코드를 재생성

        Args:
            original_code: 원본 코드
            analysis_summary: 분석 결과 요약

        Returns:
            개선사항이 적용된 전체 코드
        """
        from app.core.api_client import AnalysisWorker, AnalysisRequest

        logger.info("Regenerating improved code using LLM...")

        # 개선 요청 프롬프트 생성
        regeneration_prompt = f"""다음 코드에 아래 개선사항들을 모두 적용하여 완전한 개선된 코드를 생성해주세요.

# 원본 코드:
```
{original_code}
```

# 적용할 개선사항:
{analysis_summary}

# 요구사항:
1. 원본 코드의 모든 기능을 유지하면서 개선사항을 적용해주세요
2. 올바른 들여쓰기를 적용해주세요 (4 spaces)
3. 모든 클래스, 메서드에 XML 주석을 추가해주세요
4. 개선사항이 적용된 **전체 완성된 코드만** 출력해주세요 (설명 없이)
5. 코드 블록은 ```csharp로 시작하고 ```로 끝나야 합니다

개선된 전체 코드:
"""

        # LLM API 호출
        try:
            current_language = self.language_selector.get_selected_language()

            # 제공자 결정 (OpenAI 우선, 없으면 Anthropic)
            provider = "openai" if self.settings.has_openai_key() else "anthropic"
            model = None  # 기본 모델 사용

            request = AnalysisRequest(
                code=regeneration_prompt,
                language=current_language,
                prompt="",  # 이미 프롬프트에 포함됨
                provider=provider,
                model=model
            )

            worker = AnalysisWorker(request)
            response = None
            error_message = None

            def on_success(resp):
                nonlocal response
                response = resp

            def on_error(msg):
                nonlocal error_message
                error_message = msg

            worker.finished_success.connect(on_success)
            worker.finished_error.connect(on_error)

            # 동기 실행
            worker.run()

            if error_message:
                logger.error(f"LLM regeneration failed: {error_message}")
                return None

            if not response or not response.content:
                logger.error("No response from LLM regeneration")
                return None

            # 응답에서 코드 블록 추출
            import re
            code_match = re.search(r'```(?:csharp|java|python|vue|javascript)?\n(.*?)```',
                                 response.content, re.DOTALL)

            if code_match:
                improved_code = code_match.group(1).strip()
                logger.info(f"Successfully regenerated code with LLM ({len(improved_code)} chars)")
                return improved_code
            else:
                # 코드 블록이 없으면 전체 응답 사용
                logger.warning("No code block found in LLM response, using full response")
                return response.content.strip()

        except Exception as e:
            logger.error(f"Failed to regenerate code with LLM: {e}", exc_info=True)
            return None

    def _extract_improved_code(self, markdown_result: str) -> Optional[str]:
        """분석 결과(Markdown)에서 개선된 코드 추출

        **새로운 방식**: LLM을 사용하여 개선사항이 적용된 전체 코드를 재생성합니다.

        1. 기존 소스 보존
        2. 개선 사항 추출
        3. LLM에게 전체 개선된 코드 재작성 요청 (들여쓰기, 주석 포함)

        Args:
            markdown_result: 분석 결과 Markdown 텍스트

        Returns:
            개선사항이 적용된 전체 소스 코드 (없으면 None)
        """
        import re

        # 1. Before 패널에서 원본 코드 가져오기
        try:
            original_code = self.before_after_editor.get_before_text()
            logger.debug(f"Retrieved original code from Before panel: {len(original_code)} chars")
        except Exception as e:
            logger.warning(f"Could not access Before panel: {e}")
            original_code = ""

        if not original_code or not original_code.strip():
            logger.warning("No original code in Before panel, falling back to improved blocks only")
            # Fallback: 개선 후 블록들만 병합
            return self._extract_improved_blocks_only(markdown_result)

        # 2. LLM을 사용하여 전체 개선된 코드 재생성
        logger.info("Using LLM-based code regeneration approach...")
        improved_code = self._regenerate_code_with_llm(original_code, markdown_result)

        if improved_code:
            return improved_code

        # 3. LLM 재생성 실패 시 기존 방식으로 fallback
        logger.warning("LLM regeneration failed, falling back to pattern matching approach...")
        return self._extract_improved_code_legacy(markdown_result, original_code)

    def _extract_improved_code_legacy(self, markdown_result: str, original_code: str) -> Optional[str]:
        """기존 방식: 패턴 매칭을 통한 개선된 코드 추출 (fallback)

        Before 패널의 원본 코드를 기본으로, 분석 결과의 "개선 전→개선 후" 부분만 교체하여
        완전한 개선된 전체 소스 코드를 반환합니다.

        Args:
            markdown_result: 분석 결과 Markdown 텍스트
            original_code: 원본 코드

        Returns:
            개선사항이 적용된 전체 소스 코드 (없으면 None)
        """
        import re

        # 2. "개선 전/개선 후" 쌍 추출
        # 여러 패턴 시도 (템플릿에서 **Before**:, **After**: 형식 사용)
        patterns_to_try = [
            # Bold 마크다운 패턴 (템플릿에서 사용하는 형식)
            (r'\*\*Before\*\*:\s*```[\w]*\n(.*?)```\s*\*\*After\*\*:\s*```[\w]*\n(.*?)```', 'Bold markdown (Before/After)'),
            # 헤딩 패턴 (한국어)
            (r'###?\s*개선\s*전[:\s]*\n*```[\w]*\n(.*?)```\s*###?\s*개선\s*후[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (Korean)'),
            # 헤딩 패턴 (영어)
            (r'###?\s*Before[:\s]*\n*```[\w]*\n(.*?)```\s*###?\s*After[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (English)'),
        ]

        before_after_pairs = []
        for pattern, desc in patterns_to_try:
            before_after_pairs = re.findall(pattern, markdown_result, re.DOTALL | re.IGNORECASE)
            if before_after_pairs:
                logger.info(f"Found {len(before_after_pairs)} before/after pairs using {desc} pattern")
                break
            else:
                logger.debug(f"No matches for {desc} pattern")

        if not before_after_pairs:
            logger.warning("No before/after pairs found in analysis result, falling back to improved blocks only")
            logger.debug(f"Markdown preview (first 1000 chars): {markdown_result[:1000]}")
            return self._extract_improved_blocks_only(markdown_result)

        # 3. 원본 코드에 개선사항 적용 (After 코드의 들여쓰기 유지)
        improved_code = original_code
        replacement_count = 0

        for before_code, after_code in before_after_pairs:
            before_code_stripped = before_code.strip()
            # After 코드는 strip하지 않고 원래 들여쓰기 유지
            # (LLM이 생성한 들여쓰기가 올바른 경우가 많음)
            after_code_with_indent = after_code.strip()

            # 원본 코드에서 "개선 전" 코드를 찾아서 "개선 후" 코드로 교체
            if before_code_stripped in improved_code:
                # 들여쓰기 감지
                match_start = improved_code.find(before_code_stripped)
                # 매칭 위치의 줄 번호 계산
                lines_before_match = improved_code[:match_start].split('\n')
                line_number = len(lines_before_match) - 1

                # 원본 코드의 해당 줄 들여쓰기 감지
                original_indent = self._detect_indentation(improved_code, line_number)
                logger.debug(f"Detected original indentation at line {line_number}: {repr(original_indent)}")

                # LLM이 생성한 After 코드에 이미 들여쓰기가 있는지 확인
                after_has_indent = any(line.startswith(' ') or line.startswith('\t')
                                      for line in after_code_with_indent.split('\n') if line.strip())

                if after_has_indent:
                    # After 코드에 이미 들여쓰기가 있으면 그대로 사용
                    logger.debug("After code already has indentation, using as-is")
                    indented_after = after_code_with_indent
                elif original_indent:
                    # Before에 들여쓰기가 있으면 적용
                    logger.debug(f"Applying original indent: {repr(original_indent)}")
                    indented_after = self._apply_indentation(after_code_with_indent, original_indent)
                else:
                    # Before에 들여쓰기가 없으면 기본 들여쓰기 적용
                    default_indent = "    "  # 4 spaces (C# 표준)
                    logger.debug("No indent in original, applying default 4-space indent")
                    indented_after = self._apply_indentation(after_code_with_indent, default_indent)

                # 교체
                improved_code = improved_code.replace(before_code_stripped, indented_after, 1)
                replacement_count += 1
                logger.info(f"Applied improvement {replacement_count}: replaced {len(before_code_stripped)} chars with {len(indented_after)} chars")
            else:
                # 정확히 일치하지 않으면 공백을 정규화해서 재시도
                # 공백/탭/개행을 단일 공백으로 정규화
                normalized_before = re.sub(r'\s+', ' ', before_code_stripped).strip()

                # 원본 코드에서 공백 정규화된 버전을 찾음
                lines = improved_code.split('\n')
                found = False

                for i in range(len(lines)):
                    # 여러 줄에 걸쳐 있을 수 있으므로 sliding window로 검색
                    for j in range(i + 1, min(i + 30, len(lines) + 1)):  # 최대 30줄까지 (증가)
                        candidate = '\n'.join(lines[i:j])
                        normalized_candidate = re.sub(r'\s+', ' ', candidate).strip()

                        if normalized_before == normalized_candidate:
                            # 원본 코드의 들여쓰기 감지
                            original_indent = self._detect_indentation('\n'.join(lines), i)
                            logger.debug(f"Detected original indentation at line {i} (normalized): {repr(original_indent)}")

                            # LLM이 생성한 After 코드에 이미 들여쓰기가 있는지 확인
                            after_has_indent = any(line.startswith(' ') or line.startswith('\t')
                                                  for line in after_code_with_indent.split('\n') if line.strip())

                            if after_has_indent:
                                # After 코드에 이미 들여쓰기가 있으면 그대로 사용
                                logger.debug("After code already has indentation (normalized), using as-is")
                                indented_after = after_code_with_indent
                            elif original_indent:
                                # Before에 들여쓰기가 있으면 적용
                                logger.debug(f"Applying original indent (normalized): {repr(original_indent)}")
                                indented_after = self._apply_indentation(after_code_with_indent, original_indent)
                            else:
                                # Before에 들여쓰기가 없으면 기본 들여쓰기 적용
                                default_indent = "    "  # 4 spaces (C# 표준)
                                logger.debug("No indent in original (normalized), applying default 4-space indent")
                                indented_after = self._apply_indentation(after_code_with_indent, default_indent)

                            # 찾았으면 해당 부분을 after_code로 교체
                            before_part = '\n'.join(lines[:i])
                            after_part = '\n'.join(lines[j:])

                            # 들여쓰기를 고려한 재조립
                            if before_part:
                                improved_code = before_part + '\n' + indented_after + '\n' + after_part
                            else:
                                improved_code = indented_after + '\n' + after_part

                            replacement_count += 1
                            found = True
                            logger.info(f"Applied improvement {replacement_count} (normalized matching, indent preserved)")
                            break

                    if found:
                        break

                if not found:
                    logger.warning(f"Could not find before code snippet #{replacement_count + 1} in original code")
                    logger.debug(f"Looking for (normalized): {normalized_before[:200]}...")

        if replacement_count > 0:
            logger.info(f"Successfully applied {replacement_count} improvements to create complete improved code ({len(improved_code)} chars)")
            return improved_code
        else:
            logger.warning("No improvements could be applied, falling back to improved blocks only")
            return self._extract_improved_blocks_only(markdown_result)

    def _extract_improved_blocks_only(self, markdown_result: str) -> Optional[str]:
        """개선 후 블록만 추출 (fallback 메서드)

        Args:
            markdown_result: 분석 결과 Markdown 텍스트

        Returns:
            개선 후 코드 블록들을 병합한 문자열
        """
        import re

        logger.info("Using fallback method: extracting improved blocks only")

        # 여러 패턴 시도 (템플릿 형식에 맞춤)
        alternative_patterns = [
            # Bold 마크다운 패턴 (가장 일반적)
            (r'\*\*After\*\*:\s*```[\w]*\n(.*?)```', 'Bold markdown (After)'),
            # 헤딩 패턴들
            (r'###?\s*After[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (After)'),
            (r'###?\s*개선\s*후[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (Korean after)'),
            (r'###?\s*개선[된\s]*코드[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (Korean improved)'),
            (r'###?\s*Improved[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (Improved)'),
            (r'###?\s*수정[된\s]*코드[:\s]*\n*```[\w]*\n(.*?)```', 'Heading (Korean modified)'),
        ]

        all_blocks = []
        for pattern, desc in alternative_patterns:
            matches = re.findall(pattern, markdown_result, re.DOTALL | re.IGNORECASE)
            all_blocks.extend(matches)
            if matches:
                logger.debug(f"Found {len(matches)} blocks using {desc} pattern")

        if all_blocks:
            separator = "\n\n# " + "=" * 50 + "\n\n"
            merged_code = separator.join(block.strip() for block in all_blocks)
            logger.info(f"Fallback: Extracted {len(all_blocks)} improved code blocks (total {len(merged_code)} chars)")
            return merged_code

        logger.warning("No improved code found in analysis result")
        return None

    # ============================================================
    # End Editor Dialog Methods
    # ============================================================
