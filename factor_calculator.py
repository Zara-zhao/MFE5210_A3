import numpy as np
import pandas as pd
from scipy import stats
import os
import pickle
from tqdm import tqdm
from scipy.stats import mstats

class FactorCalculator:
    def __init__(self, data_dir='data', lookback=20):
        """
        初始化因子计算器
        
        参数:
        -----------
        data_dir : str
            数据文件所在目录
        lookback : int
            因子计算的回看期（默认20天）
        """
        self.data_dir = data_dir
        self.lookback = lookback
        self.market_value_data = self._load_market_value_data()
        self.gdp_signal_data = self._load_gdp_signal_data()
            
    def _load_market_value_data(self):
        """加载月度市值数据"""
        try:
            # 读取CSV文件
            df = pd.read_csv(os.path.join(self.data_dir, 'monthly_market_value.csv'))
            
            # 转换日期列为datetime类型，处理YYYYMMDD格式
            df['trade_date'] = pd.to_datetime(df['trade_date'].astype(str), format='%Y%m%d')
            
            # 将数据转换为宽格式（pivot）
            market_value = df.pivot(index='trade_date', columns='ts_code', values='total_mv')
            
            return market_value
            
        except Exception as e:
            raise Exception(f"加载市值数据失败: {str(e)}")
    
    def _load_gdp_signal_data(self):
        """加载GDP信号数据"""
        try:
            # 读取CSV文件，将第一列作为索引
            df = pd.read_csv(os.path.join(self.data_dir, 'gdp_signal.csv'), index_col=0)
            
            # 转换索引为datetime类型
            df.index = pd.to_datetime(df.index)
            
            return df['signal']
            
        except Exception as e:
            raise Exception(f"加载GDP信号数据失败: {str(e)}")
    
    def _winsorize(self, series, limits=(0.01, 0.01)):
        """对数据进行winsorize处理"""
        return pd.Series(mstats.winsorize(series, limits=limits), index=series.index)
    
    def _process_stock_code(self, series):
        """处理股票代码，只保留前6位"""
        if isinstance(series.index, pd.MultiIndex):
            # 获取股票代码索引
            stock_codes = series.index.get_level_values('STOCK_CODE')
            # 只保留前6位
            new_stock_codes = stock_codes.str[:6]
            # 创建新的MultiIndex
            new_index = pd.MultiIndex.from_arrays([
                series.index.get_level_values('END_DATE'),
                new_stock_codes
            ], names=['END_DATE', 'STOCK_CODE'])
            # 重新索引
            return pd.Series(series.values, index=new_index)
        return series

    def calculate_factor1(self):
        """计算因子1：市值的对数"""
        # 获取最新的市值数据
        market_value = self.market_value_data
        
        # 计算对数市值
        log_mv = np.log(market_value)
        
        # 将数据转换为长格式，确保日期格式正确
        log_mv = log_mv.stack()
        log_mv.index = pd.MultiIndex.from_arrays([
            pd.to_datetime(log_mv.index.get_level_values(0)).normalize(),
            log_mv.index.get_level_values(1)
        ], names=['END_DATE', 'STOCK_CODE'])
        
        # 处理股票代码
        return self._process_stock_code(log_mv)
    
    def calculate_factor2(self):
        """计算因子2：对数市值的三次方对市值OLS回归的残差（取相反数）"""
        # 获取市值数据
        market_value = self.market_value_data
        
        # 计算对数市值
        log_mv = np.log(market_value)
        
        # 计算对数市值的三次方
        log_mv_cubed = log_mv ** 3
        
        # 初始化结果DataFrame
        residuals = pd.DataFrame(index=market_value.index, columns=market_value.columns)
        
        # 对每个月的数据进行OLS回归
        for date in market_value.index:
            # 获取当前月份的数据
            curr_mv = market_value.loc[date]
            curr_log_mv_cubed = log_mv_cubed.loc[date]
            
            # 删除缺失值
            valid_mask = curr_mv.notna() & curr_log_mv_cubed.notna()
            if valid_mask.sum() > 10:  # 确保有足够的样本
                X = curr_mv[valid_mask].values.reshape(-1, 1)
                y = curr_log_mv_cubed[valid_mask].values
                
                # 进行OLS回归
                slope, intercept, _, _, _ = stats.linregress(X.flatten(), y)
                
                # 计算残差
                predicted = slope * X + intercept
                residual = y - predicted.flatten()
                
                # 对残差进行winsorize处理
                residual = self._winsorize(pd.Series(residual, index=curr_mv[valid_mask].index))
                
                # 存储残差（取相反数）
                residuals.loc[date, residual.index] = -residual
        
        # 将数据转换为长格式，确保日期格式正确
        residuals = residuals.stack()
        residuals.index = pd.MultiIndex.from_arrays([
            pd.to_datetime(residuals.index.get_level_values(0)).normalize(),
            residuals.index.get_level_values(1)
        ], names=['END_DATE', 'STOCK_CODE'])
        
        # 处理股票代码
        return self._process_stock_code(residuals)
    
    def calculate_factor3(self):
        """计算因子3：因子1加因子2"""
        factor1 = self.calculate_factor1()
        factor2 = self.calculate_factor2()
        
        # 确保两个因子的索引一致
        common_index = factor1.index.intersection(factor2.index)
        factor1 = factor1.loc[common_index]
        factor2 = factor2.loc[common_index]
        
        # 计算因子3
        factor3 = factor1 + factor2
        
        return factor3
    
    def calculate_factor4(self):
        """计算因子4：因子3乘以对应月份的GDP信号"""
        # 获取因子3
        factor3 = self.calculate_factor3()
        
        # 将因子3的日期转换为月份
        factor3_dates = pd.to_datetime(factor3.index.get_level_values('END_DATE')).to_period('M')
        
        # 将GDP信号数据转换为月份格式
        gdp_signal_monthly = self.gdp_signal_data.to_period('M')
        
        # 创建结果Series
        factor4 = pd.Series(index=factor3.index, dtype=float)
        
        # 对每个月份的数据进行信号相乘
        for month in factor3_dates.unique():
            # 获取当前月份的因子3数据
            month_mask = factor3_dates == month
            curr_factor3 = factor3[month_mask]
            
            # 获取对应的GDP信号
            if month in gdp_signal_monthly.index:
                signal = gdp_signal_monthly[month]
                # 将信号应用到因子3上
                factor4.loc[curr_factor3.index] = curr_factor3 * signal
        
        return factor4
    
    def save_factors_to_pkl(self, factors, output_file='factors_data.pkl'):
        """
        将因子数据保存为pickle文件
        
        参数:
        -----------
        factors : pd.DataFrame
            因子数据
        output_file : str
            输出文件名
        """
        try:
            # 保存到data目录
            output_path = os.path.join(self.data_dir, output_file)
            factors.to_pickle(output_path)
            print(f"\n因子数据已保存到: {os.path.abspath(output_path)}")
            
        except Exception as e:
            print(f"\n保存因子数据失败: {str(e)}")

    def calculate_all_factors(self, save_to_pkl=True, output_file='factors_data.pkl'):
        """
        计算所有因子并返回DataFrame
        
        参数:
        -----------
        save_to_pkl : bool
            是否保存为pickle文件
        output_file : str
            输出文件名
        """
        print("开始计算因子...")
        factors = pd.DataFrame()
        
        # 使用tqdm创建进度条
        factor_methods = [
            ('Factor1', self.calculate_factor1),
            ('Factor2', self.calculate_factor2),
            ('Factor3', self.calculate_factor3),
            ('Factor4', self.calculate_factor4)
        ]
        
        for factor_name, method in tqdm(factor_methods, desc="计算因子进度"):
            try:
                factors[factor_name] = method()
                print(f"\n{factor_name} 计算完成")
            except Exception as e:
                print(f"\n{factor_name} 计算失败: {str(e)}")
                factors[factor_name] = np.nan
        
        print("\n所有因子计算完成")
        
        # 如果需要保存为pickle
        if save_to_pkl:
            self.save_factors_to_pkl(factors, output_file)
        
        return factors 