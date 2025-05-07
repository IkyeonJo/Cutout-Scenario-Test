'''
scenariogeneration 라이브러리를 활용한 OpenSCENARIO 변환기
UN R157 2023년 1월 개정안 기준 적용
'''

import os
import logging
import math
import scenariogeneration as sg

logger = logging.getLogger('cutout_scenario.converter')

class CutOutScenarioGenerator(sg.ScenarioGenerator):
    """Cut-out 시나리오를 위한 ScenarioGenerator 확장 클래스"""
    
    def __init__(self, scenario_data, config):
        super().__init__()
        self.scenario_data = scenario_data
        self.config = config
    
    def scenario_name(self):
        """시나리오 이름 설정"""
        return f"Cut-out_Scenario_Ego_{self.scenario_data['v_ego']}_LV1_{self.scenario_data['v_lv1']}_LV2_{self.scenario_data['v_lv2']}"
    
    def road(self):
        """도로 네트워크 설정"""
        road_file = self.config['environment']['road_network']['road_file']
        return sg.xosc.RoadNetwork(roadfile=road_file)
    
    def parameters(self):
        """시나리오 파라미터 설정"""
        param_decl = sg.ParameterDeclarations()
        
        # 고정 파라미터 추가
        param_decl.add_parameter(sg.Parameter('LaneWidth', sg.ParameterType.double, str(self.config['environment']['road_network']['lane_width'])))
        
        return param_decl
    
    def entities(self):
        """시나리오 엔티티 설정"""
        # 차량 객체 목록
        entities = []
        
        # Ego 차량
        ego_config = self.config['vehicles']['ego_vehicle']
        ego_dims = ego_config['dimensions']
        
        ego = sg.ScenarioObject(name='Ego')
        ego.add_entity(sg.Vehicle('car', 
                                 sg.VehicleCategory.car, 
                                 sg.BoundingBox(ego_dims['width'], 
                                               ego_dims['length'], 
                                               ego_dims['height'], 
                                               ego_dims['width']/2, 
                                               0, 
                                               ego_dims['height']/2)))
        entities.append(ego)
        
        # LV1 (Lead Vehicle 1) 차량
        lv1_config = self.config['vehicles']['lead_vehicle_1']
        lv1_dims = lv1_config['dimensions']
        
        lv1 = sg.ScenarioObject(name='LV1')
        lv1.add_entity(sg.Vehicle('car', 
                                 sg.VehicleCategory.car, 
                                 sg.BoundingBox(lv1_dims['width'], 
                                               lv1_dims['length'], 
                                               lv1_dims['height'], 
                                               lv1_dims['width']/2, 
                                               0, 
                                               lv1_dims['height']/2)))
        entities.append(lv1)
        
        # LV2 (Lead Vehicle 2) 차량
        lv2_config = self.config['vehicles']['lead_vehicle_2']
        lv2_dims = lv2_config['dimensions']
        
        lv2 = sg.ScenarioObject(name='LV2')
        lv2.add_entity(sg.Vehicle('car', 
                                 sg.VehicleCategory.car, 
                                 sg.BoundingBox(lv2_dims['width'], 
                                               lv2_dims['length'], 
                                               lv2_dims['height'], 
                                               lv2_dims['width']/2, 
                                               0, 
                                               lv2_dims['height']/2)))
        entities.append(lv2)
        
        return entities
    
    def init(self):
        """초기 상태 설정"""
        init_actions = []
        
        # 차선 ID 및 도로 설정
        start_lane_id = self.config['environment']['road_network']['start_lane_id']
        
        # Ego 차량 초기화 (속도 및 위치)
        v_ego = self.scenario_data['v_ego'] / 3.6  # m/s로 변환
        
        # Ego 초기 위치
        init_actions.append(sg.TeleportAction(
            entity='Ego',
            position=sg.LanePosition(
                roadId=1,
                laneId=start_lane_id,
                offset=0.0,
                s=0.0
            )
        ))
        
        # Ego 초기 속도
        init_actions.append(sg.AbsoluteSpeedAction(
            entity='Ego',
            value=v_ego
        ))
        
        # LV1 차량 초기화
        v_lv1 = self.scenario_data['v_lv1'] / 3.6  # m/s로 변환
        d_ego_lv1 = self.scenario_data['d_ego_lv1']  # Ego와 LV1 사이 거리
        
        # LV1 초기 위치
        init_actions.append(sg.TeleportAction(
            entity='LV1',
            position=sg.LanePosition(
                roadId=1,
                laneId=start_lane_id,
                offset=0.0,
                s=d_ego_lv1
            )
        ))
        
        # LV1 초기 속도
        init_actions.append(sg.AbsoluteSpeedAction(
            entity='LV1',
            value=v_lv1
        ))
        
        # LV2 차량 초기화
        v_lv2 = self.scenario_data['v_lv2'] / 3.6  # m/s로 변환
        d_lv1_lv2 = self.scenario_data['d_lv1_lv2']  # LV1과 LV2 사이 거리
        
        # LV2 초기 위치
        init_actions.append(sg.TeleportAction(
            entity='LV2',
            position=sg.LanePosition(
                roadId=1,
                laneId=start_lane_id,
                offset=0.0,
                s=d_ego_lv1 + d_lv1_lv2
            )
        ))
        
        # LV2 초기 속도
        init_actions.append(sg.AbsoluteSpeedAction(
            entity='LV2',
            value=v_lv2
        ))
        
        return init_actions
    
    def create_entities(self):
        """실제 엔티티 생성"""
        return super().create_entities()
    
    def create_storyboard(self):
        """스토리보드 생성"""
        return super().create_storyboard()
    
    def maneuvers(self):
        """시나리오 기동 설정"""
        maneuver_groups = []
        
        # 차선 폭 계산
        lane_width = self.config['environment']['road_network']['lane_width']
        
        # 차선 변경 방향
        lane_change_direction = self.scenario_data['lane_change_direction']
        
        # LV1 차선 변경 기동 그룹
        lv1_maneuver_group = sg.ManeuverGroup("LV1_ManeuverGroup")
        lv1_maneuver_group.add_actor("LV1")
        
        # LV1 차선 변경 기동
        lane_change_maneuver = sg.Maneuver("LV1_LaneChange")
        
        # 차선 변경 이벤트
        lane_change_event = sg.Event("LaneChangeEvent", priority=sg.Priority.override)
        
        # 차선 변경 시작 트리거
        start_trigger = sg.ValueTrigger(
            name="LaneChangeStartTrigger",
            delay=0,
            conditionedge=sg.ConditionEdge.rising,
            valuecondition=sg.SimulationTimeCondition(1.0, sg.Rule.greaterThan)
        )
        lane_change_event.add_trigger(start_trigger)
        
        # 차선 변경 행동
        v_lv1_lat = self.scenario_data['v_lv1_lat']
        t_clear = lane_width / v_lv1_lat  # 차선 변경 완료 시간
        
        lane_change_action = sg.LaneChangeAction(
            entity="LV1",
            target_lane_offset=0.0,
            dynamics=sg.TransitionDynamics(
                shape=sg.DynamicsShape.sinusoidal,
                dimension=sg.DynamicsDimension.time,
                value=t_clear
            )
        )
        lane_change_action.set_relative_target_lane(lane_change_direction)
        lane_change_event.add_action(lane_change_action)
        
        # 이벤트를 기동에 추가
        lane_change_maneuver.add_event(lane_change_event)
        
        # 기동을 기동 그룹에 추가
        lv1_maneuver_group.add_maneuver(lane_change_maneuver)
        
        # 기동 그룹 추가
        maneuver_groups.append(lv1_maneuver_group)
        
        # LV2 감속 기동 그룹
        lv2_maneuver_group = sg.ManeuverGroup("LV2_ManeuverGroup")
        lv2_maneuver_group.add_actor("LV2")
        
        # LV2 감속 기동
        decel_maneuver = sg.Maneuver("LV2_Deceleration")
        
        # 감속 이벤트
        decel_event = sg.Event("DecelerationEvent", priority=sg.Priority.override)
        
        # 감속 시작 트리거
        trigger_delay = self.scenario_data['lv2_deceleration_trigger_delay']
        decel_trigger = sg.ValueTrigger(
            name="DecelerationStartTrigger",
            delay=trigger_delay,
            conditionedge=sg.ConditionEdge.rising,
            valuecondition=sg.SimulationTimeCondition(1.0 + t_clear, sg.Rule.greaterThan)
        )
        decel_event.add_trigger(decel_trigger)
        
        # 감속 행동
        dec_lv2 = self.scenario_data['dec_lv2']
        v_lv2 = self.scenario_data['v_lv2'] / 3.6  # m/s로 변환
        
        if dec_lv2 > 0:
            decel_action = sg.AbsoluteSpeedAction(
                entity="LV2",
                value=max(0, v_lv2 - dec_lv2 * 3.0),  # 3초 동안 감속 후 속도
                dynamics=sg.TransitionDynamics(
                    shape=sg.DynamicsShape.linear,
                    dimension=sg.DynamicsDimension.rate,
                    value=dec_lv2
                )
            )
            decel_event.add_action(decel_action)
            
            # 이벤트를 기동에 추가
            decel_maneuver.add_event(decel_event)
            
            # 기동을 기동 그룹에 추가
            lv2_maneuver_group.add_maneuver(decel_maneuver)
            
            # 기동 그룹 추가
            maneuver_groups.append(lv2_maneuver_group)
        
        return maneuver_groups
    
    def act(self):
        """시나리오 액트 설정"""
        act = sg.Act("CutOutAct")
        
        # 기동 그룹 생성 및 추가
        for maneuver_group in self.maneuvers():
            act.add_maneuver_group(maneuver_group)
        
        # 액트 시작 트리거
        act.add_start_trigger(sg.ValueTrigger(
            name="ActStartTrigger",
            delay=0,
            conditionedge=sg.ConditionEdge.rising,
            valuecondition=sg.SimulationTimeCondition(0.0, sg.Rule.greaterThan)
        ))
        
        return act
    
    def story(self):
        """시나리오 스토리 설정"""
        story = sg.Story("CutOutStory")
        
        # 액트 추가
        story.add_act(self.act())
        
        return story
    
    def storyboard(self):
        """스토리보드 설정"""
        storyboard = sg.StoryBoard()
        
        # 초기화 설정
        for init_action in self.init():
            if isinstance(init_action, sg.TeleportAction):
                storyboard.add_init_action(init_action.entity, init_action)
            elif isinstance(init_action, sg.AbsoluteSpeedAction):
                storyboard.add_init_action(init_action.entity, init_action)
        
        # 스토리 추가
        storyboard.add_story(self.story())
        
        return storyboard

class ComparativeScenarioConverter:
    """scenariogeneration 라이브러리를 활용한 OpenSCENARIO 변환기"""
    
    def __init__(self, config):
        self.config = config
        
    def convert_to_openscenario(self, test_case, output_file):
        """Test Case를 OpenSCENARIO (.xosc) 파일로 변환"""
        logger.info(f"시나리오를 OpenSCENARIO로 변환: {output_file}")
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # CutOutScenarioGenerator 인스턴스 생성
        scenario_generator = CutOutScenarioGenerator(test_case, self.config)
        
        # OpenSCENARIO 생성 및 저장
        scenario_generator.generate(output_file)
        
        logger.info(f"OpenSCENARIO 파일 생성 완료: {output_file}")
        return output_file