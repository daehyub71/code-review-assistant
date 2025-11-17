"""
Main Application Entry Point - 코드 리뷰 어시스턴트
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.ui.main_window import MainWindow


# 로깅 설정
def setup_logging():
    """로깅 초기화"""
    # Logs 디렉토리 생성
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 로그 파일 경로
    log_file = logs_dir / "app.log"
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== Code Review Assistant Started ===")
    logger.info(f"Log file: {log_file}")
    
    return logger


def main():
    """메인 함수"""
    # 로깅 초기화
    logger = setup_logging()
    
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
