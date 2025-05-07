'''
비디오 생성 프로세서
'''

import os
import subprocess
import logging
import glob

logger = logging.getLogger('cutout_scenario.video_processor')

class VideoProcessor:
    """비디오 생성 프로세서"""
    
    def __init__(self, config):
        self.config = config
        self.frame_rate = config['simulation']['output']['frame_rate']
        
    def create_video(self, image_folder, output_file):
        """이미지 파일을 비디오로 변환"""
        logger.info(f"비디오 생성 시작: {output_file}")
        
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 이미지 파일 목록 확인
        image_pattern = os.path.join(image_folder, "screenshot_*.jpg")
        image_files = sorted(glob.glob(image_pattern))
        
        if not image_files:
            logger.warning(f"이미지 파일이 없습니다: {image_pattern}")
            return False
        
        try:
            # FFmpeg 명령어 구성
            cmd = [
                "ffmpeg",
                "-framerate", str(self.frame_rate),
                "-pattern_type", "glob",
                "-i", image_pattern,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                "-y",  # 기존 파일 덮어쓰기
                output_file
            ]
            
            # FFmpeg 실행
            logger.debug(f"FFmpeg 명령어: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            # 결과 확인
            if process.returncode != 0:
                logger.error(f"비디오 생성 실패: {stderr.decode('utf-8')}")
                return False
            
            logger.info(f"비디오 생성 완료: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"비디오 생성 중 오류 발생: {str(e)}")
            return False