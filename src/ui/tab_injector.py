# -*- coding: utf-8 -*-
"""
src/ui/tab_injector.py
Antigravity 强制代理注入与管理面板（基于 yuaotian/antigravity-proxy，集成 Mac 风格终端）
"""

import os
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QSpinBox, QCheckBox, QMessageBox
)
from src.core.injector import (
    get_injector_status, inject_proxy, uninstall_proxy
)
from src.core.detector import get_listening_proxy_ports, get_registry_proxy
from src.ui.widgets.terminal_box import TerminalBox


class InjectorWorker(QThread):
    """后台执行代理注入或卸载的线程"""
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, action="inject", proxy_type="socks5", host="127.0.0.1", port=7897, restart_after=False):
        super().__init__()
        self.action = action
        self.proxy_type = proxy_type
        self.host = host
        self.port = port
        self.restart_after = restart_after

    def run(self):
        def callback(msg):
            self.log_signal.emit(str(msg))

        try:
            if self.action == "inject":
                inject_proxy(
                    proxy_type=self.proxy_type,
                    host=self.host,
                    port=self.port,
                    restart_after=self.restart_after,
                    callback=callback
                )
                self.finished_signal.emit(True, "免 TUN 强制代理已成功注入并生效！")
            elif self.action == "uninstall":
                uninstall_proxy(
                    restart_after=self.restart_after,
                    callback=callback
                )
                self.finished_signal.emit(True, "代理注入已成功卸载，Antigravity 恢复默认网络环境。")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class TabInjector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
        self.refresh_status()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # 1. 顶部状态概览卡片
        status_card = QFrame()
        status_card.setProperty("class", "CardFrame")
        sc_layout = QVBoxLayout(status_card)
        sc_layout.setContentsMargins(16, 12, 16, 12)
        sc_layout.setSpacing(6)

        head_layout = QHBoxLayout()
        card_title = QLabel("⚡ 免 TUN 强制代理注入状态")
        card_title.setProperty("class", "CardTitle")
        head_layout.addWidget(card_title)
        head_layout.addStretch()

        self.badge_status = QLabel("检测中...")
        self.badge_status.setProperty("class", "BadgeInfo")
        head_layout.addWidget(self.badge_status)
        sc_layout.addLayout(head_layout)

        self.lbl_info = QLabel("当前注入参数: --")
        self.lbl_info.setStyleSheet("color: #475569; font-size: 12px;")
        self.lbl_processes = QLabel("拦截进程: Antigravity.exe, language_server_windows_x64.exe, node.exe")
        self.lbl_processes.setStyleSheet("color: #64748b; font-size: 11px;")
        sc_layout.addWidget(self.lbl_info)
        sc_layout.addWidget(self.lbl_processes)

        layout.addWidget(status_card)

        # 2. 代理参数配置卡片
        cfg_card = QFrame()
        cfg_card.setProperty("class", "CardFrame")
        cc_layout = QVBoxLayout(cfg_card)
        cc_layout.setContentsMargins(16, 12, 16, 12)
        cc_layout.setSpacing(10)

        cc_title = QLabel("🛠 注入代理通道配置")
        cc_title.setProperty("class", "CardTitle")
        cc_layout.addWidget(cc_title)

        form_layout = QHBoxLayout()
        form_layout.setSpacing(8)

        lbl_proto = QLabel("代理协议:")
        lbl_proto.setStyleSheet("font-weight: 600; color: #475569;")
        form_layout.addWidget(lbl_proto)

        self.combo_proto = QComboBox()
        self.combo_proto.addItems(["SOCKS5", "HTTP"])
        form_layout.addWidget(self.combo_proto)

        lbl_host = QLabel("主机:")
        lbl_host.setStyleSheet("font-weight: 600; color: #475569;")
        form_layout.addWidget(lbl_host)

        self.txt_host = QLineEdit("127.0.0.1")
        form_layout.addWidget(self.txt_host)

        lbl_port = QLabel("端口:")
        lbl_port.setStyleSheet("font-weight: 600; color: #475569;")
        form_layout.addWidget(lbl_port)

        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(7897)
        form_layout.addWidget(self.spin_port)

        self.btn_auto_fill = QPushButton("⚡ 填入活跃端口")
        self.btn_auto_fill.setProperty("class", "OutlineBtn")
        self.btn_auto_fill.clicked.connect(self.auto_fill_detected_port)
        form_layout.addWidget(self.btn_auto_fill)

        cc_layout.addLayout(form_layout)

        self.chk_restart = QCheckBox("操作完成后自动启动 / 重启 Antigravity 客户端")
        self.chk_restart.setChecked(True)
        cc_layout.addWidget(self.chk_restart)

        layout.addWidget(cfg_card)

        # 3. 操作按钮卡片
        act_card = QFrame()
        act_card.setProperty("class", "CardFrame")
        ac_layout = QHBoxLayout(act_card)
        ac_layout.setContentsMargins(14, 10, 14, 10)
        ac_layout.setSpacing(10)

        self.btn_inject = QPushButton("🚀 一键注入免 TUN 代理")
        self.btn_inject.setProperty("class", "PrimaryBtn")
        self.btn_inject.clicked.connect(self.on_inject_clicked)
        ac_layout.addWidget(self.btn_inject)

        self.btn_uninstall = QPushButton("🗑 一键卸载代理 (恢复默认)")
        self.btn_uninstall.setProperty("class", "DangerBtn")
        self.btn_uninstall.clicked.connect(self.on_uninstall_clicked)
        ac_layout.addWidget(self.btn_uninstall)

        self.btn_open_cfg = QPushButton("📄 查看 config.json")
        self.btn_open_cfg.setProperty("class", "OutlineBtn")
        self.btn_open_cfg.clicked.connect(self.open_config_file)
        ac_layout.addWidget(self.btn_open_cfg)

        self.btn_open_dir = QPushButton("📂 打开安装目录")
        self.btn_open_dir.setProperty("class", "OutlineBtn")
        self.btn_open_dir.clicked.connect(self.open_app_dir)
        ac_layout.addWidget(self.btn_open_dir)

        layout.addWidget(act_card)

        # 4. Mac 风格精致日志控制台
        self.terminal = TerminalBox(title="代理注入引擎日志")
        self.terminal.setMinimumHeight(150)
        layout.addWidget(self.terminal, 1)

    def log(self, text):
        self.terminal.append(text)

    def refresh_status(self):
        info = get_injector_status()
        if not info["installed"]:
            self.badge_status.setText("未安装 Antigravity")
            self.badge_status.setProperty("class", "BadgeFail")
            self.lbl_info.setText("当前状态: 默认目录未找到 Antigravity.exe")
            self.btn_inject.setEnabled(False)
            self.btn_uninstall.setEnabled(False)
        else:
            self.btn_inject.setEnabled(True)
            self.btn_uninstall.setEnabled(True)

            if info["is_injected"]:
                self.badge_status.setText(f"已注入免 TUN 代理 ({info.get('version', 'v2.4')})")
                self.badge_status.setProperty("class", "BadgePass")
                self.lbl_info.setText(
                    f"代理配置: {info['proxy_type'].upper()}://{info['host']}:{info['port']} "
                    f"(DLL 大小: {round(info['dll_size']/1024, 1)} KB)"
                )
                idx = self.combo_proto.findText(info["proxy_type"].upper())
                if idx >= 0:
                    self.combo_proto.setCurrentIndex(idx)
                self.txt_host.setText(str(info["host"]))
                self.spin_port.setValue(int(info["port"]))
            else:
                self.badge_status.setText("未注入 (默认直连/系统代理)")
                self.badge_status.setProperty("class", "BadgeInfo")
                self.lbl_info.setText("当前状态: 原生直连，尚未注入 version.dll 进程劫持代理")
                # 自动探测并填入本机当前活跃的代理端口
                if not getattr(self, '_initial_port_set', False):
                    self._initial_port_set = True
                    self.auto_fill_detected_port()


        self.badge_status.style().unpolish(self.badge_status)
        self.badge_status.style().polish(self.badge_status)

    def auto_fill_detected_port(self):
        ports = get_listening_proxy_ports()
        if ports:
            p = ports[0]["port"]
            self.spin_port.setValue(p)
            self.log(f"[自动探测] 已填入活跃端口: {p} (进程: {ports[0]['process_name']})")
            return

        reg = get_registry_proxy()
        if reg["enabled"] and ":" in reg["server"]:
            try:
                p = int(reg["server"].split(":")[-1])
                self.spin_port.setValue(p)
                self.log(f"[系统配置] 已填入系统代理端口: {p}")
                return
            except Exception:
                pass

        self.log("[提示] 未检测到本地活跃代理端口，保持当前设置。")

    def on_inject_clicked(self):
        proto = self.combo_proto.currentText().lower()
        host = self.txt_host.text().strip() or "127.0.0.1"
        port = self.spin_port.value()
        restart = self.chk_restart.isChecked()

        self.set_buttons_enabled(False)
        self.log("\n" + "=" * 50)
        self.log(f"开始执行免 TUN 代理注入 ({proto}://{host}:{port})...")

        self.worker = InjectorWorker(
            action="inject",
            proxy_type=proto,
            host=host,
            port=port,
            restart_after=restart
        )
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def on_uninstall_clicked(self):
        reply = QMessageBox.question(
            self,
            "确认卸载",
            "是否确认卸载免 TUN 代理？\n这将移除 version.dll 劫持模块，使 Antigravity 恢复默认网络机制。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        restart = self.chk_restart.isChecked()
        self.set_buttons_enabled(False)
        self.log("\n" + "=" * 50)
        self.log("开始卸载免 TUN 代理注入...")

        self.worker = InjectorWorker(
            action="uninstall",
            restart_after=restart
        )
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, success, message):
        self.set_buttons_enabled(True)
        self.refresh_status()
        if success:
            QMessageBox.information(self, "操作成功", message)
        else:
            QMessageBox.critical(self, "操作失败", f"出现错误:\n{message}")

    def set_buttons_enabled(self, enabled):
        self.btn_inject.setEnabled(enabled)
        self.btn_uninstall.setEnabled(enabled)
        self.btn_open_cfg.setEnabled(enabled)
        self.btn_open_dir.setEnabled(enabled)

    def open_config_file(self):
        info = get_injector_status()
        cfg_path = info["paths"]["target_config"]
        if os.path.exists(cfg_path):
            os.system(f'notepad "{cfg_path}"')
        else:
            QMessageBox.information(self, "提示", f"配置文件尚未生成或已被归档: {cfg_path}")

    def open_app_dir(self):
        info = get_injector_status()
        app_dir = info["paths"]["install_dir"]
        if os.path.exists(app_dir):
            os.startfile(app_dir)
        else:
            QMessageBox.warning(self, "提示", f"目录不存在: {app_dir}")
