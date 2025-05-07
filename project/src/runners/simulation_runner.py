'''
ESmini 시뮬레이션 실행기
'''

import os
import subprocess
import logging
import time

logger = logging.getLogger('cutout_scenario.runner')

class SimulationRunner:
    """ESmini 시뮬레이션 실행기"""
    
    def __init__(self, config):
        self.config = config
        self.esmini_path = config['simulation']['esmini']['executable_path']
        self.esmini_options = config['simulation']['esmini']['options']
        
    def run_simulation(self, xosc_file, output_dir):
        """ESmini 실행 및 결과 캡처"""
        logger.info(f"ESmini 시뮬레이션 실행: {xosc_file}")
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 명령어 구성
        cmd = [self.esmini_path, f"--osc={xosc_file}", f"--path={output_dir}"]
        
        # 옵션 추가
        for option in self.esmini_options:
            cmd.append(option)
        
        try:
            # 시뮬레이션 실행
            logger.debug(f"실행 명령어: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            # 결과 확인
            if process.returncode != 0:
                logger.error(f"시뮬레이션 실행 실패: {stderr.decode('utf-8')}")
                return False
            
            logger.info(f"시뮬레이션 실행 완료: {os.path.basename(xosc_file)}")
            return True
            
        except Exception as e:
            logger.error(f"시뮬레이션 실행 중 오류 발생: {str(e)}")
            return False
