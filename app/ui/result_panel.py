"""
Result Panel Widget - 코드 리뷰 결과 표시 위젯
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextBrowser, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional
from pathlib import Path
from datetime import datetime
import logging

from app.utils.markdown_renderer import MarkdownRenderer
from app.utils.markdown_parser import MarkdownParser

logger = logging.getLogger(__name__)


class ResultPanelWidget(QWidget):
    """코드 리뷰 결과 패널
    
    마크다운 형식의 리뷰 결과를 HTML로 렌더링하여 표시합니다.
    리포트 저장 기능을 제공합니다.
    
    Signals:
        report_saved: 리포트 저장 완료 시 발생 (파일 경로 전달)
        
    Examples:
        >>> panel = ResultPanelWidget()
        >>> panel.set_markdown("# Review Result\\n\\nThis is **bold**.")
        >>> panel.get_markdown()
        '# Review Result\\n\\nThis is **bold**.'
    """
    
    # Signals
    report_saved = Signal(str)  # 파일 경로
    
    def __init__(self, parent: Optional[QWidget] = None):
        """초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        # 가시성을 위해 밝은 스타일 사용 (monokai는 어두운 배경)
        self.markdown_renderer = MarkdownRenderer(style="default", use_css=True)
        self.markdown_parser = MarkdownParser()
        
        self._current_markdown = ""  # 현재 표시 중인 마크다운
        
        self._init_ui()
        logger.info("ResultPanelWidget initialized")
    
    def _init_ui(self):
        """UI 초기화"""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (제목 + 저장 버튼)
        header_layout = QHBoxLayout()
        
        title_label = QLabel("코드 리뷰 결과")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 저장 버튼
        self.save_button = QPushButton("리포트 저장")
        self.save_button.setMinimumWidth(100)
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setEnabled(False)  # 초기에는 비활성화
        header_layout.addWidget(self.save_button)
        
        # 복사 버튼
        self.copy_button = QPushButton("복사")
        self.copy_button.setMinimumWidth(80)
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.copy_button.setEnabled(False)
        header_layout.addWidget(self.copy_button)
        
        # 초기화 버튼
        self.clear_button = QPushButton("초기화")
        self.clear_button.setMinimumWidth(80)
        self.clear_button.clicked.connect(self.clear)
        self.clear_button.setEnabled(False)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Text Browser (HTML 렌더링 + 스크롤)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)  # 외부 링크 클릭 가능
        self.text_browser.setMinimumHeight(400)

        # 폰트 설정 (한글 지원)
        font = QFont("Malgun Gothic", 10)  # Windows: Malgun Gothic, macOS: AppleGothic
        self.text_browser.setFont(font)

        # 가시성을 위한 스타일 설정 (흰 배경)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.text_browser)
        
        self.setLayout(layout)
    
    def set_markdown(self, markdown_text: str):
        """마크다운 텍스트 설정 및 렌더링
        
        Args:
            markdown_text: 마크다운 텍스트
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_markdown("# Title\\n\\nParagraph")
        """
        self._current_markdown = markdown_text
        
        # HTML 렌더링
        html = self.markdown_renderer.render(markdown_text)
        
        # CSS 추가 (inline styles)
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {self.markdown_renderer.get_css()}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # QTextBrowser에 표시
        self.text_browser.setHtml(full_html)
        
        # 버튼 활성화
        self.save_button.setEnabled(bool(markdown_text))
        self.copy_button.setEnabled(bool(markdown_text))
        self.clear_button.setEnabled(bool(markdown_text))
        
        logger.debug(f"Set markdown ({len(markdown_text)} chars)")
    
    def get_markdown(self) -> str:
        """현재 표시 중인 마크다운 텍스트 반환
        
        Returns:
            마크다운 텍스트
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_markdown("# Test")
            >>> panel.get_markdown()
            '# Test'
        """
        return self._current_markdown
    
    def append_markdown(self, markdown_text: str):
        """기존 마크다운에 텍스트 추가
        
        Args:
            markdown_text: 추가할 마크다운 텍스트
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_markdown("# Title")
            >>> panel.append_markdown("\\n\\nNew content")
        """
        new_markdown = self._current_markdown + markdown_text
        self.set_markdown(new_markdown)
    
    def clear(self):
        """패널 초기화
        
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_markdown("# Test")
            >>> panel.clear()
            >>> panel.get_markdown()
            ''
        """
        self._current_markdown = ""
        self.text_browser.clear()
        
        # 버튼 비활성화
        self.save_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        
        logger.debug("Result panel cleared")
    
    def _on_save_clicked(self):
        """저장 버튼 클릭 이벤트"""
        if not self._current_markdown:
            return
        
        # 기본 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"code_review_{timestamp}.md"
        
        # 파일 다이얼로그
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "리포트 저장",
            default_filename,
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                # 파일 저장
                Path(file_path).write_text(self._current_markdown, encoding='utf-8')
                
                logger.info(f"Report saved to: {file_path}")
                
                # 성공 메시지
                QMessageBox.information(
                    self,
                    "저장 완료",
                    f"리포트가 저장되었습니다.\n\n{file_path}"
                )
                
                # Signal 발생
                self.report_saved.emit(file_path)
                
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
                
                QMessageBox.critical(
                    self,
                    "저장 실패",
                    f"리포트 저장 중 오류가 발생했습니다.\n\n{str(e)}"
                )
    
    def _on_copy_clicked(self):
        """복사 버튼 클릭 이벤트"""
        if not self._current_markdown:
            return
        
        # 클립보드에 마크다운 복사
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self._current_markdown)
        
        logger.debug("Markdown copied to clipboard")
        
        # 확인 메시지 (일시적)
        QMessageBox.information(
            self,
            "복사 완료",
            "마크다운 텍스트가 클립보드에 복사되었습니다."
        )
    
    def set_font_size(self, size: int):
        """폰트 크기 설정
        
        Args:
            size: 폰트 크기 (포인트)
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_font_size(12)
        """
        font = self.text_browser.font()
        font.setPointSize(size)
        self.text_browser.setFont(font)
        
        logger.debug(f"Font size set to: {size}")
    
    def set_style(self, style: str):
        """Pygments 스타일 변경
        
        Args:
            style: 스타일 이름 (monokai, vim, friendly 등)
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_style("vim")
        """
        self.markdown_renderer.set_style(style)
        
        # 현재 마크다운 재렌더링
        if self._current_markdown:
            self.set_markdown(self._current_markdown)
        
        logger.info(f"Style changed to: {style}")
    
    def get_statistics(self) -> dict:
        """현재 마크다운 통계 반환
        
        Returns:
            통계 정보 딕셔너리 (단어 수, 헤더 수, 코드 블록 수)
            
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.set_markdown("# Title\\n\\nContent")
            >>> stats = panel.get_statistics()
            >>> stats['header_count']
            1
        """
        if not self._current_markdown:
            return {
                'word_count': 0,
                'header_count': 0,
                'code_block_count': 0,
                'char_count': 0
            }
        
        # 통계 계산
        word_count = self.markdown_parser.count_words(self._current_markdown)
        headers = self.markdown_parser.extract_headers(self._current_markdown)
        code_blocks = self.markdown_parser.extract_code_blocks(self._current_markdown)
        
        return {
            'word_count': word_count,
            'header_count': len(headers),
            'code_block_count': len(code_blocks),
            'char_count': len(self._current_markdown)
        }
    
    def scroll_to_top(self):
        """스크롤을 최상단으로 이동
        
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.scroll_to_top()
        """
        scrollbar = self.text_browser.verticalScrollBar()
        scrollbar.setValue(0)
    
    def scroll_to_bottom(self):
        """스크롤을 최하단으로 이동
        
        Examples:
            >>> panel = ResultPanelWidget()
            >>> panel.scroll_to_bottom()
        """
        scrollbar = self.text_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
