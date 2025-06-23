# ScanPort - 포트 스캐너 (리팩토링 버전)

밝은 톤의 UI를 가진 웹 기반 포트 스캐너입니다. 스캔 결과를 PDF/Excel로 다운로드할 수 있습니다.

## 🚀 주요 개선사항 (v05)

### 코드 구조 개선
- **모듈화**: 기능별로 파일을 분리하여 유지보수성 향상
- **설정 중앙화**: 모든 설정을 `config.py`에서 관리
- **에러 처리 강화**: 각 모듈별로 적절한 예외 처리 추가
- **타입 힌트**: 코드 가독성과 IDE 지원 향상

### 새로운 파일 구조
```
250620_v04/
├── app.py                 # 메인 애플리케이션 (간소화됨)
├── config.py             # 설정 관리 모듈 (신규)
├── scanner.py            # 포트 스캔 로직 (신규)
├── reporter.py           # 리포트 생성 로직 (신규)
├── utils.py              # 유틸리티 함수들 (신규)
├── notion_utils.py       # Notion 연동 (기존)
├── requirements.txt      # Python 의존성
├── README.md            # 사용법 설명
├── static/
│   ├── logo.png         # 로고 파일
│   └── report.css       # 스타일시트
├── templates/
│   ├── index.html       # 메인 페이지
│   └── report.html      # 리포트 페이지
└── consent_forms/       # 동의서 PDF 저장 폴더
```

## 📋 주요 기능

- ☀️ **밝은 톤 UI**: 깔끔하고 현대적인 화이트 테마
- 📊 **다양한 스캔 프로필**: 빠른(30개)/표준(60개)/상세(100개) 포트
- 📋 **Excel/PDF 리포트**: 상세한 스캔 결과 리포트 생성 및 다운로드
- 🔒 **보안 등급 평가**: 자동 보안 등급 산정 (A+, B, C, D)
- 📝 **동의서 자동 생성**: 이용약관 동의서 PDF 자동 생성
- 🔄 **실시간 진행률**: 스캔 진행 상황 실시간 표시
- 📈 **히스토리 관리**: 스캔 기록 Excel 파일로 저장
- 🔗 **Notion 연동**: 스캔 결과 자동으로 Notion DB에 저장 (선택사항)

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (선택사항)

```bash
# .env 파일 생성 또는 환경 변수 설정
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
export NOTION_TOKEN="your-notion-token"
export DATABASE_ID="your-database-id"
```

### 3. wkhtmltopdf 설치 (PDF 생성용)

Windows:
```bash
# https://wkhtmltopdf.org/downloads.html 에서 다운로드
# C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe 경로에 설치
```

### 4. 로고 파일 추가

`static/logo.png` 파일을 추가하세요.

## 🚀 사용법

### 1. 애플리케이션 실행

```bash
# 기존 버전
python app_v04.py

# 새로운 리팩토링 버전
python app.py
```

### 2. 웹 브라우저에서 접속

```
http://localhost:5000
```

### 3. 스캔 정보 입력

- **IP 주소**: 스캔할 대상 IP 주소 (유효성 검사 포함)
- **이름**: 고객사명 또는 사용자명
- **담당자**: 자동으로 "김태훈"으로 설정됨

### 4. 스캔 옵션 선택

- **스캔 범위**: 빠른(30개), 표준(60개), 상세(100개) 포트
- **스캔 속도**: 빠름(개인), 보통(IDC), 느림(해외/VPN)

### 5. 이용약관 동의 후 스캔 시작

## 📊 스캔 결과

### 웹 리포트
- 실시간 스캔 진행률 표시
- 상세한 포트 정보 및 보안 권고사항
- PDF/Excel 다운로드 기능

### 보안 등급
- **A+**: 열린 포트 없음 (최고 보안)
- **B**: 낮은 위험도 포트만 열림
- **C**: 중간 위험도 포트 존재
- **D**: 높은 위험도 포트 존재

## 🔧 모듈 설명

### `config.py`
- 애플리케이션의 모든 설정값들을 중앙에서 관리
- 환경 변수를 통한 설정 오버라이드 지원
- 포트 정보 데이터베이스 포함

### `scanner.py`
- 포트 스캔 로직을 담당하는 클래스
- 백그라운드 스레드에서 스캔 실행
- 실시간 진행률 업데이트

### `reporter.py`
- Excel 및 PDF 리포트 생성
- 스캔 히스토리 관리
- 파일 다운로드 기능

### `utils.py`
- 공통 유틸리티 함수들
- 입력 검증, 파일 처리, ID 생성 등

### `app.py`
- Flask 웹 애플리케이션 메인 파일
- 라우팅 및 에러 처리
- 각 모듈 간의 조율

## 🔄 버전별 변경사항

### v05 (현재) - 리팩토링
- ✅ **모듈화**: 기능별 파일 분리
- ✅ **설정 중앙화**: config.py로 모든 설정 관리
- ✅ **에러 처리 강화**: 각 모듈별 예외 처리
- ✅ **타입 힌트**: 코드 가독성 향상
- ✅ **유지보수성**: 코드 구조 개선

### v04 (이전)
- ☀️ **밝은 톤 UI**: 전체적으로 화이트 테마 적용
- 👤 **담당자 고정**: "김태훈"으로 담당자 고정
- 📝 **필드명 변경**: client_company → user_name
- 🎨 **UI 개선**: 더 현대적이고 사용자 친화적인 인터페이스

## ⚠️ 주의사항

1. **합법적 사용**: 허가받은 시스템에 대해서만 스캔을 수행하세요.
2. **포트 스캔**: 일부 네트워크에서는 포트 스캔이 차단될 수 있습니다.
3. **보안**: 실제 보안 진단을 위해서는 전문 보안 컨설턴트의 추가 분석이 필요합니다.
4. **환경 변수**: 프로덕션 환경에서는 반드시 환경 변수를 설정하세요.

## 🐛 문제 해결

### 일반적인 문제들

1. **포트 스캔이 느린 경우**
   - 스캔 타임아웃 값을 조정해보세요
   - 네트워크 상태를 확인해보세요

2. **PDF 생성 오류**
   - wkhtmltopdf가 올바르게 설치되었는지 확인
   - 파일 권한을 확인해보세요

3. **Notion 연동 오류**
   - 토큰과 데이터베이스 ID가 올바른지 확인
   - Notion API 권한을 확인해보세요

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 