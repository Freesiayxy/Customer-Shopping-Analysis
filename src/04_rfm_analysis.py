# -*- coding: utf-8 -*-
"""
=============================================================
第四步：客户分群 —— RFM 模型分析
=============================================================
什么是 RFM？
    RFM 是互联网和零售行业最经典的客户价值分析模型，用三个指标衡量客户：
        R (Recency)  最近一次消费：客户距今多久没来了？越近越好
        F (Frequency) 消费频率：客户一共来买过几次？越多越好
        M (Monetary) 消费金额：客户一共花了多少钱？越多越好

    把每个客户在这三个维度上打分，就能把客户分成：
    “高价值客户”“需要挽留的客户”“新客户”等群体，针对性运营。

运行方式：
    python src/04_rfm_analysis.py
    （注意：必须先运行过 02_data_cleaning.py）

运行结果：
    1. outputs/rfm_results.csv  —— 每个客户的 RFM 得分和所属分层
    2. outputs/07_rfm_segment.png —— 客户分层人数图
    3. outputs/08_rfm_scatter.png —— 消费频率 vs 消费金额散点图
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["font.size"] = 11
plt.rcParams["figure.dpi"] = 120

# ---------------- 读取清洗后的数据 ----------------
BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_PATH = BASE_DIR / "data" / "customer_shopping_cleaned.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(CLEAN_PATH, parse_dates=["invoice_date"])  # parse_dates：读入时就把日期列转回日期类型
print(f"读取数据：{df.shape[0]} 行，共 {df['customer_id'].nunique()} 位客户")

# ---------------- 1. 计算每个客户的 R、F、M ----------------
# 计算“距今多少天”需要一个参照日期。
# 惯例做法：取数据里最新的一笔交易日期 + 1 天，假装那是“今天”
snapshot_date = df["invoice_date"].max() + pd.Timedelta(days=1)
print(f"参照日期（快照日）：{snapshot_date.date()}")

# groupby("customer_id") 按客户分组，然后分别计算三个指标
rfm = df.groupby("customer_id").agg(
    # R：快照日 - 最后一次消费日期 = 多少天没来（越小越好）
    Recency=("invoice_date", lambda x: (snapshot_date - x.max()).days),
    # F：该客户有多少张不同的发票 = 消费次数
    Frequency=("invoice_no", "nunique"),
    # M：该客户所有消费金额的总和
    Monetary=("revenue", "sum"),
).reset_index()

print("\nRFM 指标预览：")
print(rfm.head())

# ---------------- 2. 给 R、F、M 打分（1~4 分） ----------------
# pd.qcut() 按“分位数”把数据切成 4 份，每份人数差不多：
#   排前 25% 的得 4 分，以此类推
# 注意：R 是“越小越好”，所以打分方向要反过来（labels 从 4 到 1）
# rank(method="first") 是为了处理数值重复导致无法均分的情况
rfm["R_score"] = pd.qcut(rfm["Recency"].rank(method="first"), q=4, labels=[4, 3, 2, 1])
rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
rfm["M_score"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4])

# 把三个分数拼成一个字符串，例如 "444" 表示三项全优
rfm["RFM_score"] = (
    rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)
)

# ---------------- 3. 根据得分划分客户分层 ----------------
def segment_customer(row):
    """根据 RFM 三项得分，给客户贴标签（分层规则可自行调整）"""
    r = int(row["R_score"])
    f = int(row["F_score"])
    m = int(row["M_score"])
    avg = (r + f + m) / 3  # 三项平均分，作为综合价值参考

    if r == 4 and f >= 3 and m >= 3:
        return "Champions 高价值客户"        # 最近常来、花得多 —— 核心资产
    elif r >= 3 and f >= 3:
        return "Loyal 忠实客户"              # 常来的老客户
    elif r == 4 and avg >= 2:
        return "Potential 潜力客户"          # 最近来过但还不频繁
    elif r <= 2 and f >= 3 and m >= 3:
        return "At Risk 流失预警客户"        # 曾经很优质，但很久没来了
    elif r <= 2 and avg < 2.5:
        return "Hibernating 沉睡客户"        # 很久没来、消费也少
    else:
        return "Others 一般客户"

# apply() 会把上面这个函数用到每一行上，axis=1 表示“按行处理”
rfm["Segment"] = rfm.apply(segment_customer, axis=1)

# ---------------- 4. 保存每个客户的结果 ----------------
rfm.to_csv(OUTPUT_DIR / "rfm_results.csv", index=False)
print(f"\n每个客户的 RFM 明细已保存到：{OUTPUT_DIR / 'rfm_results.csv'}")

# ---------------- 5. 各分层的人数和消费贡献 ----------------
# 统计每个分层有多少人、贡献了多少销售额
segment_summary = rfm.groupby("Segment").agg(
    客户数=("customer_id", "count"),
    消费总额=("Monetary", "sum"),
).sort_values("消费总额", ascending=False)
segment_summary["人数占比"] = segment_summary["客户数"] / segment_summary["客户数"].sum()
segment_summary["销售额占比"] = segment_summary["消费总额"] / segment_summary["消费总额"].sum()

print("\n各客户分层概览：")
print(segment_summary.round(3))

# ---------------- 6. 图 7：各分层客户人数 ----------------
seg_counts = rfm["Segment"].value_counts()

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(seg_counts.index, seg_counts.values, color="#4C9AFF")
ax.set_title("Customer Segments (RFM)")
ax.set_xlabel("Number of Customers")
for i, v in enumerate(seg_counts.values):
    ax.text(v, i, f" {v}", va="center")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "07_rfm_segment.png")
plt.close()
print("图表已保存：07_rfm_segment.png")

# ---------------- 7. 图 8：消费频率 vs 消费金额散点图 ----------------
# 每个点代表一位客户；颜色深浅代表“多久没来”（R 越小颜色越深 = 高价值）
fig, ax = plt.subplots(figsize=(9, 6))
scatter = ax.scatter(
    rfm["Frequency"], rfm["Monetary"],
    c=rfm["Recency"],            # 用 Recency 的值决定颜色
    cmap="RdYlGn_r",             # 红黄绿色系，_r 表示反转（红色=很久没来）
    alpha=0.5, s=15,             # 透明度和点的大小
)
ax.set_title("Frequency vs Monetary (colored by Recency)")
ax.set_xlabel("Frequency (number of invoices)")
ax.set_ylabel("Monetary (total spend)")
fig.colorbar(scatter, label="Recency (days since last purchase)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "08_rfm_scatter.png")
plt.close()
print("图表已保存：08_rfm_scatter.png")

print()
print("RFM 分析完成！项目的全部分析流程已跑通。")
