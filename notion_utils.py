import notion_client
from datetime import datetime

def add_scan_result_to_notion(token, db_id, data):
    """
    스캔 결과를 Notion 데이터베이스에 추가합니다.
    - token: Notion 통합 토큰
    - db_id: Notion 데이터베이스 ID
    - data: 저장할 통계 데이터 딕셔너리
    """
    try:
        notion = notion_client.Client(auth=token)
        
        # Notion 데이터베이스에 맞는 형식으로 프로퍼티 구성
        properties = {
            # '타임스탬프' 컬럼 (Title 타입)
            "타임스탬프": {
                "title": [
                    {
                        "text": {
                            "content": data.get("scan_timestamp")
                        }
                    }
                ]
            },
            # '보안 등급' 컬럼 (Select 타입)
            "보안 등급": {
                "select": {
                    "name": data.get("security_grade")
                }
            },
            # '열린 포트 목록' 컬럼 (Text 타입)
            "열린 포트 목록": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(data.get("open_ports_list", []))
                        }
                    }
                ]
            },
            # '높음 위험 포트 수' 컬럼 (Number 타입)
            "높음 위험 포트 수": {
                "number": data.get("high_risk_port_count", 0)
            },
            # '중간 위험 포트 수' 컬럼 (Number 타입)
            "중간 위험 포트 수": {
                "number": data.get("medium_risk_port_count", 0)
            }
        }

        # Notion에 새 페이지(행) 생성
        notion.pages.create(
            parent={"database_id": db_id},
            properties=properties
        )
        print("Notion DB에 스캔 결과 저장 성공")
        return True

    except Exception as e:
        print(f"Notion DB 저장 중 오류 발생: {e}")
        return False 