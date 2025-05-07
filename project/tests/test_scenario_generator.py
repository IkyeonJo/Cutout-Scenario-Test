'''
시나리오 생성기 테스트
'''

import unittest
from src.generators.scenario_generator import ScenarioGenerator
from src.utils.config_loader import ConfigLoader

class TestScenarioGenerator(unittest.TestCase):
    """시나리오 생성기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.config = ConfigLoader.load_config('config/scenario_config.yaml')
        self.generator = ScenarioGenerator(self.config)
    
    def test_generate_scenarios(self):
        """시나리오 생성 테스트"""
        scenarios = self.generator.generate_scenarios()
        
        # 시나리오가 생성되었는지 확인
        self.assertTrue(len(scenarios) > 0, "시나리오가 생성되지 않았습니다.")
        
        # 시나리오 형식 확인
        scenario = scenarios[0]
        self.assertIn('v_ego', scenario, "v_ego 필드가 없습니다.")
        self.assertIn('v_lv1', scenario, "v_lv1 필드가 없습니다.")
        self.assertIn('v_lv1_lat', scenario, "v_lv1_lat 필드가 없습니다.")
        self.assertIn('thw_ego_lv1', scenario, "thw_ego_lv1 필드가 없습니다.")
        self.assertIn('v_lv2', scenario, "v_lv2 필드가 없습니다.")
        self.assertIn('dec_lv2', scenario, "dec_lv2 필드가 없습니다.")
        self.assertIn('thw_ego_lv2_reveal', scenario, "thw_ego_lv2_reveal 필드가 없습니다.")

if __name__ == '__main__':
    unittest.main()