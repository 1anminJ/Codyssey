# 발표 스크립트

> 💡 **사용법**: 각 단계마다 해당 코드 블록을 화면에 띄워두고 말하기

---

## 오프닝 (30초)

"안녕하세요. 저는 암호화된 ZIP 파일의 비밀번호를 코드로 직접 크래킹하는 프로그램을 구현했습니다.
비밀번호 조건은 소문자와 숫자로 이루어진 6자리, 가능한 조합은 36의 6제곱, 약 21억 가지입니다.
이 21억 개를 얼마나 빠르게, 적은 자원으로 처리하느냐가 이번 구현의 핵심이었습니다."

---

## STEP 1 — 파일 유효성 확인

```python
if not os.path.exists(zip_path):
    print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
    return

try:
    zf = zipfile.ZipFile(zip_path, 'r')
except zipfile.BadZipFile:
    print(f'오류: {zip_path}는 유효하지 않은 zip 파일입니다.')
    return
except OSError as e:
    print(f'파일 열기 오류: {e}')
    return
```

"먼저 파일이 존재하는지, ZIP 형식이 올바른지 확인합니다.
`ZipFile()`을 바로 열어도 예외가 나긴 하는데, 오류 메시지가 Python 내부 형태라 불친절합니다.
`os.path.exists()`로 먼저 확인하면 어떤 문제인지 명확한 메시지를 줄 수 있습니다.
`BadZipFile`과 `OSError`를 나눠 잡는 것도 파일 형식 문제인지 시스템 문제인지 구분하기 위해서입니다."

---

## STEP 2 — 문자셋 & 탐색 공간 설정

```python
charset = string.ascii_lowercase + string.digits
# → 'abcdefghijklmnopqrstuvwxyz0123456789' (36자)

start_time = datetime.now()

first_entry = zf.namelist()[0]  # 루프 밖에서 미리 꺼내둠
```

"`string` 모듈 상수를 쓰는 건 하드코딩 시 오타 방지 때문입니다.
`namelist()[0]`을 루프 바깥에서 꺼내두는 건 작은 최적화입니다.
루프 안에서 매번 호출하면 21억 번 동안 불필요하게 반복되기 때문에 미리 변수에 저장해둡니다."

---

## STEP 3 — 완전 탐색 루프 (핵심)

```python
for combo in itertools.product(charset, repeat=6):
    password = ''.join(combo)
    attempt_count += 1

    if attempt_count % 1000000 == 0:
        elapsed = datetime.now() - start_time
        print(f'시도 회수: {attempt_count:,} | 경과 시간: {elapsed}')

    try:
        zf.read(first_entry, pwd=password.encode())
        found_password = password
        break
    except (RuntimeError, zipfile.BadZipFile, zlib.error):
        continue
```

**`itertools.product` 이유**
"6중 for 루프로도 같은 결과를 낼 수 있습니다. 쓴 이유는 두 가지입니다.
첫째, C로 구현돼 있어 Python 루프보다 빠릅니다.
둘째, 제너레이터처럼 동작해서 21억 개를 한 번에 메모리에 올리지 않고 하나씩만 꺼냅니다.
만약 리스트로 만들면 각 문자열이 약 50바이트라 21억 × 50 = 100GB, 메모리에 올릴 수가 없습니다."

**`read()` 이유**
"처음에 `extractall()`로 짰다가 오류가 났습니다.
`extractall()`은 비밀번호가 틀려도 파일을 디스크에 먼저 만든 뒤 복호화 단계에서 오류를 냅니다.
21억 번 반복하면 빈 파일이 계속 생기고 덮어씌워지는 부작용이 있습니다.
`read()`는 메모리에서만 복호화를 시도하기 때문에 디스크에 아무것도 쓰지 않습니다."

**예외 3가지 이유**
"ZipCrypto는 비밀번호 검증을 2단계로 합니다.
1단계는 12바이트 헤더를 복호화해서 마지막 바이트를 확인하는데, 여기서 실패하면 `RuntimeError`가 납니다.
문제는 1/256 확률로 틀린 비밀번호가 1단계를 통과하는 오탐이 있습니다.
이 경우 2단계에서 실제 데이터를 복호화하다가 `zlib.error`가 납니다.
처음에는 이 `zlib.error`가 왜 나는지 몰랐는데, ZIP 암호화 구조를 찾아보다가 이유를 알게 됐습니다."

**100만 번 출력 이유**
"매번 `print()`를 호출하면 I/O 오버헤드가 크래킹 속도를 떨어뜨립니다.
100만 번에 한 번이면 약 1초 간격으로, 프로그램이 살아있다는 걸 확인하기 충분한 주기입니다."

---

## STEP 4 — 결과 저장

```python
zf.close()

if found_password:
    with open(output_path, 'w') as f:
        f.write(found_password)
```

"찾은 비밀번호를 `password.txt`에 저장하고 끝납니다.
ZIP에서 파일을 직접 추출하지 않는 이유는, 이 프로그램의 역할이 비밀번호를 찾는 것까지이기 때문입니다.
비밀번호를 알면 사용자가 직접 ZIP을 열 수 있고, 역할을 분리하는 게 설계상 깔끔합니다."

---

## 보너스 — 멀티프로세싱 (`door_hacking_bonus.py`)

```python
tasks = [
    (zip_path, char, charset, stop_event, result_queue)
    for char in charset  # 첫 글자 36가지 → 36개 태스크
]

with multiprocessing.Pool(processes=cpu_count) as pool:
    pool.map(_crack_worker, tasks)
```

"기본 버전의 한계는 단일 프로세스라는 점입니다.
처음엔 멀티스레딩을 생각했는데, Python의 GIL 때문에 CPU 연산은 스레드를 여러 개 만들어도 실제로는 하나씩만 돌아갑니다.
그래서 별도 프로세스를 쓰는 `multiprocessing`을 사용했습니다."

"설계는 단순합니다. 첫 글자 36가지를 기준으로 탐색 공간을 36개 구간으로 나눕니다.
각 구간은 36의 5제곱, 약 6천만 개로 완전히 독립적입니다.
Pool이 8개 코어에 이 태스크들을 자동으로 배분합니다."

```python
def _crack_worker(args):
    for combo in itertools.product(charset, repeat=5):
        if stop_event.is_set():   # 다른 프로세스가 찾으면 즉시 종료
            return
        try:
            zf.read(first_entry, pwd=password.encode())
            result_queue.put(password)
            stop_event.set()      # 전 프로세스에 종료 신호
            return
        except (RuntimeError, zipfile.BadZipFile, zlib.error):
            continue
```

"`stop_event`가 핵심입니다. 비밀번호를 찾은 프로세스가 `stop_event.set()`을 호출하면,
나머지 프로세스들은 루프 맨 위에서 `is_set()`을 확인하고 즉시 종료됩니다.
없으면 35개 프로세스가 각자의 6천만 개를 끝까지 돌고 나서야 종료됩니다."

"실제로 돌려보니 1분 39초에 비밀번호 `mars06`을 찾았습니다.
`m`이 charset 13번째라 앞쪽 구간이었고, 나머지 `ars06`도 소문자와 앞쪽 숫자라 비교적 빨리 찾은 겁니다."

