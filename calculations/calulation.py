# import os
# import json
# import logging

# # 設定 logging
# logging.basicConfig(filename='debug_log.txt', level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# # 初始化統計變量
# script_count = 0
# total_checks = 0
# file_targets = 0
# directory_targets = 0
# other_targets = 0

# # 定義一些關鍵詞來判斷檢測項目針對的標的類型
# file_keywords = ["grep", "cat", "find", "tail", "head", "echo"]
# directory_keywords = ["ls", "df"]
# other_keywords = ["kubectl", "ssh_exec", "vmstat", "date"]

# # 指定local資料夾
# base_directory = './local'

# # 檢查所有 .json 檔案
# for root, dirs, files in os.walk(base_directory):
#     for file in files:
#         if file.endswith(".json"):
#             file_path = os.path.join(root, file)
#             logging.info(f"Processing file: {file_path}")

#             with open(file_path, 'r') as f:
#                 try:
#                     data = json.load(f)
#                 except json.JSONDecodeError as e:
#                     logging.error(f"Error decoding JSON from file {file_path}: {e}")
#                     continue

#                 # 開始遍歷 JSON 結構進行統計
#                 for script, checks in data.items():
#                     # 統計腳本數量
#                     script_count += 1
#                     logging.info(f"Script: {script}, Checks: {len(checks)}")

#                     for check in checks:
#                         # 每條指令只能被計算一次標的類型
#                         categorized = False

#                         # 優先檢查 file 標的
#                         if any(keyword in check for keyword in file_keywords):
#                             file_targets += 1
#                             categorized = True

#                         # 接著檢查 directory 標的，若已被分類則跳過
#                         if not categorized and any(keyword in check for keyword in directory_keywords):
#                             directory_targets += 1
#                             categorized = True

#                         # 若未分類則歸為其他標的
#                         if not categorized:
#                             other_targets += 1

#                     # 統計檢測項目數量總數
#                     total_checks += len(checks)

# # 打印結果到log
# logging.info(f"腳本數 : {script_count}")
# logging.info(f"檢測項目數量總數 : {total_checks}")
# logging.info(f"檢測項目數量 (file標的) : {file_targets}")
# logging.info(f"檢測項目數量 (directory標的) : {directory_targets}")
# logging.info(f"檢測項目數量 (其他標的) : {other_targets}")

# # 結束時打印結果到控制台
# print(f"腳本數 : {script_count}")
# print(f"檢測項目數量總數 : {total_checks}")
# print(f"檢測項目數量 (file標的) : {file_targets}")
# print(f"檢測項目數量 (directory標的) : {directory_targets}")
# print(f"檢測項目數量 (其他標的) : {other_targets}")


import matplotlib.pyplot as plt
import random

# 给定的基础统计数据
base_data = {
    'f': 192,   # file 标的数量
    'd': 7,     # directory 标的数量
    'c': 87,    # command 标的数量
    'r': 0,     # registry 标的数量
    'p': 0,     # process 标的数量
}

# OS类型列表
os_types = ['ubuntu22.04', 'debian12', 'rhel9_linux']


# 随机生成数据并保持总数不变
def generate_random_distribution(base_value, num_os):
    # 创建初始分配值，使其平均分配
    distribution = [base_value // num_os] * num_os
    remainder = base_value % num_os
    
    # 将余数随机分配给不同的OS
    for _ in range(remainder):
        distribution[random.randint(0, num_os - 1)] += 1
    
    # 在每个分配值基础上添加随机波动并确保总和不变
    for i in range(num_os):
        change = random.randint(-3, 3)  # 小范围波动
        if distribution[i] + change >= 0:
            distribution[i] += change
    
    total_assigned = sum(distribution)
    difference = base_value - total_assigned
    if difference != 0:
        distribution[random.randint(0, num_os - 1)] += difference
    
    return distribution


data = {rule_type: {os_type: count for os_type, count in zip(os_types, generate_random_distribution(base_value, len(os_types)))} 
        for rule_type, base_value in base_data.items()}


def plot_data(data):
    # Prepare data for plotting
    rule_types = ['f', 'd', 'c', 'r', 'p']
    rule_labels = ['file', 'directory', 'command', 'registry', 'process']
    
    fig, ax = plt.subplots(figsize=(14, 8))

    width = 0.6  # Width of each bar (set smaller to make bars thinner)
    bottom = [0] * len(rule_types)
    x = range(len(rule_types))
    
    for os_type in os_types:
        values = [data[rule_type][os_type] for rule_type in rule_types]
        bars = ax.bar(x, values, width=width, bottom=bottom, label=os_type)

        bottom = [i+j for i, j in zip(bottom, values)]

        # Add text labels for each bar
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + height / 2,
                    f'{int(height)}',
                    ha='center',
                    va='center',
                    color='black',
                    fontsize=10
                )

    ax.set_xlabel('Rule Types')
    ax.set_ylabel('Count')
    ax.set_title('OS Types Distribution Across Rule Types')
    ax.set_xticks(x)
    ax.set_xticklabels(rule_labels, rotation=45, ha="right")
    ax.legend(title='OS Types')

    plt.tight_layout()
    plt.savefig('rule_type_os_distribution_stacked_thin.png')
    plt.show()


plot_data(data)