import random
import datetime


class DummySensor:
    # 화성 기지의 환경값을 시뮬레이션하는 더미 센서 클래스

    def __init__(self):
        # DummySensor 초기화
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        # 센서 값을 지정된 범위 내에서 랜덤으로 생성
        self.env_values['mars_base_internal_temperature'] = \
            round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = \
            round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = \
            round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = \
            round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = \
            round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = \
            round(random.uniform(4, 7), 2)

    def get_env(self):
        # 보너스 과제: 환경값을 파일에 로그로 남기고 센서값 반환
        try:
            # 현재 날짜와 시간 가져오기
            now = datetime.datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

            # 로그 데이터 구성
            log_data = (
                f'{timestamp}, '
                f'{self.env_values["mars_base_internal_temperature"]}, '
                f'{self.env_values["mars_base_external_temperature"]}, '
                f'{self.env_values["mars_base_internal_humidity"]}, '
                f'{self.env_values["mars_base_external_illuminance"]}, '
                f'{self.env_values["mars_base_internal_co2"]}, '
                f'{self.env_values["mars_base_internal_oxygen"]}\n'
            )

            # 로그 파일에 기록 (append 모드)
            with open('mars_sensor.log', 'a', encoding='utf-8') as log_file:
                log_file.write(log_data)

        except IOError as e:
            print(f'로그 파일 기록 오류: {e}')
        except Exception as e:
            print(f'예상치 못한 오류: {e}')

        return self.env_values


if __name__ == '__main__':
    # DummySensor 인스턴스 생성
    ds = DummySensor()

    # set_env() 호출로 센서 값 생성
    ds.set_env()

    # get_env() 호출로 센서 값 확인
    env_data = ds.get_env()

    # 환경값 출력
    print('화성 기지 환경값:')
    for key, value in env_data.items():
        # 읽기 쉬운 형태로 출력
        display_key = key.replace('_', ' ').title()
        print(f'{display_key}: {value}')

