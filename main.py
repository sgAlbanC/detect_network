import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from top_Area import TopArea
from middle_Area import MiddleArea
from bottom_Area import BottomArea
from PyQt5.QtGui import QFont

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle("PyQt Main Window")

        # 创建布局
        layout = QVBoxLayout()

        # 导入各个区域的组件
        self.top_area = TopArea()
        self.middle_area = MiddleArea()
        self.middle_area.setFixedHeight(360)  # 设置固定高度
        self.bottom_area = BottomArea()

        # 添加组件到布局
        layout.addWidget(self.top_area)
        layout.addWidget(self.middle_area)
        layout.addWidget(self.bottom_area)

        # 设置主窗口布局
        self.setLayout(layout)
        # 调整窗口大小以适应内容
        self.resize(self.sizeHint())  # 使用控件的建议大小


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置全局字体：例如设置字体为 Arial，大小为 14px，粗体
    # font = QFont("SimSun")  # 可以设置字体、大小、样式
    font = QFont("Times New Roman")
    app.setFont(font)  # 设置全局字体

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
