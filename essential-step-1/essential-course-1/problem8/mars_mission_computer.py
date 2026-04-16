#!/usr/bin/env python3

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

    # setting.txt의 기본 항목 및 기본값
    DEFAULT_SETTINGS = {
        'operating_system': True,
        'operating_system_version': True,
        'cpu_type': True,
        'cpu_core_count': True,
        'memory_size_gb': True,
        'cpu_usage_percent': True,
        'memory_usage_percent': True,
    }

    def load_settings(self):
        # setting.txt를 읽어 출력할 항목을 딕셔너리로 반환
        # 파일이 없거나 파싱 오류 시 기본값(전체 출력) 사용
        settings = dict(self.DEFAULT_SETTINGS)

        setting_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'setting.txt'
        )

        try:
            with open(setting_file, 'r', encoding = 'utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 빈 줄 또는 주석(#) 무시
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    if key in settings:
                        settings[key] = value.lower() == 'true'
                    else:
                        print(f'[setting.txt] 알 수 없는 항목 무시: {key}')
        except FileNotFoundError:
            print('[설정] setting.txt 파일이 없어 기본값으로 전체 항목을 출력합니다.')
        except Exception as e:
            print(f'[설정] setting.txt 읽기 오류: {e} — 기본값으로 실행합니다.')

        return settings

    def get_mission_computer_info(self):
        # 미션 컴퓨터의 시스템 정보를 조회하는 메소드
        # setting.txt에서 True로 설정된 항목만 출력
        try:
            settings = self.load_settings()

            # 전체 시스템 정보 수집
            all_info = {
                'operating_system': platform.system(),
                'operating_system_version': platform.release(),
                'cpu_type': platform.processor(),
                'cpu_core_count': multiprocessing.cpu_count(),
                'memory_size_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2)
            }

            # setting.txt에 따라 출력할 항목만 필터링
            system_info = {
                key: value
                for key, value in all_info.items()
                if settings.get(key, True)
            }

            # JSON 형태로 출력
            print('*' * 80)
            print('미션 컴퓨터 시스템 정보')
            print('*' * 80)
            json_output = json.dumps(system_info, indent = 2)
            print(json_output)
            print('*' * 80)

            return system_info

        except Exception as e:
            print(f'시스템 정보 수집 중 오류 발생: {e}')
            return None

    def get_mission_computer_load(self):
        # 미션 컴퓨터의 실시간 부하 정보를 조회하는 메소드
        # setting.txt에서 True로 설정된 항목만 출력
        try:
            settings = self.load_settings()

            # 전체 부하 정보 수집
            all_load = {
                'cpu_usage_percent': psutil.cpu_percent(interval = 1),
                'memory_usage_percent': psutil.virtual_memory().percent
            }

            # setting.txt에 따라 출력할 항목만 필터링
            load_info = {
                key: value
                for key, value in all_load.items()
                if settings.get(key, True)
            }

            # JSON 형태로 출력
            print('*' * 80)
            print('미션 컴퓨터 시스템 부하')
            print('*' * 80)
            json_output = json.dumps(load_info, indent = 2)
            print(json_output)
            print('*' * 80)

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
