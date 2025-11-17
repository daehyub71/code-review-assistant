"""
Tests for Day 8 Widgets (Before/After Editor, File Upload, Folder Select)
"""

import pytest
import tempfile
from pathlib import Path
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt

from app.ui.before_after_editor import BeforeAfterEditorWidget
from app.ui.file_upload_widget import FileUploadWidget
from app.ui.folder_select_widget import FolderSelectWidget
from app.utils.syntax_highlighter import (
    PygmentsSyntaxHighlighter,
    apply_syntax_highlighting,
    get_plain_text_with_line_numbers,
    highlight_code_to_html
)
from app.models.language import Language


class TestBeforeAfterEditorWidget:
    """BeforeAfterEditorWidget 테스트"""

    def test_initialization(self, qtbot: QtBot):
        """위젯 초기화 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        assert widget.before_editor is not None
        assert widget.after_editor is not None
        assert widget.sync_scroll_checkbox is not None

    def test_set_before_text(self, qtbot: QtBot):
        """Before 텍스트 설정 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        test_text = "def hello():\n    print('old')"
        widget.set_before_text(test_text)

        assert widget.get_before_text() == test_text

    def test_set_after_text(self, qtbot: QtBot):
        """After 텍스트 설정 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        test_text = "def hello():\n    print('new')"
        widget.set_after_text(test_text)

        assert widget.get_after_text() == test_text

    def test_clear(self, qtbot: QtBot):
        """Clear 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        widget.set_before_text("before text")
        widget.set_after_text("after text")
        widget.clear()

        assert widget.get_before_text() == ""
        assert widget.get_after_text() == ""

    def test_before_text_changed_signal(self, qtbot: QtBot):
        """Before 텍스트 변경 시그널 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.before_text_changed, timeout=1000) as blocker:
            widget.set_before_text("new text")

        assert blocker.args[0] == "new text"

    def test_after_text_changed_signal(self, qtbot: QtBot):
        """After 텍스트 변경 시그널 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.after_text_changed, timeout=1000) as blocker:
            widget.set_after_text("new text")

        assert blocker.args[0] == "new text"

    def test_set_read_only(self, qtbot: QtBot):
        """읽기 전용 설정 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        widget.set_read_only(True, False)

        assert widget.before_editor.isReadOnly() is True
        assert widget.after_editor.isReadOnly() is False

    def test_enable_sync_scroll(self, qtbot: QtBot):
        """스크롤 동기화 활성화 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        widget.enable_sync_scroll(True)
        assert widget.sync_scroll_checkbox.isChecked() is True

        widget.enable_sync_scroll(False)
        assert widget.sync_scroll_checkbox.isChecked() is False

    def test_widget_visible(self, qtbot: QtBot):
        """위젯 표시 테스트"""
        widget = BeforeAfterEditorWidget()
        qtbot.addWidget(widget)

        widget.show()
        qtbot.waitExposed(widget)

        assert widget.isVisible()
        assert widget.before_editor.isVisible()
        assert widget.after_editor.isVisible()


class TestFileUploadWidget:
    """FileUploadWidget 테스트"""

    def test_initialization(self, qtbot: QtBot):
        """위젯 초기화 테스트"""
        widget = FileUploadWidget(max_size_mb=1.0)
        qtbot.addWidget(widget)

        assert widget.max_size_mb == 1.0
        assert widget.max_size_bytes == 1024 * 1024
        assert widget.selected_file_path is None

    def test_set_max_size(self, qtbot: QtBot):
        """최대 파일 크기 설정 테스트"""
        widget = FileUploadWidget(max_size_mb=1.0)
        qtbot.addWidget(widget)

        widget.set_max_size(2.0)
        assert widget.max_size_mb == 2.0
        assert widget.max_size_bytes == 2 * 1024 * 1024

    def test_set_file_filter(self, qtbot: QtBot):
        """파일 필터 설정 테스트"""
        widget = FileUploadWidget()
        qtbot.addWidget(widget)

        widget.set_file_filter("Python Files (*.py)")
        assert widget.file_filter == "Python Files (*.py)"

    def test_get_selected_file_none(self, qtbot: QtBot):
        """선택된 파일이 없을 때 테스트"""
        widget = FileUploadWidget()
        qtbot.addWidget(widget)

        assert widget.get_selected_file() is None

    def test_read_file_content_no_file(self, qtbot: QtBot):
        """파일 선택 없이 읽기 시도 테스트"""
        widget = FileUploadWidget()
        qtbot.addWidget(widget)

        content = widget.read_file_content()
        assert content is None

    def test_widget_visible(self, qtbot: QtBot):
        """위젯 표시 테스트"""
        widget = FileUploadWidget()
        qtbot.addWidget(widget)

        widget.show()
        qtbot.waitExposed(widget)

        assert widget.isVisible()
        assert widget.select_button.isVisible()


class TestFolderSelectWidget:
    """FolderSelectWidget 테스트"""

    def test_initialization(self, qtbot: QtBot):
        """위젯 초기화 테스트"""
        widget = FolderSelectWidget(max_files=100)
        qtbot.addWidget(widget)

        assert widget.max_files == 100
        assert widget.file_extension == "*.py"
        assert widget.selected_folder_path is None
        assert len(widget.found_files) == 0

    def test_set_max_files(self, qtbot: QtBot):
        """최대 파일 개수 설정 테스트"""
        widget = FolderSelectWidget(max_files=100)
        qtbot.addWidget(widget)

        widget.set_max_files(200)
        assert widget.max_files == 200

    def test_set_file_extension(self, qtbot: QtBot):
        """파일 확장자 설정 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        widget.set_file_extension("*.java")
        assert widget.file_extension == "*.java"

    def test_get_selected_folder_none(self, qtbot: QtBot):
        """선택된 폴더가 없을 때 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        assert widget.get_selected_folder() is None

    def test_get_found_files_empty(self, qtbot: QtBot):
        """발견된 파일이 없을 때 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        assert len(widget.get_found_files()) == 0

    def test_get_file_count(self, qtbot: QtBot):
        """파일 개수 확인 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        assert widget.get_file_count() == 0

    def test_widget_visible(self, qtbot: QtBot):
        """위젯 표시 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        widget.show()
        qtbot.waitExposed(widget)

        assert widget.isVisible()
        assert widget.select_button.isVisible()
        assert widget.file_list_widget.isVisible()


class TestPygmentsSyntaxHighlighter:
    """PygmentsSyntaxHighlighter 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        highlighter = PygmentsSyntaxHighlighter(style="monokai")
        assert highlighter.style == "monokai"

    def test_highlight_code_python(self):
        """Python 코드 강조 테스트"""
        highlighter = PygmentsSyntaxHighlighter()
        code = "def hello():\n    print('Hello')"
        html = highlighter.highlight_code(code, Language.PYTHON)

        assert isinstance(html, str)
        assert len(html) > len(code)  # HTML은 원본보다 길어야 함
        assert "def" in html  # 키워드가 포함되어야 함

    def test_highlight_code_java(self):
        """Java 코드 강조 테스트"""
        highlighter = PygmentsSyntaxHighlighter()
        code = "public class Hello {\n    public static void main(String[] args) {}\n}"
        html = highlighter.highlight_code(code, Language.JAVA)

        assert isinstance(html, str)
        assert len(html) > len(code)

    def test_get_available_styles(self):
        """사용 가능한 스타일 목록 테스트"""
        highlighter = PygmentsSyntaxHighlighter()
        styles = highlighter.get_available_styles()

        assert isinstance(styles, list)
        assert len(styles) > 0
        assert "monokai" in styles
        assert "vim" in styles

    def test_set_style(self):
        """스타일 설정 테스트"""
        highlighter = PygmentsSyntaxHighlighter(style="monokai")
        highlighter.set_style("github")
        assert highlighter.style == "github"


class TestSyntaxHighlighterHelpers:
    """Syntax Highlighter Helper Functions 테스트"""

    def test_get_plain_text_with_line_numbers(self):
        """줄 번호 추가 테스트"""
        code = "def hello():\n    print('hello')"
        numbered = get_plain_text_with_line_numbers(code)

        assert "1 |" in numbered
        assert "2 |" in numbered
        assert "def hello():" in numbered
        assert "print('hello')" in numbered

    def test_highlight_code_to_html(self):
        """HTML 변환 테스트"""
        code = "print('hello')"
        html = highlight_code_to_html(code, Language.PYTHON)

        assert isinstance(html, str)
        assert len(html) > len(code)
        assert "print" in html


class TestIntegration:
    """통합 테스트"""

    def test_before_after_editor_with_syntax_highlighting(self, qtbot: QtBot):
        """Before/After 에디터와 구문 강조 통합 테스트"""
        editor = BeforeAfterEditorWidget()
        qtbot.addWidget(editor)

        before_code = "def old():\n    print('old')"
        after_code = "def new():\n    print('new')"

        editor.set_before_text(before_code)
        editor.set_after_text(after_code)

        # 구문 강조 적용 테스트
        highlighter = PygmentsSyntaxHighlighter()
        before_html = highlighter.highlight_code(before_code, Language.PYTHON)
        after_html = highlighter.highlight_code(after_code, Language.PYTHON)

        assert isinstance(before_html, str)
        assert isinstance(after_html, str)

    def test_file_upload_with_temp_file(self, qtbot: QtBot):
        """임시 파일을 사용한 파일 업로드 테스트"""
        widget = FileUploadWidget()
        qtbot.addWidget(widget)

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('test')")
            temp_file = f.name

        try:
            # 파일 크기 확인 (작은 파일이므로 통과해야 함)
            file_size = Path(temp_file).stat().st_size
            assert file_size < widget.max_size_bytes

        finally:
            # 임시 파일 삭제
            Path(temp_file).unlink()

    def test_folder_select_with_temp_dir(self, qtbot: QtBot):
        """임시 디렉토리를 사용한 폴더 선택 테스트"""
        widget = FolderSelectWidget()
        qtbot.addWidget(widget)

        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # 테스트 파일 생성
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('test')")

            # 파일 검색 테스트
            files = widget._find_files_in_folder(temp_dir)
            assert len(files) == 1
            assert "test.py" in files[0]
