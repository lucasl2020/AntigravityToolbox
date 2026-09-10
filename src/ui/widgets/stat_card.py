# -*- coding: utf-8 -*-
"""
src/ui/widgets/stat_card.py
现代化指标统计卡片 (Modern Metric Stat Card - Fluent 2 / Apple Slate 风格)
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
)


class StatCard(QFrame):
    """
    轻量高颜值状态指标卡片：
    - 顶部：图标 + 标题 + 状态圆角微型药丸胶囊 (Badge)
    - 中部：大号粗体关键数值 (Value)
    - 底部：副文本描述说明 (Subtext)
    """
    def __init__(self, icon="📊", title="指标项", value="--", subtext="", badge_text="", badge_type="info", parent=None):
        super().__init__(parent)
        self.setProperty("class", "StatCard")
        self.setObjectName("StatCardWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # 1. 顶栏：图标 + 标题 + 胶囊徽章
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setStyleSheet("font-size: 16px; background: transparent;")
        top_layout.addWidget(self.lbl_icon)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748b; background: transparent;")
        top_layout.addWidget(self.lbl_title)

        top_layout.addStretch()

        self.lbl_badge = QLabel(badge_text)
        self.lbl_badge.setVisible(bool(badge_text))
        self.set_badge(badge_text, badge_type)
        top_layout.addWidget(self.lbl_badge)

        layout.addLayout(top_layout)

        # 2. 中间：大字号核心数值
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(
            "font-size: 17px; font-weight: 700; color: #0f172a; padding-top: 2px; background: transparent;"
        )
        self.lbl_value.setWordWrap(True)
        layout.addWidget(self.lbl_value)

        # 3. 底部：辅助说明
        self.lbl_subtext = QLabel(subtext)
        self.lbl_subtext.setStyleSheet(
            "font-size: 11px; color: #94a3b8; line-height: 1.3; background: transparent;"
        )
        self.lbl_subtext.setWordWrap(True)
        layout.addWidget(self.lbl_subtext)

    def set_value(self, text):
        self.lbl_value.setText(str(text))

    def set_subtext(self, text):
        self.lbl_subtext.setText(str(text))

    def set_badge(self, text, badge_type="info"):
        if not text:
            self.lbl_badge.setVisible(False)
            return
        self.lbl_badge.setVisible(True)
        self.lbl_badge.setText(str(text))

        # 样式分类：pass (绿色), warn (橙色), fail (红色), info (蓝色), gray (灰色)
        styles = {
            "pass": "background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;",
            "warn": "background-color: #fffbeb; color: #b45309; border: 1px solid #fde68a;",
            "fail": "background-color: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;",
            "info": "background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;",
            "gray": "background-color: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0;"
        }
        chosen = styles.get(badge_type, styles["info"])
        self.lbl_badge.setStyleSheet(
            f"{chosen} border-radius: 10px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
        )
