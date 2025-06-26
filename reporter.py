"""
리포트 생성 모듈
Excel, PDF 리포트 생성 및 다운로드 기능을 담당합니다.
"""

import io
import os
import pandas as pd
import threading
from typing import Dict, List, Any
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from config import Config

class ReportGenerator:
    """리포트 생성 클래스"""
    
    def __init__(self):
        self.history_lock = threading.Lock()
    
    def create_excel_report(self, open_ports: List[Dict], closed_ports: List[Dict], 
                           ip_address: str, user_name: str, total_scan_ports: int) -> io.BytesIO:
        """Excel 리포트를 생성합니다."""
        output = io.BytesIO()
        
        # 요약 데이터
        summary_data = {
            "항목": ["점검 대상 IP", "고객사", "담당자", "총 스캔 포트", "열린 포트 수", "닫힌 포트 수", "보안 등급"],
            "내용": [
                ip_address, 
                user_name, 
                Config.MANAGER_NAME, 
                total_scan_ports, 
                len(open_ports), 
                len(closed_ports), 
                self._calculate_security_grade(open_ports)
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # 열린 포트 데이터
        open_ports_df = pd.DataFrame(open_ports)
        if not open_ports_df.empty:
            open_ports_df = open_ports_df.rename(columns={
                'number': '포트 번호', 
                'service': '서비스', 
                'protocol': '프로토콜',
                'risk': '위험도', 
                'description': '설명', 
                'vulnerabilities': '주요 취약점', 
                'recommendation': '보안 권고'
            })
        
        # 닫힌 포트 데이터
        closed_ports_df = pd.DataFrame(closed_ports)
        if not closed_ports_df.empty:
            closed_ports_df = closed_ports_df.rename(columns={
                'number': '포트 번호', 
                'service': '서비스'
            })
        
        # Excel 파일 생성
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='요약', index=False)
            open_ports_df.to_excel(writer, sheet_name='열린 포트 상세', index=False)
            closed_ports_df.to_excel(writer, sheet_name='닫힌 포트 목록', index=False)
            
            # 컬럼 너비 자동 조정
            self._adjust_excel_column_widths(writer)
        
        output.seek(0)
        return output
    
    def _adjust_excel_column_widths(self, writer) -> None:
        """Excel 컬럼 너비를 자동으로 조정합니다."""
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
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
    
    def save_scan_history(self, scan_data: Dict[str, Any]) -> None:
        """스캔 히스토리를 Excel 파일에 저장합니다."""
        with self.history_lock:
            try:
                new_record_df = pd.DataFrame([scan_data])
                
                if os.path.exists(Config.HISTORY_FILE):
                    existing_df = pd.read_excel(Config.HISTORY_FILE)
                    combined_df = pd.concat([existing_df, new_record_df], ignore_index=True)
                else:
                    combined_df = new_record_df
                
                combined_df.to_excel(Config.HISTORY_FILE, index=False)
            except Exception as e:
                print(f"Error saving scan history: {e}")
    
    def create_history_data(self, user_name: str, scan_profile: str, 
                           open_ports: List[Dict], security_grade: str) -> Dict[str, Any]:
        """히스토리 저장용 데이터를 생성합니다."""
        return {
            "스캔 일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "사용자": user_name,
            "담당자": Config.MANAGER_NAME,
            "스캔 프로필": scan_profile,
            "보안 등급": security_grade,
            "열린 포트 수": len(open_ports),
            "열린 포트 목록": ", ".join(str(p["number"]) for p in open_ports) if open_ports else "N/A",
            "고위험 포트 수": sum(1 for p in open_ports if p['risk'] == '높음'),
            "중위험 포트 수": sum(1 for p in open_ports if p['risk'] == '중간')
        }
    
    def create_pdf_report(self, report_data: Dict[str, Any]) -> io.BytesIO:
        """PDF 리포트를 생성합니다."""
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        story = []
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 제목
        title = Paragraph("포트 스캔 결과 리포트", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 기본 정보 테이블
        basic_info = [
            ["점검 대상 IP", report_data['ip_address']],
            ["고객사", report_data['user_name']],
            ["담당자", Config.MANAGER_NAME],
            ["스캔 일시", report_data['today_date']],
            ["총 스캔 포트", str(report_data['total_ports'])],
            ["열린 포트 수", str(len(report_data['open_ports']))],
            ["보안 등급", report_data['security_grade']]
        ]
        
        basic_table = Table(basic_info, colWidths=[100, 300])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 30))
        
        # 열린 포트 상세 정보
        if report_data['open_ports']:
            story.append(Paragraph("열린 포트 상세 정보", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            open_ports_data = [["포트", "서비스", "위험도", "설명"]]
            for port in report_data['open_ports']:
                open_ports_data.append([
                    str(port['number']),
                    port['service'],
                    port['risk'],
                    port['description'][:50] + "..." if len(port['description']) > 50 else port['description']
                ])
            
            ports_table = Table(open_ports_data, colWidths=[50, 80, 60, 200])
            ports_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(ports_table)

        
        
        # PDF 생성
        doc.build(story)
        output.seek(0)
        return output 