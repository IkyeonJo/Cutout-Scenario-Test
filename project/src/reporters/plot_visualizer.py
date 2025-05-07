'''
3D 시각화 도구
'''

import os
import logging
import plotly.graph_objects as go
import numpy as np

logger = logging.getLogger('cutout_scenario.visualizer')

class PlotVisualizer:
    """3D 시각화 도구"""
    
    def __init__(self, config):
        self.config = config
        
    def create_3d_scatter_plot(self, filtered_scenarios, output_file):
        """필터링된 Test Case에 대한 3D 산점도 생성"""
        logger.info(f"3D 산점도 생성 시작: {output_file}")
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 데이터 준비
        v_ego = [scenario['v_ego'] for scenario in filtered_scenarios]
        v_lv2 = [scenario['v_lv2'] for scenario in filtered_scenarios]
        ttc_reveal = [min(scenario['ttc_reveal'], 10) for scenario in filtered_scenarios]  # 무한대 값 제한
        
        # 컬러 스케일 설정
        colorscale = 'Viridis'
        
        # 3D 산점도 생성
        fig = go.Figure(data=[go.Scatter3d(
            x=v_ego,
            y=v_lv2,
            z=ttc_reveal,
            mode='markers',
            marker=dict(
                size=5,
                color=ttc_reveal,
                colorscale=colorscale,
                opacity=0.8,
                colorbar=dict(title="TTC_reveal (s)")
            ),
            text=[f"Ego: {v_ego[i]:.1f}km/h<br>LV2: {v_lv2[i]:.1f}km/h<br>TTC: {ttc_reveal[i]:.3f}s" for i in range(len(v_ego))],
            hoverinfo='text'
        )])
        
        # 레이아웃 설정
        fig.update_layout(
            title='Cut-out 시나리오 Test Case 3D 분포 (UN R157 2023년 1월 개정안 기준)',
            scene=dict(
                xaxis_title='Ego 속도 (km/h)',
                yaxis_title='LV2 속도 (km/h)',
                zaxis_title='TTC_reveal (s)'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        
        # HTML 파일로 저장
        fig.write_html(output_file)
        logger.info(f"3D 산점도 저장 완료: {output_file}")
        
        return output_file