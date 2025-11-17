"""
Tests for Language Selector and Cost Monitor Widgets
"""

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from app.ui.language_selector import LanguageSelectorWidget
from app.ui.cost_monitor import CostMonitorWidget
from app.models.language import Language
from app.core.cost_calculator import CostEstimate, ModelType


class TestLanguageSelectorWidget:
    """LanguageSelectorWidget 테스트"""

    def test_initialization(self, qtbot: QtBot):
        """위젯 초기화 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # ComboBox가 존재하는지 확인
        assert widget.combo_box is not None
        assert widget.combo_box.count() == 4  # 4개 언어

    def test_default_language(self, qtbot: QtBot):
        """기본 언어 확인 (C# 또는 첫 번째 항목)"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        language = widget.get_selected_language()
        assert isinstance(language, Language)
        # 기본값은 첫 번째 항목 (C#)
        assert language == Language.CSHARP

    def test_language_items(self, qtbot: QtBot):
        """4개 언어가 모두 있는지 확인"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # 모든 언어가 ComboBox에 있는지 확인
        languages_in_combo = []
        for i in range(widget.combo_box.count()):
            lang = widget.combo_box.itemData(i)
            languages_in_combo.append(lang)

        assert Language.CSHARP in languages_in_combo
        assert Language.JAVA in languages_in_combo
        assert Language.PYTHON in languages_in_combo
        assert Language.VUE in languages_in_combo

    def test_get_selected_language(self, qtbot: QtBot):
        """선택된 언어 가져오기"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # Python 선택
        widget.set_selected_language(Language.PYTHON)
        assert widget.get_selected_language() == Language.PYTHON

        # Java 선택
        widget.set_selected_language(Language.JAVA)
        assert widget.get_selected_language() == Language.JAVA

    def test_set_selected_language(self, qtbot: QtBot):
        """언어 설정 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # 각 언어로 설정 후 확인
        for language in [Language.CSHARP, Language.JAVA, Language.PYTHON, Language.VUE]:
            widget.set_selected_language(language)
            assert widget.get_selected_language() == language

    def test_language_changed_signal(self, qtbot: QtBot):
        """언어 변경 시그널 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # Signal spy 생성
        with qtbot.waitSignal(widget.language_changed, timeout=1000) as blocker:
            widget.set_selected_language(Language.PYTHON)

        # Signal이 올바른 Language를 전달했는지 확인
        assert blocker.args[0] == Language.PYTHON

    def test_get_display_name(self, qtbot: QtBot):
        """표시명 가져오기 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        widget.set_selected_language(Language.PYTHON)
        display_name = widget.get_display_name()
        assert display_name == "Python"

        widget.set_selected_language(Language.CSHARP)
        display_name = widget.get_display_name()
        assert display_name == "C#"

    def test_set_enabled(self, qtbot: QtBot):
        """위젯 활성화/비활성화 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # 비활성화
        widget.set_enabled(False)
        assert not widget.combo_box.isEnabled()

        # 활성화
        widget.set_enabled(True)
        assert widget.combo_box.isEnabled()

    def test_language_selector_ui_visible(self, qtbot: QtBot):
        """UI가 올바르게 표시되는지 확인"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        # 위젯 표시
        widget.show()
        qtbot.waitExposed(widget)

        # 위젯이 표시되고 있는지 확인
        assert widget.isVisible()
        assert widget.combo_box.isVisible()


class TestCostMonitorWidget:
    """CostMonitorWidget 테스트"""

    def test_initialization(self, qtbot: QtBot):
        """위젯 초기화 테스트"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        # 라벨들이 존재하는지 확인
        assert widget.token_value_label is not None
        assert widget.input_token_value_label is not None
        assert widget.output_token_value_label is not None
        assert widget.usd_value_label is not None
        assert widget.krw_value_label is not None
        assert widget.model_value_label is not None

    def test_initial_values(self, qtbot: QtBot):
        """초기 값 확인"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        assert widget.token_value_label.text() == "0"
        assert widget.input_token_value_label.text() == "0"
        assert widget.output_token_value_label.text() == "0"
        assert widget.usd_value_label.text() == "$0.0000"
        assert widget.krw_value_label.text() == "₩0"
        assert widget.model_value_label.text() == "-"

    def test_update_cost(self, qtbot: QtBot):
        """비용 업데이트 테스트"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        # CostEstimate 생성
        cost = CostEstimate(
            input_tokens=1000,
            output_tokens=2000,
            input_cost_usd=0.00015,
            output_cost_usd=0.0012,
            total_cost_usd=0.00135,
            total_cost_krw=1.809,
            model_type=ModelType.GPT_4O_MINI
        )

        # 비용 업데이트
        widget.update_cost(cost)

        # 값 확인
        assert widget.token_value_label.text() == "3,000"
        assert widget.input_token_value_label.text() == "1,000"
        assert widget.output_token_value_label.text() == "2,000"
        assert widget.usd_value_label.text() == "$0.001350"
        assert widget.krw_value_label.text() == "₩1.81"
        assert widget.model_value_label.text() == "gpt-4o-mini"

    def test_update_tokens(self, qtbot: QtBot):
        """토큰 수만 업데이트 테스트"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        widget.update_tokens(500, 1000)

        assert widget.token_value_label.text() == "1,500"
        assert widget.input_token_value_label.text() == "500"
        assert widget.output_token_value_label.text() == "1,000"

    def test_reset(self, qtbot: QtBot):
        """초기화 테스트"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        # 먼저 값 설정
        widget.update_tokens(100, 200)

        # 초기화
        widget.reset()

        # 초기 값으로 돌아갔는지 확인
        assert widget.token_value_label.text() == "0"
        assert widget.input_token_value_label.text() == "0"
        assert widget.output_token_value_label.text() == "0"
        assert widget.usd_value_label.text() == "$0.0000"
        assert widget.krw_value_label.text() == "₩0"

    def test_cost_monitor_ui_visible(self, qtbot: QtBot):
        """UI가 올바르게 표시되는지 확인"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        # 위젯 표시
        widget.show()
        qtbot.waitExposed(widget)

        # 위젯이 표시되고 있는지 확인
        assert widget.isVisible()
        assert widget.token_value_label.isVisible()
        assert widget.usd_value_label.isVisible()
        assert widget.krw_value_label.isVisible()

    def test_korean_labels(self, qtbot: QtBot):
        """한글 라벨이 올바르게 표시되는지 확인"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        # 위젯 표시
        widget.show()
        qtbot.waitExposed(widget)

        # GroupBox 타이틀 확인 (한글)
        layout = widget.layout()
        group_box = layout.itemAt(0).widget()
        assert "비용 모니터" in group_box.title()


class TestIntegration:
    """Language Selector와 Cost Monitor 통합 테스트"""

    def test_language_selector_and_cost_monitor_together(self, qtbot: QtBot):
        """두 위젯을 함께 사용하는 테스트"""
        lang_selector = LanguageSelectorWidget()
        cost_monitor = CostMonitorWidget()

        qtbot.addWidget(lang_selector)
        qtbot.addWidget(cost_monitor)

        # 언어 선택
        lang_selector.set_selected_language(Language.PYTHON)
        selected_lang = lang_selector.get_selected_language()
        assert selected_lang == Language.PYTHON

        # 비용 업데이트
        cost = CostEstimate(
            input_tokens=100,
            output_tokens=200,
            input_cost_usd=0.00015,
            output_cost_usd=0.0012,
            total_cost_usd=0.00135,
            total_cost_krw=1.809,
            model_type=ModelType.GPT_4O_MINI
        )
        cost_monitor.update_cost(cost)

        # 값 확인
        assert cost_monitor.token_value_label.text() == "300"
        assert selected_lang == Language.PYTHON

    def test_multiple_language_changes(self, qtbot: QtBot):
        """여러 번 언어를 변경하는 테스트"""
        widget = LanguageSelectorWidget()
        qtbot.addWidget(widget)

        languages = [Language.PYTHON, Language.JAVA, Language.CSHARP, Language.VUE]

        for language in languages:
            widget.set_selected_language(language)
            assert widget.get_selected_language() == language

    def test_multiple_cost_updates(self, qtbot: QtBot):
        """여러 번 비용을 업데이트하는 테스트"""
        widget = CostMonitorWidget()
        qtbot.addWidget(widget)

        costs = [
            (100, 200),
            (500, 1000),
            (1000, 2000),
        ]

        for input_tokens, output_tokens in costs:
            widget.update_tokens(input_tokens, output_tokens)
            assert widget.input_token_value_label.text() == f"{input_tokens:,}"
            assert widget.output_token_value_label.text() == f"{output_tokens:,}"
