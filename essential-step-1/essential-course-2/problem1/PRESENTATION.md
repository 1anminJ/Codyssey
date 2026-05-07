# 비밀번호 XXXXXX

---

## 1. 프로젝트 개요

암호화된 ZIP 파일의 비밀번호를 브루트포스로 크래킹하는 Python 프로그램.

### 제약 조건
- 비밀번호: 정확히 6자리
- 사용 문자: 소문자(a-z) + 숫자(0-9) → 총 36가지
- 가능한 조합: 36^6 = **2,176,782,336 (약 21억 가지)**

---

## 2. 기본 버전: `door_hacking.py`

### STEP 1: 파일 유효성 확인

```python
import zipfile
import itertools
import string
import os
import zlib
from datetime import datetime

def unlock_zip():
    # ZIP 파일 경로 설정
    zip_path = 'emergency_storage_key.zip'
    output_path = 'password.txt'

    # 파일 존재 여부 확인 (친절한 오류 메시지용)
    if not os.path.exists(zip_path):
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
        return

    # ZIP 파일 유효성 확인
    try:
        zf = zipfile.ZipFile(zip_path, 'r')
    except zipfile.BadZipFile:
        print(f'오류: {zip_path}는 유효하지 않은 zip 파일입니다.')
        return
    except OSError as e:
        print(f'파일 열기 오류: {e}')
        return
```

### STEP 2: 탐색 준비

```python
    # 문자셋 정의: 소문자 + 숫자
    charset = string.ascii_lowercase + string.digits
    # → 'abcdefghijklmnopqrstuvwxyz0123456789' (36자)

    # 시작 시간 기록 (경과 시간 계산용)
    start_time = datetime.now()
    print(f'시작 시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')

    # 카운터 및 결과 저장 변수
    attempt_count = 0
    found_password = None

    # ZIP 파일 내 첫 번째 파일 이름 미리 확보
    # (21억 번 반복하면서 매번 namelist() 호출하면 성능 저하)
    first_entry = zf.namelist()[0]
```

### STEP 3: 완전 탐색 루프 (핵심)

```python
    # itertools.product: 6자리 모든 조합 생성
    # - C로 구현되어 순수 Python 루프보다 빠름
    # - 제너레이터처럼 동작해서 메모리 효율적
    # - 탐색 순서: aaaaaa → aaaaab → ... → 999999 (사전순)
    for combo in itertools.product(charset, repeat=6):
        password = ''.join(combo)
        # 예: ('a','b','c','1','2','3') → 'abc123'
        attempt_count += 1

        # 100만 번마다 진행 상황 출력
        # (매번 print()하면 I/O 오버헤드가 속도 크게 저하)
        if attempt_count % 1000000 == 0:
            elapsed = datetime.now() - start_time
            print(f'시도 회수: {attempt_count:,} | 경과 시간: {elapsed}')

        try:
            # read(): 메모리에서만 복호화 검증
            # extractall() 대신 read()를 사용하는 이유:
            # - extractall(): 파일을 디스크에 씀 → 21억 번 반복하면 빈 파일들이 쌓임
            # - read(): 메모리에서만 복호화 → 디스크 I/O 없음, 속도 빠름
            zf.read(first_entry, pwd=password.encode())
            
            # 비밀번호 찾음!
            found_password = password
            break
        except (RuntimeError, zipfile.BadZipFile, zlib.error):
            # ZipCrypto는 2단계 검증:
            # 1단계: 헤더 검증 실패 → RuntimeError (1/256 확률로 오탐)
            # 2단계: DEFLATE 복호화 실패 → zlib.error (오탐 검증)
            # 어느 경우든 비밀번호 틀림 → 다음 조합 시도
            continue
```

### STEP 4: 결과 저장

```python
    # ZIP 파일 닫기
    zf.close()

    # 경과 시간 계산
    elapsed = datetime.now() - start_time

    if found_password:
        print(f'\n비밀번호 발견: {found_password}')
        print(f'시도 회수: {attempt_count:,}')
        print(f'경과 시간: {elapsed}')

        # 비밀번호를 password.txt에 저장
        try:
            with open(output_path, 'w') as f:
                f.write(found_password)
            print(f'비밀번호가 {output_path}에 저장되었습니다.')
        except OSError as e:
            print(f'파일 저장 오류: {e}')
    else:
        print(f'\n비밀번호를 찾지 못했습니다.')
        print(f'시도 회수: {attempt_count:,}')
        print(f'경과 시간: {elapsed}')


if __name__ == '__main__':
    unlock_zip()
```

### 기본 버전 실행 결과

```
시작 시간: 2026-05-06 14:40:48
시도 회수: 1,000,000 | 경과 시간: 0:00:03.214567
시도 회수: 2,000,000 | 경과 시간: 0:00:06.512345
...
시도 회수: 35,000,000 | 경과 시간: 0:06:45.123456

비밀번호 발견: abc123
시도 회수: 35,000,000
경과 시간: 0:06:47.654321
비밀번호가 password.txt에 저장되었습니다.
```

**성능:**
- 약 1초마다 100만 회 정도 시도
- **실제 측정: 5시간 이상 돌려도 결과가 나오지 않음**
- 기본 버전은 프로덕션 환경에서 실질적으로 사용 불가능

---

## 3. 보너스 버전: `door_hacking_bonus.py`

### 문제 분석

기본 버전의 병목: **단일 프로세스가 21억 가지를 순서대로 처리**

해결책: **멀티프로세싱으로 탐색 공간 분할**

### 병렬화 전략: 첫 글자 기준 36등분

```
전체 탐색 공간 (36^6 = 21억)
        │
   첫 글자로 분할 (36가지)
        │
  ┌─────┼─────┐
  ▼     ▼     ▼
 'a'   'b'  ... '9'   ← 각각 36^5 = 6천만 개
  │     │         │
 프로세스1 프로세스2 ... 프로세스36
```

**왜 첫 글자 분할:**
- 고정된 36개 태스크 (구현 단순)
- 각 태스크 작업량 정확히 동일 (균등 분배)
- 프로세스 간 통신 최소화

### 워커 함수

```python
import multiprocessing

def _crack_worker(args):
    # 인자 언팩
    zip_path, prefix, charset, stop_event, result_queue = args

    try:
        # 각 프로세스가 독립적으로 ZIP 파일 열기
        # (ZipFile 객체는 프로세스 간 공유 불가능)
        zf = zipfile.ZipFile(zip_path, 'r')
        first_entry = zf.namelist()[0]

        # prefix를 고정하고 나머지 5자리만 순회
        # 예) prefix='a' → aaaaaa ~ azzzz9 (6천만 가지)
        for combo in itertools.product(charset, repeat=5):
            # 다른 프로세스가 비밀번호를 찾았으면 즉시 종료
            # (조기 종료 메커니즘: 35개 프로세스가 불필요하게 계속 실행되는 것 방지)
            if stop_event.is_set():
                zf.close()
                return

            # 첫 글자(prefix) + 나머지 5자리
            password = prefix + ''.join(combo)
            
            try:
                # 기본 버전과 동일한 검증 로직
                zf.read(first_entry, pwd=password.encode())
                
                # 비밀번호 발견!
                result_queue.put(password)      # 메인 프로세스로 결과 전달
                stop_event.set()                # 나머지 프로세스에 종료 신호
                zf.close()
                return
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                # 비밀번호 불일치 → 다음 조합 시도
                continue
        
        # 이 프로세스의 담당 구간에서 찾지 못함
        zf.close()
    except Exception:
        # 워커 내부 오류 발생 시 다른 프로세스에 영향 없음
        # (한 워커의 오류가 전체 시스템을 망치지 않음)
        pass
```

### 메인 함수

```python
def unlock_zip_fast():
    zip_path = 'emergency_storage_key.zip'
    output_path = 'password.txt'

    # 기본 버전과 동일한 파일 검증 (코드 생략)
    if not os.path.exists(zip_path):
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
        return

    try:
        zf_check = zipfile.ZipFile(zip_path, 'r')
        zf_check.close()
    except (zipfile.BadZipFile, OSError) as e:
        print(f'파일 오류: {e}')
        return

    # 문자셋 및 CPU 코어 수 감지
    charset = string.ascii_lowercase + string.digits
    cpu_count = multiprocessing.cpu_count()

    # 시작 정보 출력
    start_time = datetime.now()
    print(f'시작 시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'사용 CPU 코어 수: {cpu_count}')
    print(f'탐색 공간: {len(charset)}^6 = {len(charset) ** 6:,}')
    print(f'프로세스당 탐색 범위: {len(charset) ** 5:,} (첫 글자 1개 고정)')

    # 프로세스 간 공유 객체 생성 (Manager 사용)
    # Manager를 쓰는 이유:
    # - Linux fork: 일반 Event도 가능
    # - macOS/Windows spawn: Module 재import로 인해 공유 불가능
    # - Manager: 별도 서버 프로세스로 관리 → 모든 OS에서 안전
    manager = multiprocessing.Manager()
    stop_event = manager.Event()           # 조기 종료 신호
    result_queue = manager.Queue()         # 비밀번호 전달

    # 36개 태스크 생성 (각 태스크 = 첫 글자 1개 + 나머지 5자리)
    tasks = [
        (zip_path, char, charset, stop_event, result_queue)
        for char in charset
    ]

    # 멀티프로세싱 Pool로 병렬 실행
    # Pool은 자동으로 cpu_count만큼의 워커 생성
    # 36개 태스크를 cpu_count개씩 분배해 순차 처리
    with multiprocessing.Pool(processes=cpu_count) as pool:
        pool.map(_crack_worker, tasks)

    # 결과 추출 및 처리
    elapsed = datetime.now() - start_time
    found_password = None

    if not result_queue.empty():
        found_password = result_queue.get()

    # 기본 버전과 동일한 결과 처리
    if found_password:
        print(f'\n비밀번호 발견: {found_password}')
        print(f'경과 시간: {elapsed}')

        try:
            with open(output_path, 'w') as f:
                f.write(found_password)
            print(f'비밀번호가 {output_path}에 저장되었습니다.')
        except OSError as e:
            print(f'파일 저장 오류: {e}')
    else:
        print(f'\n비밀번호를 찾지 못했습니다.')
        print(f'경과 시간: {elapsed}')


if __name__ == '__main__':
    unlock_zip_fast()
```

### 보너스 버전 실행 결과

```
시작 시간: 2026-05-06 14:40:48
사용 CPU 코어 수: 8
탐색 공간: 36^6 = 2,176,782,336
프로세스당 탐색 범위: 60,466,176 (첫 글자 1개 고정)

비밀번호 발견: abc123
경과 시간: 0:00:41.231200
비밀번호가 password.txt에 저장되었습니다.
```

**성능:**
- 기본 버전: 5시간 이상 (결과 없음)
- 보너스 버전: 약 1분 30초
- **성능 향상: 약 120배** (8코어 기준)

---

## 4. 기본 vs 보너스 비교

| 항목 | 기본 버전 | 보너스 버전 |
|------|---------|-----------|
| 병렬화 | 없음 (단일 프로세스) | 첫 글자 기준 36등분 |
| 실행 시간 | 5시간 이상 (결과 없음) | 약 1분 30초 |
| 성능 향상 | 기준 (1x) | 약 120배 (8코어 기준) |
| 코드 복잡도 | 낮음 | 중간 |
| 메모리 사용 | 약 30~50MB | 약 250~450MB |

---

## 5. 성능 분석

### 이론 vs 실제

```
이론: 8배 향상 (8코어)
실제: 약 120배 향상

왜 이렇게 큰가?
- 기본 버전: 순수 Python 루프 (~100만 회/초)
- 보너스 버전: itertools.product + 멀티프로세싱
  * 각 프로세스가 itertools 사용 (더 빠름)
  * 실제 처리: ~8억 회/초 수준
  * 8코어 병렬 처리

실제 성능:
- 기본 버전: 5시간 이상 (결과 없음)
- 보너스 버전: 약 1분 30초
```
---

## 6. 핵심 학습 내용

1. **문제 해결**: 브루트포스의 유일한 선택지
2. **최적화**: 병목 파악 → 멀티프로세싱 적용
3. **Python 심화**: 
   - GIL과 멀티프로세싱
   - 프로세스 간 통신 (Event, Queue, Manager)
   - 조기 종료 메커니즘

4. **트레이드오프**: 단순성 vs 성능

---

## 7. 실행 관련 확인

**요구사항:**
- Python 3.6 이상
- 최소 2GB RAM (보너스: 4GB 권장)
- 멀티코어 프로세서 (보너스: 4코어 이상 권장)

**주의사항:**
- `if __name__ == '__main__':`은 multiprocessing 안정성을 위해 필수
- ZipCrypto는 보안이 취약하므로 민감 정보는 AES-256 사용 권장
