# Calculator

PyQt6로 구현한 아이폰 스타일 계산기입니다.

---

## 실행 방법

```bash
python3 calculator.py
```

---

## 전체 구조

```
calculator.py
├── 상수 정의        (레이아웃 크기, 색상)
└── Calculator 클래스
    ├── 상태 관리     (_reset_state)
    ├── UI 구성       (init_ui, _build_display, _build_grid)
    ├── 버튼 스타일   (_make_button, _apply_style)
    ├── 계산 로직     (_parse, _compute, _raw, _display)
    └── 이벤트 처리  (on_click 및 각 _on_* 메서드)
```

---

## 상수 정의

```python
BTN_SIZE = 78
BTN_RADIUS = 39
BTN_GAP = 13
BTN_FONT_SIZE = 32
OUTER_H = 14
OUTER_TOP = 16
OUTER_BOTTOM = 16
LAYOUT_GAP = 10
```

레이아웃과 관련된 모든 수치를 파일 상단에 상수로 모아두었습니다.
`BTN_SIZE` 하나만 바꿔도 창 크기(`WIN_W`, `WIN_H`)가 자동으로 재계산되도록
수식으로 연결해 두었기 때문에, 여러 곳을 따로 수정할 필요가 없습니다.

```python
WIN_W = OUTER_H * 2 + BTN_SIZE * 4 + BTN_GAP * 3
WIN_H = (
    OUTER_TOP + 140 + LAYOUT_GAP + BTN_SIZE * 5 + BTN_GAP * 4 + OUTER_BOTTOM
)
```

---

## 상태 관리

```python
def _reset_state(self):
    self.current_input = '0'   # 현재 입력 중인 숫자 (문자열)
    self.pending_value = None  # 연산자 앞쪽 피연산자 (float)
    self.pending_op = None     # 대기 중인 연산자 기호
    self.after_op = False      # 연산자 직후 여부
    self.after_eq = False      # = 직후 여부
```

계산기의 동작은 5개의 상태 변수로 관리합니다.

- `after_op` / `after_eq` 플래그가 `True`이면 다음 숫자 입력 시 화면을 초기화합니다.
  이를 통해 `3 + 5 =` 이후 바로 새 숫자를 입력하면 이전 결과를 덮어쓰는
  아이폰 계산기의 동작을 재현합니다.
- `pending_value`와 `pending_op`를 별도로 보관하기 때문에
  `3 + 5 × 2` 처럼 연속으로 연산자를 누를 때 중간 결과를 먼저 계산(체이닝)할 수 있습니다.

---

## UI 구성

### 디스플레이 (`_build_display`)

디스플레이 영역을 두 줄로 구성했습니다.

| 레이블 | 역할 | 색상 | 폰트 크기 |
|--------|------|------|-----------|
| `expr_label` | 수식 표시 (예: `3 + 5`) | 회색 | 22pt |
| `display` | 현재 숫자 표시 | 흰색 | 72 / 52 / 36pt (자동 조절) |

두 레이블 모두 오른쪽 정렬로 설정해 아이폰 계산기와 동일한 방향을 맞췄습니다.

### 버튼 그리드 (`_build_grid`)

버튼 정보를 `(라벨, 행, 열, 종류)` 튜플 리스트로 선언했습니다.

```python
buttons = [
    ('⌫', 0, 0, 'func'),  ('AC', 0, 1, 'func'),
    ('%',  0, 2, 'func'),  ('÷',  0, 3, 'op'),
    ...
]
```

버튼 종류(`kind`)를 4가지로 분류해 색상 테마를 한 곳에서 관리합니다.

| kind | 버튼 | 색상 |
|------|------|------|
| `func` | ⌫ · AC · % | 회색 |
| `num` | 0–9 · ± · . | 어두운 회색 |
| `op` | ÷ · × · − · + | 주황색 |
| `op_eq` | = | 주황색 |

루프 한 번으로 모든 버튼을 생성하기 때문에 버튼을 추가하거나 순서를 바꿀 때
리스트만 수정하면 됩니다.

### 버튼 스타일 (`_apply_style`)

```python
def _apply_style(self, btn, kind, active=False):
    ...
    btn.setStyleSheet(f'...')
    btn.setFont(QFont('Helvetica Neue', BTN_FONT_SIZE))
```

`setStyleSheet()` 직후 `setFont()`를 다시 호출하는 이유가 있습니다.
PyQt6에서 `setStyleSheet()`를 호출하면 위젯의 폰트가 초기화되는 경우가 있습니다.
연산자(`op`) 버튼은 연산자 선택/해제 시 `_activate_op` / `_deactivate_ops`에 의해
stylesheet가 재적용되는데, 이때마다 폰트가 리셋되어 다른 버튼과 크기가 달라지는
문제가 발생했습니다. stylesheet 적용 후 `setFont()`를 명시적으로 재호출해
이 문제를 해결했습니다.

연산자 버튼이 선택된 상태일 때는 배경을 흰색, 글자를 주황색으로 반전시켜
아이폰 계산기의 강조 표시를 재현했습니다.

```python
OP_NORMAL = ('background-color: #ff9f0a; color: white;', ...)
OP_ACTIVE = ('background-color: white; color: #ff9f0a;', ...)  # 선택 시 반전
```

---

## 계산 로직

### 숫자 포맷 분리 (`_raw` / `_display`)

내부 저장과 화면 출력을 분리했습니다.

```python
def _raw(self, value):
    # float → 쉼표 없는 문자열 (내부 저장용)
    # 예: 1000.0 → '1000'

def _display(self, raw):
    # 내부 문자열 → 쉼표 포함 문자열 (화면 출력용)
    # 예: '1000' → '1,000'
```

`current_input`에는 항상 쉼표 없는 순수한 숫자 문자열만 저장합니다.
`_parse()`로 float 변환 시 쉼표가 없어야 `float()` 함수가 정상 작동하기 때문입니다.
화면에 표시할 때만 `_display()`를 거쳐 쉼표를 추가합니다.

### 연산 (`_compute`)

```python
def _compute(self, a, op, b):
    if op == '÷':
        return None if b == 0 else a / b
    ...
```

0으로 나누는 경우 `None`을 반환하고, `_raw(None)`이 `'오류'`를 반환해
화면에 오류를 표시합니다.

### 연산자 처리 (`_on_operator`)

```python
def _on_operator(self, label):
    if self.pending_op and not self.after_op:
        result = self._compute(...)   # 이전 연산 먼저 처리
        self.current_input = self._raw(result)
    self.pending_value = self._parse(self.current_input)
    self.pending_op = label
    self.after_op = True
```

연산자를 연속으로 누르면 (`3 + 5 ×`) 새 연산자를 적용하기 전에
이전 연산(`3 + 5 = 8`)을 먼저 수행합니다.
이것이 아이폰 계산기의 왼쪽부터 순서대로 계산하는 체이닝 동작입니다.

### 디스플레이 폰트 자동 조절 (`_refresh_display`)

```python
def _refresh_display(self):
    text = self._display(self.current_input)
    length = len(text)
    if length <= 9:
        size = 72
    elif length <= 13:
        size = 52
    else:
        size = 36
```

숫자가 길어질수록 폰트 크기를 자동으로 줄입니다.
아이폰 계산기에서 긴 숫자를 입력할 때 글자가 작아지는 동작을 재현했습니다.

---

## 버튼별 동작 요약

| 버튼 | 동작 |
|------|------|
| `0`–`9`, `.` | 숫자 입력. `after_op`/`after_eq`가 `True`이면 초기화 후 입력 |
| `÷` `×` `−` `+` | 연산자 등록. 이전 연산이 있으면 체이닝 계산 먼저 수행 |
| `=` | 최종 계산. 수식을 위 줄에 표시하고 결과를 메인 디스플레이에 표시 |
| `AC` | 모든 상태 초기화 |
| `⌫` | 마지막 자리 삭제. `after_op`/`after_eq` 상태에서는 동작 안 함 |
| `±` | 부호 반전 (`-` 추가/제거) |
| `%` | 현재 숫자 ÷ 100 |
