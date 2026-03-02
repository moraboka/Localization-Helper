import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QPushButton, QListWidget,
    QLabel, QFrame
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QFont

# ─── 主题定义 ───────────────────────────────────────────────────────────────────
THEMES = {
    "淡灰色": {
        "bg":           "#EFEFEF",
        "sidebar_bg":   "#E0E0E0",
        "sidebar_sel":  "#BDBDBD",
        "sidebar_text": "#212121",
        "panel_bg":     "#F5F5F5",
        "input_bg":     "#FFFFFF",
        "input_border": "#CFCFCF",
        "text_color":   "#212121",
        "status_color": "#757575",
        "btn_bg":       "#2ecc71",
        "btn_text":     "#FFFFFF",
        "settings_bg":  "#E8E8E8",
        "settings_btn": "#BDBDBD",
        "theme_btn_border": "#AAAAAA",
    },
    "淡粉色": {
        "bg":           "#FCE4EC",
        "sidebar_bg":   "#F8BBD0",
        "sidebar_sel":  "#F48FB1",
        "sidebar_text": "#880E4F",
        "panel_bg":     "#FFF0F3",
        "input_bg":     "#FFFFFF",
        "input_border": "#F48FB1",
        "text_color":   "#880E4F",
        "status_color": "#C2185B",
        "btn_bg":       "#E91E8C",
        "btn_text":     "#FFFFFF",
        "settings_bg":  "#FBCDD8",
        "settings_btn": "#F48FB1",
        "theme_btn_border": "#C2185B",
    },
    "白色": {
        "bg":           "#FFFFFF",
        "sidebar_bg":   "#F7F7F7",
        "sidebar_sel":  "#E3E3E3",
        "sidebar_text": "#222222",
        "panel_bg":     "#FAFAFA",
        "input_bg":     "#FFFFFF",
        "input_border": "#DDDDDD",
        "text_color":   "#222222",
        "status_color": "#888888",
        "btn_bg":       "#2ecc71",
        "btn_text":     "#FFFFFF",
        "settings_bg":  "#F0F0F0",
        "settings_btn": "#DDDDDD",
        "theme_btn_border": "#BBBBBB",
    },
    "黑色": {
        "bg":           "#1E1E1E",
        "sidebar_bg":   "#252526",
        "sidebar_sel":  "#37373D",
        "sidebar_text": "#CCCCCC",
        "panel_bg":     "#1E1E1E",
        "input_bg":     "#2D2D2D",
        "input_border": "#3C3C3C",
        "text_color":   "#D4D4D4",
        "status_color": "#858585",
        "btn_bg":       "#0E7A0D",
        "btn_text":     "#FFFFFF",
        "settings_bg":  "#2A2A2A",
        "settings_btn": "#3E3E3E",
        "theme_btn_border": "#555555",
    },
}

THEME_SWATCH = {
    "淡灰色": "#EFEFEF",
    "淡粉色": "#FCE4EC",
    "白色":   "#FFFFFF",
    "黑色":   "#1E1E1E",
}


# ─── 圆角容器 (paintEvent 绘制圆角背景) ──────────────────────────────────────────
class RoundedWidget(QWidget):
    def __init__(self, radius=16, color="#FFFFFF", parent=None):
        super().__init__(parent)
        self._radius = radius
        self._color = QColor(color)

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self._radius, self._radius)
        painter.fillPath(path, self._color)


# ─── 主窗口 ──────────────────────────────────────────────────────────────────────
class LocalizationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("L10n 本地化增强工具")
        self.resize(960, 620)

        # 去掉系统边框 + 背景透明 → 实现圆角
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._current_theme = "淡灰色"
        self._drag_pos = None
        self._settings_visible = False

        self._build_ui()
        self._apply_theme(self._current_theme)

    # ── 拖动支持 ────────────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── 构建 UI ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # 最外层圆角容器
        self.root = RoundedWidget(radius=16, color="#EFEFEF")
        self.setCentralWidget(self.root)


        root_layout = QHBoxLayout(self.root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Settings 侧边栏 (初始隐藏) ──
        self.settings_panel = self._build_settings_panel()
        root_layout.addWidget(self.settings_panel)

        # ── Setting 图标按钮列 ──
        self.icon_col = QWidget()
        self.icon_col.setFixedWidth(44)
        icon_col_layout = QVBoxLayout(self.icon_col)
        icon_col_layout.setContentsMargins(4, 12, 4, 12)
        icon_col_layout.setSpacing(0)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setFont(QFont("Segoe UI", 16))
        self.settings_btn.setToolTip("主题设置")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self._toggle_settings)
        icon_col_layout.addWidget(self.settings_btn, alignment=Qt.AlignHCenter)
        icon_col_layout.addStretch()

        # 关闭按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setFont(QFont("Segoe UI", 11))
        self.close_btn.setToolTip("关闭")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        icon_col_layout.addWidget(self.close_btn, alignment=Qt.AlignHCenter)

        root_layout.addWidget(self.icon_col)

        # ── 功能列表 sidebar ──
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(190)
        self.sidebar.addItems([
            "单反斜杠 → 双反斜杠",
            "移除多余空格",
            "全角标点转半角",
            "自定义替换",
        ])
        self.sidebar.setCurrentRow(0)
        root_layout.addWidget(self.sidebar)

        # ── 主内容区 ──
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)

        # 文本框行
        text_row = QHBoxLayout()
        text_row.setSpacing(8)

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("请在此粘贴原文…")

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("处理结果将在此显示…")

        text_row.addWidget(self.input_box)
        text_row.addWidget(self.output_box)
        content_layout.addLayout(text_row)

        # 底部栏
        bottom_row = QHBoxLayout()
        self.status_label = QLabel("准备就绪")
        self.run_button = QPushButton("▶  Run (运行)")
        self.run_button.setFixedSize(130, 38)
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.clicked.connect(self.process_text)

        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()
        bottom_row.addWidget(self.run_button)
        content_layout.addLayout(bottom_row)

        root_layout.addWidget(content_widget, stretch=1)

    def _build_settings_panel(self):
        panel = QWidget()
        panel.setFixedWidth(0)   # 初始折叠
        panel.setMaximumWidth(160)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 16, 10, 16)
        panel_layout.setSpacing(10)

        title = QLabel("🎨  主题")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        panel_layout.addWidget(title)

        self.theme_buttons = {}
        for name, swatch in THEME_SWATCH.items():
            btn = QPushButton(f"  {name}")
            btn.setFixedHeight(34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._apply_theme(n))
            self.theme_buttons[name] = btn
            panel_layout.addWidget(btn)

        panel_layout.addStretch()
        self.settings_panel = panel
        return panel

    # ── Settings 面板滑入/滑出 ────────────────────────────────────────────────
    def _toggle_settings(self):
        self._settings_visible = not self._settings_visible
        target_w = 150 if self._settings_visible else 0

        self._anim = QPropertyAnimation(self.settings_panel, b"minimumWidth")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim.setStartValue(self.settings_panel.minimumWidth())
        self._anim.setEndValue(target_w)
        self._anim.start()

        self._anim2 = QPropertyAnimation(self.settings_panel, b"maximumWidth")
        self._anim2.setDuration(220)
        self._anim2.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim2.setStartValue(self.settings_panel.maximumWidth())
        self._anim2.setEndValue(target_w if target_w else 0)
        self._anim2.start()

    # ── 主题应用 ──────────────────────────────────────────────────────────────
    def _apply_theme(self, name: str):
        self._current_theme = name
        t = THEMES[name]

        # 更新圆角背景色
        self.root.set_color(t["bg"])

        # 更新 theme 按钮选中状态
        for btn_name, btn in self.theme_buttons.items():
            btn.setChecked(btn_name == name)

        # 整体样式表
        qss = f"""
        /* ── 根容器 ── */
        QWidget {{
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
            font-size: 13px;
            color: {t["text_color"]};
        }}

        /* ── icon 列 ── */
        #icon_col {{
            background: transparent;
        }}

        /* ── Settings 图标按钮 ── */
        QPushButton#settings_btn {{
            background: {t["settings_btn"]};
            border: none;
            border-radius: 8px;
            color: {t["sidebar_text"]};
        }}
        QPushButton#settings_btn:hover {{
            background: {t["sidebar_sel"]};
        }}

        /* ── 关闭按钮 ── */
        QPushButton#close_btn {{
            background: transparent;
            border: none;
            color: {t["status_color"]};
            border-radius: 6px;
        }}
        QPushButton#close_btn:hover {{
            background: #EF5350;
            color: white;
        }}

        /* ── Settings 面板 ── */
        QWidget#settings_panel {{
            background: {t["settings_bg"]};
            border-right: 1px solid {t["input_border"]};
        }}
        QLabel {{
            background: transparent;
            color: {t["text_color"]};
        }}

        /* ── 主题切换按钮 ── */
        QPushButton[theme="true"] {{
            background: {t["input_bg"]};
            border: 2px solid {t["theme_btn_border"]};
            border-radius: 8px;
            text-align: left;
            padding-left: 6px;
            color: {t["text_color"]};
        }}
        QPushButton[theme="true"]:hover {{
            border-color: {t["btn_bg"]};
        }}
        QPushButton[theme="true"]:checked {{
            border-color: {t["btn_bg"]};
            background: {t["sidebar_sel"]};
            font-weight: bold;
        }}

        /* ── 功能侧栏 ── */
        QListWidget {{
            background: {t["sidebar_bg"]};
            border: none;
            border-right: 1px solid {t["input_border"]};
            outline: none;
            padding: 6px 0;
            color: {t["sidebar_text"]};
        }}
        QListWidget::item {{
            padding: 10px 14px;
            border-radius: 6px;
            margin: 2px 6px;
        }}
        QListWidget::item:selected {{
            background: {t["sidebar_sel"]};
            color: {t["sidebar_text"]};
        }}
        QListWidget::item:hover {{
            background: {t["sidebar_sel"]};
        }}

        /* ── 文本框 ── */
        QTextEdit {{
            background: {t["input_bg"]};
            border: 1px solid {t["input_border"]};
            border-radius: 8px;
            padding: 8px;
            color: {t["text_color"]};
        }}

        /* ── 状态标签 ── */
        QLabel#status_label {{
            color: {t["status_color"]};
        }}

        /* ── Run 按钮 ── */
        QPushButton#run_button {{
            background: {t["btn_bg"]};
            color: {t["btn_text"]};
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 0 16px;
        }}
        QPushButton#run_button:hover {{
            opacity: 0.9;
        }}
        QPushButton#run_button:pressed {{
            padding-top: 2px;
        }}
        """
        self.root.setStyleSheet(qss)

        # 给主题按钮添加 theme 属性（用于 QSS 选择器）
        for btn in self.theme_buttons.values():
            btn.setProperty("theme", "true")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── 核心处理逻辑 ─────────────────────────────────────────────────────────
    def process_text(self):
        source_text = self.input_box.toPlainText()
        if not source_text:
            return

        current_func = self.sidebar.currentItem().text() if self.sidebar.currentItem() else ""

        if "双反斜杠" in current_func:
            result_text = source_text.replace("\\", "\\\\")
        elif "移除多余空格" in current_func:
            result_text = " ".join(source_text.split())
        elif "全角标点" in current_func:
            dic = {'，': ',', '。': '.', '！': '!', '？': '?', '；': ';', '：': ':'}
            result_text = "".join([dic.get(c, c) for c in source_text])
        else:
            result_text = source_text

        self.output_box.setPlainText(result_text)
        self.status_label.setText(f"处理完成：[{current_func}]")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LocalizationTool()

    # 给对象设置 objectName 便于 QSS 精确匹配
    window.settings_btn.setObjectName("settings_btn")
    window.close_btn.setObjectName("close_btn")
    window.icon_col.setObjectName("icon_col")
    window.settings_panel.setObjectName("settings_panel")
    window.status_label.setObjectName("status_label")
    window.run_button.setObjectName("run_button")

    # 重新应用主题（objectName 设置后需刷新）
    window._apply_theme(window._current_theme)

    window.show()
    sys.exit(app.exec())