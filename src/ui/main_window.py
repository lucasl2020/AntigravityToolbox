# -*- coding: utf-8 -*-
"""
src/ui/main_window.py
PySide6 桌面主窗口 (Fluent 2 / Apple Slate 现代明亮极简风格)
集成：4 大核心面板 (网络诊断、界面汉化、免 TUN 代理注入、开源资源热打包)
实现：秒级开窗 (Deferred Lazy Loading)
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)

from src.ui.styles import LIGHT_STYLE
from src.ui.tab_detector import TabDetector
from src.ui.tab_localizer import TabLocalizer
from src.ui.tab_injector import TabInjector
from src.ui.tab_updater import TabUpdater
from src.core.detector import get_antigravity_processes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antigravity 综合管理工具箱 (网络诊断 · 汉化管理 · 代理注入 · 在线更新)")
        self.resize(1060, 700)
        self.setMinimumSize(920, 620)
        self.setStyleSheet(LIGHT_STYLE)

        self.init_ui()

        # 延迟非核心初始化，确保界面 0.1s 瞬间绘制渲染完成
        QTimer.singleShot(400, self.deferred_init)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 侧边导航栏 (纯净浅色)
        sidebar = QFrame()
        sidebar.setObjectName("SideBar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 16)
        sb_layout.setSpacing(4)

        # 品牌 Header
        brand_frame = QFrame()
        brand_frame.setObjectName("AppBrandFrame")
        bf_layout = QVBoxLayout(brand_frame)
        bf_layout.setContentsMargins(0, 0, 0, 0)
        bf_layout.setSpacing(3)

        title_row = QHBoxLayout()
        app_title = QLabel("Antigravity")
        app_title.setObjectName("AppTitleLabel")
        title_row.addWidget(app_title)

        ver_badge = QLabel("PRO")
        ver_badge.setObjectName("AppVersionBadge")
        title_row.addWidget(ver_badge)
        title_row.addStretch()
        bf_layout.addLayout(title_row)

        app_sub = QLabel("全能管理与诊断工作台 v2.0")
        app_sub.setObjectName("AppSubTitle")
        bf_layout.addWidget(app_sub)

        sb_layout.addWidget(brand_frame)

        # 导航按钮组
        self.nav_buttons = []

        self.btn_nav_detector = QPushButton("📡  网络与代理诊断")
        self.btn_nav_detector.setProperty("class", "NavButton")
        self.btn_nav_detector.setCheckable(True)
        self.btn_nav_detector.clicked.connect(lambda: self.switch_tab(0))
        sb_layout.addWidget(self.btn_nav_detector)
        self.nav_buttons.append(self.btn_nav_detector)

        self.btn_nav_localizer = QPushButton("🌐  界面汉化管理")
        self.btn_nav_localizer.setProperty("class", "NavButton")
        self.btn_nav_localizer.setCheckable(True)
        self.btn_nav_localizer.clicked.connect(lambda: self.switch_tab(1))
        sb_layout.addWidget(self.btn_nav_localizer)
        self.nav_buttons.append(self.btn_nav_localizer)

        self.btn_nav_injector = QPushButton("⚡  免 TUN 代理注入")
        self.btn_nav_injector.setProperty("class", "NavButton")
        self.btn_nav_injector.setCheckable(True)
        self.btn_nav_injector.clicked.connect(lambda: self.switch_tab(2))
        sb_layout.addWidget(self.btn_nav_injector)
        self.nav_buttons.append(self.btn_nav_injector)

        self.btn_nav_updater = QPushButton("🔄  开源热同步与更新")
        self.btn_nav_updater.setProperty("class", "NavButton")
        self.btn_nav_updater.setCheckable(True)
        self.btn_nav_updater.clicked.connect(lambda: self.switch_tab(3))
        sb_layout.addWidget(self.btn_nav_updater)
        self.nav_buttons.append(self.btn_nav_updater)

        sb_layout.addStretch()

        # 侧边栏底部客户端状态提示
        status_box = QFrame()
        status_box.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin: 0 10px 8px 10px; padding: 7px 10px;")
        sbox_layout = QVBoxLayout(status_box)
        sbox_layout.setContentsMargins(0, 0, 0, 0)
        sbox_layout.setSpacing(3)

        lbl_box_title = QLabel("💻 客户端本地状态")
        lbl_box_title.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
        sbox_layout.addWidget(lbl_box_title)

        self.lbl_proc_status = QLabel("⚪ 检测中...")
        self.lbl_proc_status.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 500;")
        sbox_layout.addWidget(self.lbl_proc_status)
        sb_layout.addWidget(status_box)

        main_layout.addWidget(sidebar)

        # 2. 右侧主内容区域
        content_area = QWidget()
        ca_layout = QVBoxLayout(content_area)
        ca_layout.setContentsMargins(0, 0, 0, 0)
        ca_layout.setSpacing(0)

        # 顶部更新通知横幅 (默认隐藏)
        self.banner_frame = QFrame()
        self.banner_frame.setObjectName("UpdateBanner")
        self.banner_frame.setVisible(False)
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(12, 8, 12, 8)

        self.lbl_banner_text = QLabel("🔥 检测到开源项目有新版本/字典更新！")
        self.lbl_banner_text.setStyleSheet("color: #1d4ed8; font-weight: 600; font-size: 12px;")
        banner_layout.addWidget(self.lbl_banner_text)
        banner_layout.addStretch()

        btn_go_update = QPushButton("查看更新")
        btn_go_update.setProperty("class", "PrimaryBtn")
        btn_go_update.clicked.connect(lambda: self.switch_tab(3))
        banner_layout.addWidget(btn_go_update)

        btn_close_banner = QPushButton("✕")
        btn_close_banner.setProperty("class", "OutlineBtn")
        btn_close_banner.setFixedWidth(28)
        btn_close_banner.clicked.connect(lambda: self.banner_frame.setVisible(False))
        banner_layout.addWidget(btn_close_banner)

        ca_layout.addWidget(self.banner_frame)

        # 多面板堆叠容器
        self.stack = QStackedWidget()

        self.tab_detector = TabDetector(self)
        self.tab_localizer = TabLocalizer(self)
        self.tab_injector = TabInjector(self)
        self.tab_updater = TabUpdater(self)
        self.tab_updater.update_detected_signal.connect(self.show_update_banner)

        self.stack.addWidget(self.tab_detector)
        self.stack.addWidget(self.tab_localizer)
        self.stack.addWidget(self.tab_injector)
        self.stack.addWidget(self.stack_wrap(self.tab_updater))

        ca_layout.addWidget(self.stack, 1)

        main_layout.addWidget(content_area, 1)

        # 默认高亮选中第一项
        self.switch_tab(0)

    def stack_wrap(self, widget):
        return widget

    def deferred_init(self):
        """主窗口绘制完成后延迟触发的后台任务"""
        self.refresh_process_status()

        # 启动定时器刷新 Antigravity 运行状态
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_process_status)
        self.status_timer.start(5000)

        # 延迟 1.2 秒自动在后台向 GitHub 检查是否有更新
        QTimer.singleShot(1200, self.auto_check_updates_on_launch)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # 切换到对应标签时轻量刷新状态
        if index == 0:
            self.tab_detector.refresh_quick_metrics()
        elif index == 1:
            self.tab_localizer.refresh_status()
        elif index == 2:
            self.tab_injector.refresh_status()
        elif index == 3:
            self.tab_updater.refresh_display()

    def refresh_process_status(self):
        try:
            procs = get_antigravity_processes()
            if procs:
                pids = [str(p["pid"]) for p in procs]
                pids_str = ", ".join(pids[:5]) + ("..." if len(pids) > 5 else "")
                self.lbl_proc_status.setText(f"🟢 已启动 ({len(procs)}进程)")
                self.lbl_proc_status.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: 600;")
                self.lbl_proc_status.setToolTip(f"Antigravity 客户端正在运行\n检测到 {len(procs)} 个活跃进程\nPID: {pids_str}")
            else:
                self.lbl_proc_status.setText("⚪ 未启动")
                self.lbl_proc_status.setStyleSheet("color: #94a3b8; font-size: 11px;")
                self.lbl_proc_status.setToolTip("未检测到运行中的 Antigravity 客户端进程")
        except Exception:
            pass

    def auto_check_updates_on_launch(self):
        """打开应用时静默后台检测更新"""
        self.tab_updater.log("[启动自检] 正在检测开源项目是否有新版本或字典...")
        self.tab_updater.check_updates_now()

    def show_update_banner(self, message):
        self.lbl_banner_text.setText(f"🔥 {message}")
        self.banner_frame.setVisible(True)
