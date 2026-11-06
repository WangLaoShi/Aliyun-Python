"""
PySide6 跨平台桌面时间挂件：Windows / macOS / Linux。

安装依赖：
    python3 -m pip install PySide6
运行：
    python3 SystemTimerWidget.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime

try:
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError:
    print("未安装 PySide6，请先执行: python3 -m pip install PySide6", file=sys.stderr)
    raise

# 时 / 分 / 秒 的前景色
_COLOR_H = "#e06c75"
_COLOR_M = "#98c379"
_COLOR_S = "#61afef"
_BG = "#1e1e1e"
_FG_SEP = "#5c6370"


def _pick_font() -> QFont:
    if sys.platform == "darwin":
        return QFont("Menlo", 28, QFont.Weight.Bold)
    if sys.platform.startswith("win"):
        return QFont("Consolas", 28, QFont.Weight.Bold)
    return QFont("DejaVu Sans Mono", 26, QFont.Weight.Bold)


class SystemTimerWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("系统时间")
        self.setMinimumSize(300, 140)
        self.setStyleSheet(f"background-color: {_BG};")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        font = _pick_font()
        root = QVBoxLayout()
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)
        self.setLayout(root)

        time_row = QHBoxLayout()
        time_row.setSpacing(0)
        root.addLayout(time_row)

        self.lbl_h = QLabel("00")
        self.lbl_c1 = QLabel(":")
        self.lbl_m = QLabel("00")
        self.lbl_c2 = QLabel(":")
        self.lbl_s = QLabel("00")

        self.lbl_h.setStyleSheet(f"color: {_COLOR_H};")
        self.lbl_m.setStyleSheet(f"color: {_COLOR_M};")
        self.lbl_s.setStyleSheet(f"color: {_COLOR_S};")
        self.lbl_c1.setStyleSheet(f"color: {_FG_SEP};")
        self.lbl_c2.setStyleSheet(f"color: {_FG_SEP};")

        for lbl in (self.lbl_h, self.lbl_c1, self.lbl_m, self.lbl_c2, self.lbl_s):
            lbl.setFont(font)
            time_row.addWidget(lbl)

        control_row = QHBoxLayout()
        control_row.setSpacing(8)
        root.addLayout(control_row)

        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 99)
        self.spin_min.setSuffix(" 分")
        self.spin_min.setValue(1)

        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        self.spin_sec.setSuffix(" 秒")
        self.spin_sec.setValue(0)

        self.btn_start = QPushButton("开始倒计时")
        self.btn_pause = QPushButton("暂停")
        self.btn_reset = QPushButton("重置")
        self.btn_pause.setEnabled(False)

        control_row.addWidget(self.spin_min)
        control_row.addWidget(self.spin_sec)
        control_row.addWidget(self.btn_start)
        control_row.addWidget(self.btn_pause)
        control_row.addWidget(self.btn_reset)

        self.tip = QLabel("当前模式：时钟")
        self.tip.setStyleSheet("color: #aaaaaa;")
        root.addWidget(self.tip)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.btn_start.clicked.connect(self._start_countdown)
        self.btn_pause.clicked.connect(self._pause_countdown)
        self.btn_reset.clicked.connect(self._reset_countdown)

        self._countdown_running = False
        self._countdown_end_ts = 0.0
        self._remaining_seconds = 0
        self._tick()

    def _tick(self) -> None:
        if self._countdown_running:
            self._remaining_seconds = max(0, int(self._countdown_end_ts - time.time()))
            h = self._remaining_seconds // 3600
            m = (self._remaining_seconds % 3600) // 60
            s = self._remaining_seconds % 60
            self.lbl_h.setText(f"{h:02d}")
            self.lbl_m.setText(f"{m:02d}")
            self.lbl_s.setText(f"{s:02d}")
            self.tip.setText("当前模式：倒计时")
            if self._remaining_seconds == 0:
                self._countdown_running = False
                self.btn_pause.setEnabled(False)
                self.tip.setText("倒计时结束！")
                self.tip.setStyleSheet("color: #ffcc66;")
        else:
            now = datetime.now()
            self.lbl_h.setText(f"{now.hour:02d}")
            self.lbl_m.setText(f"{now.minute:02d}")
            self.lbl_s.setText(f"{now.second:02d}")
            if self.tip.text() != "倒计时结束！":
                self.tip.setText("当前模式：时钟")
                self.tip.setStyleSheet("color: #aaaaaa;")

        # 下一次刷新对齐到下一秒边界，减少视觉抖动
        delay_ms = int(1000 * (1.0 - (time.time() % 1.0)))
        if delay_ms < 1:
            delay_ms = 1
        self.timer.start(delay_ms)

    def _start_countdown(self) -> None:
        total = self.spin_min.value() * 60 + self.spin_sec.value()
        if total <= 0:
            self.tip.setText("请先设置倒计时（至少 1 秒）")
            self.tip.setStyleSheet("color: #ffcc66;")
            return
        self._remaining_seconds = total
        self._countdown_end_ts = time.time() + total
        self._countdown_running = True
        self.btn_pause.setEnabled(True)
        self.tip.setStyleSheet("color: #aaaaaa;")
        self._tick()

    def _pause_countdown(self) -> None:
        if not self._countdown_running:
            return
        self._countdown_running = False
        self.btn_pause.setEnabled(False)
        self.tip.setText(f"已暂停：剩余 {self._remaining_seconds} 秒")
        self.tip.setStyleSheet("color: #aaaaaa;")

    def _reset_countdown(self) -> None:
        self._countdown_running = False
        self._remaining_seconds = 0
        self._countdown_end_ts = 0.0
        self.btn_pause.setEnabled(False)
        self.tip.setText("当前模式：时钟")
        self.tip.setStyleSheet("color: #aaaaaa;")
        self._tick()


def main() -> None:
    app = QApplication(sys.argv)
    w = SystemTimerWidget()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
