'''
시나리오 필터 테스트
'''

import unittest
from src.filters.scenario_filter import ScenarioFilter
from src.utils.config_loader import ConfigLoader

class TestScenarioFilter(unittest.TestCase):
    """시나리오 필터 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.config = ConfigLoader.load_config('config/scenario_config.yaml')
        self.filter = ScenarioFilter(self.config)
        
        # 테스트 시나리오 목록 준비
        self.test_scenarios = [
            {
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
            },
            {
                'v_ego': 100.0,  # km/h
                'v_lv1': 90.0,  # km/h
                'v_lv1_lat': 1.0,  # m/s
                'thw_ego_lv1': 1.5,  # s
                'v_lv2': 50.0,  # km/h
                'dec_lv2': 3.0,  # m/s²
                'thw_ego_lv2_reveal': 2.5,  # s
                'd_ego_lv1': (100.0/3.6) * 1.5,  # m
                'd_lv1_lv2': (90.0/3.6) * (2.5 - 1.5),  # m
                'lane_change_direction': -1,
                'lv2_deceleration_trigger_delay': 0.1
            },
            # 조기 충돌 케이스
            {
                'v_ego': 120.0,  # km/h
                'v_lv1': 60.0,  # km/h
                'v_lv1_lat': 0.5,  # m/s (느린 차선 변경)
                'thw_ego_lv1': 0.8,  # s (짧은 간격)
                'v_lv2': 40.0,  # km/h
                'dec_lv2': 1.0,  # m/s²
                'thw_ego_lv2_reveal': 1.5,  # s
                'd_ego_lv1': (120.0/3.6) * 0.8,  # m
                'd_lv1_lv2': (60.0/3.6) * (1.5 - 0.8),  # m
                'lane_change_direction': -1,
                'lv2_deceleration_trigger_delay': 0.1
            }
        ]
    
    def test_filter_scenarios(self):
        """시나리오 필터링 테스트"""
        filtered_scenarios = self.filter.filter_scenarios(self.test_scenarios)
        
        # 필터링 결과 확인
        self.assertIsInstance(filtered_scenarios, list, "필터링 결과가 리스트가 아닙니다.")
        
        # 필터링된 시나리오에는 ttc_reveal, human_fails, ads_fails 필드가 있어야 함
        if filtered_scenarios:
            scenario = filtered_scenarios[0]
            self.assertIn('ttc_reveal', scenario, "ttc_reveal 필드가 없습니다.")
            self.assertIn('human_fails', scenario, "human_fails 필드가 없습니다.")
            self.assertIn('ads_fails', scenario, "ads_fails 필드가 없습니다.")

if __name__ == '__main__':
    unittest.main()