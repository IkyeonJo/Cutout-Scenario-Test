# Cut-out 시나리오 분석 및 시험 자동화 도구

## 개요
본 프로젝트는 고속도로 본선 주행 중 발생하는 위험 시나리오 중 하나인 'Cut-out' 상황 (선행 차량 이탈 후 다른 차량 출현)에 대한 자율주행 시스템(ADS)의 안전성을 평가하고, 관련 시험을 자동화하기 위한 소프트웨어 도구입니다.

## 주요 기능
- Cut-out 시나리오 정의 및 파라미터 설정 기능
- 파라미터 조합 기반 Concrete Scenario 자동 생성 및 기본 필터링
- 조기 충돌 및 물리적 유효성 검사 로직
- Human/ADS 모델 기반 위험도 평가 및 Test Case 1차 필터링 (UN R157 2023년 1월 개정안 기준)
- 시뮬레이션 대상 선정을 위한 비례 층화 샘플링 기능
- scenariogeneration 라이브러리를 활용한 OpenSCENARIO (.xosc) 파일 자동 변환
- ESmini 시뮬레이션 자동 실행 및 결과 비디오 생성 기능

## 설치 및 실행 방법
1. 요구 사항 설치: `pip install -r requirements.txt`
2. ESmini 및 FFmpeg 설치 (별도 진행)

3. 설정 파일 수정:
config/scenario_config.yaml 파일을 필요에 맞게 수정

4. 실행: `python run.py`

## 디렉토리 구조
- config/: 설정 파일
- src/: 소스 코드
- data/: 도로 네트워크 및 모델 파일
- output/: 생성된 시나리오, 리포트, 비디오 등 저장
- tests/: 테스트 코드

## UN R157 2023년 1월 개정안 기준 적용
본 프로젝트는 UN R157 2023년 1월 개정안에 따른 모델 파라미터를 적용하여 인간 운전자 모델과 자율주행 시스템의 성능을 비교 평가합니다.

## scenariogeneration 라이브러리 활용
OpenSCENARIO (.xosc) 파일 생성 시 scenariogeneration 라이브러리를 활용하여 표준화된 시나리오 파일을 생성합니다.

## 라이센스
이 프로젝트는 내부용으로 제작되었으며, 무단 배포를 금지합니다.