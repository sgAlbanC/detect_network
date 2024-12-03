from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from detect import YOLOPredictor
import os


class MiddleArea(QWidget):
    log_signal = pyqtSignal(str)  # 定义日志信号
    def __init__(self, logs_widget):
        super().__init__()

        self.update_logs = logs_widget.update_logs
        self.log_signal.connect(self.update_logs)

        # 变量初始化
        self.model_path = None
        self.image_path = None

        layout_operate = QVBoxLayout()
        self.load_weights_pushbutton = QPushButton("加载权重")
        self.load_weights_pushbutton.clicked.connect(self.load_weights)

        self.load_images_pushbutton = QPushButton("加载图片")
        self.load_images_pushbutton.clicked.connect(self.load_images)

        detect_pushbutton = QPushButton("点击检测")
        detect_pushbutton.clicked.connect(self.detect)

        cancel_pushbutton = QPushButton("取消")
        cancel_pushbutton.clicked.connect(self.cancel)

        layout_operate.addWidget(self.load_weights_pushbutton)
        layout_operate.addWidget(self.load_images_pushbutton)
        layout_operate.addWidget(detect_pushbutton)
        layout_operate.addWidget(cancel_pushbutton)
        layout_operate.addStretch(1)

        layput_show = QHBoxLayout()

        self.label_orign = QLabel(self)
        self.label_orign.setFixedWidth(360)
        self.label_orign.setText("原始图像")
        self.label_orign.setStyleSheet("QLabel { background-color: #ccc; }")
        self.label_predict = QLabel(self)
        self.label_predict.setFixedWidth(360)
        self.label_predict.setText("预测图像")
        self.label_predict.setStyleSheet("QLabel { background-color: #ccc; }")
        # 设置标签的对齐方式：居中显示
        self.label_orign.setAlignment(Qt.AlignCenter)
        self.label_predict.setAlignment(Qt.AlignCenter)
        layput_show.addWidget(self.label_orign)
        layput_show.addWidget(self.label_predict)

        self.device = "cpu"
        # 设置布局
        layout = QHBoxLayout()
        layout.addLayout(layout_operate)
        layout.addLayout(layput_show)
        layout.addStretch(1)
        self.setLayout(layout)

    def update_selection(self, device):
        if device == "cpu":
            self.device = device
        else:
            self.device = "cuda"
    def load_weights(self):
        # 打开文件对话框选择权重文件（.pt）
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择YOLO权重文件", "",
                                                   "PyTorch模型文件 (*.pt);;所有文件 (*.*)", options=options)

        if file_path:
            self.model_path = file_path
            self.log_signal.emit("<font color='green'>权重成功加载!</font>")
            self.load_weights_pushbutton.setEnabled(False)

    def load_images(self):
        # 打开文件对话框选择图片文件
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "",
                                                   "图片文件 (*.png *.jpg *.jpeg);;所有文件 (*.*)", options=options)

        if file_path:
            self.image_path = file_path
            # 加载图片
            pixmap = QPixmap(self.image_path)

            # 获取图片的原始宽高
            original_width = pixmap.width()
            original_height = pixmap.height()

            # 按比例缩放，保证最大宽或高为480，另一边自适应
            if original_width > original_height:
                # 宽度大于高度时，按宽度360缩放，另一边按比例缩放
                scaled_pixmap = pixmap.scaled(360, 360 * original_height // original_width, Qt.KeepAspectRatio)
            else:
                # 高度大于宽度时，按高度360缩放，另一边按比例缩放
                scaled_pixmap = pixmap.scaled(360 * original_width // original_height, 360, Qt.KeepAspectRatio)

            # 设置标签的pixmap
            self.label_orign.setPixmap(scaled_pixmap)
            self.log_signal.emit("<font color='green'>图像成功加载!</font>")

    def detect(self):
        if not self.model_path or not self.image_path:
            self.log_signal.emit("<font color='red'>请先加载权重文件和图片文件!</font>")
            return

        # 创建YOLO预测器，并传入模型路径
        model = YOLOPredictor(self.model_path)

        # 执行预测
        results = model.predict(self.image_path, device=self.device)

        # 获取保存路径
        save_dir = results[0].save_dir  # 假设 results[0] 是保存路径
        # 获取预测速度
        speed = results[0].speed

        self.log_signal.emit(f"预处理：{speed['preprocess']:.2f} ms，推理：{speed['inference']:.2f} ms，后处理：{speed['postprocess']:.2f} ms")
        self.log_signal.emit("<font color='green'>目标检测结束。</font>")

        # 提取原始图像的文件名（去掉路径和扩展名）
        image_filename = os.path.basename(self.image_path)

        # 构造预测图像的路径，假设保存的图像名与原图相同
        predicted_image_path = os.path.join(save_dir, image_filename)

        if os.path.exists(predicted_image_path):
            pixmap = QPixmap(predicted_image_path)
            # 缩放并显示预测图像
            original_width = pixmap.width()
            original_height = pixmap.height()

            # 按比例缩放
            if original_width > original_height:
                scaled_pixmap = pixmap.scaled(360, 360 * original_height // original_width, Qt.KeepAspectRatio)
            else:
                scaled_pixmap = pixmap.scaled(360 * original_width // original_height, 360, Qt.KeepAspectRatio)

            # 设置标签的pixmap
            self.label_predict.setPixmap(scaled_pixmap)
        else:
            self.log_signal.emit("<font color='red'>未找到预测图像!</font>")

    def cancel(self):
        # 清除模型和图像路径
        self.model_path = None
        self.image_path = None
        self.label_orign.clear()
        self.label_orign.setText("原始图像")
        self.label_predict.clear()
        self.label_predict.setText("预测图像")
        self.load_weights_pushbutton.setEnabled(True)
        self.log_signal.emit("<font>取消操作，已清除所有内容。</font>")
