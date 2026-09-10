# -*- coding: utf-8 -*-
"""
src/core/detector.py
Antigravity 网络环境、代理设置与核心服务连通性诊断模块
"""

import os
import time
import winreg
import psutil
import requests
from concurrent.futures import ThreadPoolExecutor

COMMON_PROXY_PORTS = [7890, 7897, 7891, 10808, 10809, 1080, 2080, 2081, 8888, 8080]

CORE_TARGETS = [
    {"id": "accounts",  "name": "Google 账号体系 (OAuth/登录)",  "url": "https://accounts.google.com"},
    {"id": "oauth2",    "name": "Google OAuth 令牌刷新通道",    "url": "https://oauth2.googleapis.com"},
    {"id": "gemini_api","name": "Gemini API (语言模型核心接口)", "url": "https://generativelanguage.googleapis.com"},
    {"id": "vertex",    "name": "Google Vertex AI 企业云平台",    "url": "https://aiplatform.googleapis.com"},
    {"id": "portal",    "name": "Antigravity 官方门户与服务",    "url": "https://antigravity.google"},
    {"id": "gemini_web","name": "Gemini 官方 Web 服务应用",      "url": "https://gemini.google.com"},
    {"id": "github",    "name": "GitHub API (扩展/Skills/更新)", "url": "https://api.github.com"},
    {"id": "npm",       "name": "npm 官方镜像 (前端扩展依赖源)",   "url": "https://registry.npmjs.org"}
]

COUNTRY_NAMES = {
    "KR": "韩国 (South Korea)",
    "JP": "日本 (Japan)",
    "SG": "新加坡 (Singapore)",
    "US": "美国 (United States)",
    "HK": "香港 (Hong Kong)",
    "TW": "台湾 (Taiwan)",
    "GB": "英国 (United Kingdom)",
    "DE": "德国 (Germany)",
    "CN": "中国大陆 (China)",
    "RU": "俄罗斯 (Russia)"
}

UNSUPPORTED_REGIONS = ["CN", "RU", "IR", "KP", "BY", "SY", "CU"]
PARTIALLY_SUPPORTED = ["HK"]


def get_registry_proxy():
    """读取 Windows 注册表 WinINet 系统代理设置"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_READ
        )
        proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
        try:
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
        except FileNotFoundError:
            proxy_server = ""
        try:
            auto_config_url, _ = winreg.QueryValueEx(key, "AutoConfigURL")
        except FileNotFoundError:
            auto_config_url = ""
        winreg.CloseKey(key)

        return {
            "enabled": bool(proxy_enable),
            "server": str(proxy_server).strip(),
            "auto_config_url": str(auto_config_url).strip()
        }
    except Exception as e:
        return {"enabled": False, "server": "", "auto_config_url": "", "error": str(e)}


def get_env_proxies():
    """读取系统和当前进程环境变量代理"""
    return {
        "http_proxy": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or "",
        "https_proxy": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "",
        "all_proxy": os.environ.get("ALL_PROXY") or os.environ.get("all_proxy") or ""
    }


def get_listening_proxy_ports():
    """扫描本机常见正在监听的代理端口"""
    found = []
    try:
        for conn in psutil.net_connections(kind="tcp"):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port in COMMON_PROXY_PORTS:
                pname = "未知进程"
                try:
                    proc = psutil.Process(conn.pid)
                    pname = proc.name()
                except Exception:
                    pass
                found.append({
                    "port": conn.laddr.port,
                    "ip": conn.laddr.ip,
                    "pid": conn.pid,
                    "process_name": pname
                })
    except Exception:
        pass
    return found


def get_antigravity_processes():
    """精确检索正在运行的 Antigravity 客户端主程序进程（排除工具箱自身与无关语言服务）"""
    procs = []
    try:
        for p in psutil.process_iter(['pid', 'name', 'memory_info']):
            name = (p.info['name'] or '').lower()
            # 排除工具箱自身进程
            if 'antigravitytoolbox' in name or 'toolbox' in name:
                continue
            # 仅精确匹配 Antigravity 客户端
            if name in ('antigravity.exe', 'antigravity'):
                mem_mb = round(p.info['memory_info'].rss / (1024 * 1024), 1) if p.info.get('memory_info') else 0
                procs.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "memory_mb": mem_mb
                })
    except Exception:
        pass
    return procs


def determine_effective_proxy(custom_proxy=None, force_direct=False):
    """自动计算生效的代理 URL"""
    if force_direct:
        return ""
    if custom_proxy and custom_proxy.strip():
        cp = custom_proxy.strip()
        if not cp.startswith("http://") and not cp.startswith("socks5://"):
            cp = f"http://{cp}"
        return cp

    reg = get_registry_proxy()
    if reg["enabled"] and reg["server"]:
        srv = reg["server"]
        if not srv.startswith("http://") and not srv.startswith("socks5://"):
            srv = f"http://{srv}"
        return srv

    env_p = get_env_proxies()
    if env_p["https_proxy"]:
        return env_p["https_proxy"]
    if env_p["http_proxy"]:
        return env_p["http_proxy"]

    ports = get_listening_proxy_ports()
    if ports:
        return f"http://127.0.0.1:{ports[0]['port']}"

    return ""


def detect_egress_ip(proxy_url=None, timeout=6):
    """通过 Cloudflare Trace 探测出口 IP 与地理位置"""
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    try:
        resp = requests.get("https://cloudflare.com/cdn-cgi/trace", proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            lines = resp.text.strip().splitlines()
            trace_dict = {}
            for line in lines:
                if "=" in line:
                    k, v = line.split("=", 1)
                    trace_dict[k.strip()] = v.strip()

            ip = trace_dict.get("ip", "未知")
            loc = trace_dict.get("loc", "未知")
            colo = trace_dict.get("colo", "")

            loc_friendly = COUNTRY_NAMES.get(loc, loc)
            region_level = "pass"
            region_msg = "支持良好"

            if loc in UNSUPPORTED_REGIONS:
                region_level = "danger"
                region_msg = f"受限地区 ({loc})，Google AI 服务会屏蔽此地区请求，建议切换节点！"
            elif loc in PARTIALLY_SUPPORTED:
                region_level = "warning"
                region_msg = f"可能受限 ({loc})，香港节点部分 Google AI 服务可能受限，建议换用 JP/SG/US 节点。"

            return {
                "success": True,
                "ip": ip,
                "loc": loc,
                "loc_friendly": loc_friendly,
                "colo": colo,
                "region_level": region_level,
                "region_msg": region_msg
            }
    except Exception as e:
        return {
            "success": False,
            "ip": "探测失败",
            "loc": "未知",
            "loc_friendly": "未知",
            "colo": "",
            "region_level": "danger",
            "region_msg": f"请求超时或代理不可达: {e}"
        }


def test_single_endpoint(target, proxy_url=None, timeout=6):
    """测试单个核心端点网络连通性与时延"""
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    start = time.perf_counter()
    try:
        # 对 accounts 等网页端点跟随重定向，以直接获取最终 200 结果
        allow_redirect = target.get("id") in ["accounts", "portal", "gemini_web"]
        resp = requests.get(target["url"], proxies=proxies, timeout=timeout, allow_redirects=allow_redirect)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        code = resp.status_code
        ok = code in [200, 204, 301, 302, 307, 308, 400, 401, 403, 404]
        return {
            "id": target["id"],
            "name": target["name"],
            "url": target["url"],
            "success": ok,
            "code": code,
            "latency_ms": elapsed_ms,
            "error": None if ok else f"HTTP {code}"
        }
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "id": target["id"],
            "name": target["name"],
            "url": target["url"],
            "success": False,
            "code": 0,
            "latency_ms": elapsed_ms,
            "error": str(e)
        }


def run_full_diagnosis(custom_proxy=None, force_direct=False, timeout=6, callback=None):
    """运行完整诊断，支持多线程并发并分步回调"""
    effective_proxy = determine_effective_proxy(custom_proxy, force_direct)

    reg_proxy = get_registry_proxy()
    env_proxies = get_env_proxies()
    listening_ports = get_listening_proxy_ports()
    ag_procs = get_antigravity_processes()

    if callback:
        callback("egress_start", "正在探测代理出口节点地理位置...")

    egress = detect_egress_ip(effective_proxy, timeout=timeout)

    if callback:
        callback("egress_done", egress)
        callback("endpoints_start", "正在测试 8 大核心端点...")

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(test_single_endpoint, t, effective_proxy, timeout)
            for t in CORE_TARGETS
        ]
        for f in futures:
            res = f.result()
            results.append(res)
            if callback:
                callback("endpoint_result", res)

    passed_count = sum(1 for r in results if r["success"])
    total_count = len(results)

    if passed_count == total_count and egress["region_level"] == "pass":
        overall_status = "PASS"
        overall_title = "完美可用"
        overall_desc = "当前本机代理环境完全满足 Google Antigravity 的全部运行需求！"
    elif passed_count >= 5:
        overall_status = "WARNING"
        overall_title = "部分可用"
        overall_desc = "核心链路基本通畅，但存在部分接口超时或地区受限，可能会影响部分扩展功能。"
    else:
        overall_status = "FAIL"
        overall_title = "不可用"
        overall_desc = "大部分核心接口无法连通，请检查代理软件运行状态、代理端口或切换代理节点。"

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "effective_proxy": effective_proxy,
        "reg_proxy": reg_proxy,
        "env_proxies": env_proxies,
        "listening_ports": listening_ports,
        "ag_procs": ag_procs,
        "egress": egress,
        "results": results,
        "passed_count": passed_count,
        "total_count": total_count,
        "overall_status": overall_status,
        "overall_title": overall_title,
        "overall_desc": overall_desc
    }

    if callback:
        callback("complete", report)

    return report
