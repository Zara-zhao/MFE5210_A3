# Factor Analysis Project

基于Tushare数据的多因子分析系统，用于计算和评估市值相关的因子。

## 项目结构

```
.
├── factor_calculator.py       # 因子计算模块
├── factor_metrics.py          # 因子评估指标模块
├── process_gdp.py            # GDP数据处理模块
├── get_market_value.py       # 市值数据获取模块
├── factor_analysis.ipynb     # 因子分析Jupyter notebook
├── requirements.txt          # 项目依赖
├── data/                     # 数据存储目录
├── factor_results/           # 因子结果存储目录
├── ic_results/              # IC分析结果存储目录
└── README.md                # 项目说明文档
```

## 因子说明

本项目实现了4个基于市值和GDP信号的因子：

1. **Factor 1**: 市值的对数
   - 计算方式：`log(market_value)`
   - 特点：捕捉市值规模效应
   - 数据来源：月度市值数据

2. **Factor 2**: 对数市值的三次方对市值OLS回归的残差（取相反数）
   - 计算方式：
     1. 计算对数市值的三次方：`(log(market_value))^3`
     2. 对每个月的数据进行OLS回归：`(log(market_value))^3 ~ market_value`
     3. 取残差的相反数
   - 特点：捕捉市值非线性效应
   - 数据来源：月度市值数据

3. **Factor 3**: 因子1和因子2的组合
   - 计算方式：`Factor1 + Factor2`
   - 特点：结合市值规模效应和非线性效应
   - 数据来源：Factor1和Factor2的计算结果

4. **Factor 4**: 因子3与GDP信号的交互
   - 计算方式：`Factor3 * GDP_signal`
   - 特点：结合宏观经济信号，捕捉经济周期对市值因子的影响
   - 数据来源：Factor3的计算结果和GDP信号数据

数据处理说明：
- 所有因子计算均基于月度数据
- 对异常值进行winsorize处理（上下1%）
- 股票代码统一处理为6位格式
- 日期格式统一处理为datetime类型

## 功能特点

- 使用Tushare获取A股市场数据
- 计算4个市值相关的技术因子
- 计算因子评估指标：
  - IC (Information Coefficient)
    - IC均值 (IC_mean)
    - IC标准差 (IC_std)
    - IC信息比率 (IC_IR)
    - IC正比例 (IC_positive_ratio)
  - 因子收益率分析
    - 分组收益率分析（默认5组）
    - 累积收益率分析
    - 收益率统计指标（Sharpe Ratio等）
  - 因子相关性分析
    - 因子间相关性矩阵
    - 相关性热力图
  - 可视化分析
    - IC时序图
    - IC热力图
    - 分组收益率图
    - 因子相关性热力图
- 支持数据导出为CSV格式
- 提供Jupyter notebook进行交互式分析
- 自动保存分析结果到指定目录

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- pandas >= 1.5.0
- numpy >= 1.21.0
- matplotlib >= 3.5.0
- seaborn >= 0.12.0
- scipy >= 1.7.0
- statsmodels >= 0.13.0
- tqdm >= 4.65.0

默认回测参数：
- 起始日期：2015-01-01
- 结束日期：2024-12-31

## 模块说明

### factor_calculator.py
- 实现4个因子的计算逻辑
- 提供统一的因子计算接口
- 支持自定义回看期

### factor_metrics.py
- 计算因子评估指标
- 计算因子相关性
- 生成可视化图表
- 提供详细的因子分析功能

### process_gdp.py
- 处理GDP相关数据
- 提供宏观经济指标分析功能

### get_market_value.py
- 获取和处理市值数据
- 提供市值相关的分析功能

### factor_analysis.ipynb
- 提供交互式因子分析环境
- 包含详细的因子分析示例
- 支持自定义分析流程

## 数据目录说明

- `data/`: 存储原始数据和中间计算结果
- `factor_results/`: 存储因子计算结果和分析报告
- `ic_results/`: 存储IC分析结果和相关图表

## 分析结果展示

### 因子综合评估结果

（1） **IC分析**
| 评估指标 | Factor 1 | Factor 2 | Factor 3 | Factor 4 |
|----------|-----------|-----------|-----------|-----------|
| IC均值 | 0.0683 | 0.1037 | 0.0658 | 0.0652 |
| IC标准差 | 0.1097 | 0.0960 | 0.0898 | 0.0726 |
| ICIR | 9.882 | 17.139 | 11.639 | 14.263 |
| IC正比例 | 0.775 | 0.903 | 0.739 | 0.867 |

（2） **收益分析** 
| 评估指标 | Factor 1 | Factor 2 | Factor 3 | Factor 4 |
|----------|-----------|-----------|-----------|-----------|
| 年化收益率 | 8.51% | 11.20% | 11.09% | 9.48% |
| 年化波动率 | 30.81% | 27.75% | 28.97% | 28.80% |
| 夏普比率 | 0.28 | 0.40 | 0.38 | 0.33 |
| 最大回撤 | -51.06% | -43.35% | -41.46% | -43.47% |
| 胜率 | 50.00% | 51.67% | 50.00% | 52.50% |
| 收益风险比 | 0.28 | 0.40 | 0.38 | 0.33 |

### 因子相关性矩阵

![因子相关性热力图](./ic_results/factor_correlation_heatmap.png)
*图1：因子相关性热力图*

### 未来计划
- 考虑对特定指数成分股进行回测




