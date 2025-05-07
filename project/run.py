'''
Cut-out 시나리오 분석 및 시험 자동화 도구 실행 스크립트
'''

import os
import logging
import sys
from src.utils.config_loader import ConfigLoader
from src.main import main

if __name__ == "__main__":
  try:
    # 설정 파일 로드
    config = ConfigLoader.load_config('config/scenario_config.yaml')
    
    # 출력 디렉토리 생성
    output_dir = config['simulation']['output']['output_directory']
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'scenarios'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'reports'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'videos'), exist_ok=True)
    
    # 로깅 설정
    log_file = os.path.join(output_dir, 'logs/run.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('cutout_scenario')
    logger.info("=" * 50)
    logger.info("Cut-out 시나리오 분석 및 시험 자동화 도구 시작")
    logger.info("=" * 50)
    logger.info("UN R157 2023년 1월 개정안 기준 적용")
    
    # 메인 실행
    filtered_scenarios, sampled_scenarios = main(config)
    
    logger.info("=" * 50)
    logger.info("실행 완료")
    logger.info(f"필터링된 Test Case 수: {len(filtered_scenarios)}")
    logger.info(f"샘플링된 Test Case 수: {len(sampled_scenarios)}")
    logger.info("=" * 50)
      
  except Exception as e:
      logging.error(f"실행 중 오류 발생: {str(e)}", exc_info=True)
      sys.exit(1)