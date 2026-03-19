# python version 3.13.3

# Mission Computer Log Analyzer
# 미션 컴퓨터 로그 파일을 읽고 분석하는 프로그램


def parse_log_lines(log_content):
    """로그 파일 내용을 파싱하여 헤더와 로그 라인 분리"""
    lines = log_content.strip().split('\n')
    
    if not lines:
        return None, []
    
    header = lines[0]
    log_lines = []
    
    for line in lines[1:]:
        if line.strip():
            parts = line.split(',', 2)
            if len(parts) == 3:
                log_lines.append({
                    'timestamp': parts[0],
                    'event': parts[1],
                    'message': parts[2]
                })
    
    return header, log_lines


def sort_logs_by_time_reverse(log_lines):
    """로그를 시간의 역순으로 정렬"""
    return sorted(log_lines, key=lambda x: x['timestamp'], reverse=True)


def find_problem_logs(log_lines):
    """문제가 되는 로그 항목 찾기"""
    problem_keywords = ['unstable', 'explosion', 'error', 'fail', 'warning']
    problem_logs = []
    
    for log_line in log_lines:
        message_lower = log_line['message'].lower()
        for keyword in problem_keywords:
            if keyword in message_lower:
                problem_logs.append(log_line)
                break
    
    return problem_logs


def format_log_line(log_line):
    """로그 라인을 원래 형식으로 포맷팅"""
    return f'{log_line["timestamp"]},{log_line["event"]},{log_line["message"]}'


def main():

    # 1. 'Hello Mars'를 출력
    print('Hello Mars')
    print()

    # 2. mission_computer_main.log 파일을 읽고 내용 출력
    log_file_path = 'mission_computer_main.log'

    try:
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            log_content = log_file.read()
            print(log_content)
    except FileNotFoundError:
        print(f'오류: {log_file_path} 파일을 찾을 수 없습니다.')
        return
    except IOError as io_error:
        print(f'파일 읽기 오류가 발생했습니다: {io_error}')
        return
    except Exception as exception:
        print(f'예상치 못한 오류가 발생했습니다: {exception}')
        return

    # ==================== 보너스 과제 ====================
    print()
    print('=' * 60)
    print('보너스 과제: 시간 역순 정렬 및 문제 항목 분석')
    print('=' * 60)
    
    try:
        # 로그 파일 파싱
        header, log_lines = parse_log_lines(log_content)
        
        if header is None or not log_lines:
            print('파싱 오류: 로그 데이터가 없습니다.')
            return
        
        # 시간 역순으로 정렬
        sorted_logs = sort_logs_by_time_reverse(log_lines)
        
        print()
        print('[1. 시간 역순 정렬 결과]')
        print(header)
        for log_line in sorted_logs:
            print(format_log_line(log_line))
        
        # 문제 로그 찾기
        problem_logs = find_problem_logs(log_lines)
        
        print()
        print('[2. 문제 항목 추출]')
        
        if problem_logs:
            print(f'총 {len(problem_logs)}개의 문제 항목 발견')
            print()
            
            # 문제 로그를 파일로 저장
            problem_file_path = 'problem_logs.txt'
            with open(problem_file_path, 'w', encoding='utf-8') as problem_file:
                problem_file.write('=' * 60 + '\n')
                problem_file.write('미션 컴퓨터 로그 - 문제 항목\n')
                problem_file.write('=' * 60 + '\n\n')
                problem_file.write(header + '\n')
                
                for log_line in problem_logs:
                    problem_file.write(format_log_line(log_line) + '\n')
            
            print(f'문제 항목이 "{problem_file_path}" 파일로 저장되었습니다.')
            print()
            print('[저장된 문제 항목 내용]')
            for log_line in problem_logs:
                print(format_log_line(log_line))
        else:
            print('문제 항목이 없습니다.')
    
    except Exception as exception:
        print(f'보너스 과제 처리 중 오류가 발생했습니다: {exception}')


if __name__ == '__main__':
    main()
