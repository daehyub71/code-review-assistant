"""
Syntax Highlighter - Pygments 기반 구문 강조
"""

from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import Qt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from typing import Optional
import logging

from app.models.language import Language

logger = logging.getLogger(__name__)


class PygmentsSyntaxHighlighter:
    """Pygments 기반 구문 강조 도우미 클래스

    QTextEdit에 Pygments를 사용한 구문 강조를 적용합니다.

    Examples:
        >>> highlighter = PygmentsSyntaxHighlighter()
        >>> code = "def hello():\n    print('Hello')"
        >>> html = highlighter.highlight_code(code, Language.PYTHON)
    """

    def __init__(self, style: str = "monokai"):
        """초기화

        Args:
            style: Pygments 스타일 (기본값: "monokai")
        """
        self.style = style
        logger.info(f"PygmentsSyntaxHighlighter initialized with style: {style}")

    def highlight_code(self, code: str, language: Language) -> str:
        """코드에 구문 강조 적용 (HTML 반환)

        Args:
            code: 강조할 코드
            language: 프로그래밍 언어

        Returns:
            HTML 형식의 강조된 코드

        Examples:
            >>> highlighter = PygmentsSyntaxHighlighter()
            >>> html = highlighter.highlight_code("print('hello')", Language.PYTHON)
        """
        try:
            # Language enum을 Pygments lexer 이름으로 변환
            lexer_name = self._get_lexer_name(language)
            lexer = get_lexer_by_name(lexer_name)

            # HTML Formatter
            formatter = HtmlFormatter(
                style=self.style,
                noclasses=True,  # Inline CSS
                nowrap=False
            )

            # Highlight
            html = highlight(code, lexer, formatter)
            logger.debug(f"Code highlighted: {len(code)} chars, language: {language.value}")
            return html

        except Exception as e:
            logger.error(f"Failed to highlight code: {e}")
            # 강조 실패 시 원본 반환 (pre 태그로 감싸기)
            return f"<pre>{code}</pre>"

    def apply_to_text_edit(self, text_edit: QTextEdit, code: str, language: Language):
        """QTextEdit에 구문 강조된 코드 적용

        Args:
            text_edit: QTextEdit 위젯
            code: 강조할 코드
            language: 프로그래밍 언어

        Examples:
            >>> highlighter = PygmentsSyntaxHighlighter()
            >>> text_edit = QTextEdit()
            >>> highlighter.apply_to_text_edit(text_edit, "print('hello')", Language.PYTHON)
        """
        html = self.highlight_code(code, language)
        text_edit.setHtml(html)
        logger.debug(f"Syntax highlighting applied to QTextEdit")

    def _get_lexer_name(self, language: Language) -> str:
        """Language enum을 Pygments lexer 이름으로 변환

        Args:
            language: Language enum

        Returns:
            Pygments lexer 이름

        Raises:
            ValueError: 지원하지 않는 언어
        """
        lexer_mapping = {
            Language.PYTHON: "python",
            Language.JAVA: "java",
            Language.CSHARP: "csharp",
            Language.VUE: "vue",
        }

        if language not in lexer_mapping:
            raise ValueError(f"Unsupported language: {language}")

        return lexer_mapping[language]

    def get_available_styles(self) -> list[str]:
        """사용 가능한 Pygments 스타일 목록 반환

        Returns:
            스타일 이름 리스트

        Examples:
            >>> highlighter = PygmentsSyntaxHighlighter()
            >>> styles = highlighter.get_available_styles()
            >>> print(styles)
            ['monokai', 'vim', 'github', ...]
        """
        from pygments.styles import get_all_styles
        return list(get_all_styles())

    def set_style(self, style: str):
        """스타일 설정

        Args:
            style: Pygments 스타일 이름

        Examples:
            >>> highlighter = PygmentsSyntaxHighlighter()
            >>> highlighter.set_style("github")
        """
        self.style = style
        logger.info(f"Style set to: {style}")


def apply_syntax_highlighting(
    text_edit: QTextEdit,
    code: str,
    language: Language,
    style: str = "monokai"
):
    """QTextEdit에 구문 강조 적용 (편의 함수)

    Args:
        text_edit: QTextEdit 위젯
        code: 강조할 코드
        language: 프로그래밍 언어
        style: Pygments 스타일 (기본값: "monokai")

    Examples:
        >>> text_edit = QTextEdit()
        >>> apply_syntax_highlighting(text_edit, "print('hello')", Language.PYTHON)
    """
    highlighter = PygmentsSyntaxHighlighter(style=style)
    highlighter.apply_to_text_edit(text_edit, code, language)


def get_plain_text_with_line_numbers(code: str) -> str:
    """코드에 줄 번호 추가

    Args:
        code: 원본 코드

    Returns:
        줄 번호가 추가된 코드

    Examples:
        >>> code = "def hello():\n    print('hello')"
        >>> numbered = get_plain_text_with_line_numbers(code)
        >>> print(numbered)
        1 | def hello():
        2 |     print('hello')
    """
    lines = code.split("\n")
    numbered_lines = []

    for i, line in enumerate(lines, start=1):
        numbered_lines.append(f"{i:4d} | {line}")

    return "\n".join(numbered_lines)


def highlight_code_to_html(code: str, language: Language, style: str = "monokai") -> str:
    """코드를 HTML로 변환 (구문 강조 포함)

    Args:
        code: 강조할 코드
        language: 프로그래밍 언어
        style: Pygments 스타일

    Returns:
        HTML 문자열

    Examples:
        >>> html = highlight_code_to_html("print('hello')", Language.PYTHON)
    """
    highlighter = PygmentsSyntaxHighlighter(style=style)
    return highlighter.highlight_code(code, language)


class SimpleSyntaxHighlighter(QSyntaxHighlighter):
    """간단한 Qt 기반 구문 강조기

    Pygments 대신 Qt의 QSyntaxHighlighter를 사용한 간단한 구현.
    키워드만 강조합니다.

    Examples:
        >>> text_edit = QTextEdit()
        >>> highlighter = SimpleSyntaxHighlighter(text_edit.document(), Language.PYTHON)
    """

    def __init__(self, document, language: Language):
        """초기화

        Args:
            document: QTextDocument
            language: 프로그래밍 언어
        """
        super().__init__(document)
        self.language = language
        self._init_formats()

    def _init_formats(self):
        """포맷 초기화"""
        # Keyword format
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#ff79c6"))  # Pink
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        # Comment format
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6272a4"))  # Gray

        # String format
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#f1fa8c"))  # Yellow

    def highlightBlock(self, text: str):
        """블록 강조 (QSyntaxHighlighter 오버라이드)

        Args:
            text: 강조할 텍스트
        """
        # 간단한 키워드 강조 (예시)
        keywords = ["def", "class", "import", "from", "if", "else", "for", "while", "return"]

        for keyword in keywords:
            index = text.find(keyword)
            while index >= 0:
                self.setFormat(index, len(keyword), self.keyword_format)
                index = text.find(keyword, index + len(keyword))
