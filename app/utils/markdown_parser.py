"""
Markdown Parser - 마크다운 파싱 유틸리티
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeBlock:
    """코드 블록 정보"""
    language: Optional[str]  # 언어 (python, java 등). None이면 언어 지정 없음
    code: str  # 코드 내용
    start_line: int  # 시작 줄 번호 (0-based)
    end_line: int  # 종료 줄 번호 (0-based)


@dataclass
class Header:
    """헤더 정보"""
    level: int  # 헤더 레벨 (1-6)
    text: str  # 헤더 텍스트
    line_number: int  # 줄 번호 (0-based)


class MarkdownParser:
    """마크다운 파서
    
    마크다운 텍스트를 파싱하여 구조적 정보를 추출합니다.
    
    Features:
        - 코드 블록 추출 (fenced code blocks)
        - 헤더 추출 (# ~ ######)
        - 링크 추출
        - 리스트 추출
        
    Examples:
        >>> parser = MarkdownParser()
        >>> text = "# Title\\n\\n```python\\nprint('hi')\\n```"
        >>> headers = parser.extract_headers(text)
        >>> len(headers)
        1
    """
    
    # 정규표현식 패턴
    FENCED_CODE_PATTERN = re.compile(
        r'^```(\w*)\n(.*?)^```',
        re.MULTILINE | re.DOTALL
    )
    
    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    
    LIST_ITEM_PATTERN = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
    
    def extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """코드 블록 추출
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            CodeBlock 리스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "```python\\nprint('hi')\\n```"
            >>> blocks = parser.extract_code_blocks(text)
            >>> len(blocks)
            1
            >>> blocks[0].language
            'python'
        """
        blocks = []
        
        for match in self.FENCED_CODE_PATTERN.finditer(text):
            language = match.group(1) if match.group(1) else None
            code = match.group(2).rstrip()
            
            # 줄 번호 계산
            start_pos = match.start()
            start_line = text[:start_pos].count('\n')
            end_line = start_line + code.count('\n') + 1
            
            blocks.append(CodeBlock(
                language=language,
                code=code,
                start_line=start_line,
                end_line=end_line
            ))
        
        logger.debug(f"Extracted {len(blocks)} code blocks")
        return blocks
    
    def extract_headers(self, text: str) -> List[Header]:
        """헤더 추출
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            Header 리스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "# H1\\n## H2\\n### H3"
            >>> headers = parser.extract_headers(text)
            >>> len(headers)
            3
            >>> headers[0].level
            1
        """
        headers = []
        
        for match in self.HEADER_PATTERN.finditer(text):
            level = len(match.group(1))  # # 개수
            header_text = match.group(2).strip()
            
            # 줄 번호 계산
            line_number = text[:match.start()].count('\n')
            
            headers.append(Header(
                level=level,
                text=header_text,
                line_number=line_number
            ))
        
        logger.debug(f"Extracted {len(headers)} headers")
        return headers
    
    def extract_links(self, text: str) -> List[Tuple[str, str]]:
        """링크 추출
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            (링크 텍스트, URL) 튜플 리스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "[Google](https://google.com)"
            >>> links = parser.extract_links(text)
            >>> len(links)
            1
            >>> links[0]
            ('Google', 'https://google.com')
        """
        links = []
        
        for match in self.LINK_PATTERN.finditer(text):
            link_text = match.group(1)
            url = match.group(2)
            links.append((link_text, url))
        
        logger.debug(f"Extracted {len(links)} links")
        return links
    
    def extract_list_items(self, text: str) -> List[str]:
        """리스트 아이템 추출
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            리스트 아이템 텍스트 리스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "- Item 1\\n- Item 2\\n- Item 3"
            >>> items = parser.extract_list_items(text)
            >>> len(items)
            3
        """
        items = []
        
        for match in self.LIST_ITEM_PATTERN.finditer(text):
            item_text = match.group(1).strip()
            items.append(item_text)
        
        logger.debug(f"Extracted {len(items)} list items")
        return items
    
    def get_toc(self, text: str, max_level: int = 3) -> str:
        """Table of Contents 생성
        
        Args:
            text: 마크다운 텍스트
            max_level: 최대 헤더 레벨 (1-6)
            
        Returns:
            TOC 마크다운 텍스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "# Chapter 1\\n## Section 1.1\\n# Chapter 2"
            >>> toc = parser.get_toc(text)
            >>> "Chapter 1" in toc
            True
        """
        headers = self.extract_headers(text)
        
        toc_lines = ["## Table of Contents\n"]
        
        for header in headers:
            if header.level > max_level:
                continue
            
            # 들여쓰기
            indent = "  " * (header.level - 1)
            
            # 링크 생성 (GitHub-style anchor)
            anchor = header.text.lower().replace(" ", "-")
            anchor = re.sub(r'[^\w\-]', '', anchor)
            
            toc_line = f"{indent}- [{header.text}](#{anchor})"
            toc_lines.append(toc_line)
        
        return "\n".join(toc_lines)
    
    def count_words(self, text: str, exclude_code: bool = True) -> int:
        """단어 수 카운트
        
        Args:
            text: 마크다운 텍스트
            exclude_code: True면 코드 블록 제외
            
        Returns:
            단어 수
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "Hello world! This is a test."
            >>> parser.count_words(text)
            6
        """
        if exclude_code:
            # 코드 블록 제거
            text = self.FENCED_CODE_PATTERN.sub('', text)
        
        # 마크다운 문법 제거 (헤더, 링크 등)
        text = self.HEADER_PATTERN.sub(r'\2', text)
        text = self.LINK_PATTERN.sub(r'\1', text)
        
        # 단어 분리
        words = text.split()
        
        return len(words)
    
    def remove_code_blocks(self, text: str) -> str:
        """코드 블록 제거
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            코드 블록이 제거된 텍스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "Text\\n```python\\ncode\\n```\\nMore text"
            >>> result = parser.remove_code_blocks(text)
            >>> "code" not in result
            True
        """
        return self.FENCED_CODE_PATTERN.sub('', text)
    
    def get_plain_text(self, text: str) -> str:
        """마크다운 문법 제거하여 플레인 텍스트 반환
        
        Args:
            text: 마크다운 텍스트
            
        Returns:
            플레인 텍스트
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "# Title\\n\\n**bold** and *italic*"
            >>> plain = parser.get_plain_text(text)
            >>> "#" not in plain and "**" not in plain
            True
        """
        # 코드 블록 제거
        text = self.remove_code_blocks(text)
        
        # 헤더 제거 (텍스트만 남김)
        text = self.HEADER_PATTERN.sub(r'\2', text)
        
        # 링크 제거 (텍스트만 남김)
        text = self.LINK_PATTERN.sub(r'\1', text)
        
        # Bold, Italic 제거
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_
        
        # 인라인 코드 제거
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # 리스트 마커 제거
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def split_by_headers(self, text: str, level: int = 1) -> Dict[str, str]:
        """헤더 기준으로 텍스트 분할
        
        Args:
            text: 마크다운 텍스트
            level: 분할 기준 헤더 레벨
            
        Returns:
            {헤더 텍스트: 내용} 딕셔너리
            
        Examples:
            >>> parser = MarkdownParser()
            >>> text = "# Section 1\\nContent 1\\n# Section 2\\nContent 2"
            >>> sections = parser.split_by_headers(text, level=1)
            >>> len(sections)
            2
        """
        sections = {}
        lines = text.split('\n')
        
        current_header = None
        current_content = []
        
        header_pattern = re.compile(r'^#{' + str(level) + r'}\s+(.+)$')
        
        for line in lines:
            match = header_pattern.match(line)
            
            if match:
                # 이전 섹션 저장
                if current_header is not None:
                    sections[current_header] = '\n'.join(current_content).strip()
                
                # 새 섹션 시작
                current_header = match.group(1)
                current_content = []
            else:
                if current_header is not None:
                    current_content.append(line)
        
        # 마지막 섹션 저장
        if current_header is not None:
            sections[current_header] = '\n'.join(current_content).strip()
        
        logger.debug(f"Split text into {len(sections)} sections by level-{level} headers")
        return sections


# Helper functions

def extract_code_blocks(text: str) -> List[CodeBlock]:
    """코드 블록 추출 (헬퍼 함수)"""
    parser = MarkdownParser()
    return parser.extract_code_blocks(text)


def extract_headers(text: str) -> List[Header]:
    """헤더 추출 (헬퍼 함수)"""
    parser = MarkdownParser()
    return parser.extract_headers(text)


def get_plain_text(text: str) -> str:
    """플레인 텍스트 변환 (헬퍼 함수)"""
    parser = MarkdownParser()
    return parser.get_plain_text(text)
