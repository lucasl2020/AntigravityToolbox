# -*- coding: utf-8 -*-
"""
app.py
Antigravity 综合管理工具箱 - 根目录快捷入口
重定向调用 src/app.py
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.app import main

if __name__ == "__main__":
    main()
