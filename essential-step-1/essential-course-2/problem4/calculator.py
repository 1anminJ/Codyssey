import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics


# ── 레이아웃 상수 ──────────────────────────────────────────────
BTN_H = 65             # 버튼 높이 (px)
BTN_RADIUS = 32        # 버튼 모서리 반지름 (px)
BTN_GAP = 10           # 버튼 사이 간격 (px)
BTN_FONT_SIZE = 22     # 버튼 글자 크기
DISP_FONT = 'Arial'    # 폰트 (버튼·디스플레이 공통)
WIN_W = 320
WIN_H = 525
# ──────────────────────────────────────────────────────────────


# ── 계산기 핵심 로직 ───────────────────────────────────────────

class Calculator:
    '''계산기 연산 로직을 담당하는 클래스 (UI 독립적)'''

    def __init__(self):
        self.reset()

    def reset(self):
        '''계산기 상태를 전부 초기화한다'''
        self._current = '0'
        self._previous = 0.0
        self._operator = None
        self._just_evaluated = False
        self._after_op = False

    def clear_entry(self):
        '''현재 입력만 지운다 (C 버튼)'''
        self._current = '0'
        self._after_op = False
        return self._current

    def backspace(self):
        '''마지막 한 자리를 지운다 (⌫ 버튼)'''
        if self._just_evaluated or len(self._current) <= 1:
            self._current = '0'
        else:
            self._current = self._current[:-1]
            if self._current == '-':
                self._current = '0'
        return self._current

    # ── 산술 연산 ─────────────────────────────────────────────

    def add(self, x, y):
        '''덧셈'''
        return x + y

    def subtract(self, x, y):
        '''뺄셈'''
        return x - y

    def multiply(self, x, y):
        '''곱셈'''
        return x * y

    def divide(self, x, y):
        '''나눗셈 (0으로 나누기 예외 처리)'''
        if y == 0:
            raise ZeroDivisionError('0으로 나눌 수 없습니다')
        return x / y

    # ── 입력 처리 ─────────────────────────────────────────────

    def input_digit(self, digit):
        '''숫자 입력: 연산자/= 직후이면 초기화 후 입력한다'''
        if self._just_evaluated or self._after_op:
            self._current = digit
            self._just_evaluated = False
            self._after_op = False
        elif self._current == '0' and digit != '.':
            self._current = digit
        else:
            self._current += digit
        return self._current

    def input_dot(self):
        '''소수점 입력: 중복 입력을 방지한다'''
        if self._just_evaluated or self._after_op:
            self._current = '0.'
            self._just_evaluated = False
            self._after_op = False
            return self._current
        if '.' not in self._current:
            self._current += '.'
        return self._current

    def input_operator(self, op):
        '''연산자 입력: 이전 연산이 있으면 먼저 계산하고 after_op를 세운다'''
        if not self._after_op:
            current_val = self._parse(self._current)
            if self._operator and not self._just_evaluated:
                result = self._calculate(
                    self._previous, current_val, self._operator
                )
                self._previous = result
                self._current = self._format(result)
            else:
                self._previous = current_val
        self._operator = op
        self._just_evaluated = False
        self._after_op = True
        return self._current

    # ── 기능 버튼 ─────────────────────────────────────────────

    def toggle_sign(self):
        '''양수/음수 전환'''
        val = self._parse(self._current)
        self._current = self._format(-val)
        return self._current

    def percent(self):
        '''현재 값을 퍼센트(÷100)로 변환'''
        val = self._parse(self._current)
        self._current = self._format(val / 100)
        return self._current

    def equal(self):
        '''연산을 실행하고 결과를 반환한다'''
        if self._operator is None:
            return self._current
        current_val = self._parse(self._current)
        result = self._calculate(
            self._previous, current_val, self._operator
        )
        self._current = self._format(result)
        self._operator = None
        self._just_evaluated = True
        self._after_op = False
        return self._current

    # ── 내부 헬퍼 ─────────────────────────────────────────────

    def _calculate(self, x, y, op):
        '''연산자에 맞는 메서드를 호출한다'''
        ops = {
            '+': self.add,
            '−': self.subtract,
            '×': self.multiply,
            '÷': self.divide,
        }
        return ops[op](x, y)

    def _parse(self, text):
        '''문자열을 float으로 변환한다'''
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _format(self, value):
        '''결과값을 쉼표 없는 내부 저장용 문자열로 변환한다'''
        try:
            if abs(value) > 1e15:
                raise OverflowError('숫자 범위를 초과했습니다')
            if value == int(value):
                return str(int(value))
            return f'{value:.10f}'.rstrip('0').rstrip('.')
        except OverflowError:
            self.reset()
            return '오류'

    @property
    def current(self):
        '''현재 표시값(쉼표 없는 raw 문자열)을 반환한다'''
        return self._current

    @property
    def operator(self):
        '''대기 중인 연산자를 반환한다'''
        return self._operator

    @property
    def previous_raw(self):
        '''이전 피연산자를 raw 문자열로 반환한다'''
        return self._format(self._previous)


# ── PyQt6 UI ──────────────────────────────────────────────────

class CalculatorWindow(QMainWindow):
    '''계산기 메인 윈도우'''

    _BUTTONS = [
        [
            ('⌫', 'back', '#636366'),
            ('AC', 'clear', '#636366'),
            ('%', 'percent', '#636366'),
            ('÷', 'op', '#ff9f0a'),
        ],
        [
            ('7', 'digit', '#333333'),
            ('8', 'digit', '#333333'),
            ('9', 'digit', '#333333'),
            ('×', 'op', '#ff9f0a'),
        ],
        [
            ('4', 'digit', '#333333'),
            ('5', 'digit', '#333333'),
            ('6', 'digit', '#333333'),
            ('−', 'op', '#ff9f0a'),
        ],
        [
            ('1', 'digit', '#333333'),
            ('2', 'digit', '#333333'),
            ('3', 'digit', '#333333'),
            ('+', 'op', '#ff9f0a'),
        ],
        [
            ('±', 'sign', '#333333'),
            ('0', 'digit', '#333333'),
            ('.', 'dot', '#333333'),
            ('=', 'equal', '#ff9f0a'),
        ],
    ]

    def __init__(self):
        super().__init__()
        self._calc = Calculator()
        self._ac_btn = None
        self._op_buttons = {}
        self._init_ui()

    def _init_ui(self):
        '''UI 구성 요소를 초기화하고 배치한다'''
        self.setWindowTitle('Calculator')
        self.setFixedSize(WIN_W, WIN_H)
        self.setStyleSheet('background-color: #1c1c1e;')

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 20, 12, 12)
        root.setSpacing(10)

        root.addWidget(self._build_display())
        root.addLayout(self._build_grid())

    def _build_display(self):
        '''수식 레이블과 숫자 디스플레이를 담은 위젯을 생성한다'''
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(2)

        self._expr_label = QLabel('')
        self._expr_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self._expr_label.setFont(QFont(DISP_FONT, 18))
        self._expr_label.setStyleSheet('color: gray;')
        self._expr_label.setFixedHeight(30)

        self._display = QLineEdit('0')
        self._display.setReadOnly(True)
        self._display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._display.setFixedHeight(85)
        self._display.setStyleSheet(
            'background: transparent; color: white; border: none;'
        )
        self._display.setFont(QFont(DISP_FONT, 40, QFont.Weight.Light))

        layout.addWidget(self._expr_label)
        layout.addWidget(self._display)
        return widget

    def _build_grid(self):
        '''버튼 그리드 레이아웃을 생성한다'''
        grid = QGridLayout()
        grid.setSpacing(BTN_GAP)

        for row_idx, row in enumerate(self._BUTTONS):
            for col_idx, (label, role, color) in enumerate(row):
                btn = self._make_button(label, role, color)
                grid.addWidget(btn, row_idx, col_idx)
                if role == 'clear':
                    self._ac_btn = btn
                if role == 'op':
                    self._op_buttons[label] = btn

        return grid

    def _make_button(self, label, role, bg_color):
        '''버튼을 생성하고 스타일·시그널을 연결한다'''
        if bg_color == '#ff9f0a':
            pressed_color = '#e08800'
        elif bg_color == '#636366':
            pressed_color = '#858585'
        else:
            pressed_color = '#555555'

        text_color = '#1c1c1e' if bg_color == '#ff9f0a' else 'white'

        btn = QPushButton(label)
        btn.setFixedHeight(BTN_H)
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: {BTN_RADIUS}px;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        ''')
        btn.setFont(QFont(DISP_FONT, BTN_FONT_SIZE))
        btn.clicked.connect(
            lambda _, lb=label, r=role: self._on_click(lb, r)
        )
        return btn

    # ── 이벤트 처리 ───────────────────────────────────────────

    def _on_click(self, label, role):
        '''버튼 클릭 이벤트를 Calculator에 위임하고 화면을 갱신한다'''
        try:
            raw = self._handle(label, role)
        except ZeroDivisionError:
            self._calc.reset()
            self._expr_label.setText('')
            self._set_ac('AC')
            self._deactivate_ops()
            raw = '오류'
        except (OverflowError, ValueError, TypeError):
            self._calc.reset()
            self._expr_label.setText('')
            self._set_ac('AC')
            self._deactivate_ops()
            raw = '오류'

        self._update_display(raw)

    def _handle(self, label, role):
        '''역할별 처리 후 표시할 raw 문자열을 반환한다'''
        if role == 'digit':
            raw = self._calc.input_digit(label)
            self._set_ac('C')

        elif role == 'dot':
            raw = self._calc.input_dot()
            self._set_ac('C')

        elif role == 'op':
            prev_str = self._fmt(self._calc.current)
            self._calc.input_operator(label)
            self._expr_label.setText(prev_str + ' ' + label)
            self._activate_op(label)
            raw = '0'

        elif role == 'equal':
            prev_str = self._fmt(self._calc.previous_raw)
            op = self._calc.operator
            cur_str = self._fmt(self._calc.current)
            raw = self._calc.equal()
            if op:
                self._expr_label.setText(
                    prev_str + ' ' + op + ' ' + cur_str
                )
            self._deactivate_ops()
            self._set_ac('AC')

        elif role == 'clear':
            if self._ac_btn and self._ac_btn.text() == 'C':
                raw = self._calc.clear_entry()
                self._set_ac('AC')
            else:
                self._calc.reset()
                self._expr_label.setText('')
                raw = '0'
            self._deactivate_ops()

        elif role == 'back':
            raw = self._calc.backspace()
            if raw == '0':
                self._set_ac('AC')

        elif role == 'sign':
            raw = self._calc.toggle_sign()

        elif role == 'percent':
            raw = self._calc.percent()

        else:
            raw = self._calc.current

        return raw

    # ── 디스플레이 갱신 ───────────────────────────────────────

    def _update_display(self, raw):
        '''쉼표 포함 문자열로 변환해 디스플레이를 갱신하고 폰트를 조절한다'''
        text = self._fmt(raw)
        size = self._fit_font_size(text)
        self._display.setFont(QFont(DISP_FONT, size, QFont.Weight.Light))
        self._display.setText(text)

    def _fit_font_size(self, text):
        '''텍스트가 디스플레이 너비에 딱 맞는 최대 폰트 크기를 반환한다'''
        # root margin(12*2) + display widget margin(4*2) + QLineEdit 내부 여백(8)
        available_w = WIN_W - 24 - 8 - 8
        for size in range(40, 13, -1):
            fm = QFontMetrics(QFont(DISP_FONT, size, QFont.Weight.Light))
            if fm.horizontalAdvance(text) <= available_w:
                return size
        return 14

    def _fmt(self, raw):
        '''내부 raw 문자열 → 소수 6자리 반올림 + 쉼표 포함 표시용 문자열'''
        if raw in ('오류', ''):
            return raw
        # 소수점 자릿수가 6을 초과하면 6자리로 반올림
        if '.' in raw:
            dec_digits = len(raw.split('.')[1])
            if dec_digits > 6:
                try:
                    raw = f'{float(raw):.6f}'.rstrip('0').rstrip('.')
                except ValueError:
                    pass
        negative = raw.startswith('-')
        body = raw.lstrip('-')
        if '.' in body:
            int_part, dec_part = body.split('.')
            try:
                int_part = f'{int(int_part):,}'
            except ValueError:
                pass
            formatted = int_part + '.' + dec_part
        else:
            try:
                formatted = f'{int(body):,}'
            except ValueError:
                formatted = body
        return ('-' + formatted) if negative else formatted

    # ── 연산자 버튼 하이라이트 ────────────────────────────────

    def _activate_op(self, label):
        '''선택된 연산자 버튼을 반전(흰색 배경·주황 글자)으로 강조한다'''
        self._deactivate_ops()
        if label not in self._op_buttons:
            return
        btn = self._op_buttons[label]
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: white;
                color: #ff9f0a;
                border-radius: {BTN_RADIUS}px;
                border: none;
            }}
            QPushButton:pressed {{
                background-color: #ffe0a0;
                color: #ff9f0a;
            }}
        ''')
        btn.setFont(QFont(DISP_FONT, BTN_FONT_SIZE))

    def _deactivate_ops(self):
        '''모든 연산자 버튼을 기본 스타일(주황 배경)로 되돌린다'''
        for btn in self._op_buttons.values():
            btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: #ff9f0a;
                    color: #1c1c1e;
                    border-radius: {BTN_RADIUS}px;
                    border: none;
                }}
                QPushButton:pressed {{
                    background-color: #e08800;
                }}
            ''')
            btn.setFont(QFont(DISP_FONT, BTN_FONT_SIZE))

    def _set_ac(self, text):
        '''AC/C 버튼의 레이블을 전환한다'''
        if self._ac_btn:
            self._ac_btn.setText(text)


# ── 진입점 ────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
