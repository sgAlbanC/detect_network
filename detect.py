import time
from ultralytics import YOLO


class YOLOPredictor:
    def __init__(self, model_path):
        """
        初始化 YOLOPredictor 类，加载预训练模型。

        :param model_path: str, 预训练模型的路径
        """
        self.model = YOLO(model_path)  # 加载预训练的 YOLO 模型

    def predict(self, source_path, device="cpu", save_results=True):
        """
        使用 YOLO 模型对指定路径的图片进行预测。

        :param device: str, "cpu" "cuda" | "cuda:0","cuda1" , "cuda:0" 表示使用第一块 GPU，"cuda:1" 表示使用第二块 GPU
        :param source_path: str, 图片或图片目录的路径
        :param save_results: bool, 是否保存预测结果，默认为 True
        :return: results, 预测的结果
        """
        # print(f"Starting prediction for source: {source_path}")
        # start_time = time.time()

        # 使用 YOLO 模型进行预测
        results = self.model.predict(source=source_path, save=save_results, device=device)

        # 打印预测耗时
        # elapsed_time = time.time() - start_time
        # print(f"Prediction completed in {elapsed_time:.2f} seconds.")

        # 返回预测结果
        return results
