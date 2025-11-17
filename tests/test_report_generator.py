"""
Tests for Report Generator - 리포트 생성기 테스트
"""

import pytest
from pathlib import Path
from datetime import datetime

from app.core.report_generator import ReportGenerator
from app.core.integrated_report_generator import IntegratedReportGenerator, FileAnalysisResult
from app.core.diagram_converter import DiagramConverter
from app.models.language import Language
from app.models.review_category import ReviewCategory


class TestReportGenerator:
    """ReportGenerator 클래스 테스트"""

    @pytest.fixture
    def temp_reports_dir(self, tmp_path):
        """임시 리포트 디렉토리"""
        return tmp_path / "reports"

    @pytest.fixture
    def generator(self, temp_reports_dir):
        """ReportGenerator 인스턴스"""
        return ReportGenerator(reports_dir=temp_reports_dir)

    def test_initialization(self, generator, temp_reports_dir):
        """초기화 테스트"""
        assert generator.reports_dir == temp_reports_dir
        assert temp_reports_dir.exists()

    def test_generate_report(self, generator):
        """리포트 생성 테스트"""
        report = generator.generate_report(
            code="def hello():\n    print('world')",
            language=Language.PYTHON,
            review_result="# Review\n\nGood code!",
            categories=[ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY],
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.01,
            cost_krw=13.4,
        )

        # 리포트 내용 검증
        assert "# 코드 리뷰 리포트" in report
        assert "python" in report
        assert "gpt-4o-mini" in report
        assert "null_reference" in report or "security" in report
        assert "100" in report  # input tokens
        assert "200" in report  # output tokens
        assert "$0.01" in report
        assert "def hello():" in report
        assert "Good code!" in report

    def test_save_report(self, generator):
        """리포트 저장 테스트"""
        report = "# Test Report\n\nContent"

        # 저장
        file_path = generator.save_report(report, language=Language.PYTHON)

        # 파일 존재 확인
        assert file_path.exists()
        assert file_path.suffix == ".md"
        assert "python" in file_path.name

        # 내용 확인
        content = file_path.read_text(encoding="utf-8")
        assert content == report

    def test_save_report_custom_filename(self, generator):
        """커스텀 파일명으로 저장"""
        report = "# Custom Report"
        file_path = generator.save_report(report, filename="custom_report.md")

        assert file_path.name == "custom_report.md"
        assert file_path.exists()

    def test_list_reports(self, generator):
        """리포트 목록 조회"""
        # 여러 리포트 저장 (커스텀 파일명으로 충돌 방지)
        generator.save_report("# Report 1", filename="python_report1.md")
        generator.save_report("# Report 2", filename="python_report2.md")
        generator.save_report("# Report 3", filename="java_report1.md")

        # 전체 조회
        all_reports = generator.list_reports()
        assert len(all_reports) == 3

        # Python만 조회
        python_reports = generator.list_reports(language=Language.PYTHON)
        assert len(python_reports) == 2

        # Java만 조회
        java_reports = generator.list_reports(language=Language.JAVA)
        assert len(java_reports) == 1

    def test_delete_report(self, generator):
        """리포트 삭제"""
        file_path = generator.save_report("# Delete Me")

        assert file_path.exists()

        # 삭제
        success = generator.delete_report(file_path)
        assert success is True
        assert not file_path.exists()


class TestIntegratedReportGenerator:
    """IntegratedReportGenerator 클래스 테스트"""

    @pytest.fixture
    def temp_reports_dir(self, tmp_path):
        return tmp_path / "reports"

    @pytest.fixture
    def generator(self, temp_reports_dir):
        return IntegratedReportGenerator(reports_dir=temp_reports_dir)

    @pytest.fixture
    def sample_results(self):
        """샘플 분석 결과"""
        return [
            FileAnalysisResult(
                file_path="src/main.py",
                code="def main(): pass",
                review_result="# Main Review\n\nGood",
                input_tokens=50,
                output_tokens=100,
            ),
            FileAnalysisResult(
                file_path="src/utils.py",
                code="def util(): pass",
                review_result="# Utils Review\n\nOK",
                input_tokens=60,
                output_tokens=120,
            ),
        ]

    def test_generate_integrated_report(self, generator, sample_results):
        """통합 리포트 생성"""
        report = generator.generate_integrated_report(
            results=sample_results,
            language=Language.PYTHON,
            categories=[ReviewCategory.NULL_SAFETY],
            model="gpt-4o-mini",
            cost_usd=0.02,
            cost_krw=26.8,
        )

        # 통합 리포트 검증
        assert "# 통합 코드 리뷰 리포트" in report
        assert "2개" in report  # 파일 수
        assert "main.py" in report
        assert "utils.py" in report
        assert "110" in report  # total input tokens
        assert "220" in report  # total output tokens

    def test_save_integrated_report(self, generator, sample_results):
        """통합 리포트 저장"""
        report = generator.generate_integrated_report(
            results=sample_results,
            language=Language.PYTHON,
            categories=[ReviewCategory.NULL_SAFETY],
            model="gpt-4o-mini",
        )

        file_path = generator.save_integrated_report(report, language=Language.PYTHON)

        assert file_path.exists()
        assert "integrated" in file_path.name
        assert file_path.suffix == ".md"


class TestDiagramConverter:
    """DiagramConverter 클래스 테스트"""

    @pytest.fixture
    def converter(self):
        return DiagramConverter()

    def test_generate_review_summary_diagram(self, converter):
        """리뷰 요약 다이어그램 생성"""
        diagram = converter.generate_review_summary_diagram(
            categories=[ReviewCategory.NULL_SAFETY, ReviewCategory.SECURITY],
            scores={"null_reference": 8, "security": 6},
        )

        assert "```mermaid" in diagram
        assert "pie title" in diagram
        assert "null_reference" in diagram or "security" in diagram

    def test_generate_file_structure_diagram(self, converter):
        """파일 구조 다이어그램 생성"""
        diagram = converter.generate_file_structure_diagram(
            file_paths=["src/main.py", "src/utils.py"], base_dir="src"
        )

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "main.py" in diagram
        assert "utils.py" in diagram

    def test_generate_analysis_flow_diagram(self, converter):
        """분석 플로우 다이어그램 생성"""
        diagram = converter.generate_analysis_flow_diagram(
            language=Language.PYTHON, categories=[ReviewCategory.NULL_SAFETY]
        )

        assert "```mermaid" in diagram
        assert "graph LR" in diagram
        assert "python" in diagram

    def test_generate_cost_breakdown_diagram(self, converter):
        """비용 분해 다이어그램 생성"""
        diagram = converter.generate_cost_breakdown_diagram(
            input_tokens=100, output_tokens=200
        )

        assert "```mermaid" in diagram
        assert "pie title" in diagram
        assert "Input Tokens" in diagram
        assert "Output Tokens" in diagram

    def test_generate_timeline_diagram(self, converter):
        """타임라인 다이어그램 생성"""
        events = [("2024-01-01", "First Review"), ("2024-01-15", "Second Review")]

        diagram = converter.generate_timeline_diagram(events)

        assert "```mermaid" in diagram
        assert "timeline" in diagram
        assert "First Review" in diagram
        assert "Second Review" in diagram


class TestIntegration:
    """통합 테스트"""

    def test_full_workflow(self, tmp_path):
        """전체 워크플로우 테스트"""
        reports_dir = tmp_path / "reports"
        generator = ReportGenerator(reports_dir=reports_dir)

        # 리포트 생성
        report = generator.generate_report(
            code="def test(): return True",
            language=Language.PYTHON,
            review_result="# Excellent code",
            categories=[ReviewCategory.NULL_SAFETY],
            model="gpt-4o-mini",
            input_tokens=50,
            output_tokens=100,
            cost_usd=0.005,
            cost_krw=6.7,
        )

        # 저장
        file_path = generator.save_report(report, language=Language.PYTHON)

        # 조회
        reports = generator.list_reports(language=Language.PYTHON)
        assert len(reports) == 1
        assert reports[0] == file_path

        # 내용 확인
        saved_content = file_path.read_text(encoding="utf-8")
        assert "Excellent code" in saved_content
