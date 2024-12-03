from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QMessageBox, QButtonGroup
import torch  # 引入 PyTorch 库


class TopArea(QWidget):
    selectionChanged = pyqtSignal(str)

    on_tasks_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # 创建一个标签
        label = QLabel("本项目利用ultralytics 调用yolo模型，实现目标检测。")

        label_device = QLabel("设备：")
        layout_device = QHBoxLayout()
        layout_device.addWidget(label_device)

        # 创建设备选择的单选按钮
        self.radioButtonCPU = QRadioButton("CPU")
        self.radioButtonCPU.setChecked(True)
        self.radioButtonGPU = QRadioButton("GPU")

        # 添加单选按钮到布局
        layout_device.addWidget(self.radioButtonCPU)
        layout_device.addWidget(self.radioButtonGPU)
        layout_device.addStretch(1)

        layout_tasks = QHBoxLayout()
        layout_tasks.addWidget(QLabel("任务："))

        # 创建设备选择的单选按钮
        self.radio_normal = QRadioButton("普通识别")
        self.radio_normal.setChecked(True)
        self.radio_gesture = QRadioButton("手势识别")

        layout_tasks.addWidget(self.radio_normal)
        layout_tasks.addWidget(self.radio_gesture)
        layout_tasks.addStretch(1)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addLayout(layout_device)
        layout.addLayout(layout_tasks)
        self.setLayout(layout)

        # 创建两个 QButtonGroup 来管理两组独立的按钮
        self.deviceGroup = QButtonGroup(self)
        self.deviceGroup.addButton(self.radioButtonCPU)
        self.deviceGroup.addButton(self.radioButtonGPU)

        self.taskGroup = QButtonGroup(self)
        self.taskGroup.addButton(self.radio_normal)
        self.taskGroup.addButton(self.radio_gesture)

        # 连接信号槽
        self.radioButtonCPU.toggled.connect(self.on_device_changed)

        # 连接信号槽
        self.radio_normal.toggled.connect(self.on_tasks_changed)


    def on_device_changed(self):
        # 当切换设备时，检查GPU是否可用
        if self.radioButtonGPU.isChecked():
            if not torch.cuda.is_available():
                # 如果没有可用的GPU，显示警告并自动切换到CPU
                QMessageBox.warning(self, "警告", "GPU不可用，自动切换到CPU。")
                self.selectionChanged.emit("cpu")
                self.radioButtonCPU.setChecked(True)
            else:
                self.selectionChanged.emit("gpu")
                self.radioButtonGPU.setChecked(True)
        else:
            self.selectionChanged.emit("cpu")
    def on_tasks_changed(self):
        # 切换任务
        if self.radio_normal.isChecked():
            self.on_tasks_signal.emit("normal")
        else:
            self.on_tasks_signal.emit("gesture")