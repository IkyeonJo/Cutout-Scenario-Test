'''
TTC 및 충돌 계산 로직
'''

import logging
import numpy as np

logger = logging.getLogger('cutout_scenario.ttc_calculator')

class TTCCalculator:
    """TTC 및 충돌 계산 로직"""
    
    def __init__(self, config):
        self.config = config
        self.min_safe_distance = config['filtering']['safety_parameters']['min_safe_distance']
        
        # 모델 파라미터 (UN R157 2023년 1월 개정안 기준)
        human_config = config['control_models']['human_model']
        ads_config = config['control_models']['ads_model']
        
        self.human_reaction_time = human_config['reaction_time']
        self.human_max_decel = human_config['max_deceleration']
        self.human_buildup_time = human_config['deceleration_buildup_time']
        
        self.ads_reaction_time = ads_config['reaction_time']
        self.ads_max_decel = ads_config['max_deceleration']
        self.ads_buildup_time = ads_config['deceleration_buildup_time']
        
        # 평가 기준 보정값
        self.human_failure_offset = config['filtering']['evaluation_criteria']['human_failure_offset']
        self.ads_failure_offset = config['filtering']['evaluation_criteria']['ads_failure_offset']
        
        # 차량 크기
        self.ego_length = config['vehicles']['ego_vehicle']['dimensions']['length']
        self.lv1_length = config['vehicles']['lead_vehicle_1']['dimensions']['length']
        self.lv2_length = config['vehicles']['lead_vehicle_2']['dimensions']['length']
        
    def calculate_early_collision(self, scenario):
        """조기 충돌 가능성 계산 (LV1 차선 변경 완료 전 충돌 여부)"""
        # 차량 속도 (m/s로 변환)
        v_ego = scenario['v_ego'] / 3.6
        v_lv1 = scenario['v_lv1'] / 3.6
        v_lv1_lat = scenario['v_lv1_lat']
        
        # 초기 거리
        d_0 = scenario['d_ego_lv1']
        
        # 상대 속도
        v_rel = v_ego - v_lv1
        
        # 차선 폭 (m)
        lane_width = self.config['environment']['road_network']['lane_width']
        
        # 차선 변경 완료 시간 (s)
        t_clear = lane_width / v_lv1_lat
        
        # 조기 충돌 시간 (상대 속도가 양수인 경우만)
        if v_rel > 0:
            # 전방 충돌 시간 (차량 길이 고려)
            t_collision = (d_0 - self.min_safe_distance) / v_rel
            
            # t_collision이 t_clear보다 작으면 조기 충돌
            if t_collision < t_clear:
                logger.debug(f"조기 충돌 가능성 감지: t_collision={t_collision:.2f}s, t_clear={t_clear:.2f}s")
                return True
        
        return False
        
    def calculate_initial_gaps(self, scenario):
        """초기 차량 간 간격 계산"""
        # Ego와 LV1 사이의 초기 간격
        d_ego_lv1_initial = scenario['d_ego_lv1']
        
        # LV1과 LV2 사이의 초기 간격
        d_lv1_lv2_initial = scenario['d_lv1_lv2']
        
        return d_ego_lv1_initial, d_lv1_lv2_initial
        
    def calculate_ttc_reveal(self, scenario):
        """LV2가 드러난 시점 기준 TTC 계산"""
        # 차량 속도 (m/s로 변환)
        v_ego = scenario['v_ego'] / 3.6
        v_lv2 = scenario['v_lv2'] / 3.6
        
        # LV2가 드러난 시점 기준 THW
        thw_reveal = scenario['thw_ego_lv2_reveal']
        
        # 드러난 시점 거리 (m)
        d_reveal = v_ego * thw_reveal
        
        # 상대 속도
        v_rel = v_ego - v_lv2
        
        # TTC 계산 (상대 속도가 양수인 경우만)
        if v_rel > 0:
            # 충돌 시점까지의 시간 (차량 길이 고려)
            ttc_reveal = (d_reveal - self.min_safe_distance) / v_rel
            return ttc_reveal
        else:
            # 상대 속도가 0 이하면 충돌하지 않음 (무한대 TTC)
            return float('inf')
        
    def evaluate_human_model(self, scenario, ttc_reveal):
        """Human 모델 실패 여부 판단 (UN R157 2023년 1월 개정안 기준)"""
        # 인간 운전자 제동 시작 시점
        t_brake_start = self.human_reaction_time
        
        # 정지 거리 계산 (제동 빌드업 고려)
        v_ego = scenario['v_ego'] / 3.6  # m/s
        
        # 1. 반응 시간 동안 이동 거리
        d_reaction = v_ego * self.human_reaction_time
        
        # 2. 제동 빌드업 동안 이동 거리 (평균 감속도 적용)
        avg_decel_during_buildup = self.human_max_decel / 2
        d_buildup = v_ego * self.human_buildup_time - 0.5 * avg_decel_during_buildup * self.human_buildup_time**2
        
        # 3. 최대 제동 적용 시 정지 거리
        t_full_brake = v_ego / self.human_max_decel
        d_full_brake = 0.5 * self.human_max_decel * t_full_brake**2
        
        # 총 정지 거리
        d_stop = d_reaction + d_buildup + d_full_brake
        
        # 정지에 필요한 총 시간
        t_stop = self.human_reaction_time + self.human_buildup_time + t_full_brake
        
        # 강화된 기준 적용 (Human 실패 조건) - UN R157 2023년 1월 개정안 기준 적용
        return ttc_reveal < (t_stop + self.human_failure_offset)
        
    def evaluate_ads_model(self, scenario, ttc_reveal):
        """ADS 모델 실패 여부 판단 (UN R157 2023년 1월 개정안 기준)"""
        # ADS 제동 시작 시점
        t_brake_start = self.ads_reaction_time
        
        # 정지 거리 계산 (제동 빌드업 고려)
        v_ego = scenario['v_ego'] / 3.6  # m/s
        
        # 1. 반응 시간 동안 이동 거리
        d_reaction = v_ego * self.ads_reaction_time
        
        # 2. 제동 빌드업 동안 이동 거리 (평균 감속도 적용)
        avg_decel_during_buildup = self.ads_max_decel / 2
        d_buildup = v_ego * self.ads_buildup_time - 0.5 * avg_decel_during_buildup * self.ads_buildup_time**2
        
        # 3. 최대 제동 적용 시 정지 거리
        t_full_brake = v_ego / self.ads_max_decel
        d_full_brake = 0.5 * self.ads_max_decel * t_full_brake**2
        
        # 총 정지 거리
        d_stop = d_reaction + d_buildup + d_full_brake
        
        # 정지에 필요한 총 시간
        t_stop = self.ads_reaction_time + self.ads_buildup_time + t_full_brake
        
        # 강화된 기준 적용 (ADS 실패 조건) - UN R157 2023년 1월 개정안 기준 적용
        return ttc_reveal < (t_stop + self.ads_failure_offset)