"""
포트 스캐너 웹 애플리케이션
리팩토링된 모듈들을 사용하는 깔끔한 메인 앱 파일입니다.
"""

from flask import Flask, request, render_template, send_file, jsonify
from scanner import PortScanner
from reporter import ReportGenerator
from utils import generate_scan_id, create_consent_form, validate_ip_address, validate_scan_profile
from config import Config
from notion_utils import add_scan_result_to_notion
import logging

app = Flask(__name__)
app.config.from_object(Config)

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 전역 객체들
scanner = PortScanner()
reporter = ReportGenerator()

@app.route("/", methods=["GET"])
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template("index.html")

@app.route("/start-scan", methods=["POST"])
def start_scan():
    """포트 스캔을 시작합니다."""
    try:
        logging.info(f"Request Headers: {request.headers}")
        logging.info(f"Request Body: {request.data}")
        
        data = request.get_json()
        if not data:
            logging.error("No JSON data received.")
            return jsonify({'error': 'JSON 데이터가 없습니다.'}), 400
        
        logging.info(f"Received data: {data}")
        
        # 입력 검증
        ip = data.get('ip', '').strip()
        user_name = data.get('user_name', 'N/A').strip()
        scan_profile = data.get('scan_profile', Config.DEFAULT_SCAN_PROFILE)
        timeout = float(data.get('scan_timeout', Config.DEFAULT_TIMEOUT))
        
        # 유효성 검사
        if not validate_ip_address(ip):
            return jsonify({'error': '유효하지 않은 IP 주소입니다.'}), 400
        
        if not validate_scan_profile(scan_profile):
            return jsonify({'error': '유효하지 않은 스캔 프로필입니다.'}), 400
        
        if not user_name:
            return jsonify({'error': '사용자명을 입력해주세요.'}), 400
        
        # 동의서 생성
        create_consent_form(user_name)
        
        # 스캔 ID 생성 및 스캔 시작
        scan_id = generate_scan_id()
        scanner.start_scan(scan_id, ip, user_name, scan_profile, timeout)
        
        return jsonify({'scan_id': scan_id})
        
    except Exception as e:
        logging.error(f"Error in /start-scan: {e}", exc_info=True)
        return jsonify({'error': f'스캔 시작 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route("/scan-status/<scan_id>")
def scan_status(scan_id):
    """스캔 상태를 반환합니다."""
    try:
        status = scanner.get_scan_status(scan_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': f'상태 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route("/report/<scan_id>")
def report(scan_id):
    """완료된 스캔의 리포트 페이지를 렌더링합니다."""
    try:
        result = scanner.get_scan_result(scan_id)
        if result:
            return render_template("report.html", is_pdf=False, **result)
        else:
            return jsonify({'error': '스캔 결과를 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': f'리포트 생성 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route("/download/excel/<scan_id>")
def download_excel(scan_id):
    """Excel 리포트를 다운로드합니다."""
    try:
        result = scanner.get_scan_result(scan_id)
        if not result:
            return jsonify({'error': '스캔 결과를 찾을 수 없습니다.'}), 404
        
        # Excel 파일 생성
        excel_file = reporter.create_excel_report(
            result['open_ports'],
            result['closed_ports'],
            result['ip_address'],
            result['user_name'],
            result['total_ports']
        )
        
        # 히스토리 저장
        history_data = reporter.create_history_data(
            result['user_name'],
            'scan_profile',  # TODO: 스캔 프로필 정보 추가 필요
            result['open_ports'],
            result['security_grade']
        )
        reporter.save_scan_history(history_data)
        
        # Notion 연동 (선택사항)
        try:
            if Config.NOTION_TOKEN != 'YOUR_NOTION_TOKEN_HERE':
                notion_data = {
                    "scan_timestamp": result['today_date'],
                    "security_grade": result['security_grade'],
                    "open_ports_list": [p['number'] for p in result['open_ports']],
                    "high_risk_port_count": sum(1 for p in result['open_ports'] if p['risk'] == '높음'),
                    "medium_risk_port_count": sum(1 for p in result['open_ports'] if p['risk'] == '중간')
                }
                add_scan_result_to_notion(Config.NOTION_TOKEN, Config.DATABASE_ID, notion_data)
        except Exception as e:
            print(f"Notion 연동 실패: {e}")
        
        filename = f"port_scan_report_{result['ip_address']}_{result['today_date']}.xlsx"
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Excel 다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route("/download/pdf/<scan_id>")
def download_pdf(scan_id):
    """PDF 리포트를 다운로드합니다."""
    try:
        result = scanner.get_scan_result(scan_id)
        if not result:
            return jsonify({'error': '스캔 결과를 찾을 수 없습니다.'}), 404
        
        # PDF 파일 생성
        pdf_file = reporter.create_pdf_report(result)
        
        filename = f"port_scan_report_{result['ip_address']}_{result['today_date']}.pdf"
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF 다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({'error': '요청한 페이지를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000) 