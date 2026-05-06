import zipfile
import itertools
import string
import os
import zlib
import multiprocessing
from datetime import datetime


def _crack_worker(args):
    # 각 프로세스에서 실행: 첫 글자를 고정하고 나머지 5자리를 완전 탐색
    zip_path, prefix, charset, stop_event, result_queue = args

    try:
        zf = zipfile.ZipFile(zip_path, 'r')
        first_entry = zf.namelist()[0]

        for combo in itertools.product(charset, repeat=5):
            # 다른 프로세스가 이미 비밀번호를 찾았으면 즉시 종료
            if stop_event.is_set():
                zf.close()
                return

            password = prefix + ''.join(combo)

            try:
                zf.read(first_entry, pwd=password.encode())
                # 예외 없이 통과 → 비밀번호 일치
                result_queue.put(password)
                stop_event.set()
                zf.close()
                return
            except (RuntimeError, zipfile.BadZipFile, zlib.error):
                continue

        zf.close()
    except Exception:
        pass


def unlock_zip_fast():
    zip_path = 'emergency_storage_key.zip'
    output_path = 'password.txt'

    # ZIP 파일 존재 여부 확인
    if not os.path.exists(zip_path):
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
        return

    # ZIP 파일 유효성 확인
    try:
        zf_check = zipfile.ZipFile(zip_path, 'r')
        zf_check.close()
    except zipfile.BadZipFile:
        print(f'오류: {zip_path}는 유효하지 않은 zip 파일입니다.')
        return
    except OSError as e:
        print(f'파일 열기 오류: {e}')
        return

    # 문자셋: 소문자 + 숫자
    charset = string.ascii_lowercase + string.digits
    cpu_count = multiprocessing.cpu_count()

    # 시작 정보 출력
    start_time = datetime.now()
    print(f'시작 시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'사용 CPU 코어 수: {cpu_count}')
    print(f'탐색 공간: {len(charset)}^6 = {len(charset) ** 6:,}')
    print(f'프로세스당 탐색 범위: {len(charset) ** 5:,} (첫 글자 1개 고정)')

    # 프로세스 간 공유 객체 생성
    manager = multiprocessing.Manager()
    stop_event = manager.Event()   # 비밀번호 발견 시 전 프로세스에 신호
    result_queue = manager.Queue()  # 발견된 비밀번호 전달용

    # 첫 번째 글자(36가지)를 기준으로 작업 분할 → 36개 태스크
    tasks = [
        (zip_path, char, charset, stop_event, result_queue)
        for char in charset
    ]

    # 멀티프로세싱 풀로 병렬 실행
    with multiprocessing.Pool(processes=cpu_count) as pool:
        pool.map(_crack_worker, tasks)

    elapsed = datetime.now() - start_time
    found_password = None

    if not result_queue.empty():
        found_password = result_queue.get()

    if found_password:
        print(f'\n비밀번호 발견: {found_password}')
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
        print(f'경과 시간: {elapsed}')


if __name__ == '__main__':
    unlock_zip_fast()
