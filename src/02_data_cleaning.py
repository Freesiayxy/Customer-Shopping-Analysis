# -*- coding: utf-8 -*-
"""
=============================================================
第二步：数据清洗（Data Cleaning）
=============================================================
本脚本的目标：
    原始数据往往不能直接分析，需要先“洗干净”。
    这份数据集质量很高（没有缺失值和重复行），主要问题是：
        1. 日期列 invoice_date 是文本，需要转成真正的日期类型
        2. 数据里没有“总金额”列，需要自己计算（数量 × 单价）
        3. 为了方便分析，补充几个衍生列：年、月、年龄段

运行方式：
    python src/02_data_cleaning.py

运行结果：
    在 data/ 文件夹下生成 customer_shopping_cleaned.csv（清洗后的数据）
"""

import pandas as pd
from pathlib import Path

# ---------------- 定位文件路径 ----------------
BASE_DIR = Path(__file__).resolve().parents[1]          # 项目根目录
RAW_PATH = BASE_DIR / "data" / "customer_shopping_data.csv"      # 原始数据
CLEAN_PATH = BASE_DIR / "data" / "customer_shopping_cleaned.csv" # 清洗后要保存的位置

# ---------------- 1. 读取原始数据 ----------------
df = pd.read_csv(RAW_PATH)
print(f"原始数据：{df.shape[0]} 行 × {df.shape[1]} 列")

# ---------------- 2. 删除重复行 ----------------
# 虽然本数据集没有重复行，但这是数据清洗的标准步骤，养成习惯
# drop_duplicates() 会删掉“整行内容完全一样”的记录，keep="first" 表示保留第一次出现的那条
before = len(df)                                   # 记录删除前的行数
df = df.drop_duplicates(keep="first")
print(f"删除重复行：{before - len(df)} 条")

# ---------------- 3. 处理缺失值 ----------------
# 本数据集没有缺失值。如果有，常见做法是：数值列填平均值/中位数，文本列填“Unknown”
# 这里只做检查，不填充，保证数据原汁原味
missing = df.isnull().sum().sum()
print(f"缺失值总数：{missing}（本数据集没有缺失，无需填充）")

# ---------------- 4. 日期列：文本 → 日期类型 ----------------
# 原始数据里 invoice_date 长这样："5/8/2022"、"16/05/2021"，是“日/月/年”格式
# dayfirst=True 告诉 pandas：数字小的在前是“日”，避免把 5/8 误解成 5 月 8 日
# errors="coerce" 表示：万一遇到无法解析的日期，变成 NaT（空日期），而不是直接报错
df["invoice_date"] = pd.to_datetime(df["invoice_date"], dayfirst=True, errors="coerce")
print(f"日期解析失败的行数：{df['invoice_date'].isnull().sum()}")
print(f"数据时间范围：{df['invoice_date'].min().date()} ~ {df['invoice_date'].max().date()}")

# ---------------- 5. 计算总金额（本数据集没有，需要自己造） ----------------
# 每条记录的总金额 = 购买数量 × 单价
# 新增的这一列叫 revenue，是后面所有“销售额”分析的核心
df["revenue"] = df["quantity"] * df["price"]

# ---------------- 6. 衍生列：年、月（方便做趋势分析） ----------------
# .dt.year / .dt.month 可以从日期里提取年份和月份
df["year"] = df["invoice_date"].dt.year
# 把日期转成 "2021-05" 这样的“年月”格式，画月度趋势图时用
df["year_month"] = df["invoice_date"].dt.to_period("M").astype(str)

# ---------------- 7. 衍生列：年龄段 ----------------
# 把连续的年龄数字分箱成几个区间，方便对比不同年龄段的行为
# pd.cut() 的作用：按照给定的边界把数值切分成组
#   bins   = 区间边界：[17,25) [25,35) [35,45) [45,55) [55,100)
#   labels = 每个区间起个名字
df["age_group"] = pd.cut(
    df["age"],
    bins=[17, 25, 35, 45, 55, 100],
    labels=["18-24", "25-34", "35-44", "45-54", "55+"],
)

# ---------------- 8. 保存清洗后的数据 ----------------
# index=False 表示不把行号写进 CSV（否则多出一列没有意义的编号）
df.to_csv(CLEAN_PATH, index=False)

print()
print("清洗完成！清洗后数据的列：")
print(df.columns.tolist())
print(f"\n清洗后数据已保存到：{CLEAN_PATH}")
print("下一步请运行 03_eda_visualization.py 生成可视化图表。")
