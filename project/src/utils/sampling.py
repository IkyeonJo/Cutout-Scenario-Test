'''
비례 층화 샘플링 유틸리티
'''

import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger('cutout_scenario.sampling')

class StratifiedSampler:
    """비례 층화 샘플링 유틸리티"""
    
    @staticmethod
    def sample_test_cases(filtered_scenarios, target_count, groupby_key, priority_key):
        """비례 층화 샘플링으로 최종 Test Case 선택"""
        logger.info(f"비례 층화 샘플링 시작: 대상 {target_count}개")
        
        if not filtered_scenarios:
            logger.warning("샘플링할 시나리오가 없습니다.")
            return []
        
        # 그룹별로 시나리오 분류
        groups = defaultdict(list)
        for scenario in filtered_scenarios:
            group_value = scenario[groupby_key]
            groups[group_value].append(scenario)
        
        logger.info(f"총 {len(groups)}개 그룹으로 분류됨")
        
        # 각 그룹의 크기 계산
        group_sizes = {group: len(scenarios) for group, scenarios in groups.items()}
        total_scenarios = len(filtered_scenarios)
        
        # 비례 할당 (각 그룹에서 샘플링할 개수 계산)
        group_allocations = {}
        remaining = target_count
        
        for group, size in group_sizes.items():
            # 비례 할당 계산 (반올림)
            allocation = round((size / total_scenarios) * target_count)
            
            # 할당 개수가 그룹 크기보다 크면 조정
            allocation = min(allocation, size)
            
            # 0개가 할당된 경우 최소 1개 할당 (샘플이 충분할 경우)
            if allocation == 0 and size > 0 and remaining > 0:
                allocation = 1
            
            group_allocations[group] = allocation
            remaining -= allocation
        
        # 남은 할당량 배분 (큰 그룹부터)
        if remaining > 0:
            sorted_groups = sorted(group_sizes.items(), key=lambda x: x[1], reverse=True)
            for group, _ in sorted_groups:
                if remaining <= 0:
                    break
                if group_allocations[group] < group_sizes[group]:
                    group_allocations[group] += 1
                    remaining -= 1
        
        # 할당량이 목표를 초과하는 경우 조정
        while sum(group_allocations.values()) > target_count:
            # 가장 큰 할당량을 가진 그룹에서 1개 감소
            max_group = max(group_allocations.items(), key=lambda x: x[1])[0]
            group_allocations[max_group] -= 1
        
        # 그룹별 할당량 로그 출력
        for group, allocation in sorted(group_allocations.items()):
            logger.info(f"그룹 {group}: {allocation}개 샘플링 (전체 {group_sizes[group]}개 중)")
        
        # 우선순위에 따라 각 그룹에서 시나리오 선택
        sampled_scenarios = []
        
        for group, scenarios in groups.items():
            allocation = group_allocations.get(group, 0)
            if allocation <= 0:
                continue
            
            # 우선순위 키로 정렬 (값이 작을수록 우선)
            sorted_scenarios = sorted(scenarios, key=lambda x: x.get(priority_key, float('inf')))
            
            # 할당된 개수만큼 선택
            selected = sorted_scenarios[:allocation]
            sampled_scenarios.extend(selected)
        
        logger.info(f"최종 샘플링된 시나리오 수: {len(sampled_scenarios)}")
        return sampled_scenarios
