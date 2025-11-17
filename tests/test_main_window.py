"""
Tests for Main Window
"""

import pytest
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from unittest.mock import MagicMock

from app.ui.main_window import MainWindow
from app.models.language import Language
from app.models.review_category import ReviewCategory


class TestMainWindow:
    """MainWindow 테스트"""
    
    def test_initialization(self, qtbot: QtBot):
        """초기화 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        assert window.windowTitle() == "Code Review Assistant"
        # 초기 언어는 드롭다운의 첫 번째 항목 (C#)
        assert window.current_language == Language.CSHARP
    
    def test_all_widgets_exist(self, qtbot: QtBot):
        """모든 위젯 존재 확인"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 위젯 존재 확인
        assert window.language_selector is not None
        assert window.cost_monitor is not None
        assert window.before_after_editor is not None
        assert window.result_panel is not None
        assert window.file_upload_widget is not None
        assert window.folder_select_widget is not None
        assert window.analyze_button is not None
    
    def test_category_checkboxes(self, qtbot: QtBot):
        """카테고리 체크박스 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 8개 체크박스 존재 확인
        assert len(window.category_checkboxes) == 8
        
        # 모두 기본적으로 선택되어 있는지 확인
        for checkbox in window.category_checkboxes.values():
            assert checkbox.isChecked()
    
    def test_get_selected_categories_all(self, qtbot: QtBot):
        """모든 카테고리 선택 시 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        selected = window.get_selected_categories()
        assert len(selected) == 8
    
    def test_get_selected_categories_none(self, qtbot: QtBot):
        """카테고리 선택 안 했을 때 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 모든 체크박스 해제
        for checkbox in window.category_checkboxes.values():
            checkbox.setChecked(False)
        
        selected = window.get_selected_categories()
        assert len(selected) == 0
    
    def test_get_selected_categories_partial(self, qtbot: QtBot):
        """일부 카테고리만 선택 시 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 첫 번째 체크박스만 선택
        for i, checkbox in enumerate(window.category_checkboxes.values()):
            checkbox.setChecked(i == 0)
        
        selected = window.get_selected_categories()
        assert len(selected) == 1
    
    def test_language_changed_signal(self, qtbot: QtBot):
        """언어 변경 시그널 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 언어 변경
        window.language_selector.set_selected_language(Language.JAVA)
        
        # 현재 언어 확인
        assert window.current_language == Language.JAVA
    
    def test_clear_all(self, qtbot: QtBot):
        """전체 초기화 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 텍스트 설정
        window.before_after_editor.set_before_text("test code")
        window.result_panel.set_markdown("# Test")
        
        # 초기화
        window.clear_all()
        
        # 확인
        assert window.before_after_editor.get_before_text() == ""
        assert window.result_panel.get_markdown() == ""
    
    def test_set_analyze_enabled(self, qtbot: QtBot):
        """분석 버튼 활성화/비활성화 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 비활성화
        window.set_analyze_enabled(False)
        assert not window.analyze_button.isEnabled()
        
        # 활성화
        window.set_analyze_enabled(True)
        assert window.analyze_button.isEnabled()
    
    def test_analyze_button_click_no_categories(self, qtbot: QtBot, monkeypatch):
        """카테고리 미선택 시 분석 버튼 클릭 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        # QMessageBox.warning을 모킹하여 팝업 방지
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # 모든 카테고리 해제
        for checkbox in window.category_checkboxes.values():
            checkbox.setChecked(False)

        # 코드 입력
        window.before_after_editor.set_before_text("def test(): pass")

        # 분석 버튼 클릭
        qtbot.mouseClick(window.analyze_button, Qt.LeftButton)

        # QMessageBox.warning이 호출되었는지 확인
        assert mock_warning.call_count == 1
        assert "카테고리 미선택" in mock_warning.call_args[0][1]
    
    def test_analyze_button_click_no_code(self, qtbot: QtBot, monkeypatch):
        """코드 없이 분석 버튼 클릭 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        # QMessageBox.warning을 모킹하여 팝업 방지
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # 코드 없이 분석 버튼 클릭
        qtbot.mouseClick(window.analyze_button, Qt.LeftButton)

        # QMessageBox.warning이 호출되었는지 확인
        assert mock_warning.call_count == 1
        assert "코드 없음" in mock_warning.call_args[0][1]
    
    def test_analyze_button_click_valid(self, qtbot: QtBot):
        """정상적인 분석 버튼 클릭 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 코드 입력
        window.before_after_editor.set_before_text("def test(): pass")
        
        # 분석 버튼 클릭
        with qtbot.waitSignal(window.analysis_requested, timeout=1000, raising=False) as blocker:
            qtbot.mouseClick(window.analyze_button, Qt.LeftButton)
    
    def test_dummy_result_display(self, qtbot: QtBot):
        """더미 결과 표시 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 코드 입력 및 분석
        window.before_after_editor.set_before_text("def test(): pass")
        qtbot.mouseClick(window.analyze_button, Qt.LeftButton)
        
        # 결과 패널에 내용이 있는지 확인
        result = window.result_panel.get_markdown()
        assert len(result) > 0
        assert "Code Review Result" in result
    
    def test_window_visible(self, qtbot: QtBot):
        """윈도우 표시 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        window.show()
        qtbot.waitExposed(window)
        
        assert window.isVisible()
    
    def test_file_upload_integration(self, qtbot: QtBot):
        """파일 업로드 통합 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        # 파일 업로드 위젯이 제대로 통합되었는지 확인
        assert window.file_upload_widget.isVisible()

    def test_folder_select_integration(self, qtbot: QtBot):
        """폴더 선택 통합 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        # 폴더 선택 위젯이 제대로 통합되었는지 확인
        assert window.folder_select_widget.isVisible()
    
    def test_get_current_language(self, qtbot: QtBot):
        """현재 언어 가져오기 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        # 기본 언어 확인 (드롭다운 첫 항목인 C#)
        assert window.get_current_language() == Language.CSHARP

        # 언어 변경 (프로그래매틱하게 변경하면 signal이 발생하지 않으므로 직접 설정)
        window.language_selector.set_selected_language(Language.PYTHON)
        # Manually trigger the signal handler
        window._on_language_changed(Language.PYTHON)

        assert window.get_current_language() == Language.PYTHON


class TestMainWindowSignals:
    """MainWindow Signal 테스트"""
    
    def test_analysis_requested_signal(self, qtbot: QtBot):
        """분석 요청 시그널 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        # 시그널 연결
        received_signals = []

        def on_analysis_requested(language, categories, code):
            received_signals.append((language, categories, code))

        window.analysis_requested.connect(on_analysis_requested)

        # 코드 입력 및 분석 요청
        test_code = "def test(): pass"
        window.before_after_editor.set_before_text(test_code)
        qtbot.mouseClick(window.analyze_button, Qt.LeftButton)

        # 시그널 수신 확인
        assert len(received_signals) == 1
        language, categories, code = received_signals[0]
        # 초기 언어는 C# (드롭다운 첫 항목)
        assert language == Language.CSHARP
        assert len(categories) > 0
        assert code == test_code


class TestIntegration:
    """통합 테스트"""
    
    def test_full_workflow(self, qtbot: QtBot):
        """전체 워크플로우 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # 1. 언어 선택
        window.language_selector.set_selected_language(Language.PYTHON)
        
        # 2. 카테고리 선택 (일부만)
        for i, checkbox in enumerate(window.category_checkboxes.values()):
            checkbox.setChecked(i < 3)  # 첫 3개만 선택
        
        # 3. 코드 입력
        test_code = "def get_user(id):\n    return db.query(User).get(id)"
        window.before_after_editor.set_before_text(test_code)
        
        # 4. 분석 실행
        qtbot.mouseClick(window.analyze_button, Qt.LeftButton)
        
        # 5. 결과 확인
        result = window.result_panel.get_markdown()
        assert len(result) > 0
    
    def test_language_change_workflow(self, qtbot: QtBot):
        """언어 변경 워크플로우 테스트"""
        window = MainWindow()
        qtbot.addWidget(window)

        # 언어 변경
        languages = [Language.CSHARP, Language.JAVA, Language.PYTHON, Language.VUE]

        for lang in languages:
            # 프로그래매틱하게 언어 변경
            window.language_selector.set_selected_language(lang)
            window._on_language_changed(lang)  # Manually trigger handler

            assert window.current_language == lang

            # 각 언어로 더미 분석 실행
            window.before_after_editor.set_before_text("test code")
            qtbot.mouseClick(window.analyze_button, Qt.LeftButton)

            # 결과에 언어가 반영되었는지 확인
            result = window.result_panel.get_markdown()
            assert lang.value.upper() in result
