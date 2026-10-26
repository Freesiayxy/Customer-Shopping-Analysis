# -*- coding: utf-8 -*-
"""
=============================================================
第三步：探索性数据分析与可视化（EDA & Visualization）
=============================================================
本脚本的目标：
    用图表回答几个业务问题：
        1. 男女客户谁的消费力更强？
        2. 哪个年龄段是消费主力？
        3. 哪些商品类别最赚钱？
        4. 销售额随时间怎么变化？（月度趋势）
        5. 客户最喜欢哪种支付方式？
        6. 哪些商场贡献了最多销售额？

运行方式：
    python src/03_eda_visualization.py
    （注意：必须先运行过 02_data_cleaning.py 生成清洗后的数据）

运行结果：
    在 outputs/ 文件夹下生成 6 张 PNG 图表，可直接用在 README 或简历中
"""

import pandas as pd
import matplotlib.pyplot as plt   # matplotlib 是 Python 最经典的画图库
from pathlib import Path

# ---------------- 全局设置 ----------------
plt.rcParams["font.size"] = 11          # 图表字体大小
plt.rcParams["figure.dpi"] = 120        # 图表清晰度

# 定义一套统一的配色，让图表风格一致、更专业
COLOR_MAIN = "#4C9AFF"
COLOR_ACCENT = "#FF7F50"

# ---------------- 读取清洗后的数据 ----------------
BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_PATH = BASE_DIR / "data" / "customer_shopping_cleaned.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)         # 如果 outputs 文件夹不存在就创建它

df = pd.read_csv(CLEAN_PATH)
print(f"读取清洗后数据：{df.shape[0]} 行 × {df.shape[1]} 列")


# =============================================================
# 图 1：性别 vs 消费总额（谁的消费力更强？）
# =============================================================
# groupby("gender")["revenue"].sum() 的意思：
#   按性别分组 → 取 revenue 列 → 每组求和
gender_revenue = df.groupby("gender")["revenue"].sum()

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(gender_revenue.index, gender_revenue.values, color=[COLOR_MAIN, COLOR_ACCENT])
ax.set_title("Total Revenue by Gender")        # 图表标题
ax.set_ylabel("Total Revenue")                 # 纵轴标题
# 在柱子上方标出具体数值，方便读图
for i, v in enumerate(gender_revenue.values):
    ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom")
plt.tight_layout()                             # 自动调整布局，防止文字被裁掉
plt.savefig(OUTPUT_DIR / "01_gender_revenue.png")
plt.close()                                    # 关掉当前图，释放内存
print("图表已保存：01_gender_revenue.png")


# =============================================================
# 图 2：年龄段消费分布（谁是消费主力？）
# =============================================================
# observed=True 是为了兼容新版 pandas 对分类列分组的提示
age_revenue = df.groupby("age_group", observed=True)["revenue"].sum()

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(age_revenue.index, age_revenue.values, color=COLOR_MAIN)
ax.set_title("Total Revenue by Age Group")
ax.set_ylabel("Total Revenue")
ax.set_xlabel("Age Group")
for i, v in enumerate(age_revenue.values):
    ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "02_age_group_revenue.png")
plt.close()
print("图表已保存：02_age_group_revenue.png")


# =============================================================
# 图 3：商品类别销售额排行（哪些品类最赚钱？）
# =============================================================
category_revenue = df.groupby("category")["revenue"].sum().sort_values()

fig, ax = plt.subplots(figsize=(9, 5))
# 横向条形图（barh）：类别名字长，横着放更好看
ax.barh(category_revenue.index, category_revenue.values, color=COLOR_MAIN)
ax.set_title("Total Revenue by Product Category")
ax.set_xlabel("Total Revenue")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "03_category_revenue.png")
plt.close()
print("图表已保存：03_category_revenue.png")


# =============================================================
# 图 4：月度销售额趋势（生意随时间怎么变？）
# =============================================================
monthly = df.groupby("year_month")["revenue"].sum().sort_index()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly.index, monthly.values, marker="o", markersize=3, color=COLOR_MAIN)
ax.set_title("Monthly Revenue Trend")
ax.set_ylabel("Monthly Revenue")
ax.set_xlabel("Month")
# x 轴标签太多会挤在一起，隔 3 个月显示一个，并旋转 45 度防止重叠
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly.index[::3], rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "04_monthly_trend.png")
plt.close()
print("图表已保存：04_monthly_trend.png")


# =============================================================
# 图 5：支付方式占比（客户喜欢怎么付钱？）
# =============================================================
payment_counts = df["payment_method"].value_counts()

fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    payment_counts.values,
    labels=payment_counts.index,
    autopct="%1.1f%%",                        # 在饼图上显示百分比
    colors=[COLOR_MAIN, COLOR_ACCENT, "#8FD6A1"],
    startangle=90,
)
ax.set_title("Payment Method Distribution")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "05_payment_method.png")
plt.close()
print("图表已保存：05_payment_method.png")


# =============================================================
# 图 6：商场销售额 TOP 榜（哪些商场贡献最大？）
# =============================================================
mall_revenue = df.groupby("shopping_mall")["revenue"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(mall_revenue.index, mall_revenue.values, color=COLOR_MAIN)
ax.set_title("Total Revenue by Shopping Mall")
ax.set_ylabel("Total Revenue")
plt.xticks(rotation=30, ha="right")           # 商场名字较长，旋转一下避免重叠
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "06_mall_revenue.png")
plt.close()
print("图表已保存：06_mall_revenue.png")


# ---------------- 打印关键结论摘要 ----------------
print()
print("=" * 50)
print("分析结论摘要")
print("=" * 50)
print(f"1. 女性客户贡献了 {gender_revenue.get('Female', 0) / gender_revenue.sum():.1%} 的销售额")
print(f"2. 消费力最强的年龄段：{age_revenue.idxmax()}（{age_revenue.max():,.0f}）")
print(f"3. 最赚钱的商品类别：{category_revenue.idxmax()}（{category_revenue.max():,.0f}）")
print(f"4. 最常用的支付方式：{payment_counts.idxmax()}（占 {payment_counts.max() / payment_counts.sum():.1%}）")
print(f"5. 销售额最高的商场：{mall_revenue.idxmax()}（{mall_revenue.max():,.0f}）")
print()
print("下一步请运行 04_rfm_analysis.py 进行客户分群（RFM 分析）。")
