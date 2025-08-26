import streamlit as st

st.set_page_config(
    page_title="Emoji測試",
    page_icon="📊",
    layout="wide"
)

# 測試CSS樣式
st.markdown("""
<style>
    .emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Twemoji Mozilla", sans-serif;
        font-size: 1.2em;
        filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.1));
        display: inline-block;
        margin-right: 0.3em;
    }
    
    .test-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
    }
    
    .test-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="test-header"><span class="emoji">📊</span>Emoji顯示測試</h1>', unsafe_allow_html=True)

st.markdown("## 直接Markdown測試")
st.markdown("📊 投資組合分析系統")
st.markdown("📈 績效分析")
st.markdown("⚠️ 風險分析")
st.markdown("🔄 比較分析")

st.markdown("## HTML包裝測試")
st.markdown('<div class="test-item"><span class="emoji">📊</span> 投資組合分析系統</div>', unsafe_allow_html=True)
st.markdown('<div class="test-item"><span class="emoji">📈</span> 績效分析</div>', unsafe_allow_html=True)
st.markdown('<div class="test-item"><span class="emoji">⚠️</span> 風險分析</div>', unsafe_allow_html=True)
st.markdown('<div class="test-item"><span class="emoji">🔄</span> 比較分析</div>', unsafe_allow_html=True)

st.markdown("## Streamlit內建組件測試")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 指標1", "100%")

with col2:
    st.metric("📈 指標2", "25.6%")

with col3:
    st.metric("⚠️ 指標3", "-15.2%")

with col4:
    st.metric("🔄 指標4", "1.25")

st.markdown("## 頁面選項測試")
page_options = ["🏠 首頁", "📈 績效分析", "⚠️ 風險分析", "🔄 比較分析"]
selected_page = st.selectbox("選擇頁面", page_options)
st.write(f"選擇的頁面: {selected_page}")

st.markdown("## 系統資訊")
st.write("如果上述emoji都能正常顯示，表示系統支援emoji。如果顯示為方塊或問號，可能需要安裝emoji字型包。")