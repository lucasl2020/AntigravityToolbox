# -*- coding: utf-8 -*-
"""
src/core/injector.py
Antigravity 强制代理注入与管理模块（基于 yuaotian/antigravity-proxy）
"""

import os
import json
import shutil
import time
import psutil
import subprocess
from .paths import get_proxy_res_dir

DEFAULT_INSTALL_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Programs\antigravity")


def get_template_dll():
    return os.path.join(get_proxy_res_dir(), "version.dll")


def get_template_config():
    return os.path.join(get_proxy_res_dir(), "config.json")


def get_installed_paths(custom_dir=None):
    """获取 Antigravity 目标路径"""
    install_dir = custom_dir or DEFAULT_INSTALL_DIR
    target_dll = os.path.join(install_dir, "version.dll")
    target_config = os.path.join(install_dir, "config.json")
    exe_path = os.path.join(install_dir, "Antigravity.exe")

    return {
        "install_dir": install_dir,
        "target_dll": target_dll,
        "target_config": target_config,
        "exe_path": exe_path,
        "installed": os.path.exists(exe_path)
    }


def get_injector_status(custom_dir=None):
    """检测 Antigravity 当前代理注入状态"""
    paths = get_installed_paths(custom_dir)
    if not paths["installed"]:
        return {
            "installed": False,
            "is_injected": False,
            "status": "未安装 Antigravity",
            "proxy_type": "socks5",
            "host": "127.0.0.1",
            "port": 7897,
            "paths": paths
        }

    dll_exists = os.path.exists(paths["target_dll"])
    config_exists = os.path.exists(paths["target_config"])

    proxy_type = "socks5"
    host = "127.0.0.1"
    port = 7897
    version_tag = "2.4"

    if config_exists:
        try:
            with open(paths["target_config"], "r", encoding="utf-8") as f:
                data = json.load(f)
                if "proxy" in data:
                    proxy_type = data["proxy"].get("type", "socks5")
                    host = data["proxy"].get("host", "127.0.0.1")
                    port = data["proxy"].get("port", 7897)
                version_tag = data.get("_version", "2.4")
        except Exception:
            pass

    is_injected = dll_exists

    return {
        "installed": True,
        "is_injected": is_injected,
        "status": "已注入免 TUN 代理" if is_injected else "未注入 (默认直连/系统代理)",
        "proxy_type": proxy_type,
        "host": host,
        "port": port,
        "version": version_tag,
        "dll_size": os.path.getsize(paths["target_dll"]) if dll_exists else 0,
        "paths": paths
    }


def kill_antigravity_processes(callback=None):
    """安全关闭占用 version.dll 的进程"""
    killed = 0
    for p in psutil.process_iter(['pid', 'name']):
        try:
            name = (p.info['name'] or '').lower()
            if 'antigravity' in name or 'language_server' in name or 'node' in name:
                try:
                    exe = p.exe().lower()
                    if 'antigravity' in exe:
                        if callback:
                            callback(f"正在结束占用进程: {p.info['name']} (PID: {p.info['pid']})")
                        p.kill()
                        killed += 1
                except Exception:
                    pass
        except Exception:
            pass
    if killed > 0:
        time.sleep(1.5)
    return killed


def build_config_content(proxy_type="socks5", host="127.0.0.1", port=7897):
    """构建定制的 config.json 内容"""
    config_data = {}
    template_config = get_template_config()
    if os.path.exists(template_config):
        try:
            with open(template_config, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            pass

    if not config_data:
        config_data = {
            "_version": "2.4",
            "_comment": "Antigravity-Proxy 配置文件",
            "child_injection": True,
            "child_injection_mode": "filtered",
            "fake_ip": {"cidr": "198.18.0.0/15", "enabled": True},
            "traffic_logging": False,
            "log_level": "info",
            "timeout": {"connect": 5000, "recv": 5000, "send": 5000},
            "diagnostics": {"agent_ip_probe": False},
            "proxy_rules": {
                "routing": {
                    "default_action": "proxy",
                    "priority_mode": "order",
                    "rules": [],
                    "use_default_private": True,
                    "enabled": True
                },
                "allowed_ports": [80, 443],
                "udp_mode": "auto",
                "ipv6_mode": "proxy",
                "udp_fallback": "block",
                "dns_mode": "direct"
            },
            "target_processes": [
                "agy.exe",
                "language_server.exe",
                "language_server_windows",
                "language_server_windows_x64.exe",
                "Antigravity.exe",
                "Antigravity IDE.exe",
                "node.exe"
            ]
        }

    config_data["proxy"] = {
        "type": proxy_type.lower(),
        "host": host.strip(),
        "port": int(port)
    }

    return config_data


def inject_proxy(proxy_type="socks5", host="127.0.0.1", port=7897, custom_dir=None, restart_after=False, callback=None):
    """
    执行代理注入
    """
    paths = get_installed_paths(custom_dir)
    if not paths["installed"]:
        raise RuntimeError(f"未找到 Antigravity 客户端: {paths['install_dir']}")

    template_dll = get_template_dll()
    if not os.path.exists(template_dll):
        raise RuntimeError(f"未找到资源库中的 version.dll: {template_dll}")

    if callback:
        callback("【步骤 1/3】正在安全退出 Antigravity 运行中进程以释放文件锁...")
    kill_antigravity_processes(callback)

    if callback:
        callback(f"【步骤 2/3】部署 DLL 劫持文件: {template_dll} -> {paths['target_dll']}")
    shutil.copy2(template_dll, paths["target_dll"])

    if callback:
        callback(f"【步骤 3/3】生成配置文件 ({proxy_type}://{host}:{port}) -> {paths['target_config']}")
    cfg_data = build_config_content(proxy_type, host, port)
    with open(paths["target_config"], "w", encoding="utf-8") as f:
        json.dump(cfg_data, f, indent=2, ensure_ascii=False)

    if callback:
        callback("【完成】免 TUN 强制代理已成功注入！")

    if restart_after and os.path.exists(paths["exe_path"]):
        if callback:
            callback(f"正在重启 Antigravity: {paths['exe_path']}")
        subprocess.Popen([paths["exe_path"]], cwd=paths["install_dir"])

    return True


def uninstall_proxy(custom_dir=None, restart_after=False, callback=None):
    """
    卸载代理注入
    """
    paths = get_installed_paths(custom_dir)
    if not paths["installed"]:
        raise RuntimeError(f"未找到 Antigravity 客户端: {paths['install_dir']}")

    if callback:
        callback("【步骤 1/2】正在退出 Antigravity 进程以释放文件锁...")
    kill_antigravity_processes(callback)

    removed = False
    if os.path.exists(paths["target_dll"]):
        try:
            os.remove(paths["target_dll"])
            removed = True
            if callback:
                callback(f"已安全移除: {paths['target_dll']}")
        except Exception as e:
            if callback:
                callback(f"移除 version.dll 失败: {e}")

    if os.path.exists(paths["target_config"]):
        try:
            bak_cfg = paths["target_config"] + ".bak"
            if os.path.exists(bak_cfg):
                os.remove(bak_cfg)
            os.rename(paths["target_config"], bak_cfg)
            if callback:
                callback(f"已归档配置文件为: {bak_cfg}")
        except Exception:
            pass

    if callback:
        callback("【步骤 2/2】代理注入已成功卸载，Antigravity 恢复默认网络机制。")

    if restart_after and os.path.exists(paths["exe_path"]):
        if callback:
            callback(f"正在重启 Antigravity: {paths['exe_path']}")
        subprocess.Popen([paths["exe_path"]], cwd=paths["install_dir"])

    return True
