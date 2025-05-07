#!/usr/bin/env python3
'''
Cut-out 시나리오 분석 및 시험 자동화 도구 메인 모듈
'''

import os
import logging
from .generators.scenario_generator import ScenarioGenerator
from .calculators.ttc_calculator import TTCCalculator
from .filters.scenario_filter import ScenarioFilter
from .reporters.excel_reporter import ExcelReporter
from .reporters.plot_visualizer import PlotVisualizer
from .utils.sampling import StratifiedSampler
from .converters.comparative_scenario_converter import ComparativeScenarioConverter
from .runners.simulation_runner import SimulationRunner
from .processors.video_processor import VideoProcessor

logger = logging.getLogger('cutout_scenario.main')

def main(config):
    '''메인 실행 함수'''
    logger.info("Cut-out 시나리오 분석 시작")
    
    # 1. Concrete Scenario 생성
    logger.info("시나리오 생성 중...")
    generator = ScenarioGenerator(config)
    concrete_scenarios = generator.generate_scenarios()
    logger.info(f"생성된 Concrete Scenario 수: {len(concrete_scenarios)}")
    
    # 2. TTC 계산 및 필터링
    logger.info("시나리오 필터링 중...")
    scenario_filter = ScenarioFilter(config)
    filtered_scenarios = scenario_filter.filter_scenarios(concrete_scenarios)
    logger.info(f"필터링된 Test Case 수: {len(filtered_scenarios)}")
    
    # 3. 엑셀 리포트 생성
    logger.info("엑셀 리포트 생성 중...")
    output_dir = config['simulation']['output']['output_directory']
    excel_file = os.path.join(output_dir, 'reports', config['simulation']['output']['excel_report_name'])
    excel_reporter = ExcelReporter(config)
    excel_reporter.create_report(filtered_scenarios)
    logger.info(f"엑셀 리포트 저장: {excel_file}")
    
    # 4. 3D 산점도 생성 (선택 사항)
    try:
        logger.info("3D 산점도 생성 중...")
        plot_file = os.path.join(output_dir, 'reports', 'scenario_3d_plot.html')
        visualizer = PlotVisualizer(config)
        visualizer.create_3d_scatter_plot(filtered_scenarios, plot_file)
        logger.info(f"3D 산점도 저장: {plot_file}")
    except Exception as e:
        logger.warning(f"3D 산점도 생성 실패: {e}")
    
    # 5. 시뮬레이션 대상 샘플링
    logger.info("시뮬레이션 대상 샘플링 중...")
    sampler = StratifiedSampler()
    target_count = config['simulation']['sampling']['target_sample_count']
    sampled_scenarios = sampler.sample_test_cases(
        filtered_scenarios,
        target_count,
        'v_ego',
        config['simulation']['sampling']['prioritize_by']
    )
    logger.info(f"샘플링된 Test Case 수: {len(sampled_scenarios)}")
    
    # 6. 엑셀 리포트에 샘플링 결과 추가
    logger.info("엑셀 리포트에 샘플링 결과 추가 중...")
    excel_reporter.add_sampled_scenarios(excel_file, sampled_scenarios)
    
    # 7. OpenSCENARIO 변환 (scenariogeneration 라이브러리 사용)
    logger.info("OpenSCENARIO 변환 중...")
    converter = ComparativeScenarioConverter(config)
    xosc_files = []
    scenarios_dir = os.path.join(output_dir, 'scenarios')
    
    for i, scenario in enumerate(sampled_scenarios):
        xosc_file = os.path.join(scenarios_dir, f"scenario_{i+1:03d}.xosc")
        converter.convert_to_openscenario(scenario, xosc_file)
        xosc_files.append(xosc_file)
    
    logger.info(f"OpenSCENARIO 파일 생성 완료: {len(xosc_files)}개")
    
    # 8. 시뮬레이션 실행
    logger.info("시뮬레이션 실행 중...")
    runner = SimulationRunner(config)
    video_processor = VideoProcessor(config)
    videos_dir = os.path.join(output_dir, 'videos')
    
    for i, xosc_file in enumerate(xosc_files):
        logger.info(f"시나리오 {i+1}/{len(xosc_files)} 실행 중...")
        
        # 시뮬레이션 실행
        sim_output_dir = os.path.join(output_dir, f"sim_temp_{i+1:03d}")
        os.makedirs(sim_output_dir, exist_ok=True)
        runner.run_simulation(xosc_file, sim_output_dir)
        
        # 비디오 생성
        video_file = os.path.join(videos_dir, f"scenario_{i+1:03d}.{config['simulation']['output']['video_format']}")
        video_processor.create_video(sim_output_dir, video_file)
        
        # 임시 파일 정리 (선택 사항)
        # import shutil
        # shutil.rmtree(sim_output_dir)
    
    logger.info("Cut-out 시나리오 분석 완료")
    return filtered_scenarios, sampled_scenarios

if __name__ == "__main__":
    print("이 모듈은 직접 실행하지 마세요. run.py를 통해 실행하세요.")
