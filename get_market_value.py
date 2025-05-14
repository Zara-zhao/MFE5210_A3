import tushare as ts
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# 设置 Tushare Token
ts.set_token('your token')
pro = ts.pro_api()

def get_monthly_last_trading_days(start_date='20150101', end_date='20241231'):
    """
    获取指定日期范围内每月最后一个交易日
    """
    # 获取交易日历
    df_cal = pro.trade_cal(exchange='SSE', 
                          start_date=start_date, 
                          end_date=end_date,
                          fields='cal_date,is_open')
    
    # 只保留交易日
    df_cal = df_cal[df_cal['is_open'] == 1]
    
    # 将日期转换为datetime格式
    df_cal['cal_date'] = pd.to_datetime(df_cal['cal_date'])
    
    # 添加年月列
    df_cal['year_month'] = df_cal['cal_date'].dt.to_period('M')
    
    # 按年月分组，获取每月最后一个交易日
    last_trading_days = df_cal.groupby('year_month')['cal_date'].max()
    
    # 转换回字符串格式
    last_trading_days = last_trading_days.dt.strftime('%Y%m%d').tolist()
    
    return last_trading_days

def get_market_value_data(trade_dates):
    """
    获取指定交易日的市值数据
    """
    all_data = []
    
    # 使用tqdm创建进度条
    for date in tqdm(trade_dates, desc="获取市值数据"):
        try:
            # 获取每日市值数据
            df = pro.daily_basic(trade_date=date, 
                                fields='ts_code,trade_date,total_mv')
            all_data.append(df)
        except Exception as e:
            print(f"\nError retrieving data for {date}: {str(e)}")
    
    # 合并所有数据
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    return None


