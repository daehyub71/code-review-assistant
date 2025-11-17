#!/usr/bin/env python3
"""
Code Review Assistant - 실행 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 메인 애플리케이션 실행
from app.main import main

if __name__ == "__main__":
    main()
