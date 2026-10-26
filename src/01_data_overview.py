# -*- coding: utf-8 -*-
"""
=============================================================
第一步：数据初探（Data Overview）
=============================================================
本脚本的目标：
    在对数据做任何修改之前，先“看一看”数据长什么样。
    这是所有数据分析项目的第一步，叫做 EDA（探索性数据分析）的准备工作。

运行方式：
    在项目根目录（customer-shopping-analysis 文件夹）下打开终端，执行：
        python src/01_data_overview.py

你会看到：
    1. 数据有多少行、多少列
    2. 每一列的名字和数据类型
    3. 前 5 行数据
    4. 数值列的统计信息（平均值、最大最小值等）
    5. 缺失值和重复行的数量
"""

# ---------------- 导入工具库 ----------------
# pandas 是 Python 里处理表格数据最常用的库，我们给它起个别名叫 pd（行业惯例）
import pandas as pd

# pathlib 用来处理文件路径，保证脚本不管在哪个文件夹下运行都能找到数据
from pathlib import Path

# ---------------- 定位数据文件 ----------------
# __file__ 表示“当前这个脚本文件”的位置
# .resolve() 把它变成绝对路径
# .parents[1] 表示“往上退一级目录”（本脚本在 src/ 里，退一级就是项目根目录）
BASE_DIR = Path(__file__).resolve().parents[1]

# 拼接出数据文件的完整路径：项目根目录/data/customer_shopping_data.csv
DATA_PATH = BASE_DIR / "data" / "customer_shopping_data.csv"

# ---------------- 1. 读取数据 ----------------
# pd.read_csv() 把 CSV 文件读成一个 DataFrame（可以理解为“程序里的 Excel 表格”）
df = pd.read_csv(DATA_PATH)

# ---------------- 2. 数据的基本规模 ----------------
print("=" * 50)
print("1. 数据规模（行数, 列数）")
print("=" * 50)
# .shape 返回一个元组：(行数, 列数)
print(df.shape)
print(f"也就是说：一共有 {df.shape[0]} 条购物记录，每条记录有 {df.shape[1]} 个字段。\n")

# ---------------- 3. 每列的名字和类型 ----------------
print("=" * 50)
print("2. 每一列的名字和数据类型")
print("=" * 50)
# .info() 会打印列名、非空值数量、数据类型（int64=整数，float64=小数，object=文本）
df.info()
print()

# ---------------- 4. 看看前几行长什么样 ----------------
print("=" * 50)
print("3. 前 5 行数据预览")
print("=" * 50)
# .head() 默认显示前 5 行，像 Excel 里只看最上面几行一样
print(df.head())
print()

# ---------------- 5. 数值列的统计摘要 ----------------
print("=" * 50)
print("4. 数值列的统计信息（年龄、数量、单价）")
print("=" * 50)
# .describe() 自动计算：数量、平均值、标准差、最小值、四分位数、最大值
print(df.describe().round(2))
print()

# ---------------- 6. 数据质量检查：缺失值 & 重复行 ----------------
print("=" * 50)
print("5. 缺失值检查（每列有多少个空值）")
print("=" * 50)
# .isnull() 把每个格子变成 True(空)/False(不空)，.sum() 统计每列 True 的数量
print(df.isnull().sum())
print()

print("=" * 50)
print("6. 完全重复的行数")
print("=" * 50)
# .duplicated() 标记整行完全重复的记录，.sum() 统计有多少条
print(f"重复行数量：{df.duplicated().sum()}")
print()

# ---------------- 7. 分类列的取值预览 ----------------
# 对于文本类型的列，我们想知道“这一列都有哪些取值”，比如性别有几种、商场有哪几个
print("=" * 50)
print("7. 各分类列的取值分布")
print("=" * 50)
# 遍历几个我们关心的分类列
for col in ["gender", "category", "payment_method", "shopping_mall"]:
    print(f"--- {col} ---")
    # .value_counts() 统计每个取值出现了多少次（类似 Excel 的数据透视表计数）
    print(df[col].value_counts())
    print()

print("数据初探完成！下一步请运行 02_data_cleaning.py 进行数据清洗。")
