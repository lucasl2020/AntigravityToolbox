# -*- coding: utf-8 -*-
"""
src/ui/tab_localizer.py
Antigravity 界面汉化与还原管理面板（基于 qqxpee/antigravity2-cn，集成 Mac 风格终端）
"""

import os
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QRadioButton, QButtonGroup, QCheckBox, QMessageBox
)
from src.core.localizer import (
    get_localization_status, install_localization, restore_official
)
from src.ui.widgets.terminal_box import TerminalBox


class LocalizerWorker(QThread):
    """后台执行汉化或还原任务的线程"""
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, action="install", brand_title="english", use_tw=False, restart_after=False):
        super().__init__()
        self.action = action
        self.brand_title = brand_title
        self.use_tw = use_tw
        self.restart_after = restart_after

    def run(self):
        def callback(msg):
            self.log_signal.emit(str(msg))

        try:
            if self.action == "install":
                install_localization(
                    brand_title=self.brand_title,
                    use_tw=self.use_tw,
                    restart_after=self.restart_after,
                    callback=callback
                )
                self.finished_signal.emit(True, "中文汉化安装部署成功！")
            elif self.action == "restore":
                restore_official(
                    restart_after=self.restart_after,
                    callback=callback
                )
                self.finished_signal.emit(True, "官方英文原版已成功还原！")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class TabLocalizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
        self.refresh_status()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        # 1. 顶部状态卡片
        status_card = QFrame()
        status_card.setProperty("class", "CardFrame")
        sc_layout = QVBoxLayout(status_card)
        sc_layout.setContentsMargins(16, 12, 16, 12)
        sc_layout.setSpacing(6)

        head_layout = QHBoxLayout()
        card_title = QLabel("🌐 Antigravity 2.0 汉化运行状态")
        card_title.setProperty("class", "CardTitle")
        head_layout.addWidget(card_title)
        head_layout.addStretch()

        self.badge_status = QLabel("检测中...")
        self.badge_status.setProperty("class", "BadgeInfo")
        head_layout.addWidget(self.badge_status)
        sc_layout.addLayout(head_layout)

        self.lbl_path = QLabel("安装目录: 检测中...")
        self.lbl_path.setStyleSheet("color: #475569; font-size: 12px;")
        self.lbl_backup = QLabel("原始备份: 检测中...")
        self.lbl_backup.setStyleSheet("color: #64748b; font-size: 12px;")
        sc_layout.addWidget(self.lbl_path)
        sc_layout.addWidget(self.lbl_backup)

        layout.addWidget(status_card)

        # 2. 定制汉化选项卡片
        opt_card = QFrame()
        opt_card.setProperty("class", "CardFrame")
        oc_layout = QVBoxLayout(opt_card)
        oc_layout.setContentsMargins(16, 12, 16, 12)
        oc_layout.setSpacing(10)

        oc_title = QLabel("⚙ 汉化个性化偏好配置")
        oc_title.setProperty("class", "CardTitle")
        oc_layout.addWidget(oc_title)

        # 品牌名显示方式
        lbl_b = QLabel("左上角品牌名称显示风格:")
        lbl_b.setStyleSheet("font-weight: 600; color: #475569;")
        oc_layout.addWidget(lbl_b)

        brand_layout = QHBoxLayout()
        self.bg_brand = QButtonGroup(self)
        self.rb_brand_en = QRadioButton("保留 Antigravity 原英文名 (推荐)")
        self.rb_brand_hide = QRadioButton("隐藏品牌名称 (更原生简洁)")
        self.rb_brand_cn = QRadioButton("完全汉化 (显示为「反重力」)")
        self.rb_brand_en.setChecked(True)

        self.bg_brand.addButton(self.rb_brand_en, 1)
        self.bg_brand.addButton(self.rb_brand_hide, 2)
        self.bg_brand.addButton(self.rb_brand_cn, 3)

        brand_layout.addWidget(self.rb_brand_en)
        brand_layout.addWidget(self.rb_brand_hide)
        brand_layout.addWidget(self.rb_brand_cn)
        brand_layout.addStretch()
        oc_layout.addLayout(brand_layout)

        # 语言字系
        lang_layout = QHBoxLayout()
        lbl_l = QLabel("语言字典选择:")
        lbl_l.setStyleSheet("font-weight: 600; color: #475569;")
        lang_layout.addWidget(lbl_l)

        self.bg_lang = QButtonGroup(self)
        self.rb_zh_cn = QRadioButton("简体中文 (zh-CN)")
        self.rb_zh_tw = QRadioButton("繁體中文 (zh-TW)")
        self.rb_zh_cn.setChecked(True)
        self.bg_lang.addButton(self.rb_zh_cn, 1)
        self.bg_lang.addButton(self.rb_zh_tw, 2)
        lang_layout.addWidget(self.rb_zh_cn)
        lang_layout.addWidget(self.rb_zh_tw)
        lang_layout.addStretch()
        oc_layout.addLayout(lang_layout)

        # 自动重启选项
        self.chk_restart = QCheckBox("操作完成后自动启动 / 重启 Antigravity 客户端")
        self.chk_restart.setChecked(True)
        oc_layout.addWidget(self.chk_restart)

        layout.addWidget(opt_card)

        # 3. 操作按钮卡片
        act_card = QFrame()
        act_card.setProperty("class", "CardFrame")
        ac_layout = QHBoxLayout(act_card)
        ac_layout.setContentsMargins(14, 10, 14, 10)
        ac_layout.setSpacing(10)

        self.btn_install = QPushButton("🚀 一键安装 / 更新中文汉化")
        self.btn_install.setProperty("class", "SuccessBtn")
        self.btn_install.clicked.connect(self.on_install_clicked)
        ac_layout.addWidget(self.btn_install)

        self.btn_restore = QPushButton("🔄 一键无痕还原官方英文原版")
        self.btn_restore.setProperty("class", "OutlineBtn")
        self.btn_restore.clicked.connect(self.on_restore_clicked)
        ac_layout.addWidget(self.btn_restore)

        self.btn_refresh = QPushButton("刷新状态")
        self.btn_refresh.setProperty("class", "OutlineBtn")
        self.btn_refresh.clicked.connect(self.refresh_status)
        ac_layout.addWidget(self.btn_refresh)

        self.btn_open_dir = QPushButton("📂 打开资源目录")
        self.btn_open_dir.setProperty("class", "OutlineBtn")
        self.btn_open_dir.clicked.connect(self.open_resources_dir)
        ac_layout.addWidget(self.btn_open_dir)

        layout.addWidget(act_card)

        # 4. Mac 风格精致日志控制台
        self.terminal = TerminalBox(title="汉化引擎工作日志")
        self.terminal.setMinimumHeight(150)
        layout.addWidget(self.terminal, 1)

    def log(self, text):
        self.terminal.append(text)

    def refresh_status(self):
        info = get_localization_status()
        paths = info["paths"]

        if not info["installed"]:
            self.badge_status.setText("未安装 Antigravity")
            self.badge_status.setProperty("class", "BadgeFail")
            self.lbl_path.setText(f"安装目录: 未在默认路径找到 ({paths['install_dir']})")
            self.lbl_backup.setText("原始备份: --")
            self.btn_install.setEnabled(False)
            self.btn_restore.setEnabled(False)
        else:
            self.lbl_path.setText(f"安装目录: {paths['install_dir']}")
            self.btn_install.setEnabled(True)
            self.btn_restore.setEnabled(True)

            if info["is_localized"]:
                self.badge_status.setText("已安装中文汉化")
                self.badge_status.setProperty("class", "BadgePass")
            else:
                self.badge_status.setText("官方英文原版")
                self.badge_status.setProperty("class", "BadgeInfo")

            bak_str = "已就绪 (app.asar.bak)" if info["has_backup"] else "未生成 (首次汉化将自动生成)"
            self.lbl_backup.setText(f"官方原始包备份: {bak_str}")

        self.badge_status.style().unpolish(self.badge_status)
        self.badge_status.style().polish(self.badge_status)

    def on_install_clicked(self):
        brand_val = "english"
        if self.rb_brand_hide.isChecked():
            brand_val = "hidden"
        elif self.rb_brand_cn.isChecked():
            brand_val = "translated"

        use_tw = self.rb_zh_tw.isChecked()
        restart = self.chk_restart.isChecked()

        self.set_buttons_enabled(False)
        self.log("\n" + "=" * 50)
        self.log("开始执行 Antigravity 中文汉化注入...")

        self.worker = LocalizerWorker(
            action="install",
            brand_title=brand_val,
            use_tw=use_tw,
            restart_after=restart
        )
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def on_restore_clicked(self):
        reply = QMessageBox.question(
            self,
            "确认还原",
            "是否确认将 Antigravity 还原为官方纯英文原版？\n这将恢复原始的 app.asar 文件并重启客户端。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply != QMessageBox.Yes:
            return

        restart = self.chk_restart.isChecked()
        self.set_buttons_enabled(False)
        self.log("\n" + "=" * 50)
        self.log("开始执行 Antigravity 官方英文还原...")

        self.worker = LocalizerWorker(
            action="restore",
            restart_after=restart
        )
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, success, message):
        self.set_buttons_enabled(True)
        self.refresh_status()
        if success:
            QMessageBox.information(self, "操作完成", message)
        else:
            QMessageBox.critical(self, "操作失败", f"出现错误:\n{message}")

    def set_buttons_enabled(self, enabled):
        self.btn_install.setEnabled(enabled)
        self.btn_restore.setEnabled(enabled)
        self.btn_refresh.setEnabled(enabled)

    def open_resources_dir(self):
        info = get_localization_status()
        res_dir = info["paths"]["resources_dir"]
        if os.path.exists(res_dir):
            os.startfile(res_dir)
        else:
            QMessageBox.warning(self, "提示", f"目录不存在: {res_dir}")
