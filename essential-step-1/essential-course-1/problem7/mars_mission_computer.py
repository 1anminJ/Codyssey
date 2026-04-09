#!/usr/bin/env python3

import json
import time
import threading
import datetime
import os
import importlib.util

# Problem6에서 DummySensor 클래스 불러오기
problem6_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'problem6', 'mars_mission_computer.py'
)
spec = importlib.util.spec_from_file_location('dummy_sensor_module', problem6_file)
dummy_sensor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dummy_sensor_module)
DummySensor = dummy_sensor_module.DummySensor


class MissionComputer:
    # 화성 기지의 센서 데이터를 수집하고 관리하는 클래스

    def __init__(self, sensor):
        # MissionComputer 초기화
        self.sensor = sensor
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.stop_flag = False
        # 5분 평균 계산을 위한 데이터 저장소
        self.five_minute_data = {
            'mars_base_internal_temperature': [],
            'mars_base_external_temperature': [],
            'mars_base_internal_humidity': [],
            'mars_base_external_illuminance': [],
            'mars_base_internal_co2': [],
            'mars_base_internal_oxygen': []
        }

    def input_listener(self):
        # 키 입력을 감지하는 스레드 함수
        try:
            while not self.stop_flag:
                user_input = input()
                if user_input.lower() in ['q', 'quit', 'exit', 'stop']:
                    self.stop_flag = True
                    print('System stopped....')
                    break
        except EOFError:
            # 입력 스트림이 종료된 경우
            pass
        except Exception as e:
            print(f'입력 처리 오류: {e}')

    def print_five_minute_average(self):
        # 5분 평균값 출력
        print('\n' + '=' * 80)
        print('5분 평균 환경값')
        print('=' * 80)

        average_values = {}
        for key, values in self.five_minute_data.items():
            if values:
                avg = sum(values) / len(values)
                average_values[key] = round(avg, 4)
            else:
                average_values[key] = 0.0

        # JSON 형태로 평균값 출력
        json_output = json.dumps(average_values, indent=2)
        print(json_output)
        print('=' * 80 + '\n')

        # 평균값 계산 후 데이터 초기화
        for key in self.five_minute_data:
            self.five_minute_data[key] = []

    def get_sensor_data(self, duration=None):
        # 센서의 값을 가져와서 env_values에 담고 5초마다 반복
        # duration: None일 경우 무한 반복, 초 단위로 지정시 해당 시간만 실행
        print('*' * 80)
        print('화성 기지 센서 데이터 수집 시작')
        print('프로그램을 중지하려면 q, quit, exit, stop 중 하나를 입력하세요.')
        print('*' * 80)

        # 키 입력을 감지하는 스레드 시작
        input_thread = threading.Thread(target=self.input_listener, daemon=True)
        input_thread.start()

        start_time = time.time()
        last_average_time = time.time()
        iteration = 1

        try:
            while not self.stop_flag:
                # duration이 지정된 경우 시간 체크
                if duration is not None:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= duration:
                        break

                # 센서에서 새로운 값 생성
                self.sensor.set_env()

                # 센서의 값을 가져와서 env_values에 담기
                self.env_values = self.sensor.get_env()

                # 5분 평균 데이터에 현재값 추가
                for key, value in self.env_values.items():
                    self.five_minute_data[key].append(value)

                # 현재 시간
                now = datetime.datetime.now()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

                # env_values를 JSON 형태로 출력
                print(f'\n[{iteration}차 수집] {timestamp}')
                print('-' * 80)
                json_output = json.dumps(self.env_values, indent=2)
                print(json_output)
                print('-' * 80)

                iteration += 1

                # 5분(300초)마다 평균값 출력
                current_time = time.time()
                if current_time - last_average_time >= 300:
                    self.print_five_minute_average()
                    last_average_time = current_time

                # 5초 대기 (마지막 반복이 아닌 경우)
                if not self.stop_flag:
                    if duration is None or time.time() - start_time < duration:
                        time.sleep(5)

        except KeyboardInterrupt:
            print('\n\n센서 데이터 수집이 중단되었습니다.')
            print('*' * 80)
        except Exception as e:
            print(f'센서 데이터 수집 중 오류 발생: {e}')
        finally:
            print('\n' + '*' * 80)
            print('화성 기지 센서 데이터 수집 종료')
            print('*' * 80)


if __name__ == '__main__':
    # DummySensor 인스턴스화
    ds = DummySensor()

    # MissionComputer 인스턴스화
    run_computer = MissionComputer(ds)

    # 보너스 과제: 키 입력 감지 및 5분 평균값 출력
    # - 특정 키(q, quit, exit, stop)를 입력하면 'System stopped....' 출력 후 중지
    # - 5분(300초)마다 각 환경값에 대한 평균값을 별도로 출력
    run_computer.get_sensor_data()

