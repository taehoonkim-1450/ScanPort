"""
설정 관리 모듈
애플리케이션의 모든 설정값들을 중앙에서 관리합니다.
"""

import os
from typing import Dict, Any

class Config:
    """애플리케이션 설정 클래스"""
    
    # Flask 설정
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Notion API 설정
    NOTION_TOKEN = os.environ.get('NOTION_TOKEN', 'YOUR_NOTION_TOKEN_HERE')
    DATABASE_ID = os.environ.get('DATABASE_ID', 'YOUR_DATABASE_ID_HERE')
    
    # 스캔 설정
    DEFAULT_TIMEOUT = 0.5
    DEFAULT_SCAN_PROFILE = 'fast'
    
    # 담당자 정보
    MANAGER_NAME = "김태훈"
    
    # 파일 경로
    HISTORY_FILE = 'scan_history.xlsx'
    CONSENT_FORMS_DIR = 'consent_forms'
    
    # 스캔 프로필별 포트 목록
    SCAN_PROFILES = {
        'fast': [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 
            1723, 3306, 3389, 5900, 8080, 1521, 2049, 5060, 1433, 1194, 
            6379, 27017, 5432, 8443, 10000
        ],
        'standard': [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
            1723, 3306, 3389, 5900, 8080, 1521, 2049, 5060, 1433, 1194, 6379,
            27017, 5432, 8443, 10000,
            20, 81, 88, 119, 161, 162, 389, 465, 514, 587, 636, 873, 1080,
            1434, 1900, 2375, 4333, 5000, 5555, 5672, 5800, 7077, 8000,
            8009, 9000, 9090, 9200, 9300, 11211, 27018
        ],
        'detailed': [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
            1723, 3306, 3389, 5900, 8080, 1521, 2049, 5060, 1433, 1194, 6379,
            27017, 5432, 8443, 10000,
            20, 81, 88, 119, 161, 162, 389, 465, 514, 587, 636, 873, 1080,
            1434, 1900, 2375, 4333, 5000, 5555, 5672, 5800, 7077, 8000,
            8009, 9000, 9090, 9200, 9300, 11211, 27018,
            1, 7, 9, 13, 17, 19, 37, 70, 79, 101, 107, 113, 115, 123, 177,
            179, 199, 311, 427, 497, 500, 512, 513, 515, 520, 544, 548,
            554, 563, 646, 787, 888, 901, 990, 1025, 1099, 1241, 1352,
            1524, 1645, 1701, 1755, 1801, 2000, 2121
        ]
    }
    
    # 포트 정보 데이터베이스
    PORT_INFO = {
        20: {"service": "FTP-data", "protocol": "TCP", "risk": "낮음", "description": "FTP 데이터 전송 채널입니다.", "vulnerabilities": "", "recommendation": "보안이 강화된 SFTP/FTPS 사용을 권장합니다."},
        21: {"service": "FTP", "protocol": "TCP", "risk": "높음", "description": "파일 전송 프로토콜(FTP) 제어 채널입니다. 데이터가 암호화되지 않아 계정 정보 탈취 위험이 있습니다.", "vulnerabilities": "Anonymous FTP 접근 허용, Brute-force 공격, 패킷 스니핑", "recommendation": "FTP 사용을 중지하고, SFTP나 FTPS와 같이 암호화된 프로토콜을 사용하세요."},
        22: {"protocol": "TCP", "service": "SSH", "description": "보안 원격 터미널 및 파일 전송", "vulnerabilities": "약한 패스워드 공격\n무차별 대입", "recommendation": "키 기반 인증, 비밀번호 정책 강화\n로그인 제한", "risk": "낮음"},
        23: {"protocol": "TCP", "service": "Telnet", "description": "원격 터미널(비암호화)", "vulnerabilities": "평문 전송으로 인한 도청\n세션 하이재킹", "recommendation": "SSH 전환, ACL 설정\nVPN 터널링", "risk": "높음"},
        25: {"protocol": "TCP", "service": "SMTP", "description": "이메일 전송", "vulnerabilities": "오픈 릴레이를 통한 스팸 발송", "recommendation": "릴레이 제한, 스팸 필터링\nTLS(587/465) 강제화", "risk": "중간"},
        53: {"protocol": "UDP/TCP", "service": "DNS", "description": "도메인 이름 해석", "vulnerabilities": "DNS 스푸핑\n증폭 공격", "recommendation": "DNSSEC 적용\nACL 및 Rate Limiting", "risk": "중간"},
        80: {"protocol": "TCP", "service": "HTTP", "description": "웹페이지 비암호화 전송", "vulnerabilities": "중간자 공격\n세션 하이재킹", "recommendation": "HTTPS 강제화(443 리디렉션)\nHSTS 설정", "risk": "중간"},
        110: {"protocol": "TCP", "service": "POP3", "description": "이메일 수신", "vulnerabilities": "평문 전송\nMITM", "recommendation": "POP3S(995) 사용\nTLS 적용", "risk": "높음"},
        139: {"protocol": "TCP", "service": "NetBIOS", "description": "윈도우 파일/프린터 공유", "vulnerabilities": "정보 노출, 인증 우회", "recommendation": "SMBv1 비활성화\n방화벽 차단", "risk": "높음"},
        443: {"protocol": "TCP", "service": "HTTPS", "description": "웹페이지 암호화 전송", "vulnerabilities": "구식 TLS 취약점\n(POODLE, Heartbleed 등)", "recommendation": "최신 TLS 버전 강제\n인증서 관리, HSTS 설정", "risk": "낮음"},
        445: {"protocol": "TCP", "service": "SMB", "description": "윈도우 파일/프린터 공유 및 원격 서비스", "vulnerabilities": "랜섬웨어(WannaCry 등)", "recommendation": "SMBv1 비활성화\n패치 적용, 네트워크 분리", "risk": "높음"},
        3306: {"protocol": "TCP", "service": "MySQL", "description": "데이터베이스 클라이언트/서버 통신", "vulnerabilities": "SQL 인젝션\n약한 인증", "recommendation": "파라미터라이즈드 쿼리\n방화벽 제어, TLS 암호화", "risk": "중간"},
        3389: {"protocol": "TCP", "service": "RDP", "description": "윈도우 원격 데스크톱 연결", "vulnerabilities": "무차별 대입\n중간자 공격", "recommendation": "NLA 사용\nVPN 후 접속 제한", "risk": "높음"},
    }
    
    @classmethod
    def get_ports_for_profile(cls, profile: str) -> list:
        """스캔 프로필에 해당하는 포트 목록을 반환합니다."""
        return cls.SCAN_PROFILES.get(profile, cls.SCAN_PROFILES['fast'])
    
    @classmethod
    def get_port_info(cls, port: int) -> Dict[str, Any]:
        """포트 정보를 반환합니다."""
        return cls.PORT_INFO.get(port, {
            "service": "Unknown",
            "protocol": "N/A",
            "risk": "낮음",
            "description": "",
            "vulnerabilities": "",
            "recommendation": ""
        }) 