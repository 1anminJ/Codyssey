# Calculator

PyQt6로 구현한 아이폰 스타일 계산기입니다.

---

## 실행 방법

```bash
pip3 install PyQt6
python3 calculator.py
```

---

## 클래스 구조

```
Calculator          연산 로직 (UI 독립)
CalculatorWindow    PyQt6 UI 및 이벤트 처리
```

---

## Calculator

계산기의 핵심 연산 로직을 담당합니다. PyQt6에 의존하지 않아 UI 없이도 단독으로 동작합니다.

### 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `reset()` | 모든 상태를 초기화한다 |
| `clear_entry()` | 현재 입력 숫자만 0으로 되돌린다 |
| `backspace()` | 마지막 한 자리를 삭제한다 |
| `input_digit(digit)` | 숫자를 입력한다 |
| `input_dot()` | 소수점을 입력한다 |
| `input_operator(op)` | 연산자를 등록하고 체이닝 계산을 처리한다 |
| `toggle_sign()` | 현재 숫자의 부호를 반전한다 |
| `percent()` | 현재 숫자를 100으로 나눈다 |
| `equal()` | 최종 계산을 실행하고 결과를 반환한다 |

### 상태 변수

| 변수 | 설명 |
|------|------|
| `_current` | 현재 입력 중인 숫자 문자열 |
| `_previous` | 연산자 앞쪽 피연산자 |
| `_operator` | 대기 중인 연산자 |
| `_just_evaluated` | `=` 직후 여부 |
| `_after_op` | 연산자 직후 여부 |

---

## CalculatorWindow

PyQt6 기반의 메인 윈도우 클래스입니다. `Calculator` 인스턴스를 내부에 가지고,
버튼 이벤트를 받아 `Calculator`에 위임한 뒤 결과를 화면에 표시합니다.

### 주요 메서드

| 메서드 | 설명 |
|--------|------|
| `_init_ui()` | 윈도우 전체 레이아웃을 초기화한다 |
| `_build_display()` | 수식 레이블과 숫자 디스플레이 영역을 생성한다 |
| `_build_grid()` | 버튼 그리드를 생성하고 참조를 저장한다 |
| `_make_button(label, role, bg_color)` | 버튼 위젯을 생성하고 스타일을 적용한다 |
| `_on_click(label, role)` | 버튼 클릭을 받아 예외 처리 후 `_handle()`을 호출한다 |
| `_handle(label, role)` | 역할별로 분기해 `Calculator` 메서드를 호출한다 |
| `_update_display(raw)` | 화면에 숫자를 표시하고 폰트 크기를 조절한다 |
| `_fit_font_size(text)` | `QFontMetrics`로 픽셀 너비를 재서 최적 폰트 크기를 반환한다 |
| `_fmt(raw)` | 내부 숫자 문자열을 쉼표 포함·소수 6자리 반올림 형태로 변환한다 |
| `_activate_op(label)` | 선택된 연산자 버튼을 강조 표시한다 |
| `_deactivate_ops()` | 모든 연산자 버튼 강조를 해제한다 |
| `_set_ac(text)` | AC / C 버튼 레이블을 전환한다 |
