# -*- coding: utf-8 -*-
"""
src/core/localizer.py
Antigravity 界面汉化与还原管理模块（基于 qqxpee/antigravity2-cn）
"""

import os
import shutil
import subprocess
import time
import psutil
from .paths import get_localization_res_dir

DEFAULT_INSTALL_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Programs\antigravity")


def get_localization_engine_js():
    return os.path.join(get_localization_res_dir(), "localization_engine.js")


def get_antigravity_paths(custom_dir=None):
    """获取 Antigravity 各关键路径"""
    install_dir = custom_dir or DEFAULT_INSTALL_DIR
    resources_dir = os.path.join(install_dir, "resources")
    asar_path = os.path.join(resources_dir, "app.asar")
    bak_path = os.path.join(resources_dir, "app.asar.bak")
    exe_path = os.path.join(install_dir, "Antigravity.exe")

    return {
        "install_dir": install_dir,
        "resources_dir": resources_dir,
        "asar_path": asar_path,
        "bak_path": bak_path,
        "exe_path": exe_path,
        "installed": os.path.exists(exe_path) or os.path.exists(asar_path)
    }


def get_localization_status(custom_dir=None):
    """检查当前汉化状态"""
    paths = get_antigravity_paths(custom_dir)
    if not paths["installed"]:
        return {
            "installed": False,
            "status": "未安装",
            "is_localized": False,
            "has_backup": False,
            "paths": paths
        }

    has_backup = os.path.exists(paths["bak_path"])
    asar_exists = os.path.exists(paths["asar_path"])

    is_localized = False
    if asar_exists and has_backup:
        try:
            asar_size = os.path.getsize(paths["asar_path"])
            bak_size = os.path.getsize(paths["bak_path"])
            is_localized = asar_size != bak_size
        except Exception:
            is_localized = True

    status_str = "已汉化" if is_localized else "官方英文原版"

    return {
        "installed": True,
        "status": status_str,
        "is_localized": is_localized,
        "has_backup": has_backup,
        "paths": paths
    }


def kill_antigravity_processes(callback=None):
    """安全关闭所有运行中的 Antigravity 与语言服务进程"""
    killed = 0
    for p in psutil.process_iter(['pid', 'name']):
        try:
            name = (p.info['name'] or '').lower()
            if 'antigravity' in name or 'language_server' in name:
                if callback:
                    callback(f"正在结束占用进程: {p.info['name']} (PID: {p.info['pid']})")
                p.kill()
                killed += 1
        except Exception:
            pass
    if killed > 0:
        time.sleep(1.5)
    return killed


def start_antigravity(custom_dir=None, callback=None):
    """启动 Antigravity 客户端"""
    paths = get_antigravity_paths(custom_dir)
    if os.path.exists(paths["exe_path"]):
        if callback:
            callback(f"正在启动 Antigravity: {paths['exe_path']}")
        subprocess.Popen([paths["exe_path"]], cwd=paths["install_dir"])
        return True
    return False


def install_localization(brand_title="english", use_tw=False, custom_dir=None, restart_after=False, callback=None):
    """
    一键安装汉化
    """
    paths = get_antigravity_paths(custom_dir)
    if not paths["installed"]:
        raise RuntimeError(f"未找到 Antigravity 安装目录: {paths['install_dir']}")

    engine_js = get_localization_engine_js()
    loc_res_dir = get_localization_res_dir()

    if not os.path.exists(engine_js):
        raise RuntimeError(f"未在资源目录中找到汉化引擎文件: {engine_js}")

    if callback:
        callback("【步骤 1/3】正在关闭可能运行的 Antigravity 客户端...")
    kill_antigravity_processes(callback)

    cmd = [
        "node",
        engine_js,
        f"--brand-title={brand_title}",
        f"--install-dir={paths['install_dir']}"
    ]
    if use_tw:
        cmd.append("--tw")

    if callback:
        callback("【步骤 2/3】正在执行汉化注入引擎...")
        callback(f"执行命令: {' '.join(cmd)}")

    proc = subprocess.Popen(
        cmd,
        cwd=loc_res_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    for line in proc.stdout:
        line_clean = line.strip()
        if line_clean and callback:
            callback(f"  [引擎] {line_clean}")

    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"汉化注入引擎执行失败 (ExitCode: {proc.returncode})")

    if callback:
        callback("【步骤 3/3】汉化注入成功！")

    if restart_after:
        start_antigravity(custom_dir, callback)

    return True


def restore_official(custom_dir=None, restart_after=False, callback=None):
    """
    一键无痕还原官方英文原版
    """
    paths = get_antigravity_paths(custom_dir)
    if not paths["installed"]:
        raise RuntimeError(f"未找到 Antigravity 安装目录: {paths['install_dir']}")

    if callback:
        callback("【步骤 1/3】正在关闭占用进程...")
    kill_antigravity_processes(callback)

    engine_js = get_localization_engine_js()
    loc_res_dir = get_localization_res_dir()

    if os.path.exists(engine_js):
        if callback:
            callback("【步骤 2/3】调用官方还原指令 (--huifu)...")
        cmd = [
            "node",
            engine_js,
            "--huifu",
            f"--install-dir={paths['install_dir']}"
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=loc_res_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        for line in proc.stdout:
            line_clean = line.strip()
            if line_clean and callback:
                callback(f"  [还原] {line_clean}")
        proc.wait()

    if os.path.exists(paths["bak_path"]):
        if callback:
            callback(f"正在校验并恢复原始包: {paths['bak_path']} -> {paths['asar_path']}")
        try:
            shutil.copy2(paths["bak_path"], paths["asar_path"])
        except Exception as e:
            if callback:
                callback(f"覆盖备份文件异常: {e}")

    if callback:
        callback("【步骤 3/3】官方原版还原成功！")

    if restart_after:
        start_antigravity(custom_dir, callback)

    return True
