'''
Concrete Scenario 생성 클래스
'''

import numpy as np
import logging
import itertools

logger = logging.getLogger('cutout_scenario.generator')

class ScenarioGenerator:
    """Concrete Scenario 생성 클래스"""
    
    def __init__(self, config):
        self.config = config
        
    def generate_scenarios(self):
        """파라미터 범위에 따라 가능한 모든 시나리오 조합 생성"""
        logger.info("파라미터 범위에 따른 시나리오 조합 생성 시작")
        
        # Ego 차량 파라미터 범위
        ego_config = self.config['vehicles']['ego_vehicle']
        v_ego_range = np.arange(
            ego_config['longitudinal_velocity']['min'],
            ego_config['longitudinal_velocity']['max'] + ego_config['longitudinal_velocity']['step'],
            ego_config['longitudinal_velocity']['step']
        )
        logger.debug(f"Ego 속도 범위: {v_ego_range} km/h")
        
        # LV1 차량 파라미터 범위
        lv1_config = self.config['vehicles']['lead_vehicle_1']
        v_lv1_range = np.arange(
            lv1_config['longitudinal_velocity']['min'],
            lv1_config['longitudinal_velocity']['max'] + lv1_config['longitudinal_velocity']['step'],
            lv1_config['longitudinal_velocity']['step']
        )
        
        v_lv1_lat_range = np.arange(
            lv1_config['lateral_velocity']['min'],
            lv1_config['lateral_velocity']['max'] + lv1_config['lateral_velocity']['step'],
            lv1_config['lateral_velocity']['step']
        )
        
        thw_ego_lv1_range = np.arange(
            lv1_config['initial_thw']['min'],
            lv1_config['initial_thw']['max'] + lv1_config['initial_thw']['step'],
            lv1_config['initial_thw']['step']
        )
        
        # LV2 차량 파라미터 범위
        lv2_config = self.config['vehicles']['lead_vehicle_2']
        v_lv2_range = np.arange(
            lv2_config['longitudinal_velocity']['min'],
            lv2_config['longitudinal_velocity']['max'] + lv2_config['longitudinal_velocity']['step'],
            lv2_config['longitudinal_velocity']['step']
        )
        
        dec_lv2_range = np.arange(
            lv2_config['longitudinal_deceleration']['min'],
            lv2_config['longitudinal_deceleration']['max'] + lv2_config['longitudinal_deceleration']['step'],
            lv2_config['longitudinal_deceleration']['step']
        )
        
        thw_ego_lv2_reveal_range = np.arange(
            lv2_config['reveal_thw']['min'],
            lv2_config['reveal_thw']['max'] + lv2_config['reveal_thw']['step'],
            lv2_config['reveal_thw']['step']
        )
        
        # 모든 파라미터 조합 생성
        all_combinations = list(itertools.product(
            v_ego_range,
            v_lv1_range,
            v_lv1_lat_range,
            thw_ego_lv1_range,
            v_lv2_range,
            dec_lv2_range,
            thw_ego_lv2_reveal_range
        ))
        
        logger.info(f"생성된 총 조합 수: {len(all_combinations)}")
        
        # 시나리오 객체 생성
        scenarios = []
        for combo in all_combinations:
            v_ego, v_lv1, v_lv1_lat, thw_ego_lv1, v_lv2, dec_lv2, thw_ego_lv2_reveal = combo
            
            # 물리적으로 불가능하거나 논리적으로 의미 없는 조합 필터링
            if not self._is_valid_combination(v_ego, v_lv1, v_lv1_lat, thw_ego_lv1, 
                                            v_lv2, dec_lv2, thw_ego_lv2_reveal):
                continue
            
            # 시나리오 객체 생성 (필요한 정보 포함)
            scenario = {
                'v_ego': v_ego,  # km/h
                'v_lv1': v_lv1,  # km/h
                'v_lv1_lat': v_lv1_lat,  # m/s
                'thw_ego_lv1': thw_ego_lv1,  # s
                'v_lv2': v_lv2,  # km/h
                'dec_lv2': dec_lv2,  # m/s²
                'thw_ego_lv2_reveal': thw_ego_lv2_reveal,  # s
                # 거리 계산 (필요시)
                'd_ego_lv1': (v_ego/3.6) * thw_ego_lv1,  # m
                'd_lv1_lv2': (v_lv1/3.6) * (thw_ego_lv2_reveal - thw_ego_lv1),  # m
                # 기타 필요한 매개변수
                'lane_change_direction': lv1_config['lane_change']['direction'],
                'lv2_deceleration_trigger_delay': lv2_config['deceleration_settings']['trigger_delay']
            }
            
            scenarios.append(scenario)
        
        logger.info(f"유효한 시나리오 수: {len(scenarios)}")
        return scenarios

    def _is_valid_combination(self, v_ego, v_lv1, v_lv1_lat, thw_ego_lv1, 
                            v_lv2, dec_lv2, thw_ego_lv2_reveal):
        """물리적으로 불가능하거나 논리적으로 의미 없는 조합 필터링"""
        
        # 1. LV2 드러난 시점 THW가 초기 THW보다 작거나 같으면 무효
        if thw_ego_lv2_reveal <= thw_ego_lv1:
            return False
        
        # 2. LV2가 Ego보다 빠르고 감속하지 않는 경우 (충돌 위험 없음)
        if v_lv2 > v_ego and dec_lv2 == 0:
            return False
        
        # 3. 필요 시 추가 조건
        
        return True
