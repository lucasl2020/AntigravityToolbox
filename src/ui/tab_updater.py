# -*- coding: utf-8 -*-
"""
src/ui/tab_updater.py
GitHub 自动检测更新与资源热打包同步面板 (现代明亮浅色主题 - 集成 Mac 风格终端)
支持 yuaotian/antigravity-proxy 和 qqxpee/antigravity2-cn
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from src.core.updater import (
    load_local_versions, check_github_updates,
    sync_proxy_resources, sync_localization_resources
)
from src.core.detector import determine_effective_proxy
from src.ui.widgets.terminal_box import TerminalBox


class UpdateCheckWorker(QThread):
    finished_signal = Signal(dict)

    def __init__(self, proxy_url=None):
        super().__init__()
        self.proxy_url = proxy_url

    def run(self):
        res = check_github_updates(self.proxy_url)
        self.finished_signal.emit(res)


class SyncWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, sync_type="all", proxy_data=None, loc_data=None, proxy_url=None):
        super().__init__()
        self.sync_type = sync_type
        self.proxy_data = proxy_data or {}
        self.loc_data = loc_data or {}
        self.proxy_url = proxy_url

    def run(self):
        def callback(msg):
            self.log_signal.emit(str(msg))

        try:
            if self.sync_type in ("proxy", "all"):
                url = self.proxy_data.get("download_url")
                tag = self.proxy_data.get("latest_version") or "v2.4"
                if url:
                    sync_proxy_resources(url, tag, self.proxy_url, callback)
                else:
                    callback("跳过代理更新 (未获取到下载包链接)")

            if self.sync_type in ("loc", "all"):
                sha = self.loc_data.get("latest_sha") or "main"
                sync_localization_resources(sha, self.proxy_url, callback)

            self.finished_signal.emit(True, "最新开源资源已成功拉取并热打包进本地 resources 库！")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class TabUpdater(QWidget):
    update_detected_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.check_result = None
        self.init_ui()
        self.refresh_display()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # 1. 顶部更新说明卡片
        top_card = QFrame()
        top_card.setProperty("class", "CardFrame")
        tc_layout = QVBoxLayout(top_card)
        tc_layout.setContentsMargins(16, 12, 16, 12)
        tc_layout.setSpacing(6)

        head_layout = QHBoxLayout()
        title = QLabel("🔄 GitHub 开源项目在线监测与资源热打包中心")
        title.setProperty("class", "CardTitle")
        head_layout.addWidget(title)
        head_layout.addStretch()

        self.lbl_last_check = QLabel("上次检测: 未检测")
        self.lbl_last_check.setStyleSheet("color: #64748b; font-size: 11px;")
        head_layout.addWidget(self.lbl_last_check)
        tc_layout.addLayout(head_layout)

        desc = QLabel(
            "当每次打开应用时，本程序会自动在后台异步向 GitHub 查询两开源项目的最新动态。\n"
            "若检测到新版本发布或新翻译字典提交，可一键将最新 DLL 和字典拉取打包至本地 resources 库中并实时生效应用。"
        )
        desc.setStyleSheet("color: #475569; font-size: 12px; line-height: 1.4;")
        tc_layout.addWidget(desc)

        layout.addWidget(top_card)

        # 2. 两大项目状态卡片 (并排网格)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        # 卡片 1: antigravity-proxy
        card_p = QFrame()
        card_p.setProperty("class", "CardFrame")
        cp_layout = QVBoxLayout(card_p)
        cp_layout.setContentsMargins(16, 14, 16, 14)
        cp_layout.setSpacing(8)

        cp_head = QHBoxLayout()
        cp_title = QLabel("⚡ yuaotian/antigravity-proxy")
        cp_title.setProperty("class", "CardTitle")
        cp_head.addWidget(cp_title)
        cp_head.addStretch()
        self.lbl_proxy_status = QLabel("待检测")
        self.lbl_proxy_status.setProperty("class", "BadgeInfo")
        cp_head.addWidget(self.lbl_proxy_status)
        cp_layout.addLayout(cp_head)

        self.lbl_proxy_cur = QLabel("本地版本: v2.4")
        self.lbl_proxy_cur.setStyleSheet("color: #0f172a; font-weight: 600;")
        self.lbl_proxy_new = QLabel("线上最新: 检测中...")
        self.lbl_proxy_new.setStyleSheet("color: #64748b; font-size: 12px;")

        cp_layout.addWidget(self.lbl_proxy_cur)
        cp_layout.addWidget(self.lbl_proxy_new)

        self.btn_sync_proxy = QPushButton("⬇ 仅拉取最新代理 DLL")
        self.btn_sync_proxy.setProperty("class", "OutlineBtn")
        self.btn_sync_proxy.clicked.connect(lambda: self.start_sync("proxy"))
        cp_layout.addWidget(self.btn_sync_proxy)

        cards_layout.addWidget(card_p)

        # 卡片 2: antigravity2-cn
        card_l = QFrame()
        card_l.setProperty("class", "CardFrame")
        cl_layout = QVBoxLayout(card_l)
        cl_layout.setContentsMargins(16, 14, 16, 14)
        cl_layout.setSpacing(8)

        cl_head = QHBoxLayout()
        cl_title = QLabel("🌐 qqxpee/antigravity2-cn")
        cl_title.setProperty("class", "CardTitle")
        cl_head.addWidget(cl_title)
        cl_head.addStretch()
        self.lbl_loc_status = QLabel("待检测")
        self.lbl_loc_status.setProperty("class", "BadgeInfo")
        cl_head.addWidget(self.lbl_loc_status)
        cl_layout.addLayout(cl_head)

        self.lbl_loc_cur = QLabel("本地版本: 最新字典包")
        self.lbl_loc_cur.setStyleSheet("color: #0f172a; font-weight: 600;")
        self.lbl_loc_new = QLabel("线上最新: 检测中...")
        self.lbl_loc_new.setStyleSheet("color: #64748b; font-size: 12px;")

        cl_layout.addWidget(self.lbl_loc_cur)
        cl_layout.addWidget(self.lbl_loc_new)

        self.btn_sync_loc = QPushButton("⬇ 仅拉取最新汉化字典")
        self.btn_sync_loc.setProperty("class", "OutlineBtn")
        self.btn_sync_loc.clicked.connect(lambda: self.start_sync("loc"))
        cl_layout.addWidget(self.btn_sync_loc)

        cards_layout.addWidget(card_l)

        layout.addLayout(cards_layout)

        # 3. 控制与操作卡片
        act_card = QFrame()
        act_card.setProperty("class", "CardFrame")
        ac_layout = QHBoxLayout(act_card)
        ac_layout.setContentsMargins(14, 10, 14, 10)
        ac_layout.setSpacing(10)

        self.btn_check_now = QPushButton("🔍 立即检查 GitHub 在线更新")
        self.btn_check_now.setProperty("class", "PrimaryBtn")
        self.btn_check_now.clicked.connect(self.check_updates_now)
        ac_layout.addWidget(self.btn_check_now)

        self.btn_sync_all = QPushButton("📦 一键拉取全部最新资源并打包")
        self.btn_sync_all.setProperty("class", "SuccessBtn")
        self.btn_sync_all.clicked.connect(lambda: self.start_sync("all"))
        ac_layout.addWidget(self.btn_sync_all)

        layout.addWidget(act_card)

        # 4. Mac 风格精致日志控制台
        self.terminal = TerminalBox(title="资源拉取与同步日志")
        self.terminal.setMinimumHeight(150)
        layout.addWidget(self.terminal, 1)

    def log(self, text):
        self.terminal.append(text)

    def refresh_display(self):
        vers = load_local_versions()
        p_tag = vers.get("antigravity_proxy", {}).get("release_tag", "v2.4")
        l_sha = vers.get("antigravity2_cn", {}).get("commit_sha", "initial")
        last_t = vers.get("antigravity_proxy", {}).get("last_checked") or "尚未检测"

        self.lbl_proxy_cur.setText(f"本地版本: {p_tag}")
        self.lbl_loc_cur.setText(f"本地 Commit: {l_sha}")
        self.lbl_last_check.setText(f"记录时间: {last_t}")

    def check_updates_now(self):
        self.btn_check_now.setEnabled(False)
        self.btn_check_now.setText("⏳ 正在查询 GitHub...")
        self.log("\n" + "=" * 50)
        self.log("正在连接 GitHub API 查询开源项目最新动态...")

        proxy_url = determine_effective_proxy()
        self.worker = UpdateCheckWorker(proxy_url=proxy_url)
        self.worker.finished_signal.connect(self.on_check_finished)
        self.worker.start()

    def on_check_finished(self, result):
        self.btn_check_now.setEnabled(True)
        self.btn_check_now.setText("🔍 立即检查 GitHub 在线更新")
        self.check_result = result

        proxy_info = result["proxy"]
        loc_info = result["localization"]

        # 处理 Proxy 卡片
        if proxy_info["error"]:
            self.lbl_proxy_new.setText(f"线上最新: 查询失败 ({proxy_info['error']})")
            self.lbl_proxy_status.setText("网络异常")
            self.lbl_proxy_status.setProperty("class", "BadgeFail")
            self.log(f"[antigravity-proxy] 查询错误: {proxy_info['error']}")
        else:
            lat_ver = proxy_info["latest_version"] or "v2.4"
            self.lbl_proxy_new.setText(f"线上最新: {lat_ver}")
            if proxy_info["has_update"]:
                self.lbl_proxy_status.setText("🔥 发现新版本！")
                self.lbl_proxy_status.setProperty("class", "BadgeWarn")
                self.log(f"[antigravity-proxy] 发现新版本: {lat_ver}")
            else:
                self.lbl_proxy_status.setText("✓ 已是最新")
                self.lbl_proxy_status.setProperty("class", "BadgePass")
                self.log(f"[antigravity-proxy] 当前已是最新版本 ({lat_ver})")

        # 处理 Loc 卡片
        if loc_info["error"]:
            self.lbl_loc_new.setText(f"线上最新: 查询失败 ({loc_info['error']})")
            self.lbl_loc_status.setText("网络异常")
            self.lbl_loc_status.setProperty("class", "BadgeFail")
            self.log(f"[antigravity2-cn] 查询错误: {loc_info['error']}")
        else:
            lat_sha = loc_info["latest_sha"] or "最新"
            self.lbl_loc_new.setText(f"线上最新: {lat_sha} ({loc_info['commit_message']})")
            if loc_info["has_update"]:
                self.lbl_loc_status.setText("🔥 发现新字典！")
                self.lbl_loc_status.setProperty("class", "BadgeWarn")
                self.log(f"[antigravity2-cn] 发现新提交字典: {lat_sha}")
            else:
                self.lbl_loc_status.setText("✓ 已是最新")
                self.lbl_loc_status.setProperty("class", "BadgePass")
                self.log(f"[antigravity2-cn] 词典当前已是最新状态 ({lat_sha})")

        self.lbl_proxy_status.style().unpolish(self.lbl_proxy_status)
        self.lbl_proxy_status.style().polish(self.lbl_proxy_status)
        self.lbl_loc_status.style().unpolish(self.lbl_loc_status)
        self.lbl_loc_status.style().polish(self.lbl_loc_status)

        if proxy_info["has_update"] or loc_info["has_update"]:
            msg = "检测到开源项目有新资源更新，点击【一键拉取全部最新资源并打包】即可同步！"
            self.update_detected_signal.emit(msg)

    def start_sync(self, sync_type="all"):
        if not self.check_result:
            proxy_data = {"latest_version": "v2.4", "download_url": "https://github.com/yuaotian/antigravity-proxy/releases/download/v2.4/antigravity-proxy-v2.4-ide-win-x64.zip"}
            loc_data = {"latest_sha": "main"}
        else:
            proxy_data = self.check_result["proxy"]
            loc_data = self.check_result["localization"]

        self.btn_sync_all.setEnabled(False)
        self.log("\n" + "=" * 50)
        self.log(f"开始同步拉取资源 ({sync_type})...")

        proxy_url = determine_effective_proxy()
        self.worker = SyncWorker(
            sync_type=sync_type,
            proxy_data=proxy_data,
            loc_data=loc_data,
            proxy_url=proxy_url
        )
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_sync_finished)
        self.worker.start()

    def on_sync_finished(self, success, msg):
        self.btn_sync_all.setEnabled(True)
        self.refresh_display()
        if success:
            QMessageBox.information(self, "同步成功", msg)
        else:
            QMessageBox.warning(self, "同步提示", f"同步过程中提示:\n{msg}")
