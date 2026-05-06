import zipfile
import itertools
import string
import os
import zlib
from datetime import datetime


def unlock_zip():
    # 대상 zip 파일 경로 설정
    zip_path = 'emergency_storage_key.zip'
    output_path = 'password.txt'

    # zip 파일 존재 여부 확인
    if not os.path.exists(zip_path):
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')
        return

    # zip 파일 유효성 확인
    try:
        zf = zipfile.ZipFile(zip_path, 'r')
    except zipfile.BadZipFile:
        print(f'오류: {zip_path}는 유효하지 않은 zip 파일입니다.')
        return
    except OSError as e:
        print(f'파일 열기 오류: {e}')
        return

    # 문자셋: 소문자 + 숫자
    charset = string.ascii_lowercase + string.digits

    # 시작 시간 기록
    start_time = datetime.now()
    print(f'시작 시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')

    attempt_count = 0
    found_password = None

    # zip 내부 첫 번째 파일 이름 확보 (read() 대상)
    first_entry = zf.namelist()[0]

    # 6자리 모든 조합 생성 및 시도
    for combo in itertools.product(charset, repeat=6):
        password = ''.join(combo)
        attempt_count += 1

        # 100만 번마다 진행 상황 출력
        if attempt_count % 1000000 == 0:
            elapsed = datetime.now() - start_time
            print(f'시도 회수: {attempt_count:,} | 경과 시간: {elapsed}')

        try:
            # extractall 대신 read()로 메모리에서만 검증 (디스크 쓰기 없음)
            zf.read(first_entry, pwd=password.encode())
            found_password = password
            break
        except (RuntimeError, zipfile.BadZipFile, zlib.error):
            # 비밀번호 불일치 → 계속 시도
            continue

    zf.close()

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
