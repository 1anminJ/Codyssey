import os


def caesar_cipher_decode(target_text):
    # 0~25 모든 시프트에 대해 복호화 결과 출력
    for shift in range(26):
        decoded = []
        for ch in target_text:
            if ch.isupper():
                # 대문자: 'A'를 기준으로 시프트 역방향 적용
                decoded.append(chr((ord(ch) - ord('A') - shift) % 26 + ord('A')))
            elif ch.islower():
                # 소문자: 'a'를 기준으로 시프트 역방향 적용
                decoded.append(chr((ord(ch) - ord('a') - shift) % 26 + ord('a')))
            else:
                # 알파벳이 아닌 문자(숫자, 공백 등)는 그대로 유지
                decoded.append(ch)
        print(f'[Shift {shift}] {"".join(decoded)}')

    print()

    # 사용자로부터 올바른 시프트 번호 입력 받기
    while True:
        try:
            shift_input = input('올바른 시프트 번호를 입력하세요 (0~25): ')
            shift_num = int(shift_input)
            if 0 <= shift_num <= 25:
                break
            print('0~25 사이의 숫자를 입력해주세요.')
        except ValueError:
            print('숫자를 입력해주세요.')

    # 선택한 시프트로 복호화된 결과 생성
    result = []
    for ch in target_text:
        if ch.isupper():
            result.append(chr((ord(ch) - ord('A') - shift_num) % 26 + ord('A')))
        elif ch.islower():
            result.append(chr((ord(ch) - ord('a') - shift_num) % 26 + ord('a')))
        else:
            result.append(ch)
    decoded_result = ''.join(result)

    # result.txt에 저장
    try:
        with open('result.txt', 'w') as f:
            f.write(decoded_result)
        print(f'\n결과: {decoded_result}')
        print(f'결과가 result.txt에 저장되었습니다.')
    except OSError as e:
        print(f'파일 저장 오류: {e}')


# ===================== 보너스 과제 =====================
def caesar_cipher_decode_auto(target_text):
    # 텍스트 사전: 암호 해독 여부를 판별할 키워드 목록
    word_dict = [
        'mars', 'earth', 'moon', 'sun', 'space', 'star',
        'the', 'and', 'for', 'are', 'but', 'not', 'you',
        'hello', 'world', 'password', 'secret', 'key',
        'emergency', 'storage', 'open', 'door', 'lock'
    ]

    for shift in range(26):
        decoded = []
        for ch in target_text:
            if ch.isupper():
                # 대문자: 'A'를 기준으로 시프트 역방향 적용
                decoded.append(chr((ord(ch) - ord('A') - shift) % 26 + ord('A')))
            elif ch.islower():
                # 소문자: 'a'를 기준으로 시프트 역방향 적용
                decoded.append(chr((ord(ch) - ord('a') - shift) % 26 + ord('a')))
            else:
                # 알파벳이 아닌 문자(숫자, 공백 등)는 그대로 유지
                decoded.append(ch)
        decoded_text = ''.join(decoded)

        # 사전의 키워드가 복호화된 텍스트에 포함되면 반복 중단
        matched_word = None
        for word in word_dict:
            if word in decoded_text.lower():
                matched_word = word
                break

        if matched_word:
            print(f'[Shift {shift}] {decoded_text}  ← 키워드 "{matched_word}" 발견! 반복 중단')

            # 발견된 결과를 result.txt에 저장
            try:
                with open('result.txt', 'w') as f:
                    f.write(decoded_text)
                print(f'결과가 result.txt에 저장되었습니다.')
            except OSError as e:
                print(f'파일 저장 오류: {e}')
            return
        else:
            print(f'[Shift {shift}] {decoded_text}')

    print('사전에서 일치하는 키워드를 찾지 못했습니다.')
# ===================== 보너스 과제 끝 =====================


def main():
    input_path = 'password.txt'

    # password.txt 존재 여부 확인
    if not os.path.exists(input_path):
        print(f'오류: {input_path} 파일을 찾을 수 없습니다.')
        return

    # password.txt 읽기
    try:
        with open(input_path, 'r') as f:
            target_text = f.read().strip()
    except OSError as e:
        print(f'파일 읽기 오류: {e}')
        return

    if not target_text:
        print('오류: 파일이 비어 있습니다.')
        return

    print(f'원문: {target_text}')
    print()

    # 모든 시프트 결과 출력 및 결과 저장
    caesar_cipher_decode(target_text)

    print()

    # 보너스: 사전 기반 자동 탐지
    print('=== 보너스: 사전 자동 탐지 ===')
    caesar_cipher_decode_auto(target_text)


if __name__ == '__main__':
    main()
