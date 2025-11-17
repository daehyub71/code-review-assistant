"""
Tests for Report History - 리포트 이력 테스트
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from app.db.report_history import ReportHistory
from app.models.language import Language
from app.models.review_category import ReviewCategory


class TestReportHistory:
    """ReportHistory 클래스 테스트"""

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """임시 데이터베이스 경로"""
        return tmp_path / "test_history.db"

    @pytest.fixture
    def history(self, temp_db_path):
        """ReportHistory 인스턴스"""
        return ReportHistory(db_path=temp_db_path)

    def test_initialization(self, history, temp_db_path):
        """초기화 테스트"""
        assert history.db_path == temp_db_path
        assert temp_db_path.exists()

    def test_save_analysis(self, history):
        """분석 이력 저장"""
        record_id = history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
            cost_krw=13.4,
            file_count=1,
            categories=[ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY],
            report_path="/path/to/report.md",
            notes="Test analysis",
        )

        assert record_id > 0

    def test_get_recent_analyses(self, history):
        """최근 분석 이력 조회"""
        # 여러 분석 저장
        history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )
        history.save_analysis(
            language=Language.JAVA,
            model="gpt-4o-mini",
            input_tokens=150,
            output_tokens=250,
            cost_usd=0.015,
        )

        # 전체 조회
        all_records = history.get_recent_analyses(limit=10)
        assert len(all_records) == 2

        # Python만 조회
        python_records = history.get_recent_analyses(limit=10, language=Language.PYTHON)
        assert len(python_records) == 1
        assert python_records[0]["language"] == "python"

    def test_get_analysis_by_id(self, history):
        """ID로 분석 조회"""
        record_id = history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )

        record = history.get_analysis_by_id(record_id)

        assert record is not None
        assert record["id"] == record_id
        assert record["language"] == "python"
        assert record["input_tokens"] == 100

    def test_get_analysis_by_id_not_found(self, history):
        """존재하지 않는 ID 조회"""
        record = history.get_analysis_by_id(999)
        assert record is None

    def test_get_total_cost(self, history):
        """총 비용 조회"""
        history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
            cost_krw=13.4,
        )
        history.save_analysis(
            language=Language.JAVA,
            model="gpt-4o-mini",
            input_tokens=150,
            output_tokens=250,
            cost_usd=0.015,
            cost_krw=20.1,
        )

        cost = history.get_total_cost()

        assert cost["total_usd"] == pytest.approx(0.025, rel=1e-6)
        assert cost["total_krw"] == pytest.approx(33.5, rel=1e-2)

    def test_get_statistics(self, history):
        """전체 통계 조회"""
        history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )
        history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o",
            input_tokens=150,
            output_tokens=250,
            cost_usd=0.02,
        )
        history.save_analysis(
            language=Language.JAVA,
            model="gpt-4o-mini",
            input_tokens=120,
            output_tokens=220,
            cost_usd=0.015,
        )

        stats = history.get_statistics()

        assert stats["total_analyses"] == 3
        assert stats["language_counts"]["python"] == 2
        assert stats["language_counts"]["java"] == 1
        assert stats["model_counts"]["gpt-4o-mini"] == 2
        assert stats["model_counts"]["gpt-4o"] == 1
        assert stats["total_input_tokens"] == 370
        assert stats["total_output_tokens"] == 670
        assert stats["total_cost_usd"] == pytest.approx(0.045, rel=1e-6)

    def test_delete_analysis(self, history):
        """분석 이력 삭제"""
        record_id = history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )

        # 삭제
        success = history.delete_analysis(record_id)
        assert success is True

        # 조회 시 없음
        record = history.get_analysis_by_id(record_id)
        assert record is None

    def test_delete_analysis_not_found(self, history):
        """존재하지 않는 이력 삭제"""
        success = history.delete_analysis(999)
        assert success is False

    def test_clear_all_history(self, history):
        """전체 이력 삭제"""
        history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
        )
        history.save_analysis(
            language=Language.JAVA,
            model="gpt-4o-mini",
            input_tokens=150,
            output_tokens=250,
            cost_usd=0.015,
        )

        # 전체 삭제
        deleted_count = history.clear_all_history()
        assert deleted_count == 2

        # 조회 시 0건
        records = history.get_recent_analyses(limit=10)
        assert len(records) == 0

    def test_categories_json_serialization(self, history):
        """카테고리 JSON 직렬화 테스트"""
        categories = [ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY]

        record_id = history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
            categories=categories,
        )

        record = history.get_analysis_by_id(record_id)

        import json

        saved_categories = json.loads(record["enabled_categories"])
        assert len(saved_categories) == 2
        assert "null_reference" in saved_categories or "security" in saved_categories


class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self, tmp_path):
        """전체 워크플로우 테스트"""
        db_path = tmp_path / "workflow_test.db"
        history = ReportHistory(db_path=db_path)

        # 분석 저장
        record_id1 = history.save_analysis(
            language=Language.PYTHON,
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
            cost_krw=13.4,
            categories=[ReviewCategory.NULL_SAFETY],
        )

        record_id2 = history.save_analysis(
            language=Language.JAVA,
            model="gpt-4o",
            input_tokens=200,
            output_tokens=400,
            cost_usd=0.03,
            cost_krw=40.2,
            categories=[ReviewCategory.SECURITY, ReviewCategory.PERFORMANCE],
        )

        # 조회
        recent = history.get_recent_analyses(limit=10)
        assert len(recent) == 2

        # 통계
        stats = history.get_statistics()
        assert stats["total_analyses"] == 2
        assert stats["total_cost_usd"] == pytest.approx(0.04, rel=1e-6)

        # 삭제
        history.delete_analysis(record_id1)

        # 재조회
        recent = history.get_recent_analyses(limit=10)
        assert len(recent) == 1
        assert recent[0]["id"] == record_id2
