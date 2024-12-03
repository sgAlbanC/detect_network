import json

def save_gesture_data_as_json(data, label, filename='gesture_data.json'):
    """
    将手势数据和标签保存到指定的json文件中，每次都追加。

    参数:
    - data (torch.Tensor): 手势数据，形状为 [1, 21, 3]。
    - label (str): 手势对应的标签。
    - filename (str): 保存数据的json文件路径。
    """
    # 将手势数据转换为列表，并将其格式化为字典格式
    data_list = data.squeeze().cpu().numpy().tolist()  # 转换为2D列表，移除batch维度
    if not data_list:
        return False  # 空列表时返回 False

    # 打开文件并读取数据
    try:
        with open(filename, 'r') as f:
            gesture_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或文件为空，则初始化一个空字典
        gesture_data = {}

    # 检查是否已经存在相同的 label，如果有，则自动修改为 label_1, label_2 等
    original_label = label
    counter = 1
    while label in gesture_data:
        label = f"{original_label}_{counter}"
        counter += 1

    # 将数据添加到字典中
    gesture_data[label] = data_list

    # 将更新后的字典保存回文件
    with open(filename, 'w') as f:
        json.dump(gesture_data, f, ensure_ascii=False, indent=4)

    return True
