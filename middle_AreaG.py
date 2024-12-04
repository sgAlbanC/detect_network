from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QInputDialog, \
    QListWidget, QListWidgetItem, QMessageBox, QFrame
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from detect import YOLOPredictor
import os
import compareG, saveLabelG
import json, cv2, time

class CameraThread(QThread):
    """摄像头线程：负责从摄像头读取图像帧"""
    frame_signal = pyqtSignal(object)  # 用于传递捕获到的帧

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False

    def run(self):
        """启动摄像头并读取视频帧"""
        self.cap = cv2.VideoCapture(0)  # 使用摄像头ID 0
        if not self.cap.isOpened():
            return

        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_signal.emit(frame)  # 将读取到的帧传递给主线程
            time.sleep(0.03)  # 每帧等待 30ms，大约 33 FPS
        self.cap.release()

    def stop(self):
        """停止摄像头线程"""
        self.running = False
        self.wait()


class DetectionThread(QThread):
    """目标检测线程：负责处理图像并进行目标检测"""
    result_signal = pyqtSignal(object)  # 用于传递检测结果

    def __init__(self, model_path, device="cpu"):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self.model = YOLOPredictor(self.model_path)  # 假设 YOLOPredictor 是目标检测模型

    def run(self):
        """执行目标检测"""
        while True:
            if hasattr(self, 'frame'):
                frame = self.frame
                # 进行检测
                results = self.model.predict(frame, device=self.device)
                self.result_signal.emit(results)  # 将检测结果传递给主线程

class MiddleAreaG(QWidget):
    log_signal = pyqtSignal(str)  # 定义日志信号
    def __init__(self, logs_widget):
        super().__init__()

        self.update_logs = logs_widget.update_logs
        self.log_signal.connect(self.update_logs)

        self.device = "cpu"
        self.keys = []
        self.newData = None
        self.cap = None
        self.camera_thread = None
        self.detection_thread = None
        # 变量初始化
        self.model_path = None
        self.image_path = None

        layout_operate = QVBoxLayout()
        self.load_weights_pushbutton = QPushButton("加载权重")
        self.load_weights_pushbutton.clicked.connect(self.load_weights)

        self.load_images_pushbutton = QPushButton("加载图片")
        self.load_images_pushbutton.clicked.connect(self.load_images)

        self.open_camera_pushbutton = QPushButton("摄像头")
        self.open_camera_pushbutton.clicked.connect(self.detect_camera)

        detect_pushbutton = QPushButton("点击检测")
        detect_pushbutton.clicked.connect(self.detect)

        cancel_pushbutton = QPushButton("取消")
        cancel_pushbutton.clicked.connect(self.cancel)

        layout_operate.addWidget(self.load_weights_pushbutton)
        layout_operate.addWidget(self.load_images_pushbutton)
        layout_operate.addWidget(detect_pushbutton)
        layout_operate.addWidget(self.open_camera_pushbutton)
        layout_operate.addWidget(cancel_pushbutton)
        layout_operate.addStretch(1)

        layput_show = QHBoxLayout()

        self.label_orign = QLabel(self)
        self.label_orign.setFixedWidth(360)
        self.label_orign.setText("图像显示")
        self.label_orign.setStyleSheet("QLabel { background-color: #ccc; }")
        # 设置标签的对齐方式：居中显示
        self.label_orign.setAlignment(Qt.AlignCenter)
        layput_show.addWidget(self.label_orign)

        # 右边添加和显示手势布局
        layout_operateR = QHBoxLayout()
        layout_operateR1 = QVBoxLayout()
        self.add_gesture_pushbutton = QPushButton("添加手势")
        layout_operateR1.addWidget(self.add_gesture_pushbutton)
        layout_operateR1.addStretch(1)

        layout_operateR.addLayout(layout_operateR1)
        self.add_gesture_pushbutton.clicked.connect(self.add_gesture)

        # 创建 QListWidget 并设置其大小限制
        self.listWidget = QListWidget(self)
        self.listWidget.setFixedHeight(340)  # 设置高度，超过时显示滚动条
        self.listWidget.setStyleSheet("QListWidget { background-color: transparent; border: none }")
        layout_operateR.addWidget(self.listWidget)

        layout_operateR.addStretch(1)


        # 设置布局
        layout = QHBoxLayout()
        layout.addLayout(layout_operate)
        layout.addLayout(layput_show)
        layout.addLayout(layout_operateR)
        layout.addStretch(1)
        self.setLayout(layout)

        self.getLabelList()


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
        # 关闭摄像头（如果摄像头正在运行）
        self.stop_camera()
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

    def detect_camera(self):
        """开始摄像头线程并启动目标检测"""
        if not self.model_path:
            self.log_signal.emit("<font color='red'>请先加载权重文件!</font>")
            return

        self.add_gesture_pushbutton.setEnabled(False)
        # 启动摄像头线程
        self.camera_thread = CameraThread()
        self.camera_thread.frame_signal.connect(self.process_frame)
        self.camera_thread.start()

        # 启动目标检测线程
        self.detection_thread = DetectionThread(self.model_path)
        self.detection_thread.result_signal.connect(self.process_detection_results)
        self.detection_thread.start()

    def process_frame(self, frame):
        """处理从摄像头读取的帧并传递给检测线程"""
        self.current_frame = frame
        if self.detection_thread:
            self.detection_thread.frame = frame  # 将帧传递给检测线程

        # 将图像转换为 QPixmap 并显示
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # 缩放并显示图像到 QLabel
        scaled_pixmap = pixmap.scaled(self.label_orign.width(), self.label_orign.height(), Qt.KeepAspectRatio)
        self.label_orign.setPixmap(scaled_pixmap)

    def process_detection_results(self, results):
        """处理目标检测的结果并绘制框"""
        if results:
            frame = self.current_frame
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                for box in boxes:
                    x1, y1, x2, y2 = box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, 'x', (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 转换并显示结果
            self.process_frame(frame)

    def stop_camera(self):
        """停止摄像头并停止线程"""
        if self.camera_thread:
            self.camera_thread.stop()
        if self.detection_thread:
            self.detection_thread.quit()
            self.detection_thread.wait()
        self.add_gesture_pushbutton.setEnabled(True)

    def detect(self):
        if not self.model_path or not self.image_path:
            self.log_signal.emit("<font color='red'>请先加载权重文件和图片文件!</font>")
            return

        # 创建YOLO预测器，并传入模型路径
        model = YOLOPredictor(self.model_path)

        # 执行预测
        results = model.predict(self.image_path, device=self.device)
        try:
            data = results[0].keypoints.data[0]
        except IndexError:  # 捕获可能的索引错误
            self.log_signal.emit("<font color='red'>未识别到关键点信息！</font>")
        except Exception as e:  # 捕获其他异常
            print(f"An error occurred: {e}")
            self.log_signal.emit("<font color='red'>发生错误，请检查是否使用正确的权重参数！</font>")
            return

        self.newData = data
        detect_gesture = compareG.compare_gesture_data(data)

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
            self.label_orign.setPixmap(scaled_pixmap)
            if detect_gesture:
                self.log_signal.emit(f"<font color='green'>检测到的手势为 <b>{detect_gesture}</b>。</font>")
                print(f"最相似的手势标签是: {detect_gesture}")
            else:
                self.log_signal.emit("<font color='red'>未识别到手势！</font>")
                print("没有找到匹配的手势。")

        else:
            self.log_signal.emit("<font color='red'>未找到预测图像!</font>")

    def cancel(self):
        # 清除其他内容
        self.model_path = None
        self.image_path = None
        self.load_weights_pushbutton.setEnabled(True)
        self.load_images_pushbutton.setEnabled(True)
        self.stop_camera()

    def add_gesture(self):
        # 弹出输入框，输入gesture_label
        gesture_label, ok = QInputDialog.getText(self, "输入手势标签", "请输入手势标签:")

        # 检查用户是否点击了 OK 并且输入值不为空且长度小于等于5
        if ok and gesture_label and len(gesture_label) <= 5:
            if self.newData is not None:
                # 保存手势数据
                is_success_save = saveLabelG.save_gesture_data_as_json(self.newData, gesture_label)
                if is_success_save:
                    self.log_signal.emit(f"<font color='green'>新手势已成功保存！</font>")
                    self.getLabelList()
            else:
                # 如果没有新的数据，发出错误信息（可选）
                self.log_signal.emit("<font color='red'>没有新数据可保存！</font>")
        else:
            # 如果点击 Cancel 或输入无效，发出错误信息
            if not ok:
                # 用户点击了取消
                self.log_signal.emit("操作已取消。")
            elif len(gesture_label) > 5:
                # 用户输入超过了 5 个字符
                self.log_signal.emit("<font color='red'>标签长度不能超过 5 个字符。</font>")
            else:
                # 用户没有输入任何值
                self.log_signal.emit("<font color='red'>标签不能为空。</font>")

    def getLabelList(self):
        """加载 JSON 文件并获取所有键，然后渲染到 QListWidget 中"""
        json_file = "gesture_data.json"
        try:
            with open(json_file, 'r') as file:
                self.json_data = json.load(file)
            self.keys = list(self.json_data.keys())
        except FileNotFoundError:
            self.log_signal.emit("<font color='red'>gesture_data.json 文件不存在。</font>")
            return

        self.listWidget.clear()  # 清空现有的列表

        # 遍历 keys，添加到 QListWidget 中
        for key in self.keys:
            item_widget = QWidget()  # 创建一个QWidget来包装列表项
            item_layout = QHBoxLayout()  # 使用水平布局
            item_layout.setContentsMargins(10, 0, 0, 0)  # 去除间距

            # 显示手势标签（key值）
            label = QLabel(key)
            item_layout.addWidget(label)

            item_layout.addStretch(1)

            # 创建删除按钮
            delete_button = QPushButton("删除")
            delete_button.clicked.connect(lambda checked, key=key: self.delete_gesture(key))
            item_layout.addWidget(delete_button)

            # 将布局添加到QWidget中
            item_widget.setLayout(item_layout)

            # 创建列表项，将QWidget作为列表项的部件
            list_item = QListWidgetItem(self.listWidget)
            list_item.setSizeHint(item_widget.sizeHint())  # 设置列表项的大小

            self.listWidget.addItem(list_item)  # 添加列表项
            self.listWidget.setItemWidget(list_item, item_widget)  # 设置列表项的部件为我们的QWidget

    def delete_gesture(self, gesture_label):
        """删除手势数据并更新列表"""
        # 创建确认删除弹框
        reply = QMessageBox.question(
            self, '确认删除', f"你确定要删除手势 '{gesture_label}' 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 从JSON数据中删除对应的gesture_label
            if gesture_label in self.json_data:
                del self.json_data[gesture_label]

                # 保存更新后的数据到JSON文件
                with open("gesture_data.json", 'w') as file:
                    json.dump(self.json_data, file, ensure_ascii=False, indent=4)

                # 更新QListWidget
                self.getLabelList()  # 重新加载更新后的标签列表

                self.log_signal.emit(f"<font color='green'>手势 '{gesture_label}' 已删除。</font>")
            else:
                self.log_signal.emit(f"<font color='red'>未找到手势 '{gesture_label}'。</font>")