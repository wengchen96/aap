import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="AI智能預測系統", layout="centered")
st.title("🤖 AI智能預測系統")

# ===== 歷史資料輸入 =====
raw_text = st.text_area("請貼入歷史資料，每列 10 個號碼（空格或逗號分隔）")

# ===== 選擇預測名次 =====
pred_rank = st.slider("選擇要預測第幾名", 1, 10, 1)

# ===== 選擇預測碼數 =====
num_count = st.slider("選擇要預測碼數 (最多9碼)", 1, 10, 5)
num_count = min(num_count, 9)  # 限制最多9碼

# ===== 開始分析按鈕 =====
if st.button("開始分析"):
    # 解析歷史資料
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error(f"每列必須有 10 個號碼，目前列長度為 {len(row)}")
            st.stop()
        DATA.append([int(x) for x in row])

    if len(DATA) < 1:
        st.warning("請輸入至少一列歷史資料")
        st.stop()

    N = len(DATA)

    st.success(f"成功載入 {N} 期資料")

    # ===== 計算各名次號碼出現次數 =====
    position_counts = {pos: defaultdict(int) for pos in range(10)}
    for row in DATA:
        for idx, num in enumerate(row):
            position_counts[idx][num] += 1

    # ===== 計算預測名次熱冷號 =====
    pred_idx = pred_rank - 1
    counts = position_counts[pred_idx]

    # 排序熱號/冷號
    sorted_counts = sorted(counts.items(), key=lambda x: -x[1])
    hot_numbers = [num for num, _ in sorted_counts[:10]]  # 熱號取前10
    cold_numbers = [num for num, _ in sorted_counts[10:]]  # 冷號剩下為冷號

    # ===== 計算熱冷號數量 =====
    hot_count = round(num_count * 0.85)
    cold_count = num_count - hot_count

    # 避免數量不足
    hot_selected = hot_numbers[:hot_count]
    cold_selected = cold_numbers[:cold_count] if cold_count <= len(cold_numbers) else cold_numbers

    final_numbers = sorted(hot_selected + cold_selected)

    # ===== 顯示預測結果 =====
    st.subheader("🎯 預測結果")
    st.write(f"第 {pred_rank} 名: {', '.join(map(str, final_numbers))}")

    # ===== 計算該名次所有號碼分數及百分比 =====
    POSITION_WEIGHTS = {0:1.5,1:1.3,2:1.1,3:1.0,4:1.0,5:1.0,6:1.0,7:1.1,8:1.3,9:1.5}
    rank_scores = defaultdict(float)
    for row in DATA:
        num = row[pred_idx]
        rank_scores[num] += POSITION_WEIGHTS.get(pred_idx,1.0)

    total_score = sum(rank_scores.values())
    rank_percent = {num: round(rank_scores.get(num,0)/total_score*100,1) for num in range(1,11)}
    df_rank = pd.DataFrame(sorted(rank_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])

    st.subheader(f"📊 預測第 {pred_rank} 名各號碼百分比")
    st.dataframe(df_rank)

    # ===== 顯示中段(3~8名)分析 =====
    mid_counts = defaultdict(int)
    for row in DATA:
        for idx in range(2,8):
            mid_counts[row[idx]] +=1
    mid_percent = {num: round(mid_counts.get(num,0)/ (6*N) *100,1) for num in range(1,11)}
    df_mid = pd.DataFrame(sorted(mid_percent.items(), key=lambda x:-x[1]), columns=["號碼","中段百分比"])
    st.subheader("📊 中段 (第3~8名) 各號碼百分比")
    st.dataframe(df_mid)
