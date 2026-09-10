# -*- coding: utf-8 -*-
"""
scripts/build.py
现代化独立可执行程序构建打包脚本
生成秒开、完全脱离 Python 环境的绿色便携分发包
输出目录: dist/AntigravityToolbox/
"""

import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
TARGET_DIR = os.path.join(DIST_DIR, "AntigravityToolbox")


def run_build():
    print("=" * 60)
    print(">> Antigravity 综合管理工具箱 - 开始构建独立便携分发包")
    print(f">> 项目根目录: {PROJECT_ROOT}")
    print(f">> 源码目录:   {SRC_DIR}")
    print(f">> 目标输出:   {TARGET_DIR}")
    print("=" * 60)

    # 1. 确保安装 PyInstaller
    try:
        import PyInstaller
        print(f">> 检测到 PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print(">> 未检测到 PyInstaller，正在自动安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. 清理可能运行中的旧进程与历史构建产物
    try:
        import psutil
        for p in psutil.process_iter(['name']):
            if (p.info['name'] or '').lower() == 'antigravitytoolbox.exe':
                p.kill()
    except Exception:
        pass

    if os.path.exists(TARGET_DIR):
        print(">> 清理历史目标目录...")
        try:
            shutil.rmtree(TARGET_DIR, ignore_errors=True)
        except Exception as e:
            print(f"   [警告] 清理历史目录提示: {e}")


    # 3. 组织 PyInstaller 命令参数
    # 使用 --onedir 绿色目录分发模式：实现 <0.4s 秒开，避免 --onefile 解压到临时目录的迟钝与防病毒扫描
    entry_point = os.path.join(SRC_DIR, "app.py")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        entry_point,
        "--name=AntigravityToolbox",
        "--onedir",
        "--noconsole",
        "--clean",
        "--noconfirm",
        f"--paths={PROJECT_ROOT}",
        f"--paths={SRC_DIR}",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}"
    ]

    print(">> 正在调用 PyInstaller 编译打包...")
    print(f">> 执行指令: {' '.join(cmd)}")
    subprocess.check_call(cmd)

    # 4. 同步 resources 资源包至 EXE 所在目录同级
    target_res = os.path.join(TARGET_DIR, "resources")
    print(f">> 正在同步资源包至 EXE 所在目录: {target_res}")
    if os.path.exists(RESOURCES_DIR):
        if os.path.exists(target_res):
            shutil.rmtree(target_res, ignore_errors=True)
        shutil.copytree(RESOURCES_DIR, target_res)
        print(">> 资源包同步完成（内含 version.dll、汉化引擎与词典库）！")
    else:
        os.makedirs(target_res, exist_ok=True)
        print("   [提示] 创建空白 resources 目录")

    # 5. 生成快捷启动批处理
    launcher_bat = os.path.join(TARGET_DIR, "启动工具箱.bat")
    with open(launcher_bat, "w", encoding="ascii") as f:
        f.write("@echo off\r\nstart \"\" \"%~dp0AntigravityToolbox.exe\"\r\n")

    root_launcher = os.path.join(PROJECT_ROOT, "启动工具箱.bat")
    with open(root_launcher, "w", encoding="ascii") as f:
        f.write("@echo off\r\nstart \"\" \"%~dp0dist\\AntigravityToolbox\\AntigravityToolbox.exe\"\r\n")

    # 6. 自动将绿色便携目录压缩为可直接上传 GitHub Releases 的 zip 包
    zip_path = os.path.join(DIST_DIR, "AntigravityToolbox-v2.0.0-windows-x64")
    print(f">> 正在生成发布压缩包: {zip_path}.zip ...")
    final_zip = shutil.make_archive(zip_path, 'zip', root_dir=DIST_DIR, base_dir='AntigravityToolbox')
    zip_size_mb = round(os.path.getsize(final_zip) / (1024 * 1024), 2)

    exe_file = os.path.join(TARGET_DIR, "AntigravityToolbox.exe")
    print("=" * 60)
    print(">> [SUCCESS] 打包构建圆满完成！")
    print(f">> 独立主程序目录: {TARGET_DIR}")
    print(f">> 资源目录:       {target_res}")
    print(f">> GitHub 发布包:  {final_zip} ({zip_size_mb} MB)")
    print(">> 特性说明:       完全免 Python 环境独立运行，瞬间秒开 (<0.5s)，资源随 EXE 存放。")
    print("=" * 60)



if __name__ == "__main__":
    run_build()
