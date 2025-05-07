'''
scenariogeneration을 활용한 시나리오 변환기 테스트
'''

import unittest
import os
import tempfile
from src.converters.comparative_scenario_converter import ComparativeScenarioConverter
from src.utils.config_loader import ConfigLoader

class TestComparativeScenarioConverter(unittest.TestCase):
    """시나리오 변환기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.config = ConfigLoader.load_config('config/scenario_config.yaml')
        self.converter = ComparativeScenarioConverter(self.config)
        
        # 테스트 시나리오 데이터
        self.test_scenario = {
            'v_ego': 80.0,  # km/h
            'v_lv1': 70.0,  # km/h
            'v_lv1_lat': 1.5,  # m/s
            'thw_ego_lv1': 2.0,  # s
            'v_lv2': 60.0,  # km/h
            'dec_lv2': 2.0,  # m/s²
            'thw_ego_lv2_reveal': 3.0,  # s
            'd_ego_lv1': (80.0/3.6) * 2.0,  # m
            'd_lv1_lv2': (70.0/3.6) * (3.0 - 2.0),  # m
            'lane_change_direction': -1,
            'lv2_deceleration_trigger_delay': 0.1
        }
        
    def test_convert_to_openscenario(self):
        """OpenSCENARIO 변환 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(suffix='.xosc', delete=False) as temp_file:
            output_file = temp_file.name
            
        try:
            # 변환 실행
            result_file = self.converter.convert_to_openscenario(self.test_scenario, output_file)
            
            # 파일 생성 확인
            self.assertTrue(os.path.exists(result_file), "XOSC 파일이 생성되지 않았습니다.")
            
            # 파일 내용 확인 (최소한의 XML 구조 확인)
            with open(result_file, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content, "XML 선언이 없습니다.")
                self.assertIn('<OpenSCENARIO', content, "OpenSCENARIO 태그가 없습니다.")
                
        finally:
            # 임시 파일 삭제
            if os.path.exists(output_file):
                os.unlink(output_file)

if __name__ == '__main__':
    unittest.main()