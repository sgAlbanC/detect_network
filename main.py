import sys

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from top_Area import TopArea
from middle_Area import MiddleArea
from middle_AreaG import MiddleAreaG
from bottom_Area import BottomArea
from PyQt5.QtGui import QFont

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle("目标检测小程序")

        # 创建布局
        self.layout = QVBoxLayout()

        # 导入各个区域的组件
        self.top_area = TopArea()
        self.bottom_area = BottomArea()

        # 默认添加 normal 任务的 middle_area
        self.middle_area = MiddleArea(self.bottom_area)
        self.middle_area.setFixedHeight(360)  # 设置固定高度

        # 连接信号
        self.top_area.selectionChanged.connect(self.middle_area.update_selection)
        self.top_area.on_tasks_signal.connect(self.change_middle_area)

        # 添加组件到布局
        self.layout.addWidget(self.top_area)
        self.layout.addWidget(self.middle_area)
        self.layout.addWidget(self.bottom_area)

        # 设置主窗口布局
        self.setLayout(self.layout)
        # 调整窗口大小以适应内容
        self.resize(self.sizeHint())  # 使用控件的建议大小

    def change_middle_area(self, task):
        # 移除当前的 middle_area
        old_middle_area = self.middle_area
        self.layout.removeWidget(old_middle_area)
        old_middle_area.deleteLater()  # 删除旧的组件，释放资源

        if hasattr(self.middle_area, 'cap') and self.middle_area.cap is not None:
            self.middle_area.cancel()  # 假设A组件有停止摄像头的方法

        # 根据 task 选择不同的 middle_area
        if task == "normal":
            self.middle_area = MiddleArea(self.bottom_area)
        else:
            self.middle_area = MiddleAreaG(self.bottom_area)

        # 设置新的 middle_area
        self.middle_area.setFixedHeight(360)  # 如果需要，可以再次设置高度
        # 将新的 middle_area 插入到 top_area 和 bottom_area 之间
        self.layout.insertWidget(1, self.middle_area)  # 索引 1 是 middle_area 的位置

    def closeEvent(self, event: QEvent):
        """ 在窗口关闭时清理资源 """
        if hasattr(self.middle_area, 'cap') and self.middle_area.cap is not None:
            self.middle_area.cancel()  # 假设A组件有停止摄像头的方法
        event.accept()  # 继续关闭窗口

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置全局字体：例如设置字体为 Arial，大小为 14px，粗体
    font = QFont("Times New Roman")
    app.setFont(font)  # 设置全局字体

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
