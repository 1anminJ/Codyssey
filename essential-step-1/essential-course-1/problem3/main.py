#!/usr/bin/env python3

# 화성 기지의 입고된 물질 목록을 분석하고 위험 물질을 분류하는 프로그램

import csv
import pickle


def read_csv_file(filename):
    """CSV 파일을 읽고 내용을 출력하는 함수"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            print('=' * 80)
            print('CSV 파일 원본 내용 출력:')
            print('=' * 80)
            print(content)
            print('=' * 80)
    except FileNotFoundError:
        print(f'오류: {filename} 파일을 찾을 수 없습니다.')
    except IOError as e:
        print(f'파일 읽기 오류: {e}')


def csv_to_list(filename):
    """CSV 파일을 리스트 객체로 변환하는 함수"""
    inventory_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                inventory_list.append(row)
    except FileNotFoundError:
        print(f'오류: {filename} 파일을 찾을 수 없습니다.')
    except IOError as e:
        print(f'파일 읽기 오류: {e}')
    return inventory_list


def sort_by_flammability(inventory_list):
    """인화성 지수로 정렬하는 함수 (높은 순)"""
    try:
        sorted_list = sorted(
            inventory_list,
            key=lambda x: float(x['Flammability']),
            reverse=True
        )
        return sorted_list
    except (ValueError, KeyError) as e:
        print(f'정렬 오류: {e}')
        return inventory_list


def filter_dangerous_materials(inventory_list, threshold=0.7):
    """인화성 지수가 threshold 이상인 물질 필터링"""
    dangerous_materials = []
    try:
        for item in inventory_list:
            flammability = float(item['Flammability'])
            if flammability >= threshold:
                dangerous_materials.append(item)
    except (ValueError, KeyError) as e:
        print(f'필터링 오류: {e}')
    return dangerous_materials


def print_inventory(inventory_list, title='물질 목록'):
    """물질 목록을 포맷된 형태로 출력"""
    print('\n' + '=' * 80)
    print(title)
    print('=' * 80)
    if not inventory_list:
        print('목록이 없습니다.')
        return

    # 헤더 출력
    headers = ['Substance', 'Flammability', 'Weight (g/cm³)']
    print(f'{headers[0]:<30} {headers[1]:<15} {headers[2]:<20}')
    print('-' * 80)

    # 내용 출력
    for item in inventory_list:
        substance = item['Substance']
        flammability = item['Flammability']
        weight = item['Weight (g/cm³)']
        print(f'{substance:<30} {flammability:<15} {weight:<20}')
    print('=' * 80)


def save_dangerous_to_csv(dangerous_materials, filename):
    """위험한 물질을 CSV 파일로 저장"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if dangerous_materials:
                fieldnames = dangerous_materials[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dangerous_materials)
            print(f'\n✓ {filename} 파일이 생성되었습니다.')
    except IOError as e:
        print(f'파일 쓰기 오류: {e}')


# ============================================================================
# 보너스 과제: 이진 파일 처리
# ============================================================================

def save_to_binary(data, filename):
    """정렬된 데이터를 이진 파일로 저장"""
    try:
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        print(f'\n✓ {filename} 이진 파일이 생성되었습니다.')
    except IOError as e:
        print(f'이진 파일 쓰기 오류: {e}')


def load_from_binary(filename):
    """이진 파일에서 데이터를 읽음"""
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        print(f'오류: {filename} 파일을 찾을 수 없습니다.')
        return []
    except IOError as e:
        print(f'이진 파일 읽기 오류: {e}')
        return []





def main():
    """메인 프로그램"""
    csv_filename = 'Mars_Base_Inventory_List.csv'
    dangerous_filename = 'Mars_Base_Inventory_danger.csv'
    binary_filename = 'Mars_Base_Inventory_List.bin'

    print('*' * 60)
    print('화성 기지 화물 목록 분석 프로그램')
    print('*' * 60)

    # 1. CSV 파일 읽고 출력
    print('\n[1단계] CSV 파일 읽기 및 출력')
    read_csv_file(csv_filename)

    # 2. CSV를 리스트로 변환
    print('\n[2단계] CSV 파일을 리스트로 변환')
    inventory_list = csv_to_list(csv_filename)
    print(f'✓ 총 {len(inventory_list)}개의 물질이 로드되었습니다.')

    # 3. 인화성 지수로 정렬
    print('\n[3단계] 인화성 지수로 정렬 (높은 순)')
    sorted_inventory = sort_by_flammability(inventory_list)
    print('✓ 인화성 지수 높은 순으로 정렬 완료')

    # 정렬된 전체 목록 출력
    print_inventory(sorted_inventory, '정렬된 전체 화물 목록 (인화성 높은 순)')

    # 4. 위험한 물질 필터링 (인화성 >= 0.7)
    print('\n[4단계] 위험한 물질 필터링 (인화성 >= 0.7)')
    dangerous_materials = filter_dangerous_materials(sorted_inventory, 0.7)
    print(f'✓ 위험한 물질 {len(dangerous_materials)}개를 식별했습니다.')

    # 위험한 물질 목록 출력
    print_inventory(dangerous_materials, '위험한 화물 목록 (인화성 >= 0.7)')

    # 5. 위험한 물질을 CSV로 저장
    print('\n[5단계] 위험한 물질을 CSV 파일로 저장')
    save_dangerous_to_csv(dangerous_materials, dangerous_filename)

    # ========================================================================
    # 보너스 과제: 이진 파일 처리
    # ========================================================================

    print('*' * 60)
    print('보너스 과제: 이진 파일 처리')
    print('*' * 60)

    # 보너스 1: 정렬된 데이터를 이진 파일로 저장
    print('\n[보너스 1단계] 정렬된 배열을 이진 파일로 저장')
    save_to_binary(sorted_inventory, binary_filename)

    # 보너스 2: 이진 파일에서 데이터 읽기 및 출력
    print('\n[보너스 2단계] 이진 파일에서 데이터 읽기 및 출력')
    loaded_data = load_from_binary(binary_filename)
    if loaded_data:
        print(f'✓ {binary_filename}에서 {len(loaded_data)}개의 항목을 로드했습니다.')
        print_inventory(loaded_data, '이진 파일에서 로드한 화물 목록')



if __name__ == '__main__':
    main()

