import json
import os
import importlib.util
import platform
import multiprocessing

try:
    import psutil
except ImportError as e:
    print('psutil 라이브러리가 설치되지 않았습니다.')
    print('pip3 install psutil 을 실행해주세요.')
    print(f'오류 메시지: {e}')
    exit(1)

# Problem7에서 MissionComputer 클래스 불러오기
problem7_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'problem7', 'mars_mission_computer.py'
)
spec = importlib.util.spec_from_file_location('mission_computer_module', problem7_file)
mission_computer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mission_computer_module)
BaseMissionComputer = mission_computer_module.MissionComputer
DummySensor = mission_computer_module.DummySensor


class MissionComputer(BaseMissionComputer):
    # Problem7의 MissionComputer를 상속받아 시스템 정보/부하 조회 기능을 추가한 클래스

    def get_mission_computer_info(self):
        # 미션 컴퓨터의 시스템 정보를 조회하는 메소드
        try:
            # 운영체계 정보 수집
            system_info = {
                'operating_system': platform.system(),
                'operating_system_version': platform.release(),
                'cpu_type': platform.processor(),
                'cpu_core_count': multiprocessing.cpu_count(),
                'memory_size_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2)
            }

            # JSON 형태로 출력
            print('미션 컴퓨터 시스템 정보')
            print('=' * 50)
            json_output = json.dumps(system_info, indent = 2)
            print(json_output)
            print('')

            return system_info

        except Exception as e:
            print(f'시스템 정보 수집 중 오류 발생: {e}')
            return None

    def get_mission_computer_load(self):
        # 미션 컴퓨터의 실시간 부하 정보를 조회하는 메소드
        try:
            # CPU 실시간 사용량 (%)
            cpu_usage = psutil.cpu_percent(interval = 1)

            # 메모리 실시간 사용량 (%)
            memory_usage = psutil.virtual_memory().percent

            # 부하 정보 딕셔너리
            load_info = {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage
            }

            # JSON 형태로 출력
            print('미션 컴퓨터 시스템 부하')
            print('=' * 50)
            json_output = json.dumps(load_info, indent = 2)
            print(json_output)

            return load_info

        except Exception as e:
            print(f'시스템 부하 정보 수집 중 오류 발생: {e}')
            return None


if __name__ == '__main__':
    # DummySensor 인스턴스화
    ds = DummySensor()

    # MissionComputer 인스턴스화
    run_computer = MissionComputer(ds)

    # 미션 컴퓨터 시스템 정보 출력
    run_computer.get_mission_computer_info()

    # 미션 컴퓨터 시스템 부하 정보 출력
    run_computer.get_mission_computer_load()

