# -*- coding: utf-8 -*-
"""
src/app.py
Antigravity 综合管理工具箱 - 主程序入口 (秒级极速响应架构)
"""

import sys
import os

# 确保项目根目录与 src 均在 sys.path 中
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.ui.main_window import MainWindow


def main():
    # 启用高分屏自适应
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("AntigravityToolbox")
    app.setOrganizationName("AntigravityCommunity")

    # 瞬间创建并展现主窗口，后台任务延迟装载
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
