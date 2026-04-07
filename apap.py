import streamlit as st
import pandas as pd
from collections import defaultdict
import random

# ===============================
# AI智能預測系統
# ===============================
st.set_page_config(page_title="AI智能預測系統", layout="centered")
st.title("🎯 AI智能預測系統")

# ===== 側邊操作說明 =====
st.sidebar.header("操作說明")
st.sidebar.write("""
1. 每列輸入一個歷史期數，第1~第10名號碼，逗號或空格分隔。
2. 點擊『開始分析』即可獲得預測結果與名次分數。
3. 預測結果依據熱號 85% / 冷號 15% 計算。
""")

# ===== 今日密碼 =====
TODAY_PASSWORD = st.text_input("請輸入今日密碼", type="password")
if TODAY_PASSWORD != "1234":  # 你每天可自行改這個密碼
    st.warning("請輸入正確今日密碼才能開始分析")
    st.stop()

# ===== 歷史資料輸入 =====
raw_text = st.text_area("請貼入歷史資料，每列 10 個號碼（空格或逗號分隔）")

# ===== 預測碼數選擇 =====
pred_count = st.slider("選擇預測碼數", min_value=1, max_value=9, value=6)

# ===== 預測名次選擇 =====
pred_rank = st.slider("選擇要預測第幾名", min_value=1, max_value=10, value=5)

# ===== 開始分析 =====
if st.button("開始分析"):

    # ---- 解析歷史資料 ----
    DATA = []
    for row in raw_text.strip().split("\n"):
        row = row.replace(",", " ").split()
        if len(row) != 10:
            st.error(f"每列必須有 10 個號碼，目前列長度為 {len(row)}")
            st.stop()
        DATA.append([int(x) for x in row])

    if len(DATA) < 1:
        st.warning("請至少輸入一列歷史資料")
        st.stop()

    N = len(DATA)
    st.success(f"成功載入 {N} 期資料")

    # ---- 熱號 / 冷號計算 ----
    pred_idx = pred_rank - 1
    rank_counts = defaultdict(int)
    for row in DATA:
        rank_counts[row[pred_idx]] += 1

    # 按出現次數排序，熱號在前
    sorted_counts = sorted(rank_counts.items(), key=lambda x: -x[1])
    hot_count = int(pred_count * 0.85)
    cold_count = pred_count - hot_count

    hot_numbers = [num for num, cnt in sorted_counts[:hot_count]]
    cold_numbers = [num for num, cnt in sorted_counts[hot_count:]]  # 剩下的當冷號

    # 若冷號不夠，從未出現的號碼補
    all_numbers = set(range(1,11))
    used_numbers = set(hot_numbers + cold_numbers)
    remaining_numbers = list(all_numbers - used_numbers)
    while len(cold_numbers) < cold_count and remaining_numbers:
        cold_numbers.append(remaining_numbers.pop(0))

    final_numbers = hot_numbers + cold_numbers
    final_numbers.sort()  # 小到大

    # ---- 顯示預測結果 ----
    st.subheader("🔥 預測結果")
    st.write(f"第 {pred_rank} 名 預測號碼: {', '.join(map(str, final_numbers))}")

    # ---- 計算預測名次分數 ----
    POSITION_WEIGHTS = {i+0:1.5 if i in [0,9] else 1.3 if i in [1,8] else 1.1 if i in [2,7] else 1.0 for i in range(10)}
    rank_scores = defaultdict(float)
    for row in DATA:
        num = row[pred_idx]
        rank_scores[num] += POSITION_WEIGHTS.get(pred_idx,1.0)

    total_score = sum(rank_scores.values())
    rank_percent = {num: round(rank_scores.get(num,0)/total_score*100,1) for num in range(1,11)}

    st.subheader(f"🎯 預測名次分數 (第 {pred_rank} 名)")
    df_pred_rank = pd.DataFrame(sorted(rank_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])
    st.dataframe(df_pred_rank)

    # ---- 區段機率分析 ----
    front_counts = defaultdict(int)
    middle_counts = defaultdict(int)
    back_counts = defaultdict(int)
    for row in DATA:
        for idx, num in enumerate(row):
            if idx <5:
                front_counts[num] +=1
            elif idx <8:
                middle_counts[num] +=1
            else:
                back_counts[num] +=1
    st.subheader("📊 區段機率分析")
    df_front = pd.DataFrame({ "號碼": list(front_counts.keys()), "前段%": [round(v/N*100,1) for v in front_counts.values()]})
    df_middle = pd.DataFrame({ "號碼": list(middle_counts.keys()), "中段%": [round(v/N*100,1) for v in middle_counts.values()]})
    df_back = pd.DataFrame({ "號碼": list(back_counts.keys()), "後段%": [round(v/N*100,1) for v in back_counts.values()]})

    st.write("前段 (第1~5名)")
    st.dataframe(df_front.sort_values(by="前段%", ascending=False))
    st.write("中段 (第3~8名)")
    st.dataframe(df_middle.sort_values(by="中段%", ascending=False))
    st.write("後段 (第6~10名)")
    st.dataframe(df_back.sort_values(by="後段%", ascending=False))
