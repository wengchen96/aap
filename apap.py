import streamlit as st
import pandas as pd
from collections import defaultdict
import random

# =======================
# 設定
# =======================
st.set_page_config(page_title="AI智能預測系統", layout="centered")
st.title("🤖 AI智能預測系統")

st.sidebar.header("操作說明")
st.sidebar.write("""
1. 每列輸入一個歷史期數，第1~第10名號碼，逗號或空格分隔（0=10）。
2. 選擇預測名次與要預測的碼數。
3. 輸入今日密碼後，點擊『開始分析』即可得到預測結果。
""")

# =======================
# 今日密碼
# =======================
TODAY_PASSWORD = "1234"  # 每天手動修改此值

input_password = st.text_input("請輸入今日密碼", type="password")

# =======================
# 歷史資料輸入
# =======================
raw_text = st.text_area("請貼入歷史資料，每列 10 個號碼（空格或逗號分隔）")

# =======================
# 預測名次與碼數選擇
# =======================
pred_rank = st.slider("選擇要預測第幾名", min_value=1, max_value=10, value=1)
num_count = st.slider("選擇要預測的碼數 (1~9)", min_value=1, max_value=9, value=6)

# =======================
# 開始分析按鈕
# =======================
if st.button("開始分析"):

    # 驗證密碼
    if input_password != TODAY_PASSWORD:
        st.error("密碼錯誤！無法開始分析")
        st.stop()

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

    # =======================
    # 預測名次分數分析（冷熱交互）
    # =======================
    POSITION_WEIGHTS = {0:1.5,1:1.3,2:1.1,3:1.0,4:1.0,5:1.0,6:1.0,7:1.1,8:1.3,9:1.5}
    pred_idx = pred_rank - 1

    # 計算每個號碼在該名次的分數
    rank_scores = defaultdict(float)
    for row in DATA:
        num = row[pred_idx]
        rank_scores[num] += POSITION_WEIGHTS.get(pred_idx,1.0)

    # 排序熱號與冷號
    sorted_rank = sorted(rank_scores.items(), key=lambda x:x[1], reverse=True)
    heat_count = int(num_count * 0.85)
    cold_count = num_count - heat_count
    heat_nums = [num for num,score in sorted_rank[:heat_count]]
    cold_nums = [num for num,score in sorted_rank[-cold_count:]] if cold_count>0 else []
    pred_nums = sorted(heat_nums + cold_nums)
    
    # =======================
    # 顯示預測結果
    # =======================
    st.subheader("🎯 預測結果")
    st.write(f"第 {pred_rank} 名 → 號碼：{', '.join(str(n) if n!=0 else '10' for n in pred_nums)}")

    # =======================
    # 區段分析: 前段/中段/後段
    # =======================
    front_counts = defaultdict(int)
    mid_counts = defaultdict(int)
    back_counts = defaultdict(int)

    for row in DATA:
        for idx,num in enumerate(row):
            if idx < 5:
                front_counts[num] +=1
            elif 2<=idx<=7:
                mid_counts[num] +=1
            else:
                back_counts[num] +=1

    # 計算百分比
    front_percent = {num: round(c/N*100,1) for num,c in front_counts.items()}
    mid_percent = {num: round(c/N*100,1) for num,c in mid_counts.items()}
    back_percent = {num: round(c/N*100,1) for num,c in back_counts.items()}

    # 顯示
    st.subheader("📊 區段機率分析")
    st.write("前段 (1~5名)：")
    df_front = pd.DataFrame(sorted(front_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])
    st.dataframe(df_front)
    
    st.write("中段 (3~8名)：")
    df_mid = pd.DataFrame(sorted(mid_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])
    st.dataframe(df_mid)

    st.write("後段 (6~10名)：")
    df_back = pd.DataFrame(sorted(back_percent.items(), key=lambda x:-x[1]), columns=["號碼","百分比"])
    st.dataframe(df_back)
