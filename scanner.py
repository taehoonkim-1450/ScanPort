"""
포트 스캐너 모듈
포트 스캔 로직과 관련 기능들을 담당합니다.
"""

import socket
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import Config

class PortScanner:
    """포트 스캐너 클래스"""
    
    def __init__(self):
        self.scan_jobs = {}
    
    def start_scan(self, scan_id: str, ip: str, user_name: str, 
                   scan_profile: str, timeout: float) -> None:
        """백그라운드에서 포트 스캔을 시작합니다."""
        ports_to_scan = Config.get_ports_for_profile(scan_profile)
        
        # 스캔 작업 초기화
        self.scan_jobs[scan_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Initializing scan...'
        }
        
        # 백그라운드 스레드에서 스캔 실행
        thread = threading.Thread(
            target=self._run_scan,
            args=(scan_id, ip, user_name, ports_to_scan, timeout, scan_profile)
        )
        thread.start()
    
    def _run_scan(self, scan_id: str, ip: str, user_name: str, 
                  ports_to_scan: List[int], timeout: float, scan_profile: str) -> None:
        """실제 포트 스캔을 수행합니다."""
        job = self.scan_jobs[scan_id]
        job['status'] = 'running'
        
        open_ports = []
        closed_ports = []
        total_ports = len(ports_to_scan)
        
        for i, port_num in enumerate(ports_to_scan):
            # 진행률 업데이트
            job['message'] = f"Scanning port {port_num}... ({i+1}/{total_ports})"
            job['progress'] = ((i + 1) / total_ports) * 100
            
            # 포트 스캔
            port_data = self._scan_single_port(ip, port_num, timeout)
            
            if port_data['status'] == 'open':
                open_ports.append(port_data)
            else:
                closed_ports.append(port_data)
        
        # 스캔 완료 처리
        job['status'] = 'complete'
        job['message'] = 'Scan complete. Generating report...'
        
        # 결과 데이터 구성
        report_data = self._create_report_data(
            scan_id, ip, user_name, total_ports, open_ports, closed_ports
        )
        job['result'] = report_data
    
    def _scan_single_port(self, ip: str, port: int, timeout: float) -> Dict[str, Any]:
        """단일 포트를 스캔합니다."""
        port_info = Config.get_port_info(port)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            try:
                s.connect((ip, port))
                return {
                    "number": port,
                    "service": port_info.get("service", "Unknown"),
                    "protocol": port_info.get("protocol", "N/A"),
                    "risk": port_info.get("risk", "낮음"),
                    "description": port_info.get("description", ""),
                    "vulnerabilities": port_info.get("vulnerabilities", ""),
                    "recommendation": port_info.get("recommendation", ""),
                    "status": "open"
                }
            except (socket.timeout, socket.error):
                return {
                    "number": port,
                    "service": port_info.get("service", "Unknown"),
                    "status": "closed"
                }
    
    def _create_report_data(self, scan_id: str, ip: str, user_name: str,
                           total_ports: int, open_ports: List[Dict], 
                           closed_ports: List[Dict]) -> Dict[str, Any]:
        """스캔 결과 리포트 데이터를 생성합니다."""
        return {
            "scan_id": scan_id,
            "ip_address": ip,
            "today_date": datetime.now().strftime("%Y-%m-%d"),
            "user_name": user_name,
            "total_ports": total_ports,
            "open_ports": open_ports,
            "closed_ports": closed_ports,
            "security_grade": self._calculate_security_grade(open_ports),
            "has_danger": any(p['risk'] in ['높음', '중간'] for p in open_ports)
        }
    
    def _calculate_security_grade(self, open_ports: List[Dict]) -> str:
        """보안 등급을 계산합니다."""
        if not open_ports:
            return "A+"
        
        risks = [port['risk'] for port in open_ports]
        if "높음" in risks:
            return "D"
        if "중간" in risks:
            return "C"
        return "B"
    
    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """스캔 상태를 반환합니다."""
        job = self.scan_jobs.get(scan_id, {})
        return {
            'status': job.get('status', 'not_found'),
            'progress': job.get('progress', 0),
            'message': job.get('message', 'Scan job not found.')
        }
    
    def get_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """완료된 스캔 결과를 반환합니다."""
        job = self.scan_jobs.get(scan_id, {})
        if job.get('status') == 'complete':
            return job.get('result')
        return None 