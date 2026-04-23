import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QGridLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# ── 간격 조정 변수 ────────────────────────────────────────────
BTN_SIZE = 78          # 버튼 한 변 크기 (px)
BTN_RADIUS = 39        # 버튼 모서리 반지름 (BTN_SIZE // 2 이면 원형)
BTN_GAP = 13           # 버튼 사이 간격 (px)
BTN_FONT_SIZE = 32     # 버튼 글자 크기 (px) ← 이 값을 바꾸면 모든 버튼에 적용
OUTER_H = 14           # 좌우 바깥 여백 (px)
OUTER_TOP = 16         # 상단 바깥 여백 (px)
OUTER_BOTTOM = 16      # 하단 바깥 여백 (px)
LAYOUT_GAP = 10        # 디스플레이와 버튼 그리드 사이 간격 (px)
# ─────────────────────────────────────────────────────────────

WIN_W = OUTER_H * 2 + BTN_SIZE * 4 + BTN_GAP * 3
WIN_H = (
    OUTER_TOP + 140 + LAYOUT_GAP + BTN_SIZE * 5 + BTN_GAP * 4 + OUTER_BOTTOM
)

OP_NORMAL = ('background-color: #ff9f0a; color: white;',
             'background-color: #ffb340; color: white;')
OP_ACTIVE = ('background-color: white; color: #ff9f0a;',
             'background-color: #ffe0a0; color: #ff9f0a;')

STYLE = {
    'func': ('#636366', '#8e8e93'),
    'num':  ('#2c2c2e', '#48484a')
}


class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self._reset_state()
        self.op_buttons = {}
        self.init_ui()

    def _reset_state(self):
        self.current_input = '0'
        self.pending_value = None
        self.pending_op = None
        self.after_op = False
        self.after_eq = False

    # ── UI 구성 ───────────────────────────────────────────────

    def init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(WIN_W, WIN_H)
        self.setStyleSheet('background-color: #1c1c1e;')

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(
            OUTER_H, OUTER_TOP, OUTER_H, OUTER_BOTTOM
        )
        main_layout.setSpacing(LAYOUT_GAP)

        main_layout.addWidget(self._build_display())
        main_layout.addLayout(self._build_grid())

    def _build_display(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(0)

        self.expr_label = QLabel('')
        self.expr_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self.expr_label.setFont(QFont('Helvetica Neue', 22))
        self.expr_label.setStyleSheet('color: gray;')
        self.expr_label.setFixedHeight(40)

        self.display = QLabel('0')
        self.display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self.display.setFont(
            QFont('Helvetica Neue', 72, QFont.Weight.Light)
        )
        self.display.setStyleSheet('color: white;')
        self.display.setFixedHeight(90)

        layout.addWidget(self.expr_label)
        layout.addWidget(self.display)
        return widget

    def _build_grid(self):
        grid = QGridLayout()
        grid.setSpacing(BTN_GAP)

        buttons = [
            ('⌫',  0, 0, 'func'),
            ('AC',  0, 1, 'func'),
            ('%',   0, 2, 'func'),
            ('÷',   0, 3, 'op'),
            ('7',   1, 0, 'num'),
            ('8',   1, 1, 'num'),
            ('9',   1, 2, 'num'),
            ('×',   1, 3, 'op'),
            ('4',   2, 0, 'num'),
            ('5',   2, 1, 'num'),
            ('6',   2, 2, 'num'),
            ('−',   2, 3, 'op'),
            ('1',   3, 0, 'num'),
            ('2',   3, 1, 'num'),
            ('3',   3, 2, 'num'),
            ('+',   3, 3, 'op'),
            ('+/-',   4, 0, 'num'),
            ('0',   4, 1, 'num'),
            ('.',   4, 2, 'num'),
            ('=',   4, 3, 'op_eq'),
        ]

        for label, row, col, kind in buttons:
            btn = self._make_button(label, kind)
            grid.addWidget(btn, row, col)
            if kind == 'op':
                self.op_buttons[label] = btn
            btn.clicked.connect(
                lambda checked, t=label, k=kind: self.on_click(t, k)
            )

        return grid

    def _make_button(self, label, kind):
        btn = QPushButton(label)
        btn.setFixedSize(BTN_SIZE, BTN_SIZE)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(btn, kind, active=False)
        return btn

    def _apply_style(self, btn, kind, active=False):
        if kind == 'op':
            normal, pressed = OP_ACTIVE if active else OP_NORMAL
        elif kind == 'op_eq':
            normal, pressed = OP_NORMAL
        else:
            bg, bg_p = STYLE[kind]
            normal = f'background-color: {bg}; color: white;'
            pressed = f'background-color: {bg_p}; color: white;'

        btn.setStyleSheet(f'''
            QPushButton {{
                {normal}
                border-radius: {BTN_RADIUS}px;
                border: none;
            }}
            QPushButton:pressed {{
                {pressed}
            }}
        ''')
        btn.setFont(QFont('Helvetica Neue', BTN_FONT_SIZE))

    def _deactivate_ops(self):
        for btn in self.op_buttons.values():
            self._apply_style(btn, 'op', active=False)

    def _activate_op(self, label):
        self._deactivate_ops()
        if label in self.op_buttons:
            self._apply_style(self.op_buttons[label], 'op', active=True)

    # ── 계산 로직 ─────────────────────────────────────────────

    def _parse(self, text):
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _compute(self, a, op, b):
        if op == '+':
            return a + b
        if op == '−':
            return a - b
        if op == '×':
            return a * b
        if op == '÷':
            return None if b == 0 else a / b
        return b

    def _raw(self, value):
        """float → 쉼표 없는 내부 저장용 문자열."""
        if value is None:
            return '오류'
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f'{value:.10g}'

    def _display(self, raw):
        """내부 문자열 → 쉼표 포함 표시용 문자열."""
        if raw in ('오류', ''):
            return raw
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

    # ── 버튼 이벤트 ───────────────────────────────────────────

    def on_click(self, label, kind):
        if kind == 'num':
            self._on_digit(label)
        elif kind == 'op':
            self._on_operator(label)
        elif kind == 'op_eq':
            self._on_equal()
        elif label == 'AC':
            self._on_clear()
        elif label == '⌫':
            self._on_backspace()
        elif label == '±':
            self._on_negate()
        elif label == '%':
            self._on_percent()

        self._refresh_display()

    def _on_digit(self, label):
        self._deactivate_ops()
        if label == '.' and '.' in self.current_input:
            return
        if self.after_op or self.after_eq:
            self.current_input = '0.' if label == '.' else label
            self.after_op = False
            self.after_eq = False
        elif self.current_input == '0' and label != '.':
            self.current_input = label
        else:
            self.current_input += label

    def _on_operator(self, label):
        if self.pending_op and not self.after_op:
            result = self._compute(
                self.pending_value, self.pending_op,
                self._parse(self.current_input)
            )
            self.current_input = self._raw(result)

        self.pending_value = self._parse(self.current_input)
        self.pending_op = label
        self.after_op = True
        self.after_eq = False
        self.expr_label.setText(
            self._display(self._raw(self.pending_value)) + ' ' + label
        )
        self._activate_op(label)

    def _on_equal(self):
        if self.pending_op is None:
            return
        expr_text = (
            self._display(self._raw(self.pending_value))
            + ' ' + self.pending_op
            + ' ' + self._display(self.current_input)
        )
        result = self._compute(
            self.pending_value, self.pending_op,
            self._parse(self.current_input)
        )
        self.current_input = self._raw(result)
        self.pending_value = None
        self.pending_op = None
        self.after_eq = True
        self.after_op = False
        self.expr_label.setText(expr_text)
        self._deactivate_ops()

    def _on_clear(self):
        self._reset_state()
        self.expr_label.setText('')
        self._deactivate_ops()

    def _on_backspace(self):
        if self.after_op or self.after_eq:
            return
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = '0'

    def _on_negate(self):
        if self.current_input == '0':
            return
        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = '-' + self.current_input

    def _on_percent(self):
        value = self._parse(self.current_input) / 100
        self.current_input = self._raw(value)

    def _refresh_display(self):
        text = self._display(self.current_input)
        self.display.setText(text)
        length = len(text)
        if length <= 9:
            size = 72
        elif length <= 13:
            size = 52
        else:
            size = 36
        self.display.setFont(
            QFont('Helvetica Neue', size, QFont.Weight.Light)
        )


def main():
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
