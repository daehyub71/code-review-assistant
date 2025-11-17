"""
Markdown Renderer - 마크다운 렌더링 유틸리티
"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MarkdownRenderer:
    """마크다운 렌더러
    
    python-markdown과 Pygments를 사용하여 마크다운을 HTML로 렌더링합니다.
    코드 블록에는 자동으로 syntax highlighting이 적용됩니다.
    
    Features:
        - Fenced code blocks with syntax highlighting
        - Tables
        - Table of contents
        - Korean text support
        
    Examples:
        >>> renderer = MarkdownRenderer()
        >>> html = renderer.render("# Hello\\n\\nThis is **bold**.")
        >>> print(html)
        <h1>Hello</h1>
        <p>This is <strong>bold</strong>.</p>
    """
    
    def __init__(self, style: str = "monokai", use_css: bool = True):
        """초기화
        
        Args:
            style: Pygments 스타일 (monokai, vim, friendly 등)
            use_css: True면 CSS 클래스 사용, False면 인라인 스타일 사용
        """
        self.style = style
        self.use_css = use_css
        
        # Markdown extensions 설정
        self.extensions = [
            FencedCodeExtension(),
            CodeHiliteExtension(
                pygments_style=style,
                noclasses=not use_css,  # use_css=True면 클래스 사용
                linenums=False
            ),
            TableExtension(),
            TocExtension(),
            'nl2br',  # 줄바꿈을 <br>로 변환
            'sane_lists',  # 리스트 파싱 개선
        ]
        
        # Markdown 인스턴스
        self.md = markdown.Markdown(extensions=self.extensions)
        
        logger.info(f"MarkdownRenderer initialized with style: {style}")
    
    def render(self, text: str) -> str:
        """마크다운 텍스트를 HTML로 렌더링
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            렌더링된 HTML 문자열
            
        Examples:
            >>> renderer = MarkdownRenderer()
            >>> html = renderer.render("# Title\\n\\nParagraph")
            >>> "h1" in html
            True
        """
        if not text:
            return ""
        
        try:
            # Markdown 렌더링
            html = self.md.convert(text)
            
            # Reset markdown instance for next use
            self.md.reset()
            
            logger.debug(f"Rendered {len(text)} chars to {len(html)} chars of HTML")
            return html
            
        except Exception as e:
            logger.error(f"Markdown rendering failed: {e}")
            # Fallback: 텍스트를 <pre> 태그로 감싸서 반환
            return f"<pre>{text}</pre>"
    
    def render_with_css(self, text: str) -> Dict[str, str]:
        """마크다운 렌더링 + CSS 스타일시트 반환
        
        코드 하이라이팅을 위한 CSS를 별도로 생성합니다.
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            dict with "html" and "css" keys
            
        Examples:
            >>> renderer = MarkdownRenderer(use_css=True)
            >>> result = renderer.render_with_css("```python\\nprint('hi')\\n```")
            >>> "html" in result and "css" in result
            True
        """
        html = self.render(text)
        css = self.get_css()
        
        return {
            "html": html,
            "css": css
        }
    
    def get_css(self) -> str:
        """Pygments CSS 스타일시트 생성
        
        Returns:
            CSS 문자열
            
        Examples:
            >>> renderer = MarkdownRenderer()
            >>> css = renderer.get_css()
            >>> ".codehilite" in css or ".highlight" in css
            True
        """
        formatter = HtmlFormatter(style=self.style)
        css = formatter.get_style_defs('.codehilite')
        
        # 추가 스타일 (테이블, 일반 텍스트 등)
        additional_css = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        
        h3 {
            font-size: 1.25em;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }
        
        th {
            background-color: #f6f8fa;
            font-weight: 600;
        }
        
        tr:hover {
            background-color: #f6f8fa;
        }
        
        code {
            background-color: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #ddd;
            padding-left: 16px;
            color: #666;
            margin: 16px 0;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """
        
        return css + "\n" + additional_css
    
    def render_code_block(self, code: str, language: Optional[str] = None) -> str:
        """코드 블록만 렌더링 (마크다운 없이)
        
        Args:
            code: 소스 코드
            language: 언어 이름 (python, java, csharp 등). None이면 자동 감지
            
        Returns:
            HTML 문자열
            
        Examples:
            >>> renderer = MarkdownRenderer()
            >>> html = renderer.render_code_block("print('hi')", "python")
            >>> "print" in html
            True
        """
        try:
            if language:
                # 언어 명시적 지정
                lexer = get_lexer_by_name(language)
            else:
                # 자동 감지
                lexer = guess_lexer(code)
            
            formatter = HtmlFormatter(
                style=self.style,
                noclasses=not self.use_css,
                linenos=False
            )
            
            html = highlight(code, lexer, formatter)
            logger.debug(f"Rendered code block ({language or 'auto'}) to HTML")
            return html
            
        except ClassNotFound:
            logger.warning(f"Lexer not found for language: {language}")
            # Fallback: plain text
            return f"<pre><code>{code}</code></pre>"
        except Exception as e:
            logger.error(f"Code block rendering failed: {e}")
            return f"<pre><code>{code}</code></pre>"
    
    def set_style(self, style: str):
        """Pygments 스타일 변경
        
        Args:
            style: 스타일 이름 (monokai, vim, friendly 등)
            
        Examples:
            >>> renderer = MarkdownRenderer()
            >>> renderer.set_style("vim")
            >>> renderer.style
            'vim'
        """
        self.style = style
        
        # Markdown 인스턴스 재생성
        self.md = markdown.Markdown(extensions=self.extensions)
        
        logger.info(f"Style changed to: {style}")
    
    def get_available_styles(self) -> list:
        """사용 가능한 Pygments 스타일 목록 반환
        
        Returns:
            스타일 이름 리스트
            
        Examples:
            >>> renderer = MarkdownRenderer()
            >>> styles = renderer.get_available_styles()
            >>> len(styles) > 0
            True
        """
        from pygments.styles import get_all_styles
        return list(get_all_styles())


def render_markdown(text: str, style: str = "monokai") -> str:
    """마크다운 렌더링 헬퍼 함수
    
    Args:
        text: 마크다운 텍스트
        style: Pygments 스타일
        
    Returns:
        렌더링된 HTML
        
    Examples:
        >>> html = render_markdown("# Hello")
        >>> "h1" in html
        True
    """
    renderer = MarkdownRenderer(style=style)
    return renderer.render(text)


def render_code_to_html(code: str, language: str, style: str = "monokai") -> str:
    """코드를 HTML로 렌더링 (헬퍼 함수)
    
    Args:
        code: 소스 코드
        language: 언어 이름
        style: Pygments 스타일
        
    Returns:
        HTML 문자열
        
    Examples:
        >>> html = render_code_to_html("print('hi')", "python")
        >>> "print" in html
        True
    """
    renderer = MarkdownRenderer(style=style)
    return renderer.render_code_block(code, language)
