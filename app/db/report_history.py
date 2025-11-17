"""
Report History - 리포트 이력 관리

SQLite 데이터베이스를 사용하여 코드 리뷰 분석 이력을 저장하고 조회합니다.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import json
import logging

from app.models.language import Language
from app.models.review_category import ReviewCategory

logger = logging.getLogger(__name__)


class ReportHistory:
    """리포트 이력 관리 클래스

    SQLite를 사용하여 분석 이력을 저장하고 조회합니다.

    Examples:
        >>> history = ReportHistory()
        >>> record_id = history.save_analysis(
        ...     language=Language.PYTHON,
        ...     model="gpt-4o-mini",
        ...     input_tokens=100,
        ...     output_tokens=200,
        ...     cost_usd=0.01
        ... )
        >>> records = history.get_recent_analyses(limit=10)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """초기화

        Args:
            db_path: 데이터베이스 파일 경로 (기본: 프로젝트 루트/data/report_history.db)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "report_history.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

        logger.info(f"ReportHistory initialized with db: {self.db_path}")

    def _init_database(self):
        """데이터베이스 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # review_history 테이블 생성
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                language TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_cost_usd REAL,
                total_cost_krw REAL,
                file_count INTEGER DEFAULT 1,
                enabled_categories TEXT,
                report_path TEXT,
                notes TEXT
            )
        """
        )

        conn.commit()
        conn.close()

        logger.debug("Database tables initialized")

    def save_analysis(
        self,
        language: Language,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        cost_krw: float = 0.0,
        file_count: int = 1,
        categories: Optional[List[ReviewCategory]] = None,
        report_path: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> int:
        """분석 이력 저장

        Args:
            language: 프로그래밍 언어
            model: 사용된 모델
            input_tokens: 입력 토큰 수
            output_tokens: 출력 토큰 수
            cost_usd: 비용 (USD)
            cost_krw: 비용 (KRW)
            file_count: 분석한 파일 수
            categories: 선택된 카테고리
            report_path: 저장된 리포트 경로
            notes: 메모

        Returns:
            생성된 레코드 ID

        Examples:
            >>> history = ReportHistory()
            >>> record_id = history.save_analysis(
            ...     language=Language.PYTHON,
            ...     model="gpt-4o-mini",
            ...     input_tokens=100,
            ...     output_tokens=200,
            ...     cost_usd=0.01
            ... )
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 카테고리를 JSON으로 변환
        categories_json = (
            json.dumps([cat.value for cat in categories]) if categories else None
        )

        cursor.execute(
            """
            INSERT INTO review_history (
                language, model, input_tokens, output_tokens,
                total_cost_usd, total_cost_krw, file_count,
                enabled_categories, report_path, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                language.value,
                model,
                input_tokens,
                output_tokens,
                cost_usd,
                cost_krw,
                file_count,
                categories_json,
                report_path,
                notes,
            ),
        )

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Analysis record saved with ID: {record_id}")

        return record_id

    def get_recent_analyses(
        self, limit: int = 10, language: Optional[Language] = None
    ) -> List[Dict]:
        """최근 분석 이력 조회

        Args:
            limit: 조회 개수 제한
            language: 특정 언어로 필터링 (옵션)

        Returns:
            분석 이력 레코드 리스트

        Examples:
            >>> history = ReportHistory()
            >>> records = history.get_recent_analyses(limit=5)
            >>> print(len(records))
            5
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # dict-like access
        cursor = conn.cursor()

        if language:
            cursor.execute(
                """
                SELECT * FROM review_history
                WHERE language = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (language.value, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM review_history
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

        rows = cursor.fetchall()
        conn.close()

        # Row to dict
        records = [dict(row) for row in rows]

        logger.debug(f"Retrieved {len(records)} recent analyses")

        return records

    def get_analysis_by_id(self, record_id: int) -> Optional[Dict]:
        """ID로 분석 이력 조회

        Args:
            record_id: 레코드 ID

        Returns:
            분석 이력 레코드 (없으면 None)

        Examples:
            >>> history = ReportHistory()
            >>> record = history.get_analysis_by_id(1)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM review_history
            WHERE id = ?
        """,
            (record_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_total_cost(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """기간별 총 비용 조회

        Args:
            start_date: 시작 날짜 (옵션)
            end_date: 종료 날짜 (옵션)

        Returns:
            {"total_usd": ..., "total_krw": ...}

        Examples:
            >>> history = ReportHistory()
            >>> cost = history.get_total_cost()
            >>> print(f"Total: ${cost['total_usd']:.2f}")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT SUM(total_cost_usd), SUM(total_cost_krw) FROM review_history"
        params = []

        if start_date or end_date:
            query += " WHERE "
            conditions = []

            if start_date:
                conditions.append("timestamp >= ?")
                params.append(start_date.isoformat())

            if end_date:
                conditions.append("timestamp <= ?")
                params.append(end_date.isoformat())

            query += " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        total_usd = row[0] if row[0] else 0.0
        total_krw = row[1] if row[1] else 0.0

        logger.debug(f"Total cost: ${total_usd:.2f} / ₩{total_krw:.2f}")

        return {"total_usd": total_usd, "total_krw": total_krw}

    def get_statistics(self) -> Dict:
        """전체 통계 조회

        Returns:
            통계 정보 딕셔너리

        Examples:
            >>> history = ReportHistory()
            >>> stats = history.get_statistics()
            >>> print(stats['total_analyses'])
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 전체 분석 수
        cursor.execute("SELECT COUNT(*) FROM review_history")
        total_analyses = cursor.fetchone()[0]

        # 언어별 분석 수
        cursor.execute(
            """
            SELECT language, COUNT(*) as count
            FROM review_history
            GROUP BY language
            ORDER BY count DESC
        """
        )
        language_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # 모델별 분석 수
        cursor.execute(
            """
            SELECT model, COUNT(*) as count
            FROM review_history
            GROUP BY model
            ORDER BY count DESC
        """
        )
        model_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # 총 토큰 수
        cursor.execute(
            "SELECT SUM(input_tokens), SUM(output_tokens) FROM review_history"
        )
        token_row = cursor.fetchone()
        total_input_tokens = token_row[0] if token_row[0] else 0
        total_output_tokens = token_row[1] if token_row[1] else 0

        # 총 비용
        cost = self.get_total_cost()

        conn.close()

        stats = {
            "total_analyses": total_analyses,
            "language_counts": language_counts,
            "model_counts": model_counts,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost_usd": cost["total_usd"],
            "total_cost_krw": cost["total_krw"],
        }

        logger.debug(f"Statistics retrieved: {total_analyses} analyses")

        return stats

    def delete_analysis(self, record_id: int) -> bool:
        """분석 이력 삭제

        Args:
            record_id: 레코드 ID

        Returns:
            True if deleted successfully

        Examples:
            >>> history = ReportHistory()
            >>> success = history.delete_analysis(1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM review_history WHERE id = ?", (record_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if deleted:
            logger.info(f"Analysis record {record_id} deleted")
        else:
            logger.warning(f"Analysis record {record_id} not found")

        return deleted

    def clear_all_history(self) -> int:
        """모든 이력 삭제 (주의!)

        Returns:
            삭제된 레코드 수

        Examples:
            >>> history = ReportHistory()
            >>> count = history.clear_all_history()
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM review_history")
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()

        logger.warning(f"All history cleared: {deleted_count} records deleted")

        return deleted_count


# 모듈 레벨 export
__all__ = ["ReportHistory"]
