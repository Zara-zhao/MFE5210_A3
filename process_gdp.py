import pandas as pd
import os

def process_gdp_data(gdp_filepath=None, start_date='2015-01-01', end_date='2025-01-01'):
    """
    处理GDP数据，将季度数据转换为月度数据并生成信号
    
    Parameters:
    -----------
    gdp_filepath : str, optional
        GDP数据文件路径，默认为'data/中国_GDP_不变价_当季同比.csv'
    start_date : str, optional
        起始日期，默认为'2015-01-01'
    end_date : str, optional
        结束日期，默认为'2025-01-01'
    
    Returns:
    --------
    pandas.DataFrame
        处理后的GDP信号数据，包含GDP_yoy_now列
    """
    # 设置默认文件路径
    if gdp_filepath is None:
        gdp_filepath = os.path.join('data', '中国_GDP_不变价_当季同比.csv')
    
    # 2.1 加载和预处理GDP数据
    GDP_data = pd.read_csv(gdp_filepath, encoding='GBK')
    GDP_data = GDP_data.iloc[:-1]  # 删除最后一行
    GDP_data.set_index('指标名称', inplace=True)  # 设置指标名称为索引
    GDP_data = GDP_data.rename_axis(None)  # 移除索引名称

    # 2.2 筛选GDP时间段
    GDP_data = GDP_data[GDP_data.index < end_date]

    # 2.3 列名重命名
    column_mapping_GDP = {'中国:GDP:不变价:当季同比': 'GDP_yoy_now'}
    GDP_data.rename(columns=column_mapping_GDP, inplace=True)

    # 2.5 筛选起始日期之后的数据
    GDP_data = GDP_data[GDP_data.index > start_date]

    # 创建final_data
    final_data = GDP_data.copy()

    # 将索引转换为datetime类型
    final_data.index = pd.to_datetime(final_data.index)
    
    # 计算GDP同比变化方向
    final_data['GDP_yoy_now'] = final_data['GDP_yoy_now'].diff()
    final_data['signal'] = final_data['GDP_yoy_now'].apply(lambda x: 1 if x >= 0 else -1)

    # 创建完整的月度索引
    monthly_index = pd.date_range(start=start_date, end=end_date, freq='M')
    
    # 重新索引数据，使用月度频率，并用前向填充方法填充缺失值
    final_data = final_data.reindex(monthly_index, method='bfill')
    
    # 提取信号
    signal = final_data[['signal']]
    
    return signal
