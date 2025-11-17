"""
Main Application Entry Point - 코드 리뷰 어시스턴트
"""

import sys
import logging
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가 (절대 임포트 지원)
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.ui.main_window import MainWindow


# 로깅 설정
def setup_logging(log_level: str = "INFO"):
    """로깅 초기화

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Logs 디렉토리 생성
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 로그 파일 경로
    log_file = logs_dir / "app.log"

    # 로그 레벨 변환
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # 로깅 설정
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=== Code Review Assistant Started ===")
    logger.info(f"Log level: {log_level.upper()}")
    logger.info(f"Log file: {log_file}")

    return logger


def main():
    """메인 함수"""
    # 커맨드라인 인자 파싱
    parser = argparse.ArgumentParser(
        description="Code Review Assistant - AI-powered code review tool"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)"
    )

    args = parser.parse_args()

    # 로깅 초기화
    logger = setup_logging(log_level=args.log_level)

    try:
        # QApplication 초기화
        app = QApplication(sys.argv)

        # 애플리케이션 정보 설정
        app.setApplicationName("Code Review Assistant")
        app.setOrganizationName("CodeReview")
        app.setApplicationVersion("1.0.0")

        # High DPI 스케일링 지원
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        logger.info("QApplication initialized")

        # Main Window 생성 및 표시
        window = MainWindow()
        window.show()

        logger.info("Main window displayed")

        # 이벤트 루프 실행
        exit_code = app.exec()

        logger.info(f"=== Application exited with code: {exit_code} ===")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Critical error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
