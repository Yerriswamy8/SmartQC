APP_STYLE = """
QMainWindow, QWidget { background: #111827; color: #e5e7eb; font-family: Segoe UI; font-size: 10pt; }
QTabWidget::pane { border: 1px solid #374151; background: #111827; }
QTabBar::tab { background: #1f2937; color: #d1d5db; padding: 10px 18px; margin-right: 2px; }
QTabBar::tab:selected { background: #2563eb; color: white; }
QGroupBox { border: 1px solid #374151; border-radius: 6px; margin-top: 12px; padding-top: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QLineEdit, QComboBox, QTextEdit, QSpinBox { background: #0f172a; border: 1px solid #475569; border-radius: 4px; padding: 6px; color: #f8fafc; }
QPushButton { background: #2563eb; border: none; border-radius: 5px; padding: 7px 12px; color: white; font-weight: 600; }
QPushButton:hover { background: #1d4ed8; }
QPushButton:disabled { background: #4b5563; }
QTableWidget { background: #0f172a; alternate-background-color: #182235; gridline-color: #374151; }
QHeaderView::section { background: #1f2937; color: #f3f4f6; padding: 7px; border: 0; }
QLabel#MetricValue { font-size: 24px; font-weight: 800; color: #60a5fa; }
QLabel#StatusGood { color: #34d399; font-weight: 800; font-size: 18px; }
QLabel#StatusDefect { color: #f87171; font-weight: 800; font-size: 18px; }
"""
