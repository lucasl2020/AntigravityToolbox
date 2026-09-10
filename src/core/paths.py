# -*- coding: utf-8 -*-
"""
src/core/paths.py
统一路径管理模块：
支持源码开发运行与 PyInstaller 打包后的独立 EXE 运行环境。
确保所有下载、配置与更新的 resources 资源包永远位于 exe 所在目录的同级路径。
"""

import sys
import os


def get_app_dir():
    """
    获取应用程序主运行根目录：
    - 当通过 PyInstaller 打包的独立 EXE 运行时，返回该 EXE 文件所在的实际物理目录
    - 当在源码开发环境下运行时，返回项目根目录（从 src/core/ 向上追溯 3 层）
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 当前文件在 src/core/paths.py，向上追溯三级得到项目根目录
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_resources_dir():
    """获取 resources 目录路径（位于 exe 或项目根目录下的 resources/）"""
    res_dir = os.path.join(get_app_dir(), "resources")
    os.makedirs(res_dir, exist_ok=True)
    return res_dir


def get_versions_file():
    """获取 versions.json 配置文件路径"""
    return os.path.join(get_resources_dir(), "versions.json")


def get_proxy_res_dir():
    """获取 proxy_injector 资源目录路径"""
    p_dir = os.path.join(get_resources_dir(), "proxy_injector")
    os.makedirs(p_dir, exist_ok=True)
    return p_dir


def get_localization_res_dir():
    """获取 localization 资源目录路径"""
    l_dir = os.path.join(get_resources_dir(), "localization")
    os.makedirs(l_dir, exist_ok=True)
    return l_dir


def get_dicts_dir():
    """获取 localization/dicts 字典目录路径"""
    d_dir = os.path.join(get_localization_res_dir(), "dicts")
    os.makedirs(d_dir, exist_ok=True)
    return d_dir
