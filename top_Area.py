from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton


class TopArea(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个标签
        label = QLabel("本项目利用ultralytics 调用yolov8模型，实现目标检测。", self)

        label_device = QLabel("设备：")
        label_device.setObjectName("label_device")  # 全局属性

        layout_device = QHBoxLayout()
        layout_device.addWidget(label_device)
        self.radioButtonCPU = QRadioButton("CPU")
        self.radioButtonCPU.setChecked(True)
        self.radioButtonGPU = QRadioButton("GPU")
        layout_device.addWidget(self.radioButtonCPU)
        layout_device.addWidget(self.radioButtonGPU)
        layout_device.addStretch(1)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(layout_device)

        # 添加一个拉伸控件到布局中
        # layout.addStretch(1)  # 1 是拉伸因子，数值越大，拉伸空间越大
        self.setLayout(layout)
