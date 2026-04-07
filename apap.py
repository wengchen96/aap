import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="AI智能預測系統", layout="centered")
st.title("🤖 AI智能預測系統")

# ===== 歷史資料輸入 =====
raw_text = st.text_area("請貼入歷史資料，每列 10 個號碼（空格或逗號分隔）")

# ===== 選擇預測名次 =====
pred_rank = st.slider("選擇要預測第幾名", min_value=1, max_value=10, value=1)

# ===== 選擇預測碼數 =====
pred_count = st.slider("選擇要預測的號碼數 (最多9碼)", min_value=1, max_value=9, value=6)

# ===== 分析按鈕 =====
if st.button("開始分析"):

    # ===== 解析歷史資料 =====
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error(f"每列必須有 10 個號碼，目前列長度為 {len(row)}")
            st.stop()
        DATA.append([int(x) if int(x) != 10 else 0 for x in row])  # 將10改為0

    if len(DATA) < 1:
        st.warning("請輸入至少一列歷史資料")
        st.stop()

    N = len(DATA)
    st.success(f"成功載入 {N} 期資料")

    # ===== 計算選定名次的熱冷號 =====
    pred_idx = pred_rank - 1  # 0-index
    rank_counts = defaultdict(int)
    for row in DATA:
        num = row[pred_idx]
        rank_counts[num] += 1

    # 將號碼依出現次數排序
    sorted_rank = sorted(rank_counts.items(), key=lambda x: x[1], reverse=True)
    hot_count = int(pred_count * 0.85)
    cold_count = pred_count - hot_count

    hot_numbers = [num for num, _ in sorted_rank[:hot_count]]
    cold_numbers = [num for num, _ in sorted_rank[hot_count:hot_count + cold_count]]
    pred_numbers = sorted(hot_numbers + cold_numbers)
    
    # ===== 顯示預測結果 =====
    st.subheader("🎯 預測結果")
    st.write(f"第 {pred_rank} 名 預測號碼: {', '.join(map(str, pred_numbers))}")

    # ===== 計算預測名次分數（所有號碼） =====
    POSITION_WEIGHTS = {0:1.5, 1:1.3, 2:1.1, 3:1.0, 4:1.0, 5:1.0, 6:1.0, 7:1.1, 8:1.3, 9:1.5}
    rank_scores = defaultdict(float)
    for row in DATA:
        num = row[pred_idx]
        rank_scores[num] += POSITION_WEIGHTS.get(pred_idx,1.0)

    total_score = sum(rank_scores.values())
    rank_percent = {num: round(rank_scores.get(num,0)/total_score*100,1) for num in range(0,10)}

    st.subheader(f"📊 第 {pred_rank} 名各號碼分數及機率")
    df_pred = pd.DataFrame(sorted(rank_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])
    st.dataframe(df_pred)

    # ===== 區段機率分析 =====
    front_counts = defaultdict(int)
    middle_counts = defaultdict(int)
    back_counts = defaultdict(int)

    for row in DATA:
        for idx, num in enumerate(row):
            if idx < 5:
                front_counts[num] += 1
            if 2 <= idx <= 7:
                middle_counts[num] += 1
            if idx >=5:
                back_counts[num] +=1

    front_percent = {num: round(front_counts.get(num,0)/N*100,1) for num in range(0,10)}
    middle_percent = {num: round(middle_counts.get(num,0)/N*100,1) for num in range(0,10)}
    back_percent = {num: round(back_counts.get(num,0)/N*100,1) for num in range(0,10)}

    st.subheader("🔥 區段機率分析")
    st.write("前段 (第1~5名)")
    st.dataframe(pd.DataFrame(sorted(front_percent.items()), columns=["號碼","百分比"]))

    st.write("中段 (第3~8名)")
    st.dataframe(pd.DataFrame(sorted(middle_percent.items()), columns=["號碼","百分比"]))

    st.write("後段 (第6~10名)")
    st.dataframe(pd.DataFrame(sorted(back_percent.items()), columns=["號碼","百分比"]))
