"""
Tests for Day 9 Components (Markdown Renderer, Parser, Result Panel)
"""

import pytest
import tempfile
from pathlib import Path
from pytestqt.qtbot import QtBot

from app.utils.markdown_renderer import (
    MarkdownRenderer,
    render_markdown,
    render_code_to_html
)
from app.utils.markdown_parser import (
    MarkdownParser,
    CodeBlock,
    Header,
    extract_code_blocks,
    extract_headers,
    get_plain_text
)
from app.ui.result_panel import ResultPanelWidget


class TestMarkdownRenderer:
    """MarkdownRenderer 테스트"""
    
    def test_initialization(self):
        """초기화 테스트"""
        renderer = MarkdownRenderer()
        assert renderer.style == "monokai"
        assert renderer.use_css is True
    
    def test_render_simple_markdown(self):
        """간단한 마크다운 렌더링"""
        renderer = MarkdownRenderer()
        html = renderer.render("# Hello\n\nThis is **bold**.")
        
        assert "<h1" in html
        assert "Hello" in html
        assert "<strong>" in html or "bold" in html
    
    def test_render_empty_text(self):
        """빈 텍스트 렌더링"""
        renderer = MarkdownRenderer()
        html = renderer.render("")
        assert html == ""
    
    def test_render_code_block(self):
        """코드 블록 렌더링"""
        renderer = MarkdownRenderer()
        markdown = "```python\nprint('hello')\n```"
        html = renderer.render(markdown)
        
        assert "print" in html
        assert "hello" in html
    
    def test_render_with_css(self):
        """CSS 포함 렌더링"""
        renderer = MarkdownRenderer(use_css=True)
        result = renderer.render_with_css("# Title")
        
        assert "html" in result
        assert "css" in result
        assert isinstance(result["html"], str)
        assert isinstance(result["css"], str)
    
    def test_get_css(self):
        """CSS 생성 테스트"""
        renderer = MarkdownRenderer()
        css = renderer.get_css()
        
        assert isinstance(css, str)
        assert len(css) > 0
        assert "body" in css or "codehilite" in css
    
    def test_render_code_block_with_language(self):
        """언어 지정 코드 블록 렌더링"""
        renderer = MarkdownRenderer()
        html = renderer.render_code_block("print('hi')", "python")
        
        assert isinstance(html, str)
        assert "print" in html
    
    def test_render_code_block_without_language(self):
        """언어 미지정 코드 블록 렌더링"""
        renderer = MarkdownRenderer()
        html = renderer.render_code_block("def hello(): pass", None)
        
        assert isinstance(html, str)
        assert "hello" in html
    
    def test_set_style(self):
        """스타일 변경 테스트"""
        renderer = MarkdownRenderer(style="monokai")
        renderer.set_style("vim")
        assert renderer.style == "vim"
    
    def test_get_available_styles(self):
        """사용 가능한 스타일 목록 테스트"""
        renderer = MarkdownRenderer()
        styles = renderer.get_available_styles()
        
        assert isinstance(styles, list)
        assert len(styles) > 0
        assert "monokai" in styles
        assert "vim" in styles
    
    def test_render_table(self):
        """테이블 렌더링 테스트"""
        renderer = MarkdownRenderer()
        markdown = """
| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
        html = renderer.render(markdown)
        
        assert "<table" in html
        assert "Column 1" in html
        assert "Cell 1" in html
    
    def test_helper_function_render_markdown(self):
        """헬퍼 함수 테스트"""
        html = render_markdown("# Test")
        assert "Test" in html
    
    def test_helper_function_render_code(self):
        """코드 렌더링 헬퍼 함수 테스트"""
        html = render_code_to_html("print('test')", "python")
        assert "print" in html


class TestMarkdownParser:
    """MarkdownParser 테스트"""
    
    def test_extract_code_blocks(self):
        """코드 블록 추출 테스트"""
        parser = MarkdownParser()
        markdown = "```python\nprint('hi')\n```"
        blocks = parser.extract_code_blocks(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print" in blocks[0].code
    
    def test_extract_code_blocks_multiple(self):
        """다중 코드 블록 추출"""
        parser = MarkdownParser()
        markdown = """
```python
code1
```

```java
code2
```
"""
        blocks = parser.extract_code_blocks(markdown)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "java"
    
    def test_extract_code_blocks_no_language(self):
        """언어 미지정 코드 블록"""
        parser = MarkdownParser()
        markdown = "```\ncode\n```"
        blocks = parser.extract_code_blocks(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].language is None
    
    def test_extract_headers(self):
        """헤더 추출 테스트"""
        parser = MarkdownParser()
        markdown = "# H1\n## H2\n### H3"
        headers = parser.extract_headers(markdown)
        
        assert len(headers) == 3
        assert headers[0].level == 1
        assert headers[0].text == "H1"
        assert headers[1].level == 2
        assert headers[2].level == 3
    
    def test_extract_links(self):
        """링크 추출 테스트"""
        parser = MarkdownParser()
        markdown = "[Google](https://google.com) and [GitHub](https://github.com)"
        links = parser.extract_links(markdown)
        
        assert len(links) == 2
        assert links[0] == ("Google", "https://google.com")
        assert links[1] == ("GitHub", "https://github.com")
    
    def test_extract_list_items(self):
        """리스트 아이템 추출 테스트"""
        parser = MarkdownParser()
        markdown = "- Item 1\n- Item 2\n- Item 3"
        items = parser.extract_list_items(markdown)
        
        assert len(items) == 3
        assert "Item 1" in items
        assert "Item 2" in items
    
    def test_get_toc(self):
        """목차 생성 테스트"""
        parser = MarkdownParser()
        markdown = "# Chapter 1\n## Section 1.1\n# Chapter 2"
        toc = parser.get_toc(markdown)
        
        assert "Chapter 1" in toc
        assert "Chapter 2" in toc
        assert "Table of Contents" in toc
    
    def test_count_words(self):
        """단어 수 카운트 테스트"""
        parser = MarkdownParser()
        text = "Hello world! This is a test."
        count = parser.count_words(text)
        
        assert count == 6
    
    def test_count_words_exclude_code(self):
        """코드 제외 단어 카운트"""
        parser = MarkdownParser()
        text = "Hello\n```python\ncode here\n```\nworld"
        count = parser.count_words(text, exclude_code=True)
        
        # "Hello" and "world" only
        assert count == 2
    
    def test_remove_code_blocks(self):
        """코드 블록 제거 테스트"""
        parser = MarkdownParser()
        text = "Text\n```python\ncode\n```\nMore text"
        result = parser.remove_code_blocks(text)
        
        assert "code" not in result
        assert "Text" in result
        assert "More text" in result
    
    def test_get_plain_text(self):
        """플레인 텍스트 변환 테스트"""
        parser = MarkdownParser()
        markdown = "# Title\n\n**bold** and *italic*"
        plain = parser.get_plain_text(markdown)
        
        assert "#" not in plain
        assert "**" not in plain
        assert "*" not in plain
        assert "bold" in plain
        assert "italic" in plain
    
    def test_split_by_headers(self):
        """헤더 기준 분할 테스트"""
        parser = MarkdownParser()
        markdown = "# Section 1\nContent 1\n# Section 2\nContent 2"
        sections = parser.split_by_headers(markdown, level=1)
        
        assert len(sections) == 2
        assert "Section 1" in sections
        assert "Section 2" in sections
        assert "Content 1" in sections["Section 1"]
    
    def test_helper_function_extract_code_blocks(self):
        """코드 블록 추출 헬퍼 함수"""
        markdown = "```python\ncode\n```"
        blocks = extract_code_blocks(markdown)
        assert len(blocks) == 1
    
    def test_helper_function_extract_headers(self):
        """헤더 추출 헬퍼 함수"""
        markdown = "# Title"
        headers = extract_headers(markdown)
        assert len(headers) == 1
    
    def test_helper_function_get_plain_text(self):
        """플레인 텍스트 헬퍼 함수"""
        markdown = "**bold**"
        plain = get_plain_text(markdown)
        assert "**" not in plain


class TestResultPanelWidget:
    """ResultPanelWidget 테스트"""
    
    def test_initialization(self, qtbot: QtBot):
        """초기화 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        assert panel.text_browser is not None
        assert panel.save_button is not None
        assert panel.copy_button is not None
        assert panel.clear_button is not None
    
    def test_set_markdown(self, qtbot: QtBot):
        """마크다운 설정 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        markdown = "# Test\n\nThis is **bold**."
        panel.set_markdown(markdown)
        
        assert panel.get_markdown() == markdown
        assert panel.save_button.isEnabled()
    
    def test_get_markdown_empty(self, qtbot: QtBot):
        """빈 마크다운 가져오기"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        assert panel.get_markdown() == ""
    
    def test_append_markdown(self, qtbot: QtBot):
        """마크다운 추가 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        panel.set_markdown("# Title")
        panel.append_markdown("\n\nNew content")
        
        markdown = panel.get_markdown()
        assert "Title" in markdown
        assert "New content" in markdown
    
    def test_clear(self, qtbot: QtBot):
        """초기화 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        panel.set_markdown("# Test")
        panel.clear()
        
        assert panel.get_markdown() == ""
        assert not panel.save_button.isEnabled()
    
    def test_report_saved_signal(self, qtbot: QtBot):
        """리포트 저장 시그널 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        # Signal spy
        with qtbot.waitSignal(panel.report_saved, timeout=5000, raising=False):
            # 실제로 파일 다이얼로그를 띄우지 않고 테스트하기 어려움
            # 이 테스트는 수동 테스트로 진행
            pass
    
    def test_set_font_size(self, qtbot: QtBot):
        """폰트 크기 설정 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        panel.set_font_size(14)
        assert panel.text_browser.font().pointSize() == 14
    
    def test_set_style(self, qtbot: QtBot):
        """스타일 변경 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        panel.set_style("vim")
        assert panel.markdown_renderer.style == "vim"
    
    def test_get_statistics_empty(self, qtbot: QtBot):
        """빈 텍스트 통계"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        stats = panel.get_statistics()
        assert stats['word_count'] == 0
        assert stats['header_count'] == 0
        assert stats['code_block_count'] == 0
    
    def test_get_statistics_with_content(self, qtbot: QtBot):
        """콘텐츠 통계"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        markdown = "# Title\n\nSome text\n\n```python\ncode\n```"
        panel.set_markdown(markdown)
        
        stats = panel.get_statistics()
        assert stats['header_count'] == 1
        assert stats['code_block_count'] == 1
        assert stats['word_count'] > 0
    
    def test_scroll_to_top(self, qtbot: QtBot):
        """스크롤 최상단 이동"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        # 긴 텍스트 설정
        long_text = "# Title\n\n" + ("Line\n\n" * 100)
        panel.set_markdown(long_text)
        
        panel.scroll_to_top()
        scrollbar = panel.text_browser.verticalScrollBar()
        assert scrollbar.value() == 0
    
    def test_scroll_to_bottom(self, qtbot: QtBot):
        """스크롤 최하단 이동"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        # 긴 텍스트 설정
        long_text = "# Title\n\n" + ("Line\n\n" * 100)
        panel.set_markdown(long_text)
        
        panel.scroll_to_bottom()
        scrollbar = panel.text_browser.verticalScrollBar()
        assert scrollbar.value() == scrollbar.maximum()
    
    def test_widget_visible(self, qtbot: QtBot):
        """위젯 표시 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        panel.show()
        qtbot.waitExposed(panel)
        
        assert panel.isVisible()
        assert panel.text_browser.isVisible()
        assert panel.save_button.isVisible()


class TestIntegration:
    """통합 테스트"""
    
    def test_markdown_render_and_parse(self):
        """렌더링 후 파싱 통합 테스트"""
        markdown = "# Title\n\n```python\nprint('hi')\n```"
        
        # 렌더링
        renderer = MarkdownRenderer()
        html = renderer.render(markdown)
        assert "Title" in html
        
        # 파싱
        parser = MarkdownParser()
        headers = parser.extract_headers(markdown)
        code_blocks = parser.extract_code_blocks(markdown)
        
        assert len(headers) == 1
        assert len(code_blocks) == 1
    
    def test_result_panel_with_complex_markdown(self, qtbot: QtBot):
        """복잡한 마크다운 표시 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        markdown = """
# Code Review Report

## Issues Found

### Null Reference
- Issue 1
- Issue 2

### Performance
```python
# Bad
for i in range(len(arr)):
    print(arr[i])

# Good
for item in arr:
    print(item)
```

## Summary
Total issues: 2
"""
        
        panel.set_markdown(markdown)
        
        # 통계 확인
        stats = panel.get_statistics()
        assert stats['header_count'] >= 3
        assert stats['code_block_count'] >= 1
        
        # 마크다운 확인
        assert "Code Review Report" in panel.get_markdown()
    
    def test_save_and_load_report(self, qtbot: QtBot):
        """리포트 저장 및 로드 테스트"""
        panel = ResultPanelWidget()
        qtbot.addWidget(panel)
        
        markdown = "# Test Report\n\nThis is a test."
        panel.set_markdown(markdown)
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(panel.get_markdown())
            temp_file = f.name
        
        try:
            # 파일에서 다시 읽기
            content = Path(temp_file).read_text(encoding='utf-8')
            assert content == markdown
        finally:
            # 임시 파일 삭제
            Path(temp_file).unlink()
