# -*- coding: utf-8 -*-
"""
src/ui/styles.py
现代极简明亮浅色主题 (Modern Clean Light Theme - Fluent 2 & Apple Clean Slate 风格)
特点：
- 严格全浅色系，清爽通透，摒弃厚重暗黑元素
- 现代化卡片式层级，10-12px 优雅微圆角
- 柔和精致的边框交互 (#e2e8f0 -> #cbd5e1 -> #2563eb)
- 鲜明直观的状态药丸胶囊微标 (Badge)
"""

LIGHT_STYLE = """
/* 全局基础设置 */
QWidget {
    background-color: #f8fafc;
    color: #334155;
    font-family: "Segoe UI", "Microsoft YaHei UI", -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

/* 主窗口容器 */
QMainWindow {
    background-color: #f8fafc;
}

/* 侧边栏导航面板 */
#SideBar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
    min-width: 215px;
    max-width: 235px;
}

#AppBrandFrame {
    padding: 16px 14px 10px 14px;
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 10px;
}

#AppTitleLabel {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
}

#AppSubTitle {
    font-size: 11px;
    color: #64748b;
    padding-top: 2px;
}

#AppVersionBadge {
    background-color: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 9px;
    font-size: 10px;
    font-weight: 700;
    padding: 1px 6px;
}

/* 侧边栏导航按钮 */
QPushButton.NavButton {
    background-color: transparent;
    color: #475569;
    text-align: left;
    padding: 11px 16px;
    border: 1px solid transparent;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    margin: 2px 10px;
}

QPushButton.NavButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QPushButton.NavButton:checked {
    background-color: #eff6ff;
    color: #2563eb;
    font-weight: 700;
    border: 1px solid #bfdbfe;
}

/* 现代化卡片容器 */
QFrame.CardFrame {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
}

QFrame.CardFrame:hover {
    border: 1px solid #cbd5e1;
}

/* 现代化指标统计卡片 (StatCard) */
QFrame.StatCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QFrame.StatCard:hover {
    border: 1px solid #cbd5e1;
}

/* 标题样式 */
QLabel.CardTitle {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    padding-bottom: 2px;
}

QLabel.SectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    padding: 4px 0;
}

/* 药丸徽章 Badge 样式 */
QLabel.BadgePass {
    background-color: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
    border-radius: 10px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.BadgeWarn {
    background-color: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
    border-radius: 10px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.BadgeFail {
    background-color: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

QLabel.BadgeInfo {
    background-color: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

/* 按钮通用精致化样式 */
QPushButton.PrimaryBtn {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryBtn:hover {
    background-color: #1d4ed8;
}

QPushButton.PrimaryBtn:pressed {
    background-color: #1e40af;
}

QPushButton.PrimaryBtn:disabled {
    background-color: #94a3b8;
    color: #f8fafc;
}

QPushButton.SuccessBtn {
    background-color: #16a34a;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.SuccessBtn:hover {
    background-color: #15803d;
}

QPushButton.SuccessBtn:pressed {
    background-color: #166534;
}

QPushButton.SuccessBtn:disabled {
    background-color: #94a3b8;
    color: #f8fafc;
}

QPushButton.DangerBtn {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.DangerBtn:hover {
    background-color: #b91c1c;
}

QPushButton.DangerBtn:pressed {
    background-color: #991b1b;
}

QPushButton.DangerBtn:disabled {
    background-color: #94a3b8;
    color: #f8fafc;
}

QPushButton.OutlineBtn {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 15px;
    font-weight: 500;
    font-size: 12px;
}

QPushButton.OutlineBtn:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
}

QPushButton.OutlineBtn:pressed {
    background-color: #e2e8f0;
}

QPushButton.OutlineBtn:disabled {
    color: #cbd5e1;
    border-color: #e2e8f0;
}

/* 输入控件与下拉框 */
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 12px;
    color: #0f172a;
    font-size: 13px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #2563eb;
    background-color: #ffffff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

/* 核心端点表格 */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    selection-background-color: #eff6ff;
    selection-color: #1e3a8a;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 12px;
}

/* 单选框与复选框 */
QRadioButton, QCheckBox {
    color: #334155;
    font-size: 13px;
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #cbd5e1;
    background: #ffffff;
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* 顶部更新横幅 */
#UpdateBanner {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 10px 16px;
    margin: 12px 18px 0px 18px;
}
"""
