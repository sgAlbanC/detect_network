import json
import numpy as np


def load_gesture_data(filename):
    """
    加载保存在JSON文件中的手势数据。

    参数:
    - filename (str): JSON文件路径。

    返回:
    - gesture_data (dict): 包含手势标签和数据的字典。
    """
    try:
        with open(filename, 'r') as f:
            gesture_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        gesture_data = {}
    return gesture_data


def calculate_distance(point1, point2):
    """
    计算两个点之间的欧几里得距离。

    参数:
    - point1 (tuple): 第一个点的 (x, y) 坐标。
    - point2 (tuple): 第二个点的 (x, y) 坐标。

    返回:
    - distance (float): 两点之间的距离。
    """
    return np.linalg.norm(np.array(point1) - np.array(point2))

def compare_gesture_data(new_data, filename="gesture_data.json", threshold=0.6):
    """
    比较新数据与文件中保存的数据，返回最相似的标签。
    比较新数据与文件中保存的数据，返回最相似的标签。

    参数:
    - new_data (torch.Tensor): 新的手势数据，形状为 [1, 21, 3]。
    - filename (str): 存储手势数据的 JSON 文件路径。
    - threshold (float): 匹配阈值，默认 0.6（60%）。

    返回:
    - best_label (str): 最相似的手势标签。
    """
    gesture_data = load_gesture_data(filename)

    if not gesture_data:
        print("没有找到保存的手势数据。")
        return None

    # 获取新数据的第一个和第二个点的坐标
    new_data_points = new_data.squeeze().cpu().numpy()[:, :2]  # 获取 (x, y) 坐标

    best_label = None
    best_similarity = float('inf')  # 初始化为一个很大的数

    for label, data_list in gesture_data.items():
        saved_data_points = np.array(data_list)[:, :2]

        # 归一化数据
        new_data_points_normalized = new_data_points / np.max(new_data_points)
        saved_data_points_normalized = saved_data_points / np.max(saved_data_points)

        # 计算距离
        distance_1 = calculate_distance(new_data_points_normalized[0], saved_data_points_normalized[0])
        distance_2 = calculate_distance(new_data_points_normalized[1], saved_data_points_normalized[1])

        # 相似度：使用距离差的平均值
        similarity = (distance_1 + distance_2) / 2
        print("Similarity:", similarity)

        if similarity <= threshold and similarity < best_similarity:
            best_similarity = similarity
            best_label = label

    return best_label