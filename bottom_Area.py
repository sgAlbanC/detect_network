from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class BottomArea(QWidget):

    def __init__(self):
        super().__init__()
        self.layout_operator = QHBoxLayout()
        self.label_logs = QLabel("日志:")
        self.pushButton_clear = QPushButton('清除')
        self.pushButton_clear.clicked.connect(self.clear_logs)
        self.layout_operator.addWidget(self.label_logs)
        self.layout_operator.addWidget(self.pushButton_clear)
        self.layout_operator.addStretch(1)

        self.edit_logs = QTextBrowser()
        self.edit_logs.setReadOnly(True)
        self.edit_logs.setFixedHeight(150)
        font = QFont("宋体", 11)  # 设置字体为 "宋体"，大小为11
        self.edit_logs.setFont(font)  # 应用字体设置到 QTextBrowser 控件

        self.edit_logs.setStyleSheet("""
            background-color: white;
            border: none;
        """)
        self.edit_logs.setMaximumWidth(900)

        # 设置布局
        layout = QVBoxLayout()
        layout.addLayout(self.layout_operator)
        layout.addWidget(self.edit_logs)
        layout.addStretch(1)
        self.setLayout(layout)

    def update_logs(self, log_message):
        self.edit_logs.append(log_message)

    def clear_logs(self):
        self.edit_logs.clear()
