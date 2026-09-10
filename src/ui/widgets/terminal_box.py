# -*- coding: utf-8 -*-
"""
src/ui/widgets/terminal_box.py
Mac 风格现代化精致控制台组件 (Modern Light macOS Terminal Console)
特点：
- macOS 拟物三色交通灯 (🔴 🟡 🟢)
- 纯浅色柔和底色 (#f8fafc)，绝不刺眼，纯净现代
- 等宽专业字体 (Cascadia Code / Consolas)
- 内置「一键复制」与「清空」操作按钮
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QApplication
)


class TerminalBox(QFrame):
    """Mac 风格现代化日志控制台组件"""

    def __init__(self, title="执行控制台", parent=None):
        super().__init__(parent)
        self.setProperty("class", "TerminalFrame")
        self.setObjectName("TerminalBox")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 顶部 Mac 窗口控制栏
        header_bar = QFrame()
        header_bar.setObjectName("TerminalHeader")
        header_bar.setStyleSheet("""
            #TerminalHeader {
                background-color: #f1f5f9;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #e2e8f0;
                padding: 6px 12px;
            }
        """)
        h_layout = QHBoxLayout(header_bar)
        h_layout.setContentsMargins(4, 4, 8, 4)
        h_layout.setSpacing(6)

        # 拟物化红黄绿圆点 (10px x 10px)
        dot_red = QLabel()
        dot_red.setFixedSize(11, 11)
        dot_red.setStyleSheet("background-color: #ff5f56; border-radius: 5px; border: 1px solid #e0443e;")

        dot_yellow = QLabel()
        dot_yellow.setFixedSize(11, 11)
        dot_yellow.setStyleSheet("background-color: #ffbd2e; border-radius: 5px; border: 1px solid #dea123;")

        dot_green = QLabel()
        dot_green.setFixedSize(11, 11)
        dot_green.setStyleSheet("background-color: #27c93f; border-radius: 5px; border: 1px solid #1aab29;")

        h_layout.addWidget(dot_red)
        h_layout.addWidget(dot_yellow)
        h_layout.addWidget(dot_green)

        # 居中标题
        self.lbl_title = QLabel(f"  {title}")
        self.lbl_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; background: transparent;")
        h_layout.addWidget(self.lbl_title)
        h_layout.addStretch()

        # 右侧操作按钮：复制、清空
        btn_copy = QPushButton("📋 复制")
        btn_copy.setToolTip("复制所有日志至剪贴板")
        btn_copy.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #0f172a;
            }
        """)
        btn_copy.clicked.connect(self.copy_all)
        h_layout.addWidget(btn_copy)

        btn_clear = QPushButton("🗑 清空")
        btn_clear.setToolTip("清空控制台输出")
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                color: #b91c1c;
                border-color: #fca5a5;
            }
        """)
        btn_clear.clicked.connect(self.clear)
        h_layout.addWidget(btn_clear)

        main_layout.addWidget(header_bar)

        # 2. 控制台文本输出区域 (现代明亮浅色)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                color: #334155;
                font-family: "Cascadia Code", "Consolas", "JetBrains Mono", monospace;
                font-size: 12px;
                line-height: 1.4;
                border: none;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                padding: 10px 12px;
            }
        """)
        main_layout.addWidget(self.text_edit, 1)

        # 外层圆角边框
        self.setStyleSheet("""
            #TerminalBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)

    def append(self, text):
        """追加日志并自动滚动到底部"""
        self.text_edit.append(str(text))
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)

    def clear(self):
        """清空日志"""
        self.text_edit.clear()

    def copy_all(self):
        """复制全部日志"""
        text = self.text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.append("[系统] 已复制全部日志到剪贴板。")
