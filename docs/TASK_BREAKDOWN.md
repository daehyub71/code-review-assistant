# Code Review Assistant - 상세 작업 분할표

## Phase 1: 핵심 기능 구현 (15일)

---

## Week 1: 모델 & 템플릿 (Day 1-5)

### Day 1: 프로젝트 환경 설정 & Language Model ✅

**작업 내용**
- [x] requirements.txt 의존성 확인 및 설치
- [x] .env 파일 생성 (OpenAI API 키 설정)
- [x] app/models/language.py 구현
  - Language enum 정의 (CSHARP, JAVA, PYTHON, VUE)
  - LanguageConfig dataclass 정의
  - YAML 로더 구현

**체크 사항**
- [x] venv 정상 활성화
- [x] OpenAI API 키 연결 테스트 성공
- [x] Language enum 4개 정의 완료
- [x] LanguageConfig.load() 메서드 동작 확인

---

### Day 2: 언어별 YAML 설정 파일 ✅

**작업 내용**
- [x] resources/languages/csharp.yaml 작성
- [x] resources/languages/java.yaml 작성
- [x] resources/languages/python.yaml 작성
- [x] resources/languages/vue.yaml 작성
- [x] app/models/review_category.py 구현
  - ReviewCategory enum 정의 (8개 카테고리)

**체크 사항**
- [x] 4개 YAML 파일 생성 완료
- [x] 각 YAML에 display_name, file_extensions, comment_style, doc_style, keywords 포함
- [x] YAML 파일 로딩 테스트 성공
- [x] ReviewCategory enum 8개 정의 완료

---

### Day 3: C# & Java 템플릿 작성

**작업 내용**
- [x] resources/templates/review_categories/csharp/ 8개 템플릿 작성
  - null_reference.md
  - exception_handling.md
  - resource_management.md
  - performance.md
  - security.md
  - naming_convention.md
  - code_documentation.md
  - hardcoding_to_config.md
- [x] resources/templates/review_categories/java/ 8개 템플릿 작성

**체크 사항**
- [x] C# 템플릿 8개 작성 완료
- [x] Java 템플릿 8개 작성 완료
- [x] 각 템플릿 형식 통일 (What to Check, Best Practices, Example, References)
- [x] 예제 코드 Before/After 포함 확인

---

### Day 4: Python & Vue 템플릿 작성

**작업 내용**
- [x] resources/templates/review_categories/python/ 8개 템플릿 작성
- [x] resources/templates/review_categories/vue/ 8개 템플릿 작성

**체크 사항**
- [x] Python 템플릿 8개 작성 완료
- [x] Vue 템플릿 8개 작성 완료
- [x] 총 32개 템플릿 파일 존재 확인
- [x] 각 언어별 특성 반영 확인

---

### Day 5: Prompt Builder 구현

**작업 내용**
- [x] app/core/prompt_builder.py 구현
  - load_template() 메서드
  - build_prompt() 메서드 (언어 + 카테고리 조합)
  - 템플릿 캐싱 로직
- [x] tests/test_prompt_builder.py 작성
  - 템플릿 로딩 테스트
  - 프롬프트 조립 테스트

**체크 사항**
- [x] 언어별 템플릿 정상 로딩
- [x] 선택된 카테고리만 프롬프트에 포함
- [x] 템플릿 파일 없을 시 에러 처리
- [x] 단위 테스트 전체 통과 (17/17 passed)

---

## Week 2: UI & 비용 관리 (Day 6-10)

### Day 6: Cost Calculator 구현 ✅

**작업 내용**
- [x] app/core/cost_calculator.py 구현
  - 모델별 가격 정의 (gpt-5-mini, gpt-4o-mini, claude-3-5-haiku)
  - count_tokens() 메서드 (tiktoken 사용)
  - estimate_cost() 메서드 (USD/KRW 계산)
- [x] app/utils/token_counter.py 구현
  - Debounce 로직 (500ms)
- [x] tests/test_cost_calculator.py 작성

**체크 사항**
- [x] tiktoken 정상 동작
- [x] 토큰 카운팅 정확도 검증
- [x] USD/KRW 환율 적용 확인
- [x] 단위 테스트 통과 (30/30 passed)

---

### Day 7: Language Selector & Cost Monitor Widget ✅

**작업 내용**
- [x] app/ui/language_selector.py 구현
  - QComboBox 위젯
  - 4개 언어 드롭다운 (C#, Java, Python, Vue.js)
  - get_selected_language() 메서드
  - set_selected_language() 메서드
  - language_changed Signal
- [x] app/ui/cost_monitor.py 구현
  - 토큰 수 표시 라벨 (총/Input/Output)
  - 예상 비용 표시 라벨 (USD/KRW)
  - update_cost() 메서드
  - update_tokens() 메서드
  - reset() 메서드
- [x] tests/test_language_selector.py 작성

**체크 사항**
- [x] 언어 선택 시 Language enum 반환 확인
- [x] 비용 모니터 UI 표시 정상
- [x] 한국어 라벨 정상 표시
- [x] UI 테스트 통과 (19/19 passed)

---

### Day 8: Before/After Editor & File Upload Widget

**작업 내용**
- [ ] app/ui/before_after_editor.py 구현
  - QTextEdit 2개 (Before/After)
  - 복사 버튼
  - 스크롤 동기화 옵션
- [ ] app/ui/file_upload_widget.py 구현
  - 파일 선택 버튼
  - 파일 크기 제한 (1MB)
- [ ] app/ui/folder_select_widget.py 구현
  - 폴더 선택 버튼
  - 파일 개수 제한 (100개)
- [ ] app/utils/syntax_highlighter.py 구현 (Pygments)

**체크 사항**
- [ ] Before/After 에디터 정상 표시
- [ ] 파일 업로드 동작 확인
- [ ] 폴더 선택 시 파일 목록 표시
- [ ] 파일 크기/개수 제한 동작 확인

---

### Day 9: Result Panel & Markdown Renderer

**작업 내용**
- [ ] app/ui/result_panel.py 구현
  - Markdown 렌더링 영역
  - 리포트 저장 버튼
  - 스크롤 가능한 패널
- [ ] app/utils/markdown_renderer.py 구현
  - python-markdown 사용
  - Pygments 코드 블록 하이라이팅
- [ ] app/utils/markdown_parser.py 구현
  - 마크다운 파싱 유틸리티

**체크 사항**
- [ ] 마크다운 정상 렌더링
- [ ] 코드 블록 syntax highlighting 동작
- [ ] 저장 버튼 클릭 시 파일 저장
- [ ] 한국어 텍스트 정상 표시

---

### Day 10: Main Window 통합

**작업 내용**
- [ ] app/ui/main_window.py 구현
  - 전체 레이아웃 구성
  - Language Selector 배치
  - Before/After Editor 배치 (QSplitter)
  - Cost Monitor 배치 (하단 상태바)
  - Result Panel 배치
  - 카테고리 체크박스 8개 배치
  - 분석하기 버튼
- [ ] app/main.py 구현
  - QApplication 초기화
  - MainWindow 실행

**체크 사항**
- [ ] 전체 UI 레이아웃 정상
- [ ] 위젯 간 연결 동작 확인
- [ ] 언어 선택 시 에디터 변경 확인
- [ ] 앱 실행 및 종료 정상

---

## Week 3: 통합 & 테스트 (Day 11-15)

### Day 11: API Client 구현

**작업 내용**
- [ ] app/core/api_client.py 구현
  - OpenAI 클라이언트 초기화
  - Claude 클라이언트 초기화
  - analyze_code() 메서드 (스트리밍)
  - QThread 기반 비동기 처리
- [ ] app/config/__init__.py 구현
  - .env 로딩
  - 설정 관리 클래스
- [ ] tests/test_api_client.py 작성 (Mock API)

**체크 사항**
- [ ] OpenAI API 호출 성공
- [ ] 스트리밍 응답 수신 확인
- [ ] UI 스레드 블로킹 없음
- [ ] 에러 처리 동작 확인

---

### Day 12: Report Generator & Database

**작업 내용**
- [ ] app/core/report_generator.py 구현
  - generate_report() 메서드
  - 마크다운 포맷 생성
  - 파일 저장 로직
- [ ] app/core/integrated_report_generator.py 구현
  - 배치 분석 결과 통합
- [ ] app/core/diagram_converter.py 구현
  - Mermaid 다이어그램 생성 (옵션)
- [ ] app/db/report_history.py 구현
  - SQLite 테이블 생성
  - 분석 이력 저장/조회

**체크 사항**
- [ ] 리포트 마크다운 정상 생성
- [ ] reports/ 폴더에 파일 저장 확인
- [ ] SQLite DB 생성 및 INSERT 성공
- [ ] 히스토리 조회 기능 동작

---

### Day 13: Batch Analyzer 구현

**작업 내용**
- [ ] app/core/batch_analyzer.py 구현
  - analyze_folder() 메서드
  - 파일별 분석 로직
  - 진행률 표시
  - 통합 리포트 생성
- [ ] 배치 분석 UI 연동
  - 진행 바 추가
  - 취소 버튼

**체크 사항**
- [ ] 폴더 내 모든 파일 분석 완료
- [ ] 진행률 표시 정상 동작
- [ ] 파일별 리포트 + 통합 리포트 생성
- [ ] 취소 기능 동작 확인

---

### Day 14: 통합 테스트 & 버그 수정

**작업 내용**
- [ ] End-to-End 테스트 시나리오 작성
  - C# 코드 분석 (단일 파일)
  - Java 코드 분석 (단일 파일)
  - Python 폴더 분석 (다중 파일)
  - Vue 파일 분석
- [ ] 발견된 버그 수정
- [ ] 로깅 추가 (logs/ 폴더)
- [ ] 에러 핸들링 보완

**체크 사항**
- [ ] 4개 언어 모두 정상 분석
- [ ] 비용 계산 정확도 검증
- [ ] 리포트 품질 확인
- [ ] 메모리 사용량 500MB 이하
- [ ] 단일 파일 분석 5초 이내

---

### Day 15: 문서화 & 최종 점검

**작업 내용**
- [ ] README.md 작성
  - 프로젝트 소개
  - 설치 방법
  - 사용법
  - 스크린샷
- [ ] CLAUDE.md 최종 검토
- [ ] .env.example 업데이트
- [ ] requirements.txt 최종 확인
- [ ] 코드 커버리지 확인 (목표: 80%)
- [ ] 최종 빌드 테스트

**체크 사항**
- [ ] README.md 완성
- [ ] 모든 문서 한국어 작성
- [ ] pytest 전체 통과
- [ ] 코드 커버리지 80% 이상
- [ ] 앱 실행 → 분석 → 리포트 생성 정상
- [ ] Git commit & push 완료

---

## Phase 1 완료 체크리스트

### 기능 검증
- [ ] C#, Java, Python, Vue 4개 언어 정상 분석
- [ ] 8개 카테고리 모두 동작
- [ ] 비용 모니터링 실시간 업데이트
- [ ] Before/After 에디터 syntax highlighting
- [ ] 리포트 저장 및 히스토리 조회
- [ ] 배치 폴더 분석 동작

### 품질 검증
- [ ] 단위 테스트 커버리지 80% 이상
- [ ] 통합 테스트 통과
- [ ] UI 반응성 60 FPS
- [ ] 단일 파일 분석 3-5초
- [ ] 메모리 사용량 500MB 이하

### 문서 검증
- [ ] README.md 완성
- [ ] CLAUDE.md 완성
- [ ] PROJECT_PLAN.md 최신화
- [ ] 코드 주석 충분
- [ ] API 문서화

### 배포 준비
- [ ] .gitignore 확인
- [ ] .env.example 확인
- [ ] requirements.txt 확인
- [ ] LICENSE 파일 확인
- [ ] GitHub 저장소 공개 준비

---

## 참고 사항

### 일일 작업 시간
- 평균 6-8시간/일
- 핵심 개발 시간: 4-5시간
- 테스트 & 문서화: 2-3시간

### 우선순위 원칙
1. 동작하는 코드 우선 (기능 완성)
2. 테스트 코드 작성
3. 문서화

### 막힐 때 대처
- PROJECT_PLAN.md 재확인
- CLAUDE.md 참고
- 기존 프로젝트 참고: https://github.com/daehyub71/csharp-code-reviewer-api
- 단위 테스트부터 작성하여 설계 검증

### 마일스톤 체크포인트
- **Day 5**: 템플릿 시스템 완성
- **Day 10**: UI 완성
- **Day 15**: Phase 1 완료
