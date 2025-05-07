'''
Test Case 필터링 로직
'''

import logging
from ..calculators.ttc_calculator import TTCCalculator

logger = logging.getLogger('cutout_scenario.scenario_filter')

class ScenarioFilter:
    """Test Case 필터링 로직"""
    
    def __init__(self, config):
        self.config = config
        self.ttc_calculator = TTCCalculator(config)
        
    def filter_scenarios(self, scenarios):
        """모든 조건을 만족하는 Test Case 필터링"""
        logger.info(f"총 {len(scenarios)}개 시나리오 필터링 시작")
        
        filtered_scenarios = []
        
        # 각 시나리오에 대해 필터링 적용
        for scenario in scenarios:
            # 1. 조기 충돌 확인
            if self.ttc_calculator.calculate_early_collision(scenario):
                logger.debug(f"조기 충돌 시나리오 제외: v_ego={scenario['v_ego']}, v_lv1={scenario['v_lv1']}")
                continue
            
            # 2. 물리적 유효성 검사
            d_ego_lv1, d_lv1_lv2 = self.ttc_calculator.calculate_initial_gaps(scenario)
            min_safe_distance = self.config['filtering']['safety_parameters']['min_safe_distance']
            
            if d_ego_lv1 < min_safe_distance or d_lv1_lv2 < min_safe_distance:
                logger.debug(f"물리적 유효성 실패 시나리오 제외: d_ego_lv1={d_ego_lv1:.2f}, d_lv1_lv2={d_lv1_lv2:.2f}")
                continue
            
            # 3. TTC_reveal 계산
            ttc_reveal = self.ttc_calculator.calculate_ttc_reveal(scenario)
            
            # 계산된 TTC를 시나리오에 추가
            scenario['ttc_reveal'] = ttc_reveal
            
            # 4. Human/ADS 모델 실패 여부 판단
            human_fails = self.ttc_calculator.evaluate_human_model(scenario, ttc_reveal)
            ads_fails = self.ttc_calculator.evaluate_ads_model(scenario, ttc_reveal)
            
            # 판단 결과를 시나리오에 추가
            scenario['human_fails'] = human_fails
            scenario['ads_fails'] = ads_fails
            
            # 5. '조기 충돌 없음 & 물리적 유효 & Human 실패 & ADS 성공' 조건 확인
            if human_fails and not ads_fails:
                filtered_scenarios.append(scenario)
                
        logger.info(f"필터링 완료: {len(filtered_scenarios)}개 Test Case 선택됨")
        return filtered_scenarios
