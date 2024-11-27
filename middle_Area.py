from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class MiddleArea(QWidget):
    def __init__(self):
        super().__init__()

        layout_operate = QVBoxLayout()
        load_weights_pushbutton = QPushButton("加载权重")
        load_weights_pushbutton.clicked.connect(self.load_weights)

        load_images_pushbutton = QPushButton("加载图片")
        load_images_pushbutton.clicked.connect(self.load_images)

        detect_pushbutton = QPushButton("点击检测")
        detect_pushbutton.clicked.connect(self.detect)

        cancel_pushbutton = QPushButton("取消")
        cancel_pushbutton.clicked.connect(self.cancel)

        layout_operate.addWidget(load_weights_pushbutton)
        layout_operate.addWidget(load_images_pushbutton)
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

        # 设置布局
        layout = QHBoxLayout()
        layout.addLayout(layout_operate)
        layout.addLayout(layput_show)
        layout.addStretch(1)
        self.setLayout(layout)


    def load_weights(self):
        pass

    def load_images(self):
        # 加载图片
        pixmap = QPixmap("peo.jpg")  # 替换成你图片的路径

        # 获取图片的原始宽高
        original_width = pixmap.width()
        original_height = pixmap.height()

        # 按比例缩放，保证最大宽或高为480，另一边自适应
        if original_width > original_height:
            # 宽度大于高度时，按宽度480缩放，另一边按比例缩放
            scaled_pixmap = pixmap.scaled(360, 360 * original_height // original_width, Qt.KeepAspectRatio)
        else:
            # 高度大于宽度时，按高度480缩放，另一边按比例缩放
            scaled_pixmap = pixmap.scaled(360 * original_width // original_height, 360, Qt.KeepAspectRatio)

        # 设置标签的pixmap
        self.label_orign.setPixmap(scaled_pixmap)
        self.label_predict.setPixmap(scaled_pixmap)

    def detect(self):
        pass

    def cancel(self):
        pass