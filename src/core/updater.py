# -*- coding: utf-8 -*-
"""
src/core/updater.py
GitHub 自动更新检测与资源热拉取打包模块
负责检测 yuaotian/antigravity-proxy 和 qqxpee/antigravity2-cn 的最新发布与资源同步
确保下载的资源永远写入 exe 所在路径下的 resources/ 目录中
"""

import os
import io
import json
import time
import zipfile
import requests
from .paths import (
    get_resources_dir, get_versions_file, get_proxy_res_dir,
    get_localization_res_dir, get_dicts_dir
)

REPO_PROXY = "yuaotian/antigravity-proxy"
REPO_LOC = "qqxpee/antigravity2-cn"


def load_local_versions():
    """读取本地存储的资源版本元数据"""
    versions_file = get_versions_file()
    if os.path.exists(versions_file):
        try:
            with open(versions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "antigravity_proxy": {
            "repo": REPO_PROXY,
            "version": "v2.4",
            "release_tag": "v2.4",
            "last_checked": "",
            "download_url": ""
        },
        "antigravity2_cn": {
            "repo": REPO_LOC,
            "version": "2026.09",
            "commit_sha": "initial",
            "last_checked": "",
            "branch": "main"
        }
    }


def save_local_versions(data):
    """保存版本元数据至 versions.json"""
    versions_file = get_versions_file()
    with open(versions_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_github_updates(proxy_url=None, timeout=8):
    """
    检查两个项目的最新发布与更新
    """
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    headers = {"User-Agent": "Antigravity-GUI-Updater/1.0", "Accept": "application/vnd.github.v3+json"}

    local_vers = load_local_versions()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "timestamp": now_str,
        "proxy": {
            "has_update": False,
            "current_version": local_vers.get("antigravity_proxy", {}).get("release_tag", "v2.4"),
            "latest_version": "",
            "download_url": "",
            "release_notes": "",
            "error": None
        },
        "localization": {
            "has_update": False,
            "current_sha": local_vers.get("antigravity2_cn", {}).get("commit_sha", "initial"),
            "latest_sha": "",
            "commit_message": "",
            "error": None
        }
    }

    # 1. 检测 yuaotian/antigravity-proxy 最新 Release
    try:
        url = f"https://api.github.com/repos/{REPO_PROXY}/releases/latest"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            rel = resp.json()
            tag = rel.get("tag_name", "").strip()
            result["proxy"]["latest_version"] = tag
            result["proxy"]["release_notes"] = rel.get("body", "")

            download_url = ""
            for asset in rel.get("assets", []):
                name = asset.get("name", "").lower()
                if "win-x64" in name or ("win" in name and "64" in name):
                    download_url = asset.get("browser_download_url", "")
                    break

            result["proxy"]["download_url"] = download_url
            curr_tag = local_vers.get("antigravity_proxy", {}).get("release_tag", "")
            if tag and curr_tag and tag.lower() != curr_tag.lower():
                result["proxy"]["has_update"] = True
        else:
            result["proxy"]["error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        result["proxy"]["error"] = str(e)

    # 2. 检测 qqxpee/antigravity2-cn 最新 Commit
    try:
        url = f"https://api.github.com/repos/{REPO_LOC}/commits/main"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            commit_data = resp.json()
            sha = commit_data.get("sha", "")[:8]
            msg = commit_data.get("commit", {}).get("message", "")
            result["localization"]["latest_sha"] = sha
            result["localization"]["commit_message"] = msg.splitlines()[0] if msg else ""

            curr_sha = local_vers.get("antigravity2_cn", {}).get("commit_sha", "")
            if sha and curr_sha and curr_sha != "initial" and sha != curr_sha:
                result["localization"]["has_update"] = True
        else:
            result["localization"]["error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        result["localization"]["error"] = str(e)

    return result


def sync_proxy_resources(download_url, new_tag, proxy_url=None, callback=None):
    """
    下载最新的 antigravity-proxy Release 资产包并提取到 resources/proxy_injector
    """
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    headers = {"User-Agent": "Antigravity-GUI-Updater/1.0"}

    if not download_url:
        raise ValueError("未提供下载链接")

    if callback:
        callback(f"正在下载最新代理注入资源 ({new_tag}): {download_url}")

    resp = requests.get(download_url, headers=headers, proxies=proxies, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"下载代理资产包失败 (HTTP {resp.status_code})")

    proxy_dir = get_proxy_res_dir()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        for filename in z.namelist():
            lower = filename.lower()
            if lower.endswith("version.dll"):
                target_file = os.path.join(proxy_dir, "version.dll")
                with open(target_file, "wb") as f:
                    f.write(z.read(filename))
                if callback:
                    callback(f"已更新本地资源: {target_file}")
            elif lower.endswith("config.json"):
                target_cfg = os.path.join(proxy_dir, "config.json")
                with open(target_cfg, "wb") as f:
                    f.write(z.read(filename))
                if callback:
                    callback(f"已更新本地模板: {target_cfg}")

    vers = load_local_versions()
    vers["antigravity_proxy"]["release_tag"] = new_tag
    vers["antigravity_proxy"]["version"] = new_tag
    vers["antigravity_proxy"]["last_checked"] = time.strftime("%Y-%m-%d %H:%M:%S")
    vers["antigravity_proxy"]["download_url"] = download_url
    save_local_versions(vers)

    if callback:
        callback(f"【完成】antigravity-proxy 资源已热更新并打包至 {new_tag}！")
    return True


def sync_localization_resources(new_sha, proxy_url=None, callback=None):
    """
    拉取最新的 antigravity2-cn 汉化引擎和字典并存入 resources/localization
    """
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    headers = {"User-Agent": "Antigravity-GUI-Updater/1.0"}
    raw_base = f"https://raw.githubusercontent.com/{REPO_LOC}/main"

    loc_dir = get_localization_res_dir()
    dicts_dir = get_dicts_dir()

    # 1. 拉取 localization_engine.js
    if callback:
        callback("正在拉取最新 localization_engine.js...")
    engine_url = f"{raw_base}/localization_engine.js"
    r = requests.get(engine_url, headers=headers, proxies=proxies, timeout=15)
    if r.status_code == 200:
        engine_path = os.path.join(loc_dir, "localization_engine.js")
        with open(engine_path, "w", encoding="utf-8") as f:
            f.write(r.text)

    # 2. 拉取字典文件
    dict_files = [
        "common.json", "menu_nav.json", "page_agents.json",
        "page_mcp_knowledge.json", "page_settings.json", "page_workspaces.json"
    ]
    for df in dict_files:
        if callback:
            callback(f"正在拉取最新字典: {df}")
        d_url = f"{raw_base}/dicts/{df}"
        r = requests.get(d_url, headers=headers, proxies=proxies, timeout=15)
        if r.status_code == 200:
            df_path = os.path.join(dicts_dir, df)
            with open(df_path, "w", encoding="utf-8") as f:
                f.write(r.text)

    vers = load_local_versions()
    vers["antigravity2_cn"]["commit_sha"] = new_sha
    vers["antigravity2_cn"]["last_checked"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_local_versions(vers)

    if callback:
        callback(f"【完成】antigravity2-cn 汉化字典已热更新至最新 Commit ({new_sha})！")
    return True
