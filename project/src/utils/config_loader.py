'''
설정 파일 로딩 유틸리티
'''

import os
import yaml
import logging

logger = logging.getLogger('cutout_scenario.config_loader')

class ConfigLoader:
    """설정 파일 로딩 유틸리티"""
    
    @staticmethod
    def load_config(config_file):
        """YAML 설정 파일 로드"""
        logger.info(f"설정 파일 로드: {config_file}")
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info("설정 파일 로드 완료")
                return config
        except yaml.YAMLError as e:
            logger.error(f"YAML 파싱 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            raise