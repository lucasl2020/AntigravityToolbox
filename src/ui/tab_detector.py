# -*- coding: utf-8 -*-
"""
src/ui/tab_detector.py
网络与代理连通性检测面板 (现代明亮浅色主题 - 集成 4 大指标卡与 Mac 风格终端)
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QCheckBox, QApplication
)

from src.core.detector import run_full_diagnosis, determine_effective_proxy
from src.core.localizer import get_localization_status
from src.core.injector import get_injector_status
from src.ui.widgets.stat_card import StatCard
from src.ui.widgets.terminal_box import TerminalBox


class DiagnosisWorker(QThread):
    """后台异步诊断线程，避免阻塞 UI 界面"""
    step_signal = Signal(str, object)
    finished_signal = Signal(dict)

    def __init__(self, custom_proxy=None, force_direct=False, timeout=6):
        super().__init__()
        self.custom_proxy = custom_proxy
        self.force_direct = force_direct
        self.timeout = timeout

    def run(self):
        def callback(event_type, data):
            self.step_signal.emit(event_type, data)

        report = run_full_diagnosis(
            custom_proxy=self.custom_proxy,
            force_direct=self.force_direct,
            timeout=self.timeout,
            callback=callback
        )
        self.finished_signal.emit(report)


class TabDetector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # 1. 顶部 4 大核心指标卡片组 (Stat Cards)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card_proxy = StatCard(
            icon="🛰️",
            title="代理通道",
            value="检测中...",
            subtext="系统 / 环境变量 / 活跃端口",
            badge_text="就绪",
            badge_type="info"
        )
        self.card_egress = StatCard(
            icon="🌍",
            title="物理出口 / 地区",
            value="--",
            subtext="等待发起网络探测",
            badge_text="待探测",
            badge_type="gray"
        )
        self.card_loc = StatCard(
            icon="🇨🇳",
            title="界面汉化状态",
            value="检测中...",
            subtext="app.asar 增强包",
            badge_text="检测中",
            badge_type="info"
        )
        self.card_inj = StatCard(
            icon="⚡",
            title="免 TUN 注入状态",
            value="检测中...",
            subtext="version.dll 拦截劫持",
            badge_text="检测中",
            badge_type="info"
        )

        cards_layout.addWidget(self.card_proxy)
        cards_layout.addWidget(self.card_egress)
        cards_layout.addWidget(self.card_loc)
        cards_layout.addWidget(self.card_inj)
        layout.addLayout(cards_layout)

        # 2. 控制栏操作卡片
        ctrl_card = QFrame()
        ctrl_card.setProperty("class", "CardFrame")
        cc_layout = QHBoxLayout(ctrl_card)
        cc_layout.setContentsMargins(14, 10, 14, 10)
        cc_layout.setSpacing(10)

        lbl_p = QLabel("测试代理:")
        lbl_p.setStyleSheet("font-weight: 600; color: #475569;")
        cc_layout.addWidget(lbl_p)

        self.txt_proxy = QLineEdit()
        self.txt_proxy.setPlaceholderText("留空自动检测本机代理，或输入如: http://127.0.0.1:7897")
        self.txt_proxy.setText(determine_effective_proxy())
        cc_layout.addWidget(self.txt_proxy, 1)

        self.chk_direct = QCheckBox("强制直连")
        cc_layout.addWidget(self.chk_direct)

        self.btn_run = QPushButton("🚀 开始全面诊断")
        self.btn_run.setProperty("class", "PrimaryBtn")
        self.btn_run.clicked.connect(self.start_diagnosis)
        cc_layout.addWidget(self.btn_run)

        self.btn_copy_env = QPushButton("📋 复制终端代理环境变量")
        self.btn_copy_env.setProperty("class", "OutlineBtn")
        self.btn_copy_env.clicked.connect(self.copy_terminal_env)
        cc_layout.addWidget(self.btn_copy_env)

        layout.addWidget(ctrl_card)

        # 3. 核心服务端点连通性表格卡片
        table_card = QFrame()
        table_card.setProperty("class", "CardFrame")
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(14, 12, 14, 12)
        tc_layout.setSpacing(8)

        tbl_head = QHBoxLayout()
        tbl_label = QLabel("Antigravity & Google 核心服务连通性矩阵")
        tbl_label.setProperty("class", "SectionTitle")
        tbl_head.addWidget(tbl_label)
        tbl_head.addStretch()

        self.lbl_overall_badge = QLabel("准备就绪")
        self.lbl_overall_badge.setProperty("class", "BadgeInfo")
        tbl_head.addWidget(self.lbl_overall_badge)
        tc_layout.addLayout(tbl_head)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["服务通道", "目标地址", "连通状态", "响应时延", "HTTP 状态"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(170)
        tc_layout.addWidget(self.table)

        # 友好技术提示条，消除用户对 404 等网关状态码的疑惑
        lbl_hint = QLabel("💡 为什么 API 网关显示 404？这类接口（generativelanguage、oauth2 等）为纯后端服务，只接收具体的 API 方法调用（如 AI 聊天），根路径不提供网页故 Google 官方统一返回 404。能收到 Google 服务器亲手签发的 404，恰恰 100% 证明网络已穿透代理直连海外，完全可以正常使用！")
        lbl_hint.setStyleSheet("color: #475569; font-size: 11px; margin-top: 5px; padding: 4px 6px; background: #f1f5f9; border-radius: 4px;")
        lbl_hint.setWordWrap(True)
        tc_layout.addWidget(lbl_hint)

        layout.addWidget(table_card, 1)

        # 4. Mac 风格精致控制台
        self.terminal = TerminalBox(title="网络诊断控制台日志")
        self.terminal.setMaximumHeight(130)
        layout.addWidget(self.terminal)

        # 填充表格初始占位行与快速刷新静态指标
        self.init_table_rows()
        self.refresh_quick_metrics()

    def init_table_rows(self):
        targets = [
            ("Google 账号体系 (OAuth/登录)", "https://accounts.google.com"),
            ("Google OAuth 令牌刷新通道", "https://oauth2.googleapis.com"),
            ("Gemini API (语言模型核心接口)", "https://generativelanguage.googleapis.com"),
            ("Google Vertex AI 企业云平台", "https://aiplatform.googleapis.com"),
            ("Antigravity 官方门户与服务", "https://antigravity.google"),
            ("Gemini 官方 Web 服务应用", "https://gemini.google.com"),
            ("GitHub API (扩展/Skills/更新)", "https://api.github.com"),
            ("npm 官方镜像 (前端扩展源)", "https://registry.npmjs.org")
        ]
        self.table.setRowCount(len(targets))
        for row, (name, url) in enumerate(targets):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(url))
            self.table.setItem(row, 2, QTableWidgetItem("待检测"))
            self.table.setItem(row, 3, QTableWidgetItem("--"))
            self.table.setItem(row, 4, QTableWidgetItem("--"))

    def refresh_quick_metrics(self):
        """轻量级读取本地汉化与注入状态，瞬间刷新卡片"""
        try:
            eff = determine_effective_proxy()
            if eff:
                self.card_proxy.set_value(eff.replace("http://", "").replace("socks5://", ""))
                self.card_proxy.set_subtext("当前有效代理通道")
                self.card_proxy.set_badge("活跃", "pass")
            else:
                self.card_proxy.set_value("直连模式")
                self.card_proxy.set_subtext("未检测到本地代理")
                self.card_proxy.set_badge("直连", "warn")

            loc_info = get_localization_status()
            if loc_info["installed"]:
                if loc_info["is_localized"]:
                    self.card_loc.set_value("已汉化 (zh-CN)")
                    self.card_loc.set_badge("就绪", "pass")
                else:
                    self.card_loc.set_value("英文原版")
                    self.card_loc.set_badge("官方", "info")
            else:
                self.card_loc.set_value("未安装客户端")
                self.card_loc.set_badge("未找到", "fail")

            inj_info = get_injector_status()
            if inj_info["installed"]:
                if inj_info["is_injected"]:
                    self.card_inj.set_value(f"已注入 ({inj_info.get('version', 'v2.4')})")
                    self.card_inj.set_subtext(f"{inj_info['proxy_type'].upper()}://{inj_info['host']}:{inj_info['port']}")
                    self.card_inj.set_badge("生效中", "pass")
                else:
                    self.card_inj.set_value("未注入")
                    self.card_inj.set_subtext("原生直连 / 外部代理")
                    self.card_inj.set_badge("默认", "info")
            else:
                self.card_inj.set_value("未安装客户端")
                self.card_inj.set_badge("未找到", "fail")
        except Exception as e:
            self.terminal.append(f"[警告] 读取初始状态异常: {e}")

    def log(self, text):
        self.terminal.append(text)

    def start_diagnosis(self):
        proxy = self.txt_proxy.text().strip()
        force_direct = self.chk_direct.isChecked()

        self.btn_run.setEnabled(False)
        self.btn_run.setText("⏳ 正在诊断中...")
        self.lbl_overall_badge.setText("诊断中...")
        self.lbl_overall_badge.setProperty("class", "BadgeWarn")
        self.lbl_overall_badge.style().unpolish(self.lbl_overall_badge)
        self.lbl_overall_badge.style().polish(self.lbl_overall_badge)

        self.log("\n" + "=" * 50)
        self.log(f"开始网络诊断 (代理: {proxy if not force_direct else '直连模式'})...")

        self.worker = DiagnosisWorker(custom_proxy=proxy, force_direct=force_direct)
        self.worker.step_signal.connect(self.on_step)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def on_step(self, event_type, data):
        if event_type == "egress_done":
            ip = data.get("ip", "未知")
            loc = data.get("loc_friendly", "未知")
            msg = data.get("region_msg", "")
            lvl = data.get("region_level", "pass")

            self.card_egress.set_value(ip)
            self.card_egress.set_subtext(f"{loc} ({msg})")
            b_type = "pass" if lvl == "pass" else ("warn" if lvl == "warning" else "fail")
            self.card_egress.set_badge(data.get("loc", "出口"), b_type)

            self.log(f"出口 IP 探测完成: {ip} | 地区: {loc} ({msg})")

        elif event_type == "endpoint_result":
            res = data
            for row in range(self.table.rowCount()):
                if self.table.item(row, 1).text() == res["url"]:
                    status_text = "● 畅通 (PASS)" if res["success"] else "● 阻断 (FAIL)"
                    status_item = QTableWidgetItem(status_text)
                    status_item.setForeground(QColor("#15803d") if res["success"] else QColor("#b91c1c"))
                    self.table.setItem(row, 2, status_item)

                    lat_item = QTableWidgetItem(f"{res['latency_ms']} ms")
                    if res["latency_ms"] < 600:
                        lat_item.setForeground(QColor("#15803d"))
                    elif res["latency_ms"] < 1500:
                        lat_item.setForeground(QColor("#b45309"))
                    else:
                        lat_item.setForeground(QColor("#b91c1c"))
                    self.table.setItem(row, 3, lat_item)

                    # 格式化 HTTP 状态码与友好技术说明
                    code = res["code"]
                    if code == 200:
                        code_str = "200 (OK)"
                        code_color = QColor("#15803d")
                        code_tip = "HTTP 200 成功：服务通信正常。"
                    elif code in (301, 302, 307, 308):
                        code_str = f"{code} (重定向)"
                        code_color = QColor("#0284c7")
                        code_tip = f"HTTP {code} 重定向：已成功触达 Google 认证中心。"
                    elif code == 404:
                        code_str = "404 (网关存活)"
                        code_color = QColor("#15803d")
                        code_tip = "HTTP 404 正常：Google 核心 API 网关已正常响应。\n根路径不提供前端页面故返回 404，属于 Google 官方规范，证明网络穿透与直连完全畅通。"
                    elif code in (401, 403):
                        code_str = f"{code} (需鉴权)"
                        code_color = QColor("#15803d")
                        code_tip = f"HTTP {code} 正常：API 网关连通，需要调用者提供有效 Token/API Key。"
                    elif res["success"]:
                        code_str = f"{code} (正常)"
                        code_color = QColor("#15803d")
                        code_tip = f"HTTP {code} 正常连通"
                    else:
                        code_str = "超时/阻断" if code == 0 else f"{code} (异常)"
                        code_color = QColor("#b91c1c")
                        code_tip = f"连接失败: {res.get('error', '未知错误')}"

                    code_item = QTableWidgetItem(code_str)
                    code_item.setForeground(code_color)
                    code_item.setToolTip(code_tip)
                    self.table.setItem(row, 4, code_item)
                    break
            self.log(f"端点测试: {res['name']} -> {'通过' if res['success'] else '失败'} ({res['latency_ms']}ms)")

    def on_finished(self, report):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("🚀 重新全面诊断")

        status = report["overall_status"]
        title = report["overall_title"]
        self.lbl_overall_badge.setText(f"{title} ({report['passed_count']}/{report['total_count']})")
        badge_cls = "BadgePass" if status == "PASS" else ("BadgeWarn" if status == "WARNING" else "BadgeFail")
        self.lbl_overall_badge.setProperty("class", badge_cls)
        self.lbl_overall_badge.style().unpolish(self.lbl_overall_badge)
        self.lbl_overall_badge.style().polish(self.lbl_overall_badge)

        self.log(f"诊断完成: {report['overall_desc']}")

    def copy_terminal_env(self):
        proxy = self.txt_proxy.text().strip() or "http://127.0.0.1:7897"
        cmd = f'$env:HTTP_PROXY = "{proxy}"; $env:HTTPS_PROXY = "{proxy}"'
        QApplication.clipboard().setText(cmd)
        self.log(f"已复制 PowerShell 环境变量命令到剪贴板:\n{cmd}")
