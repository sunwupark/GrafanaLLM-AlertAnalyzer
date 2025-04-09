"""
Logging Module
"""

import logging


def setup_logging():
    # 로깅 설정 - 콘솔에만 출력
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    # 루트 로거 반환
    return logging.getLogger("alert_analyzer")


# 전역 로거 인스턴스 생성
logger = setup_logging()
