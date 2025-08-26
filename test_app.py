import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="投資組合分析系統測試",
    page_icon="📊",
    layout="wide"
)

st.title("📊 投資組合分析系統")
st.write("這是一個測試頁面，確認Streamlit能正常運行。")

# 測試數據載入
try:
    great_reward = pd.read_excel('great reward.xlsx')
    low_risk = pd.read_excel('low risk.xlsx')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 高報酬策略")
        st.dataframe(great_reward)
    
    with col2:
        st.subheader("🛡️ 低風險策略")
        st.dataframe(low_risk)
        
    st.success("✅ 數據載入成功！主要app.py應該能正常運行。")
    
except Exception as e:
    st.error(f"❌ 數據載入錯誤: {e}")
    st.info("請確保Excel檔案存在且格式正確。")

# 測試圖表
st.subheader("📈 測試圖表")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['高報酬策略', '低風險策略', '基準'])

st.line_chart(chart_data)