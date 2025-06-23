"""
유틸리티 모듈
공통으로 사용되는 유틸리티 함수들을 담당합니다.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Tuple
from config import Config

def generate_scan_id() -> str:
    """고유한 스캔 ID를 생성합니다."""
    return uuid.uuid4().hex

def create_consent_form(user_name: str) -> Optional[Tuple[str, str]]:
    """동의서 PDF를 생성합니다."""
    try:
        # 동의서 폴더 생성
        os.makedirs(Config.CONSENT_FORMS_DIR, exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consent_form_{timestamp}_{user_name}.pdf"
        filepath = os.path.join(Config.CONSENT_FORMS_DIR, filename)
        
        # 여기에 실제 PDF 생성 로직이 들어갈 수 있습니다
        # 현재는 파일 경로만 반환
        return filepath, filename
        
    except Exception as e:
        print(f"Error creating consent form: {e}")
        return None

def validate_ip_address(ip: str) -> bool:
    """IP 주소 유효성을 검사합니다."""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        
        return True
    except:
        return False

def validate_scan_profile(profile: str) -> bool:
    """스캔 프로필 유효성을 검사합니다."""
    return profile in Config.SCAN_PROFILES

def format_timestamp(timestamp: datetime) -> str:
    """타임스탬프를 포맷팅합니다."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def get_file_extension(filename: str) -> str:
    """파일 확장자를 추출합니다."""
    return os.path.splitext(filename)[1].lower()

def ensure_directory_exists(directory: str) -> None:
    """디렉토리가 존재하지 않으면 생성합니다."""
    os.makedirs(directory, exist_ok=True) 