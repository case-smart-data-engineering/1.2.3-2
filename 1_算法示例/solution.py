
import pandas as pd
import numpy as np

def calculate_query_probability(df, query_order, query_ranges):
    """
    根据查询条件进行采样，并计算查询的概率估计值。

    参数：
    df (pd.DataFrame): 包含数据的DataFrame。
    query_order (list): 查询中属性的顺序。
    query_ranges (dict): 每个属性的查询范围，字典的键是属性名，值是一个元组，表示该属性的最小值和最大值（或允许的值列表）。

    返回：
    float: 查询的概率估计值。
    以及每次采样的结果
    """
    #np.random.seed(42)  # 设置随机种子以确保可重复性
    sampled_values = {}
    query_probability = 1.0  # 初始化查询概率为1，因为我们将要乘以每个属性的条件概率

    # 检查query_order中的每个元素是否是有效的列名
    for attribute in query_order:
        if attribute not in df.columns:
            raise ValueError(f"Invalid attribute '{attribute}' in query_order. It is not a column in the dataframe.")

    # 逐步采样每个属性
    for i, attribute in enumerate(query_order):


        # 对于第一个属性，直接使用满足查询范围的数据框的概率分布
        if i == 0:
            probs = df[attribute].value_counts(normalize=True)
        else:
            prev_value = sampled_values[query_order[i - 1]]
            probs = df[df[query_order[i - 1]] == prev_value][attribute].value_counts(normalize=True)
        # 获取当前属性的查询范围
        query_range = query_ranges.get(attribute, None)
        if query_range is None:
            raise ValueError(f"No query range specified for attribute '{attribute}'.")
        else:
            sumpr=0

            for pr in query_range:
                #print("probs[pr]=",probs[pr])
                sumpr+=probs[pr]

        # 检查是否有有效的概率分布（避免除以零错误）
        #print(probs)
        if sumpr == 0:
            return 0
            #如果属性选择范围没有对应的值，则查询命中的概率为0

        # 采样并存储结果
        query_range_list = list(query_range)
        # 使用列表索引来过滤 probs
        # 使用列表索引来过滤 probs
        probs_range = probs.loc[query_range_list]

        # 检查 probs_range 是否为空
        if probs_range.empty:
            raise ValueError(f"No data found for query range {query_range_list}")

        # 计算 probs_range 的总和
        probs_sum = probs_range.values.sum()

        # 如果总和不是1（考虑到浮点误差），则进行归一化
        if not np.isclose(probs_sum, 1.0):
            probs_range_normalized = probs_range / probs_sum
            # 使用归一化后的概率进行随机选择
            sampled_value = np.random.choice(probs_range_normalized.index, p=probs_range_normalized.values)
        else:
            # 如果总和已经是1（或非常接近），则直接使用原始概率
            sampled_value = np.random.choice(probs_range.index, p=probs_range.values)
        # 将采样值存储到 sampled_values 字典中，其中 attribute 是某个特定的键
        sampled_values[attribute] = sampled_value


        query_probability *= sumpr

    # 返回查询的概率估计值
    return query_probability, sampled_values

# 读取CSV数据（假设数据已经按照需要预处理过）
df = pd.read_csv('datasets/dmv-tiny.csv')

# 定义查询条件的顺序和范围
query_order= ['Registration Class','City']
# query_order = ['Record Type' , "VIN","Registration Class","City","State","Zip"
#     ,"County","Model Year","Make","Body Type","Fuel Type","Unladen Weight",
#     "Maximum Gross Weight","Passengers","Reg Valid Date","Reg Expiration Date"
#     ,"Color","Scofflaw Indicator"
#     ,"Suspension Indicator","Revocation Indicator"]  # 替换为实际的属性名
query_ranges = {
    'Registration Class': ('PAS','HIS' ),  # 替换为实际的范围或值列表
    'City': ('ALEXANDRIA BAY ', 'NEW YORK       ','BROOKLYN       ',"HOLBROOK       "),
     # 也可以是一个值列表
}

# 执行采样过程并计算查询的概率估计值
try:
    #S为采样次数
    S=10
    query_prob=0
    for i in range(S):
        progres,lis = calculate_query_probability(df, query_order, query_ranges)
        print(lis)
        query_prob += progres

    print("Query probability estimate:", query_prob/S)
except ValueError as e:
    print(e)
