# 문제 8: 불안정한 미션 컴퓨터 진단하기

## 📖 스토리

별다른 코딩을 한 것도 아닌데 미션 컴퓨터가 중간 중간 다운되는 현상이 일어나기 시작했다. 아직 생명유지와 관련된 기능까지 연결되어 있다면 문제가 심각해 질 것 같다. 컴퓨터의 상태를 좀 알고 싶긴한데 우주 기지에 설치된 컴퓨터라 완전히 밀봉되어 있어서 뜯어 보지도 못할 것 같다. 미션 컴퓨터의 지금 상태는 뭐가 문제인지 알 수가 없다.

지금 미션 컴퓨터의 상태를 알아보고 문제를 파악해 봐야겠는데 일단은 미션 컴퓨터 정보를 가져오는 코드를 좀 작성해서 상태를 파악해 봐야겠다.

---

## 🎯 수행 과제

### 1. 시스템 정보 조회 메소드: `get_mission_computer_info()`
- **운영체계** (Operating System)
- **운영체계 버전** (OS Version)
- **CPU의 타입** (CPU Type)
- **CPU의 코어 수** (CPU Core Count)
- **메모리의 크기** (Memory Size in GB)

### 2. 시스템 부하 조회 메소드: `get_mission_computer_load()`
- **CPU 실시간 사용량** (CPU Usage %)
- **메모리 실시간 사용량** (Memory Usage %)

### 3. JSON 형식 출력
- 두 메소드 모두 수집된 정보를 JSON 형식으로 화면에 출력

### 4. 메소드 호출 및 테스트
- `run_computer` 인스턴스로 두 메소드 호출하여 정상 동작 확인

### 5. 최종 저장
- 모든 코드를 `mars_mission_computer.py` 파일로 저장

---

## 🛠️ 코드 구현 설명

### 1. 클래스 설계: 상속을 통한 확장

```python
class MissionComputer(BaseMissionComputer):
    # Problem7의 MissionComputer를 상속받아 확장
```

**설계 포인트:**
- Problem7에서 작성한 `MissionComputer` 클래스를 베이스 클래스(`BaseMissionComputer`)로 사용
- 상속을 통해 기존 기능(센서 데이터 수집)은 유지하면서 새로운 기능 추가
- 객체 지향 프로그래밍의 확장성과 재사용성을 활용

### 2. Problem7 모듈 불러오기

```python
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
```

**구현 방식:**
- `importlib.util`을 사용하여 동적으로 다른 디렉토리의 모듈 로드
- 절대 경로(`os.path.abspath()`)와 상대 경로(`'..'`)를 조합하여 문제 7의 파일 위치 지정
- `MissionComputer` 클래스와 `DummySensor` 클래스를 동시에 불러옴

### 3. `get_mission_computer_info()` 메소드

```python
def get_mission_computer_info(self):
    try:
        system_info = {
            'operating_system': platform.system(),
            'operating_system_version': platform.release(),
            'cpu_type': platform.processor(),
            'cpu_core_count': multiprocessing.cpu_count(),
            'memory_size_gb': round(psutil.virtual_memory().total / (1024 ** 3), 2)
        }
        
        print('미션 컴퓨터 시스템 정보')
        print('=' * 50)
        json_output = json.dumps(system_info, indent = 2)
        print(json_output)
        
        return system_info
        
    except Exception as e:
        print(f'시스템 정보 수집 중 오류 발생: {e}')
        return None
```

**구현 세부사항:**

| 항목 | 라이브러리 | 함수 | 설명 |
|------|----------|------|------|
| **Operating System** | `platform` | `platform.system()` | 운영체계 이름 반환 (Darwin, Windows, Linux 등) |
| **OS Version** | `platform` | `platform.release()` | 운영체계 버전 번호 반환 |
| **CPU Type** | `platform` | `platform.processor()` | CPU 프로세서 정보 반환 |
| **CPU Cores** | `multiprocessing` | `cpu_count()` | 물리 CPU 코어 수 반환 |
| **Memory (GB)** | `psutil` | `virtual_memory().total` | 전체 메모리 바이트 단위로 반환 후 GB로 변환 |

**에러 처리:**
- `try-except` 블록으로 시스템 정보 수집 중 발생 가능한 예외 처리
- 오류 발생 시 오류 메시지 출력하고 `None` 반환

### 4. `get_mission_computer_load()` 메소드

```python
def get_mission_computer_load(self):
    try:
        cpu_usage = psutil.cpu_percent(interval = 1)
        memory_usage = psutil.virtual_memory().percent
        
        load_info = {
            'cpu_usage_percent': cpu_usage,
            'memory_usage_percent': memory_usage
        }
        
        print('미션 컴퓨터 시스템 부하')
        print('=' * 50)
        json_output = json.dumps(load_info, indent = 2)
        print(json_output)
        
        return load_info
        
    except Exception as e:
        print(f'시스템 부하 정보 수집 중 오류 발생: {e}')
        return None
```

**구현 세부사항:**

| 항목 | 함수 | 설명 |
|------|------|------|
| **CPU 사용량** | `psutil.cpu_percent(interval=1)` | 1초 동안의 CPU 사용률(%)을 계산 후 반환 |
| **메모리 사용량** | `psutil.virtual_memory().percent` | 현재 메모리 사용률(%)을 실시간 반환 |

**특징:**
- 실시간(Real-time) 정보 수집으로 컴퓨터의 현재 부하 상태 파악 가능
- `interval=1`은 1초 동안의 평균 CPU 사용률 계산을 의미
- 시스템 상태 진단에 매우 유용한 정보 제공

### 5. 메인 실행 블록

```python
if __name__ == '__main__':
    # DummySensor 인스턴스화
    ds = DummySensor()
    
    # MissionComputer 인스턴스화
    run_computer = MissionComputer(ds)
    
    # 미션 컴퓨터 시스템 정보 출력
    run_computer.get_mission_computer_info()
    
    # 미션 컴퓨터 시스템 부하 정보 출력
    run_computer.get_mission_computer_load()
```

**실행 순서:**
1. `DummySensor` 인스턴스 생성
2. `MissionComputer` 인스턴스 생성 (Problem7의 센서 기능 포함)
3. 시스템 정보 메소드 호출 및 출력
4. 시스템 부하 메소드 호출 및 출력

---

## 📊 실행 결과 예시

```
미션 컴퓨터 시스템 정보
==================================================
{
  "operating_system": "Darwin",
  "operating_system_version": "25.3.0",
  "cpu_type": "arm",
  "cpu_core_count": 8,
  "memory_size_gb": 16.0
}

미션 컴퓨터 시스템 부하
==================================================
{
  "cpu_usage_percent": 21.2,
  "memory_usage_percent": 78.7
}
```

---

## 🔑 핵심 구현 개념

### 1. **동적 모듈 로딩 (Dynamic Module Loading)**
- `importlib.util`을 사용하여 런타임에 다른 모듈 동적 로드
- 파일 경로를 동적으로 생성하여 유연성 제공

### 2. **클래스 상속 (Class Inheritance)**
- Problem7의 `MissionComputer` 클래스를 상속받아 새로운 기능 추가
- 기존 코드 재사용으로 개발 효율성 증대

### 3. **크로스 플랫폼 호환성**
- `platform` 모듈로 운영체계 정보 추상화
- Windows, macOS, Linux 등 다양한 플랫폼에서 동작

### 4. **시스템 모니터링**
- `psutil` 라이브러리로 CPU, 메모리 등 시스템 자원 모니터링
- 실시간 시스템 상태 파악으로 미션 컴퓨터 안정성 진단

### 5. **JSON 형식 출력**
- 구조화된 데이터 형식으로 가독성 향상
- 다른 시스템과의 통신/연동 시 호환성 제공

---

## 🛡️ 예외 처리

모든 메소드는 다음과 같은 예외 처리 구조를 적용합니다:

```python
try:
    # 시스템 정보 수집 로직
    ...
    return 결과
except Exception as e:
    print(f'오류 메시지: {e}')
    return None
```

**장점:**
- 시스템 정보 수집 중 발생 가능한 모든 예외 포착
- 프로그램 중단 없이 우아한 오류 처리 (Graceful Error Handling)
- 사용자에게 명확한 오류 메시지 제공

---

## 🎓 학습 포인트

이 문제를 통해 다음과 같은 고급 Python 개념을 학습할 수 있습니다:

1. **모듈 시스템:** 동적 모듈 로딩과 네임스페이스 관리
2. **객체 지향 설계:** 상속을 통한 코드 확장과 재사용
3. **시스템 프로그래밍:** 운영체계 정보 접근과 시스템 자원 모니터링
4. **데이터 직렬화:** JSON 형식으로 구조화된 데이터 표현
5. **에러 처리:** 견고한 프로그래밍을 위한 예외 처리 전략

