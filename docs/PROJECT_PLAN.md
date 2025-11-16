# Code Review Assistant - 구현 계획서

## 📋 프로젝트 개요

**프로젝트명**: Code Review Assistant
**목적**: 다중 프로그래밍 언어를 지원하는 AI 기반 코드 리뷰 자동화 도구
**기반 프로젝트**: C# Code Reviewer API (아키텍처 참고)
**주요 기능**: 8개 카테고리 기반 코드 품질 분석 및 개선 제안
**UI 언어**: 한국어 단일 언어

---

## 🎯 목표 및 범위

### 핵심 목표
1. **다중 언어 지원**: C#, Java, Python, Vue.js를 시작으로 점진적 확장
2. **일관된 리뷰 품질**: 8개 표준 카테고리 기반 리뷰
3. **사용자 친화적 인터페이스**: 콤보박스 언어 선택, 한국어 UI
4. **확장 가능한 아키텍처**: 새 언어 추가 용이
5. **비용 관리**: API 토큰 사용량 모니터링 및 예상 비용 표시

### 제외 사항 (1차 개발)
- 언어 자동 감지 (사용자가 직접 선택)
- 멀티파일 분석 시 언어 혼합 (한 언어만 선택)
- 실시간 IDE 플러그인
- 자동 코드 수정 (제안만 제공)
- Git 통합
- CI/CD 파이프라인 통합
- 다국어 지원 (한국어만)

---

## 🗣️ 지원 언어 (우선순위)

### Phase 1: 핵심 언어 (4개)
1. **C#** - 기존 기능 기반
2. **Java** - Spring Boot 포함
3. **Python** - FastAPI/Django 포함
4. **Vue.js** - Vue 3 Composition API

### Phase 2: 확장 언어 (4개)
5. **TypeScript**
6. **JavaScript** (ES6+)
7. **Go**
8. **React** (JSX/TSX)

### Phase 3: 프레임워크 특화 + 추가 언어
- **프레임워크 특화 리뷰**: Spring Boot, Django, Vue 3, Express.js
- **추가 언어**: Kotlin, Swift, Rust, PHP

---

## 🏗️ 아키텍처 설계

### 계층 구조

```
┌─────────────────────────────────────────────┐
│         Presentation Layer (PySide6)        │
│  - 언어 선택 (콤보박스)                      │
│  - Before/After 에디터 (syntax highlight)   │
│  - 결과 패널 (Markdown viewer)              │
│  - 비용 모니터링 위젯 (NEW)                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Business Logic Layer               │
│  - Prompt Builder (language-aware)          │
│  - Report Generator (language-specific)     │
│  - Batch Analyzer (single language only)    │
│  - Cost Calculator (NEW)                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       API Integration Layer                 │
│  - OpenAI GPT-5/Claude API Client           │
│  - Streaming Response Handler               │
│  - Token Counter (NEW)                      │
└─────────────────────────────────────────────┘
```

---

## 📊 8개 카테고리 - 언어별 매핑

### 공통 카테고리 (언어 무관)

| # | 카테고리 | C# | Java | Python | Vue |
|---|---------|-------|------|--------|-----|
| 1 | **Null/Undefined 안전성** | `?.`, `??` | `Optional<T>`, `Objects.requireNonNull()` | `if x is not None:`, type hints | `v-if`, optional chaining `?.` |
| 2 | **예외/에러 처리** | `try-catch-finally`, 구체적 예외 | `try-catch-finally`, 커스텀 예외 | `try-except-finally`, context managers | `try-catch`, error boundaries |
| 3 | **리소스 관리** | `using`, `IDisposable` | `try-with-resources`, `AutoCloseable` | `with`, context managers | `onUnmounted`, cleanup |
| 4 | **성능 최적화** | LINQ, async/await, StringBuilder | Stream API, CompletableFuture, StringBuilder | list comprehension, generators, async/await | Computed, reactive refs, v-once |
| 5 | **보안 모범 사례** | SQL injection, XSS, 입력 검증 | SQL injection, OWASP Top 10, Spring Security | SQL injection, XSS, secrets 관리 | XSS, CSRF, sanitization |
| 6 | **네이밍 컨벤션** | PascalCase, camelCase, _privateFields | camelCase, UPPER_SNAKE_CASE | snake_case, PEP 8 | camelCase, PascalCase (components) |
| 7 | **문서화** | XML `///` comments | JavaDoc `/** */` | Docstrings `"""` | JSDoc `/** */` |
| 8 | **설정 관리** | appsettings.json, IConfiguration | application.properties, @Value | .env, environment variables | .env, import.meta.env |

---

## 🔧 기술 스택

### 코어
- **Backend**: Python 3.11+
- **GUI**: PySide6 (Qt6)
- **LLM**: OpenAI GPT-5 / Anthropic Claude
- **Database**: SQLite (report history)
- **Markdown**: python-markdown, Pygments

### 신규 추가
- **Syntax Highlighting**: Pygments lexers (C#, Java, Python, Vue, TypeScript 등)
- **Configuration**: YAML 기반 언어별 설정 (`resources/languages/*.yaml`)
- **Token Counting**: tiktoken (OpenAI) / anthropic-tokenizer

---

## 📁 프로젝트 구조

```
code-review-assistant/
├── app/
│   ├── main.py                          # Entry point
│   ├── ui/
│   │   ├── main_window.py               # 메인 윈도우 (언어 선택 콤보박스)
│   │   ├── language_selector.py         # 언어 선택 위젯
│   │   ├── cost_monitor.py              # 비용 모니터링 위젯
│   │   ├── before_after_editor.py       # 다중 언어 syntax highlighting
│   │   ├── file_upload_widget.py        # 파일 업로드
│   │   ├── folder_select_widget.py      # 폴더 선택 (단일 언어)
│   │   └── result_panel.py              # 결과 표시
│   ├── core/
│   │   ├── api_client.py                # API 클라이언트
│   │   ├── prompt_builder.py            # 언어별 템플릿 로딩
│   │   ├── batch_analyzer.py            # 단일 언어 배치 처리
│   │   ├── report_generator.py          # 리포트 생성
│   │   ├── integrated_report_generator.py # 통합 리포트
│   │   ├── cost_calculator.py           # 비용 계산
│   │   └── diagram_converter.py         # Mermaid 다이어그램
│   ├── utils/
│   │   ├── syntax_highlighter.py        # 다중 언어 하이라이팅
│   │   ├── markdown_renderer.py         # Markdown 렌더링
│   │   ├── markdown_parser.py           # Markdown 파싱
│   │   └── token_counter.py             # 토큰 카운팅
│   ├── models/
│   │   ├── language.py                  # Language enum, config
│   │   └── review_category.py           # ReviewCategory model
│   ├── db/
│   │   └── report_history.py            # SQLite (language, cost 컬럼)
│   └── config/
│       └── __init__.py
├── resources/
│   ├── languages/                       # 언어별 설정 YAML
│   │   ├── csharp.yaml
│   │   ├── java.yaml
│   │   ├── python.yaml
│   │   └── vue.yaml
│   ├── templates/
│   │   └── review_categories/           # 언어별 템플릿
│   │       ├── csharp/
│   │       │   ├── null_reference.md
│   │       │   ├── exception_handling.md
│   │       │   ├── resource_management.md
│   │       │   ├── performance.md
│   │       │   ├── security.md
│   │       │   ├── naming_convention.md
│   │       │   ├── code_documentation.md
│   │       │   └── hardcoding_to_config.md
│   │       ├── java/
│   │       ├── python/
│   │       └── vue/
│   └── styles/
├── tests/
│   ├── test_prompt_builder.py
│   ├── test_cost_calculator.py
│   ├── test_api_client.py
│   └── test_language_selector.py
├── docs/
│   └── PROJECT_PLAN.md                  # 이 문서
├── logs/                                # 로그 파일
├── reports/                             # 생성된 리포트
├── .env                                 # 환경 변수 (gitignore)
├── .env.example                         # 환경 변수 예시
├── .gitignore
├── requirements.txt
├── README.md
├── LICENSE
└── CLAUDE.md                            # Claude Code 가이드
```

---

## 🧩 주요 컴포넌트 설계

### 1. Language Model (`app/models/language.py`)

```python
from enum import Enum
from dataclasses import dataclass
import yaml

class Language(Enum):
    """지원 언어 목록"""
    CSHARP = "csharp"
    JAVA = "java"
    PYTHON = "python"
    VUE = "vue"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    REACT = "react"

    @property
    def display_name(self) -> str:
        """UI 표시용 한국어 이름"""
        names = {
            "csharp": "C#",
            "java": "Java",
            "python": "Python",
            "vue": "Vue.js",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "go": "Go",
            "react": "React",
        }
        return names[self.value]

@dataclass
class LanguageConfig:
    """언어별 설정"""
    name: str
    display_name: str
    file_extensions: list[str]
    comment_style: str
    doc_style: str
    keywords: list[str]

    @staticmethod
    def load(language: Language) -> 'LanguageConfig':
        """YAML 파일에서 설정 로드"""
        with open(f"resources/languages/{language.value}.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return LanguageConfig(**data)
```

### 2. Cost Calculator (`app/core/cost_calculator.py`)

```python
import tiktoken
from app.models.language import Language

class CostCalculator:
    """API 사용 비용 계산"""

    # 모델별 가격 (1M tokens 기준, USD)
    PRICING = {
        "gpt-5-mini": {"input": 0.25, "output": 2.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-haiku": {"input": 0.80, "output": 3.20},
    }

    def __init__(self, model: str = "gpt-5-mini"):
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        return len(self.encoding.encode(text))

    def estimate_cost(self, prompt: str, expected_output_tokens: int = 2000) -> dict:
        """
        예상 비용 계산

        Returns:
            {
                "input_tokens": 1500,
                "output_tokens": 2000,
                "input_cost": 0.000375,
                "output_cost": 0.004000,
                "total_cost": 0.004375,
                "total_krw": 5.85  # 1 USD = 1,340 KRW 가정
            }
        """
        input_tokens = self.count_tokens(prompt)

        pricing = self.PRICING[self.model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (expected_output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_tokens": input_tokens,
            "output_tokens": expected_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "total_krw": total_cost * 1340  # USD to KRW
        }
```

### 3. Language Selector Widget (`app/ui/language_selector.py`)

```python
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget
from app.models.language import Language

class LanguageSelectorWidget(QWidget):
    """언어 선택 콤보박스 위젯"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()

        self.label = QLabel("언어 선택:")
        self.combo = QComboBox()

        # Phase 1: 4개 언어만
        self.combo.addItems(["C#", "Java", "Python", "Vue.js"])

        self.combo.currentIndexChanged.connect(self.on_language_changed)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        self.setLayout(layout)

    def get_selected_language(self) -> Language:
        """현재 선택된 언어 반환"""
        mapping = {
            "C#": Language.CSHARP,
            "Java": Language.JAVA,
            "Python": Language.PYTHON,
            "Vue.js": Language.VUE
        }
        return mapping[self.combo.currentText()]
```

### 4. Cost Monitor Widget (`app/ui/cost_monitor.py`)

```python
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

class CostMonitorWidget(QWidget):
    """비용 모니터링 위젯 (하단 상태바)"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()

        self.token_label = QLabel("입력 토큰: 0")
        self.cost_label = QLabel("예상 비용: $0.00 (₩0)")

        layout.addWidget(self.token_label)
        layout.addStretch()
        layout.addWidget(self.cost_label)

        self.setLayout(layout)

    def update_cost(self, input_tokens: int, total_cost: float, total_krw: float):
        """비용 정보 업데이트"""
        self.token_label.setText(f"입력 토큰: {input_tokens:,}")
        self.cost_label.setText(f"예상 비용: ${total_cost:.4f} (₩{total_krw:.0f})")
```

---

## 🎨 UI/UX 설계

### 메인 윈도우 레이아웃

```
┌─────────────────────────────────────────────────────────────┐
│  코드 리뷰 어시스턴트                             [_][□][×]  │
├─────────────────────────────────────────────────────────────┤
│  [📝 텍스트 입력]  [📄 파일 업로드]  [📁 폴더 선택]          │
├─────────────────────────────────────────────────────────────┤
│  언어 선택: [C# ▼]          [⚙️ 설정]  [📊 히스토리]        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │ Before (원본 코드)    │  │ After (개선된 코드)          │ │
│  │                      │  │                              │ │
│  │  public class User { │  │  // 분석 후 표시됩니다       │ │
│  │    String name;      │  │                              │ │
│  │    ...               │  │                              │ │
│  │  [📋 복사]           │  │  [📋 복사]                   │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                               │
│  [✓] Null 안전성  [✓] 예외 처리  [✓] 리소스 관리  [✓] 성능  │
│  [✓] 보안         [✓] 네이밍     [✓] 문서화       [✓] 설정  │
│                                                               │
│  [분석하기]  [✓ 스크롤 동기화]                               │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  📊 코드 리뷰 리포트                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ## 요약                                                │  │
│  │ 언어: Java                                             │  │
│  │ 발견된 문제: 5개                                       │  │
│  │ - Null 안전성: 2개                                     │  │
│  │ - 문서화: 3개                                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  입력 토큰: 1,234  예상 비용: $0.0035 (₩4.7)                │
│  모델: openai/gpt-5-mini    API 연결됨 ✓                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 개발 단계 및 일정

### Phase 1: 핵심 기능 (3주)
**목표**: C#, Java, Python, Vue 4개 언어 지원

**Week 1: 모델 & 템플릿**
- [ ] Language Model & Config 설계
- [ ] YAML 언어 설정 파일 작성 (4개 언어)
- [ ] 8개 카테고리 템플릿 작성 (Java, Python, Vue용)
- [ ] 한국어 UI 문구 정리

**Week 2: UI & 비용 관리**
- [ ] Language Selector Widget 구현
- [ ] Cost Calculator 구현
- [ ] Cost Monitor Widget 구현
- [ ] Prompt Builder 수정
- [ ] Syntax Highlighter 수정
- [ ] Main Window UI 수정

**Week 3: 통합 & 테스트**
- [ ] Batch Analyzer 수정
- [ ] Report Generator 언어별 포맷
- [ ] Database 스키마 수정
- [ ] 통합 테스트
- [ ] 문서 작성
- [ ] 버그 수정

**마일스톤 1**: 4개 언어 코드 리뷰 + 비용 모니터링

---

### Phase 2: 확장 언어 (2주)
**목표**: TypeScript, JavaScript, Go, React 추가

**Week 4: 템플릿 & 설정**
- [ ] 4개 언어 YAML 설정
- [ ] 8개 카테고리 템플릿 작성
- [ ] Language Selector에 추가

**Week 5: 통합 & 테스트**
- [ ] Syntax Highlighter 추가
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] 문서 업데이트

**마일스톤 2**: 8개 언어 지원

---

### Phase 3: 프레임워크 특화 (3주)
**목표**: Spring Boot, Django, Vue 3, Express.js 심화 리뷰

**Week 6: 프레임워크 감지**
- [ ] 프레임워크 감지 로직
- [ ] 프레임워크별 설정 파일

**Week 7-8: 특화 템플릿**
- [ ] Spring Boot 특화 템플릿
- [ ] Django 특화 템플릿
- [ ] Vue 3 특화 템플릿
- [ ] Express.js 특화 템플릿
- [ ] 통합 테스트 & 문서화

**마일스톤 3**: 프레임워크 심화 리뷰

---

### Phase 4: 최적화 & 릴리스 (1주)
**Week 9**:
- [ ] 성능 최적화
- [ ] 비용 최적화
- [ ] UI/UX 개선
- [ ] 최종 문서화
- [ ] 릴리스 준비

**마일스톤 4**: v1.0.0 릴리스

---

## 💰 비용 관리 상세

### 비용 모니터링 기능

1. **실시간 토큰 카운팅**
   - Before 에디터 입력 시 즉시 계산
   - Debounce 적용 (500ms 지연)

2. **예상 비용 표시**
   - 입력 토큰 + 예상 출력 토큰(2000개)
   - USD 및 KRW 동시 표시
   - 환율: 1 USD = 1,340 KRW

3. **히스토리 추적**
   - SQLite에 각 분석 비용 저장
   - 월별/주별 누적 통계
   - CSV 내보내기

4. **경고 시스템**
   - 일일 예산 설정
   - 예산 80% 도달 시 경고
   - 예산 초과 시 차단 옵션

---

## 📦 의존성

### `requirements.txt`

```txt
# UI
PySide6>=6.10.0
PySide6-Addons>=6.10.0
PySide6-Essentials>=6.10.0

# LLM APIs
openai>=2.7.0
anthropic>=0.40.0

# Token counting
tiktoken>=0.7.0

# Configuration
python-dotenv>=1.2.0
PyYAML>=6.0

# Markdown & Syntax Highlighting
python-markdown>=3.6
Pygments>=2.18.0

# Testing
pytest>=8.0.0
pytest-qt>=4.0.0
pytest-cov>=5.0.0
```

---

## 🔐 보안 고려사항

1. **API 키 관리**: .env 파일, gitignore 포함
2. **업로드 제한**: 파일 크기 최대 1MB, 100개 파일
3. **데이터 프라이버시**: 로컬 처리, API 전송 전 사용자 동의
4. **SQLite Injection 방지**: Parameterized queries

---

## 📊 성능 목표

- **단일 파일 분석**: 3-5초 (GPT-5-mini)
- **폴더 분석 (10개 파일)**: 30-60초
- **토큰 카운팅**: <100ms
- **UI 반응성**: 60 FPS
- **메모리 사용량**: <500MB

---

## ✅ 마일스톤 체크리스트

### Phase 1 완료 조건
- [ ] 4개 언어 정상 분석
- [ ] 비용 모니터링 작동
- [ ] 한국어 UI 완성
- [ ] 단위 테스트 80% 커버리지
- [ ] README.md, CLAUDE.md 완성
- [ ] GitHub 저장소 공개

### Phase 2 완료 조건
- [ ] 8개 언어 정상 분석
- [ ] 성능 최적화 (3초 이내)
- [ ] 통합 테스트 통과

### Phase 3 완료 조건
- [ ] 프레임워크 특화 리뷰
- [ ] 비용 최적화
- [ ] v1.0.0 릴리스

---

## 📚 참고 자료

- **기반 프로젝트**: https://github.com/daehyub71/csharp-code-reviewer-api
- **OpenAI API**: https://platform.openai.com/docs/
- **Anthropic Claude**: https://docs.anthropic.com/
- **PySide6**: https://doc.qt.io/qtforpython-6/
- **Pygments**: https://pygments.org/

---

**작성일**: 2025-11-15
**버전**: 1.0.0
**작성자**: Code Review Assistant 개발팀
