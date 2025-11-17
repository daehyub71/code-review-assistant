# Code Review Assistant

> AI 기반 다국어 코드 리뷰 도구 - PySide6 데스크톱 애플리케이션

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.10%2B-green.svg)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-daehyub71%2Fcode--review--assistant-black)](https://github.com/daehyub71/code-review-assistant)

## 📋 목차

- [소개](#-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [설치](#-설치)
- [사용 방법](#-사용-방법)
- [설정](#-설정)
- [개발 일정](#-개발-일정)
- [모델 성능 비교](#-모델-성능-비교)
- [프로젝트 구조](#-프로젝트-구조)
- [기여](#-기여)
- [라이선스](#-라이선스)

## 📖 소개

**Code Review Assistant**는 AI를 활용하여 여러 프로그래밍 언어의 코드를 자동으로 분석하고 개선점을 제안하는 데스크톱 애플리케이션입니다.

### 왜 Code Review Assistant인가?

- ✅ **다국어 지원**: C#, Java, Python, Vue.js 등 여러 언어 지원
- ✅ **8가지 표준 검토 카테고리**: Null 안전성, 예외 처리, 보안, 성능 등
- ✅ **실시간 비용 모니터링**: 토큰 사용량 및 API 비용 추적
- ✅ **최신 AI 모델 통합**: OpenAI GPT-4o/5, Anthropic Claude
- ✅ **배치 분석**: 여러 파일/폴더 동시 분석
- ✅ **직관적 UI**: 깔끔한 데스크톱 인터페이스

## 🎯 주요 기능

### 1. 다국어 코드 지원
- **Phase 1 현재 지원**: C#, Java, Python, Vue.js
- **Phase 2 예정**: TypeScript, Go
- **Phase 3 예정**: React, Angular 등 프레임워크 특화 검토

### 2. 8가지 표준 검토 카테고리

| 카테고리 | 설명 | 예시 |
|---------|------|------|
| **Null/Undefined 안전성** | Null 참조 예외 방지 | C# `?.`, Java `Optional<T>`, Python type hints |
| **예외/에러 처리** | 적절한 예외 처리 구현 | try-catch, 특정 예외 타입 사용 |
| **리소스 관리** | 파일, DB 등 리소스 정리 | C# `using`, Java try-with-resources, Python `with` |
| **성능 최적화** | 효율적 알고리즘 구현 | LINQ, Stream API, comprehension, computed properties |
| **보안 모범 사례** | 보안 취약점 방지 | SQL Injection, XSS, 입력 검증 |
| **네이밍 규칙** | 일관된 명명 규칙 | PascalCase, camelCase, snake_case |
| **코드 문서화** | 적절한 주석 및 문서화 | XML 주석, JavaDoc, docstring, JSDoc |
| **설정 관리** | 하드코딩 제거 | appsettings.json, .properties, .env 활용 |

### 3. 실시간 비용 모니터링
- 토큰 사용량 실시간 계산 (tiktoken)
- USD/KRW 환율 적용
- 리뷰 기록 SQLite DB 저장
- 일일 예산 설정 및 알림

### 4. Before/After 코드 비교
- Syntax highlighting (Pygments)
- 개선 전/후 코드 비교
- 변경 사항 강조 표시

### 5. 배치 분석
- 폴더 내 여러 파일 동시 분석
- 진행률 표시 및 중단 기능
- 통합 리포트 생성

## 🛠️ 기술 스택

### Frontend
- **PySide6 (Qt6)**: 네이티브 데스크톱 UI
- **Pygments**: Syntax highlighting

### Backend
- **Python 3.13+**
- **OpenAI SDK**: GPT 모델 직접 통합
- **Anthropic SDK**: Claude 모델 직접 통합
- **tiktoken**: 토큰 카운팅

### AI Models
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-5, GPT-5-mini
- **Anthropic**: Claude 3.5 Haiku

### Data
- **SQLite**: 리뷰 기록 저장
- **YAML**: 언어별 설정 저장

## 📦 설치

### 1. 저장소 복제

```bash
git clone https://github.com/daehyub71/code-review-assistant.git
cd code-review-assistant
```

### 2. 가상환경 생성 및 활성화

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic API 키 (선택)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-latest

# 환율 모니터링
USD_TO_KRW_RATE=1340
DAILY_BUDGET_USD=10.00
```

## 🚀 사용 방법

### 애플리케이션 실행

```bash
python app/main.py
```

### 기본 사용 흐름

1. **언어 선택**: 드롭다운에서 코드 언어 선택
2. **코드 입력**:
   - 직접 입력: Before 편집기에 코드 붙여넣기
   - 파일 불러오기: 파일 열기 버튼 클릭
   - 폴더 분석: 폴더 선택 (배치 분석)
3. **카테고리 선택**: 검토할 카테고리 체크박스 선택
4. **비용 확인**: 예상 토큰 수와 비용 확인
5. **분석 실행**: "분석하기" 버튼 클릭
6. **결과 확인**:
   - 분석 결과 (개선 전후 코드 확인)
   - After 편집기에서 개선 코드 확인
7. **리포트 저장**: "리포트 저장" 버튼으로 결과 저장

### 테스트 실행

```bash
# 전체 테스트
pytest

# 커버리지 측정
pytest --cov=app --cov-report=html

# 특정 테스트
pytest tests/test_language_selector.py -v
```

## ⚙️ 설정

### 모델 선택 가이드

#### 일반 사용 (권장)
```bash
OPENAI_MODEL=gpt-4o-mini  # 약 0.45원/리뷰
```

#### 품질 우선
```bash
OPENAI_MODEL=gpt-5-mini   # 약 4.98원/리뷰
```

#### 보안 중시
```bash
ANTHROPIC_MODEL=claude-3-5-haiku-latest  # 약 3.25원/리뷰
```

#### 최고 프로젝트
```bash
OPENAI_MODEL=gpt-4o       # 약 9.52원/리뷰
```

### 새로운 언어 추가하기

새 언어를 추가하려면:

1. `app/models/language.py`에 enum 추가
2. `resources/languages/{language}.yaml` 생성
3. `resources/templates/review_categories/{language}/` 템플릿 생성

예시 YAML 형식:

```yaml
display_name: "Python"
file_extensions:
  - ".py"
  - ".pyw"
comment_style: "#"
doc_style: "\"\"\""
keywords:
  - "def"
  - "class"
  # ...
```

## 📅 개발 일정

### Phase 1: 핵심 기능 구현 (15일) - ✅ 완료

#### Week 1: 모델 & 템플릿 작성 ✅

- [x] **Day 1**: 프로젝트 환경 설정 & Language Model
- [x] **Day 2**: 언어별 YAML 설정 파일 & ReviewCategory
- [x] **Day 3**: C# & Java 템플릿 생성 (8개 카테고리 × 2개 언어)
- [x] **Day 4**: Python & Vue 템플릿 생성 (8개 카테고리 × 2개 언어)
- [x] **Day 5**: Prompt Builder 구현 (템플릿 기반 프롬프트 생성)

#### Week 2: UI & 비용 관리 (Day 6-10) ✅

- [x] **Day 6-7**: Cost Calculator (tiktoken 기반 토큰 카운팅)
- [x] **Day 8**: Language Selector & Cost Monitor Widget (실시간 비용 표시)
- [x] **Day 9**: Before/After Editor & Result Panel (스크롤 동기화)
- [x] **Day 10**: File/Folder Upload Widget (파일 업로드 UI)
- [x] **Day 11**: Main Window 통합 (전체 UI 조립)

#### Week 3: 통합 & 테스트 (Day 12-15) ✅

- [x] **Day 12**: API Client (OpenAI/Claude 스트리밍, LLM 기반 코드 재생성)
- [x] **Day 13**: Report Generator & Database (Markdown 리포트, SQLite 히스토리)
- [x] **Day 13**: Batch Analyzer (배치 분석, 진행률 표시, 취소 기능)
- [x] **Day 14**: 통합 테스트 & 버그 수정 (208개 테스트 100% 통과)
- [x] **Day 15**: 문서화 & 최종 점검 (README, 커버리지, 빌드 테스트)

### 진행률

**완료**: 15/15일 (100%) ✅

### 테스트 현황

- **전체 테스트**: 208개
- **통과율**: 100%
- **평균 테스트 시간**: 0.81초/테스트
- **4개 언어 지원**: C#, Java, Python, Vue.js
- **8개 검토 카테고리**: 모든 언어별 템플릿 완성

## 📊 모델 성능 비교

### 비용 비교 (동일 코드 기준)

| 순위 | 모델 | 비용 | 상대비용 | 특징 |
|------|------|------|----------|------|
| 🥇 | GPT-4o-mini | 약 0.45원 | 1.0x | 가장 경제적 |
| 🥈 | GPT-5-nano | 약 1.09원 | 2.4x | 출력 불안정함 |
| 🥉 | Claude 3.5 Haiku | 약 3.25원 | 7.2x | 가장 보안 중심 |
| 4위 | GPT-5-mini | 약 4.98원 | 11.1x | 가장 품질 우수 |
| 5위 | GPT-4o | 약 9.52원 | 21.1x | 가장 빠른 응답 |
| 6위 | GPT-5 | 약 27.14원 | 60.3x | 출력 불안정함 |

### 품질 비교

| 모델 | 응답시간 | 품질 | 특징 |
|------|----------|------|------|
| **GPT-4o-mini** | 13.32초 | ★★★★ | 균형, 실용적 제안 |
| **GPT-4o** | 6.94초 | ★★★★★ | 상세 설명, 즉각 응답 |
| **Claude 3.5 Haiku** | 6.88초 | ★★★★ | 보안 강조, Type Safety |
| **GPT-5-mini** | 24.84초 | ★★★★★ | Decimal/logging, 통합 코드 |

### 일일 예상 비용 (10파일 프로젝트)

| 모델 | 비용 | 추천 용도 |
|------|------|-----------|
| GPT-4o-mini | 약 4.5원 | 일반 일상 리뷰 |
| Claude 3.5 Haiku | 약 32.5원 | 보안 강조 |
| GPT-5-mini | 약 49.8원 | 품질 강조 |
| GPT-4o | 약 95.2원 | 긴급 프로젝트 |

자세한 비교 분석은 [docs/DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md)를 참고하세요.

## 📂 프로젝트 구조

```
code-review-assistant/
├── app/
│   ├── models/
│   │   ├── language.py          # Language enum & Config
│   │   └── review_category.py   # 8개 검토 카테고리
│   ├── core/
│   │   ├── api_client.py        # OpenAI/Claude 클라이언트
│   │   ├── cost_calculator.py   # 토큰 카운팅 & 비용 계산
│   │   ├── prompt_builder.py    # 템플릿 기반 프롬프트 생성
│   │   ├── batch_analyzer.py    # 배치 분석
│   │   └── report_generator.py  # 리포트 생성
│   ├── ui/
│   │   ├── main_window.py       # 메인 윈도우
│   │   ├── language_selector.py # 언어 선택 위젯
│   │   ├── cost_monitor.py      # 비용 모니터링
│   │   ├── before_after_editor.py # 코드 편집기
│   │   └── result_panel.py      # 결과 패널
│   ├── db/
│   │   └── report_history.py    # SQLite 기록 관리
│   └── main.py                  # 애플리케이션 진입점
├── resources/
│   ├── languages/               # 언어별 YAML 설정
│   │   ├── csharp.yaml
│   │   ├── java.yaml
│   │   ├── python.yaml
│   │   └── vue.yaml
│   └── templates/
│       └── review_categories/   # 언어별 검토 템플릿 (마크다운)
├── docs/
│   ├── PROJECT_PLAN.md          # 프로젝트 계획서
│   ├── TASK_BREAKDOWN.md        # 작업 분할표
│   └── DEVELOPMENT_LOG.md       # 개발 로그
├── tests/                       # 단위/통합 테스트
├── requirements.txt             # Python 의존성
├── .env.example                 # 환경 변수 예제
└── README.md                    # 본 문서
```

## 🤝 기여

기여를 환영합니다! 다음 과정을 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 커밋 컨벤션

```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 포맷팅 (기능 변경 없음)
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드/설정 변경
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 👤 개발자 정보

**daehyub71**

- GitHub: [@daehyub71](https://github.com/daehyub71)
- Repository: [code-review-assistant](https://github.com/daehyub71/code-review-assistant)

## 🙏 참고한 기술

이 프로젝트는 다음 기술들을 활용했습니다:

- [OpenAI API](https://openai.com/api/)
- [Anthropic Claude](https://www.anthropic.com/)
- [PySide6](https://www.qt.io/qt-for-python)
- [tiktoken](https://github.com/openai/tiktoken)

---

**⭐ 이 프로젝트가 유용하셨다면 Star를 눌러주세요!**

**🤖 Powered by AI Code Review**
