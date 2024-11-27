from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont

class BottomArea(QWidget):
    def __init__(self):
        super().__init__()

        edit_logs = QTextEdit()
        edit_logs.setReadOnly(True)
        edit_logs.setText("日志区域")
        edit_logs.setFixedHeight(150)
        font = QFont("宋体", 11)  # 设置字体为 "宋体"，大小为12
        edit_logs.setFont(font)  # 应用字体设置到 QTextEdit 控件

        edit_logs.setStyleSheet("""
            background-color: white;
            border: none;
        """)
        edit_logs.setMaximumWidth(1000)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(edit_logs)
        layout.addStretch(1)
        self.setLayout(layout)
