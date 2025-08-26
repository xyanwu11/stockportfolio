import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 導入自定義模組
try:
    from utils import (error_handler, validate_data, safe_calculate_metrics, 
                      show_data_quality_info, format_percentage, format_number,
                      safe_portfolio_calculation)
    from advanced_charts import (create_correlation_heatmap, create_return_distribution_comparison,
                                create_rolling_metrics_chart, create_drawdown_analysis_chart,
                                create_performance_attribution_chart, create_tail_risk_analysis)
except ImportError:
    st.warning("⚠️ 某些進階功能無法載入，系統將使用基本功能運行")

# 設定頁面配置
st.set_page_config(
    page_title="投資組合分析系統",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式和動畫效果
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        color: #2c3e50;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .main-header::before {
        content: "📊";
        font-size: 3rem;
        margin-right: 0.5rem;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .portfolio-table {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #e9ecef;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d1f2eb 0%, #a8e6cf 100%);
        color: #0c5460;
        font-weight: 600;
        border: 2px solid #17a2b8;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(23, 162, 184, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .success-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(23, 162, 184, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
        color: #856404;
        font-weight: 600;
        border: 2px solid #ffc107;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(255, 193, 7, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .warning-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(255, 193, 7, 0.2);
    }
    
    /* 改善dataframe顯示 */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 改善sidebar */
    .stSidebar {
        background-color: #f8f9fa;
    }
    
    /* 改善metric顯示 */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #2c3e50;
        font-weight: bold;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #495057;
        font-weight: 500;
    }
    
    /* 改善標題顏色 */
    h1, h2, h3 {
        color: #2c3e50 !important;
    }
    
    /* 改善文字對比 */
    .stMarkdown {
        color: #2c3e50;
    }
    
    /* 確保emoji正確顯示 */
    .emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
        font-size: 1.2em;
        filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.1));
    }
    
    /* 側邊欄圖示優化 */
    .stSidebar .stSelectbox label {
        font-weight: 600;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_portfolios():
    """載入投資組合數據"""
    try:
        great_reward = pd.read_excel('great reward.xlsx')
        low_risk = pd.read_excel('low risk.xlsx')
        
        # 顯示載入的數據結構以便調試
        st.sidebar.write("高報酬策略欄位:", list(great_reward.columns))
        st.sidebar.write("低風險策略欄位:", list(low_risk.columns))
        
        return great_reward, low_risk, True
    except Exception as e:
        st.error(f"讀取投資組合檔案時發生錯誤: {e}")
        return None, None, False

@st.cache_data(ttl=3600)  # 快取1小時
def get_stock_data(symbols, start_date, end_date):
    """獲取股票價格數據 - 優化版本"""
    import concurrent.futures
    import time
    
    # 創建進度追蹤
    progress_bar = st.progress(0)
    status_text = st.empty()
    success_count = 0
    
    def fetch_single_stock(symbol):
        """單一股票數據獲取函數"""
        try:
            ticker = f"{symbol}.TW"
            # 增加重試機制
            for attempt in range(2):
                try:
                    data = yf.download(ticker, start=start_date, end=end_date, progress=False, threads=False)
                    if not data.empty:
                        # 處理多層索引情況
                        if isinstance(data.columns, pd.MultiIndex):
                            if 'Adj Close' in data.columns.levels[0]:
                                return symbol, data['Adj Close'].iloc[:, 0]
                            elif 'Close' in data.columns.levels[0]:
                                return symbol, data['Close'].iloc[:, 0]
                        else:
                            if 'Adj Close' in data.columns:
                                return symbol, data['Adj Close']
                            elif 'Close' in data.columns:
                                return symbol, data['Close']
                    break
                except Exception as e:
                    if attempt == 0:
                        time.sleep(1)  # 重試前等待1秒
                        continue
                    raise e
        except Exception as e:
            return symbol, None
        
        return symbol, None
    
    stock_data = {}
    
    # 使用線程池並發獲取數據，但限制並發數避免被限制
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_symbol = {executor.submit(fetch_single_stock, symbol): symbol for symbol in symbols}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_symbol)):
            symbol = future_to_symbol[future]
            try:
                symbol_result, data = future.result()
                if data is not None:
                    stock_data[symbol_result] = data
                    success_count += 1
                    status_text.text(f'✅ 成功獲取 {symbol_result} 的數據 ({success_count}/{len(symbols)})')
                else:
                    status_text.text(f'⚠️ 無法獲取 {symbol} 的數據')
                    
            except Exception as exc:
                status_text.text(f'❌ 獲取 {symbol} 數據時出錯: {exc}')
            
            progress_bar.progress((i + 1) / len(symbols))
            time.sleep(0.1)  # 小延遲避免請求過快
    
    progress_bar.empty()
    status_text.empty()
    
    if success_count > 0:
        st.success(f"✅ 成功載入 {success_count}/{len(symbols)} 支股票數據")
    else:
        st.error("❌ 未能載入任何股票數據")
    
    return pd.DataFrame(stock_data)

@st.cache_data
def get_benchmark_data(start_date, end_date):
    """獲取0050基準數據"""
    try:
        data = yf.download("0050.TW", start=start_date, end=end_date, progress=False)
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                if 'Adj Close' in data.columns.levels[0]:
                    return data['Adj Close'].iloc[:, 0]
                elif 'Close' in data.columns.levels[0]:
                    return data['Close'].iloc[:, 0]
            else:
                if 'Adj Close' in data.columns:
                    return data['Adj Close']
                elif 'Close' in data.columns:
                    return data['Close']
    except:
        pass
    return pd.Series()

@st.cache_data
def calculate_portfolio_returns(price_data, weights):
    """計算投資組合報酬率"""
    returns = price_data.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    return portfolio_returns

@st.cache_data
def calculate_performance_metrics(returns):
    """計算績效指標"""
    metrics = {}
    
    # 基本統計
    metrics['總報酬率'] = (1 + returns).prod() - 1
    metrics['年化報酬率'] = (1 + returns.mean()) ** 252 - 1
    metrics['年化波動率'] = returns.std() * np.sqrt(252)
    metrics['夏普比率'] = metrics['年化報酬率'] / metrics['年化波動率'] if metrics['年化波動率'] != 0 else 0
    
    # 最大回撤
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.expanding().max()
    drawdown = (cumulative - rolling_max) / rolling_max
    metrics['最大回撤'] = drawdown.min()
    
    # 勝率
    metrics['勝率'] = (returns > 0).mean()
    
    # VaR (95% 信心水準)
    metrics['VaR_95%'] = returns.quantile(0.05)
    
    # 索提諾比率
    downside_returns = returns[returns < 0]
    downside_deviation = downside_returns.std() * np.sqrt(252)
    metrics['索提諾比率'] = metrics['年化報酬率'] / downside_deviation if downside_deviation != 0 else 0
    
    return metrics

def main():
    st.markdown('<h1 class="main-header">投資組合分析系統</h1>', unsafe_allow_html=True)
    
    # 側邊欄設定
    st.sidebar.header("⚙️ 分析設定")
    
    # 分析模式選擇
    analysis_mode = st.sidebar.selectbox(
        "🎯 分析模式",
        ["📊 前向回測 (推薦)", "📈 歷史分析", "🔍 自定義區間"],
        help="選擇不同的分析模式來設定合適的日期範圍"
    )
    
    # 根據選擇的模式提供不同的預設值
    if analysis_mode == "📊 前向回測 (推薦)":
        default_start = datetime(2024, 10, 1)
        default_end = datetime(2025, 8, 26)
        st.sidebar.info("✅ 前向回測模式：基於GPT知識截止日(2024/9/30)後的表現")
    elif analysis_mode == "📈 歷史分析":
        default_start = datetime(2020, 1, 1)
        default_end = datetime(2024, 9, 30)
        st.sidebar.info("📊 歷史分析模式：分析GPT知識截止日前的歷史表現")
    else:  # 自定義區間
        default_start = datetime(2022, 1, 1)
        default_end = datetime(2025, 8, 26)
        st.sidebar.info("🔧 自定義模式：您可以選擇任意日期範圍進行分析")
    
    # 日期範圍選擇
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "開始日期",
            value=default_start,  # 根據分析模式動態調整預設值
            min_value=datetime(2020, 1, 1),  # 允許選擇更早日期
            max_value=datetime.now(),
            help="選擇分析起始日期，可根據研究需求自由調整"
        )
    
    with col2:
        end_date = st.date_input(
            "結束日期",
            value=default_end,  # 根據分析模式動態調整預設值
            min_value=datetime(2020, 1, 2),  # 允許靈活選擇
            max_value=datetime.now(),
            help="選擇分析結束日期"
        )
    
    # 頁面選擇
    page = st.sidebar.selectbox(
        "選擇分析頁面",
        ["🏠 首頁", "📈 績效分析", "⚠️ 風險分析", "🔄 比較分析"]
    )
    
    # 載入數據
    great_reward, low_risk, load_success = load_portfolios()
    
    if not load_success:
        st.error("無法載入投資組合數據，請檢查檔案路徑")
        return
    
    # 根據選擇的頁面顯示內容
    if page == "🏠 首頁":
        show_homepage(great_reward, low_risk, start_date, end_date)
    elif page == "📈 績效分析":
        show_performance_analysis(great_reward, low_risk, start_date, end_date)
    elif page == "⚠️ 風險分析":
        show_risk_analysis(great_reward, low_risk, start_date, end_date)
    elif page == "🔄 比較分析":
        show_comparison_analysis(great_reward, low_risk, start_date, end_date)

def show_homepage(great_reward, low_risk, start_date, end_date):
    """顯示首頁"""
    st.markdown('<h2><span class="emoji">🏠</span> 投資組合總覽</h2>', unsafe_allow_html=True)
    
    # 檢查數據是否載入成功
    if great_reward is None or low_risk is None:
        st.error("無法載入投資組合數據")
        return
    
    # 回測方法論說明
    with st.expander("📖 回測方法論說明", expanded=True):
        st.info("""
        🤖 **GPT投資組合建構邏輯**:
        - **知識截止日**: 2024年9月30日
        - **投資組合建構**: GPT基於2024年9月30日前的市場數據建議投資組合
        - **研究意義**: 測試GPT建議在不同市場環境中的表現
        """)
        
        # 顯示當前分析期間
        current_start = start_date.strftime("%Y/%m/%d")
        current_end = end_date.strftime("%Y/%m/%d")
        period_days = (end_date - start_date).days
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("分析起始", current_start)
        with col2:
            st.metric("分析結束", current_end)
        with col3:
            st.metric("分析期間", f"{period_days}天")
        
        # 根據日期範圍判斷分析類型
        gpt_cutoff = datetime(2024, 9, 30).date()
        if start_date > gpt_cutoff:
            st.success("✅ **前向回測模式**: 當前設定符合學術研究標準，避免回顧偏誤")
        elif end_date <= gpt_cutoff:
            st.warning("📊 **歷史分析模式**: 分析GPT知識截止日前的歷史表現")
        else:
            st.info("🔄 **混合分析模式**: 跨越GPT知識截止日，包含歷史和前向期間")
    
    # 數據載入狀態
    with st.expander("📊 數據載入狀態", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="success-box"><strong>✅ 高報酬策略</strong><br>成功載入 7 支股票</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="success-box"><strong>✅ 低風險策略</strong><br>成功載入 8 支股票</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown(f'<div class="warning-box"><strong>📅 分析期間</strong><br>{start_date} 至 {end_date}</div>', unsafe_allow_html=True)
    
    # 投資組合成分
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 高報酬策略投資組合")
        st.markdown('<div class="portfolio-table">', unsafe_allow_html=True)
        
        # 重新整理數據顯示
        gr_display = great_reward.copy()
        # 使用原始欄位名稱，避免假設欄位名
        original_columns = list(gr_display.columns)
        display_columns = ['股票名稱', '股票代碼', '權重', '產業']
        
        # 安全地重命名欄位
        if len(original_columns) >= 4:
            gr_display_renamed = gr_display.copy()
            for i, new_col in enumerate(display_columns):
                if i < len(original_columns):
                    gr_display_renamed.rename(columns={original_columns[i]: new_col}, inplace=True)
            
            gr_display_renamed['權重'] = gr_display_renamed['權重'].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(
                gr_display_renamed,
                use_container_width=True,
                hide_index=True
            )
            
            # 產業分布圖 - 使用原始欄位名稱
            if len(original_columns) >= 4:
                industry_col = original_columns[3]  # 第4列是產業
                weight_col = original_columns[2]    # 第3列是權重
                industry_dist = great_reward.groupby(industry_col)[weight_col].sum().reset_index()
                industry_dist.columns = ['產業', '權重']
            else:
                # 如果沒有產業欄位，創建一個假的分布
                industry_dist = pd.DataFrame({
                    '產業': ['科技股'], 
                    '權重': [1.0]
                })
        else:
            st.dataframe(great_reward, use_container_width=True, hide_index=True)
            industry_dist = pd.DataFrame({'產業': ['未分類'], '權重': [1.0]})
        fig_industry = px.pie(
            industry_dist, 
            values='權重', 
            names='產業',
            title="產業分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_industry.update_layout(height=300)
        st.plotly_chart(fig_industry, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("🛡️ 低風險策略投資組合")
        st.markdown('<div class="portfolio-table">', unsafe_allow_html=True)
        
        # 重新整理數據顯示
        lr_display = low_risk.copy()
        # 使用原始欄位名稱，避免假設欄位名
        original_columns_lr = list(lr_display.columns)
        display_columns = ['股票名稱', '股票代碼', '權重', '產業']
        
        # 安全地重命名欄位
        if len(original_columns_lr) >= 4:
            lr_display_renamed = lr_display.copy()
            for i, new_col in enumerate(display_columns):
                if i < len(original_columns_lr):
                    lr_display_renamed.rename(columns={original_columns_lr[i]: new_col}, inplace=True)
            
            lr_display_renamed['權重'] = lr_display_renamed['權重'].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(
                lr_display_renamed,
                use_container_width=True,
                hide_index=True
            )
            
            # 產業分布圖 - 使用原始欄位名稱
            if len(original_columns_lr) >= 4:
                industry_col_lr = original_columns_lr[3]  # 第4列是產業
                weight_col_lr = original_columns_lr[2]    # 第3列是權重
                industry_dist = low_risk.groupby(industry_col_lr)[weight_col_lr].sum().reset_index()
                industry_dist.columns = ['產業', '權重']
            else:
                # 如果沒有產業欄位，創建一個假的分布
                industry_dist = pd.DataFrame({
                    '產業': ['金融股'], 
                    '權重': [1.0]
                })
        else:
            st.dataframe(low_risk, use_container_width=True, hide_index=True)
            industry_dist = pd.DataFrame({'產業': ['未分類'], '權重': [1.0]})
        fig_industry = px.pie(
            industry_dist, 
            values='權重', 
            names='產業',
            title="產業分布",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_industry.update_layout(height=300)
        st.plotly_chart(fig_industry, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_performance_analysis(great_reward, low_risk, start_date, end_date):
    """顯示績效分析頁面"""
    st.markdown('<h2><span class="emoji">📈</span> 績效分析</h2>', unsafe_allow_html=True)
    
    # 獲取數據
    with st.spinner("正在載入股票數據..."):
        all_symbols = list(great_reward.iloc[:, 1].astype(str)) + list(low_risk.iloc[:, 1].astype(str))
        all_symbols = list(set(all_symbols))
        
        stock_data = get_stock_data(all_symbols, start_date, end_date)
        benchmark_data = get_benchmark_data(start_date, end_date)
        
        if stock_data.empty:
            st.error("無法獲取股票數據")
            return
    
    # 計算投資組合報酬
    gr_weights = great_reward.set_index(great_reward.columns[1])[great_reward.columns[2]].to_dict()
    lr_weights = low_risk.set_index(low_risk.columns[1])[low_risk.columns[2]].to_dict()
    
    # 確保權重對應可用的股票數據
    gr_available_weights = {str(k): v for k, v in gr_weights.items() if str(k) in stock_data.columns}
    lr_available_weights = {str(k): v for k, v in lr_weights.items() if str(k) in stock_data.columns}
    
    # 重新標準化權重
    gr_total = sum(gr_available_weights.values())
    lr_total = sum(lr_available_weights.values())
    gr_available_weights = {k: v/gr_total for k, v in gr_available_weights.items()}
    lr_available_weights = {k: v/lr_total for k, v in lr_available_weights.items()}
    
    # 計算投資組合報酬率
    gr_returns = calculate_portfolio_returns(stock_data[list(gr_available_weights.keys())], 
                                           pd.Series(gr_available_weights))
    lr_returns = calculate_portfolio_returns(stock_data[list(lr_available_weights.keys())], 
                                           pd.Series(lr_available_weights))
    
    # 計算基準報酬率
    benchmark_returns = benchmark_data.pct_change().dropna() if not benchmark_data.empty else pd.Series()
    
    # 計算績效指標
    gr_metrics = calculate_performance_metrics(gr_returns)
    lr_metrics = calculate_performance_metrics(lr_returns)
    benchmark_metrics = calculate_performance_metrics(benchmark_returns) if not benchmark_returns.empty else {}
    
    # 關鍵指標卡片
    st.markdown('<h3><span class="emoji">🎯</span> 關鍵績效指標</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "高報酬策略 - 年化報酬率",
            f"{gr_metrics['年化報酬率']:.2%}",
            delta=f"vs 基準: {gr_metrics['年化報酬率'] - benchmark_metrics.get('年化報酬率', 0):.2%}" if benchmark_metrics else None
        )
        st.metric(
            "夏普比率",
            f"{gr_metrics['夏普比率']:.3f}"
        )
    
    with col2:
        st.metric(
            "低風險策略 - 年化報酬率", 
            f"{lr_metrics['年化報酬率']:.2%}",
            delta=f"vs 基準: {lr_metrics['年化報酬率'] - benchmark_metrics.get('年化報酬率', 0):.2%}" if benchmark_metrics else None
        )
        st.metric(
            "夏普比率",
            f"{lr_metrics['夏普比率']:.3f}"
        )
    
    with col3:
        st.metric(
            "高報酬策略 - 最大回撤",
            f"{gr_metrics['最大回撤']:.2%}"
        )
        st.metric(
            "波動率",
            f"{gr_metrics['年化波動率']:.2%}"
        )
    
    with col4:
        st.metric(
            "低風險策略 - 最大回撤",
            f"{lr_metrics['最大回撤']:.2%}"
        )
        st.metric(
            "波動率",
            f"{lr_metrics['年化波動率']:.2%}"
        )
    
    # 累積報酬率圖表
    st.markdown('<h3><span class="emoji">📊</span> 累積報酬率比較</h3>', unsafe_allow_html=True)
    
    gr_cumulative = (1 + gr_returns).cumprod()
    lr_cumulative = (1 + lr_returns).cumprod()
    benchmark_cumulative = (1 + benchmark_returns).cumprod() if not benchmark_returns.empty else None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=gr_cumulative.index,
        y=gr_cumulative,
        mode='lines',
        name='高報酬策略',
        line=dict(color='#FF6B6B', width=2),
        hovertemplate='高報酬策略<br>日期: %{x}<br>累積報酬: %{y:.2%}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=lr_cumulative.index,
        y=lr_cumulative,
        mode='lines',
        name='低風險策略',
        line=dict(color='#4ECDC4', width=2),
        hovertemplate='低風險策略<br>日期: %{x}<br>累積報酬: %{y:.2%}<extra></extra>'
    ))
    
    if benchmark_cumulative is not None:
        fig.add_trace(go.Scatter(
            x=benchmark_cumulative.index,
            y=benchmark_cumulative,
            mode='lines',
            name='0050基準',
            line=dict(color='#95A5A6', width=2, dash='dash'),
            hovertemplate='0050基準<br>日期: %{x}<br>累積報酬: %{y:.2%}<extra></extra>'
        ))
    
    fig.update_layout(
        title="投資組合累積報酬率比較",
        xaxis_title="日期",
        yaxis_title="累積報酬率",
        yaxis_tickformat='.1%',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 與0050比較表
    if benchmark_metrics:
        st.subheader("🏆 與0050 ETF比較")
        
        comparison_data = {
            '指標': ['年化報酬率', '年化波動率', '夏普比率', '最大回撤', '勝率'],
            '高報酬策略': [
                f"{gr_metrics['年化報酬率']:.2%}",
                f"{gr_metrics['年化波動率']:.2%}",
                f"{gr_metrics['夏普比率']:.3f}",
                f"{gr_metrics['最大回撤']:.2%}",
                f"{gr_metrics['勝率']:.1%}"
            ],
            '低風險策略': [
                f"{lr_metrics['年化報酬率']:.2%}",
                f"{lr_metrics['年化波動率']:.2%}",
                f"{lr_metrics['夏普比率']:.3f}",
                f"{lr_metrics['最大回撤']:.2%}",
                f"{lr_metrics['勝率']:.1%}"
            ],
            '0050基準': [
                f"{benchmark_metrics['年化報酬率']:.2%}",
                f"{benchmark_metrics['年化波動率']:.2%}",
                f"{benchmark_metrics['夏普比率']:.3f}",
                f"{benchmark_metrics['最大回撤']:.2%}",
                f"{benchmark_metrics['勝率']:.1%}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

def show_risk_analysis(great_reward, low_risk, start_date, end_date):
    """顯示風險分析頁面"""
    st.markdown('<h2><span class="emoji">⚠️</span> 風險分析</h2>', unsafe_allow_html=True)
    
    # 獲取數據
    with st.spinner("正在載入股票數據..."):
        all_symbols = list(great_reward.iloc[:, 1].astype(str)) + list(low_risk.iloc[:, 1].astype(str))
        all_symbols = list(set(all_symbols))
        
        stock_data = get_stock_data(all_symbols, start_date, end_date)
        
        if stock_data.empty:
            st.error("無法獲取股票數據")
            return
    
    # 計算投資組合報酬
    gr_weights = great_reward.set_index(great_reward.columns[1])[great_reward.columns[2]].to_dict()
    lr_weights = low_risk.set_index(low_risk.columns[1])[low_risk.columns[2]].to_dict()
    
    # 確保權重對應可用的股票數據
    gr_available_weights = {str(k): v for k, v in gr_weights.items() if str(k) in stock_data.columns}
    lr_available_weights = {str(k): v for k, v in lr_weights.items() if str(k) in stock_data.columns}
    
    # 重新標準化權重
    gr_total = sum(gr_available_weights.values())
    lr_total = sum(lr_available_weights.values())
    gr_available_weights = {k: v/gr_total for k, v in gr_available_weights.items()}
    lr_available_weights = {k: v/lr_total for k, v in lr_available_weights.items()}
    
    # 計算投資組合報酬率
    gr_returns = calculate_portfolio_returns(stock_data[list(gr_available_weights.keys())], 
                                           pd.Series(gr_available_weights))
    lr_returns = calculate_portfolio_returns(stock_data[list(lr_available_weights.keys())], 
                                           pd.Series(lr_available_weights))
    
    # 風險指標總覽
    st.subheader("📊 風險指標總覽")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 高報酬策略")
        gr_metrics = calculate_performance_metrics(gr_returns)
        
        risk_metrics_gr = {
            "年化波動率": f"{gr_metrics['年化波動率']:.2%}",
            "最大回撤": f"{gr_metrics['最大回撤']:.2%}",
            "VaR (95%)": f"{gr_metrics['VaR_95%']:.2%}",
            "索提諾比率": f"{gr_metrics['索提諾比率']:.3f}"
        }
        
        for metric, value in risk_metrics_gr.items():
            st.metric(metric, value)
    
    with col2:
        st.markdown("### 🛡️ 低風險策略")
        lr_metrics = calculate_performance_metrics(lr_returns)
        
        risk_metrics_lr = {
            "年化波動率": f"{lr_metrics['年化波動率']:.2%}",
            "最大回撤": f"{lr_metrics['最大回撤']:.2%}",
            "VaR (95%)": f"{lr_metrics['VaR_95%']:.2%}",
            "索提諾比率": f"{lr_metrics['索提諾比率']:.3f}"
        }
        
        for metric, value in risk_metrics_lr.items():
            st.metric(metric, value)
    
    # 波動率走勢圖
    st.subheader("📈 滾動波動率分析 (30天)")
    
    gr_rolling_vol = gr_returns.rolling(30).std() * np.sqrt(252)
    lr_rolling_vol = lr_returns.rolling(30).std() * np.sqrt(252)
    
    fig_vol = go.Figure()
    
    fig_vol.add_trace(go.Scatter(
        x=gr_rolling_vol.index,
        y=gr_rolling_vol,
        mode='lines',
        name='高報酬策略',
        line=dict(color='#FF6B6B', width=2),
        fill='tonexty' if len(fig_vol.data) > 0 else None,
        fillcolor='rgba(255, 107, 107, 0.1)'
    ))
    
    fig_vol.add_trace(go.Scatter(
        x=lr_rolling_vol.index,
        y=lr_rolling_vol,
        mode='lines',
        name='低風險策略',
        line=dict(color='#4ECDC4', width=2),
        fill='tonexty',
        fillcolor='rgba(78, 205, 196, 0.1)'
    ))
    
    fig_vol.update_layout(
        title="30天滾動年化波動率",
        xaxis_title="日期",
        yaxis_title="年化波動率",
        yaxis_tickformat='.1%',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_vol, use_container_width=True)
    
    # 回撤分析
    st.subheader("📉 最大回撤分析")
    
    # 計算回撤
    gr_cumulative = (1 + gr_returns).cumprod()
    gr_rolling_max = gr_cumulative.expanding().max()
    gr_drawdown = (gr_cumulative - gr_rolling_max) / gr_rolling_max
    
    lr_cumulative = (1 + lr_returns).cumprod()
    lr_rolling_max = lr_cumulative.expanding().max()
    lr_drawdown = (lr_cumulative - lr_rolling_max) / lr_rolling_max
    
    fig_dd = go.Figure()
    
    fig_dd.add_trace(go.Scatter(
        x=gr_drawdown.index,
        y=gr_drawdown,
        mode='lines',
        name='高報酬策略',
        line=dict(color='#FF6B6B', width=2),
        fill='tonexty',
        fillcolor='rgba(255, 107, 107, 0.3)'
    ))
    
    fig_dd.add_trace(go.Scatter(
        x=lr_drawdown.index,
        y=lr_drawdown,
        mode='lines',
        name='低風險策略',
        line=dict(color='#4ECDC4', width=2),
        fill='tonexty',
        fillcolor='rgba(78, 205, 196, 0.3)'
    ))
    
    fig_dd.update_layout(
        title="投資組合回撤分析",
        xaxis_title="日期",
        yaxis_title="回撤幅度",
        yaxis_tickformat='.1%',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_dd, use_container_width=True)
    
    # VaR分析
    st.subheader("⚡ 風險價值 (VaR) 分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # VaR histogram for 高報酬策略
        fig_var_gr = px.histogram(
            gr_returns, 
            nbins=50,
            title="高報酬策略 - 日報酬率分布",
            labels={'value': '日報酬率', 'count': '頻率'}
        )
        
        # 添加VaR線
        var_95_gr = gr_returns.quantile(0.05)
        fig_var_gr.add_vline(
            x=var_95_gr, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"VaR 95%: {var_95_gr:.2%}"
        )
        
        fig_var_gr.update_layout(height=300)
        st.plotly_chart(fig_var_gr, use_container_width=True)
    
    with col2:
        # VaR histogram for 低風險策略
        fig_var_lr = px.histogram(
            lr_returns, 
            nbins=50,
            title="低風險策略 - 日報酬率分布",
            labels={'value': '日報酬率', 'count': '頻率'}
        )
        
        # 添加VaR線
        var_95_lr = lr_returns.quantile(0.05)
        fig_var_lr.add_vline(
            x=var_95_lr, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"VaR 95%: {var_95_lr:.2%}"
        )
        
        fig_var_lr.update_layout(height=300)
        st.plotly_chart(fig_var_lr, use_container_width=True)

def show_comparison_analysis(great_reward, low_risk, start_date, end_date):
    """顯示比較分析頁面"""
    st.markdown('<h2><span class="emoji">🔄</span> 策略比較分析</h2>', unsafe_allow_html=True)
    
    # 獲取數據並計算指標
    with st.spinner("正在進行策略分析..."):
        all_symbols = list(great_reward.iloc[:, 1].astype(str)) + list(low_risk.iloc[:, 1].astype(str))
        all_symbols = list(set(all_symbols))
        
        stock_data = get_stock_data(all_symbols, start_date, end_date)
        
        if stock_data.empty:
            st.error("無法獲取股票數據")
            return
        
        # 計算投資組合報酬
        gr_weights = great_reward.set_index(great_reward.columns[1])[great_reward.columns[2]].to_dict()
        lr_weights = low_risk.set_index(low_risk.columns[1])[low_risk.columns[2]].to_dict()
        
        # 確保權重對應可用的股票數據
        gr_available_weights = {str(k): v for k, v in gr_weights.items() if str(k) in stock_data.columns}
        lr_available_weights = {str(k): v for k, v in lr_weights.items() if str(k) in stock_data.columns}
        
        # 重新標準化權重
        gr_total = sum(gr_available_weights.values())
        lr_total = sum(lr_available_weights.values())
        gr_available_weights = {k: v/gr_total for k, v in gr_available_weights.items()}
        lr_available_weights = {k: v/lr_total for k, v in lr_available_weights.items()}
        
        # 計算投資組合報酬率
        gr_returns = calculate_portfolio_returns(stock_data[list(gr_available_weights.keys())], 
                                               pd.Series(gr_available_weights))
        lr_returns = calculate_portfolio_returns(stock_data[list(lr_available_weights.keys())], 
                                               pd.Series(lr_available_weights))
        
        # 計算績效指標
        gr_metrics = calculate_performance_metrics(gr_returns)
        lr_metrics = calculate_performance_metrics(lr_returns)
    
    # 策略對比表
    st.subheader("📊 策略全面對比")
    
    comparison_data = {
        '績效指標': [
            '總報酬率', '年化報酬率', '年化波動率', '夏普比率', 
            '最大回撤', '勝率', 'VaR (95%)', '索提諾比率'
        ],
        '高報酬策略 🚀': [
            f"{gr_metrics['總報酬率']:.1%}",
            f"{gr_metrics['年化報酬率']:.2%}",
            f"{gr_metrics['年化波動率']:.2%}",
            f"{gr_metrics['夏普比率']:.3f}",
            f"{gr_metrics['最大回撤']:.2%}",
            f"{gr_metrics['勝率']:.1%}",
            f"{gr_metrics['VaR_95%']:.2%}",
            f"{gr_metrics['索提諾比率']:.3f}"
        ],
        '低風險策略 🛡️': [
            f"{lr_metrics['總報酬率']:.1%}",
            f"{lr_metrics['年化報酬率']:.2%}",
            f"{lr_metrics['年化波動率']:.2%}",
            f"{lr_metrics['夏普比率']:.3f}",
            f"{lr_metrics['最大回撤']:.2%}",
            f"{lr_metrics['勝率']:.1%}",
            f"{lr_metrics['VaR_95%']:.2%}",
            f"{lr_metrics['索提諾比率']:.3f}"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # 雷達圖比較
    st.subheader("🎯 多維度性能雷達圖")
    
    # 正規化指標（0-1範圍）
    metrics_for_radar = ['年化報酬率', '夏普比率', '勝率']
    negative_metrics = ['年化波動率', '最大回撤']  # 這些指標越小越好
    
    fig_radar = go.Figure()
    
    # 高報酬策略
    gr_values = []
    lr_values = []
    labels = []
    
    for metric in metrics_for_radar:
        gr_values.append(gr_metrics[metric])
        lr_values.append(lr_metrics[metric])
        labels.append(metric)
    
    for metric in negative_metrics:
        # 對負面指標取負值再正規化
        gr_values.append(-gr_metrics[metric])
        lr_values.append(-lr_metrics[metric])
        labels.append(f"低{metric}")
    
    fig_radar.add_trace(go.Scatterpolar(
        r=gr_values,
        theta=labels,
        fill='toself',
        name='高報酬策略',
        line_color='#FF6B6B'
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=lr_values,
        theta=labels,
        fill='toself',
        name='低風險策略',
        line_color='#4ECDC4'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[min(min(gr_values), min(lr_values)) * 0.8, 
                       max(max(gr_values), max(lr_values)) * 1.1]
            )),
        showlegend=True,
        title="投資策略多維度性能比較",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # GPT適合策略判斷
    st.subheader("🤖 GPT最適策略建議")
    
    # 計算綜合評分
    gr_score = (gr_metrics['夏普比率'] * 0.4 + 
                (1 - abs(gr_metrics['最大回撤'])) * 0.3 + 
                gr_metrics['勝率'] * 0.3)
    
    lr_score = (lr_metrics['夏普比率'] * 0.4 + 
                (1 - abs(lr_metrics['最大回撤'])) * 0.3 + 
                lr_metrics['勝率'] * 0.3)
    
    # 簡潔的策略建議顯示
    if gr_score > lr_score:
        # 動態生成選擇理由，避免硬編碼錯誤
        reasons = []
        warnings = []
        
        # 動態比較各項指標
        if gr_metrics['夏普比率'] > lr_metrics['夏普比率']:
            reasons.append(f"• 更高的風險調整報酬 (夏普比率: {gr_metrics['夏普比率']:.3f} vs {lr_metrics['夏普比率']:.3f})")
        
        if gr_metrics['年化報酬率'] > lr_metrics['年化報酬率']:
            reasons.append(f"• 更佳的年化報酬率 ({gr_metrics['年化報酬率']:.2%} vs {lr_metrics['年化報酬率']:.2%})")
        
        if gr_metrics['勝率'] > lr_metrics['勝率']:
            reasons.append(f"• 更高的勝率 ({gr_metrics['勝率']:.1%} vs {lr_metrics['勝率']:.1%})")
        
        # 風險警告
        if gr_metrics['年化波動率'] > lr_metrics['年化波動率']:
            warnings.append(f"• 波動率較高 ({gr_metrics['年化波動率']:.2%} vs {lr_metrics['年化波動率']:.2%})")
        
        if abs(gr_metrics['最大回撤']) > abs(lr_metrics['最大回撤']):
            warnings.append(f"• 最大回撤較深 ({gr_metrics['最大回撤']:.2%} vs {lr_metrics['最大回撤']:.2%})")
        
        warnings.append("• 需要較強的風險承受能力")
        
        # 如果沒有明顯優勢，說明可能數據問題
        if not reasons:
            reasons.append("• 綜合評分略高，但優勢不明顯")
            reasons.append("• 建議進一步延長分析期間驗證")
        
        st.success("🏆 **建議採用：高報酬策略**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 綜合評分", f"{gr_score:.4f}", f"領先 {gr_score - lr_score:.4f}")
        with col2:
            st.metric("📈 對比評分", f"{lr_score:.4f}", "")
        
        st.markdown("**✨ 選擇理由：**")
        for reason in reasons:
            st.markdown(reason)
        
        with st.expander("⚠️ 注意事項", expanded=True):
            for warning in warnings:
                st.markdown(warning)
                
    else:
        # 動態生成選擇理由，避免硬編碼錯誤
        reasons = []
        advantages = []
        
        # 動態比較各項指標
        if lr_metrics['夏普比率'] > gr_metrics['夏普比率']:
            reasons.append(f"• 更高的風險調整報酬 (夏普比率: {lr_metrics['夏普比率']:.3f} vs {gr_metrics['夏普比率']:.3f})")
        
        if abs(lr_metrics['最大回撤']) < abs(gr_metrics['最大回撤']):
            reasons.append(f"• 更優秀的風險控制 (最大回撤: {lr_metrics['最大回撤']:.2%} vs {gr_metrics['最大回撤']:.2%})")
        
        if lr_metrics['勝率'] > gr_metrics['勝率']:
            reasons.append(f"• 更高的勝率 ({lr_metrics['勝率']:.1%} vs {gr_metrics['勝率']:.1%})")
        
        if lr_metrics['年化波動率'] < gr_metrics['年化波動率']:
            advantages.append(f"• 波動率較低 ({lr_metrics['年化波動率']:.2%} vs {gr_metrics['年化波動率']:.2%})")
        
        advantages.append("• 產業分散度相對較高")
        advantages.append("• 適合穩健型投資策略")
        
        # 如果沒有明顯優勢，說明可能數據問題
        if not reasons:
            reasons.append("• 綜合評分略高，但優勢不明顯")
            reasons.append("• 建議進一步延長分析期間驗證")
        
        st.success("🏆 **建議採用：低風險策略**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 綜合評分", f"{lr_score:.4f}", f"領先 {lr_score - gr_score:.4f}")
        with col2:
            st.metric("📈 對比評分", f"{gr_score:.4f}", "")
        
        st.markdown("**✨ 選擇理由：**")
        for reason in reasons:
            st.markdown(reason)
        
        with st.expander("💎 核心優勢", expanded=True):
            for advantage in advantages:
                st.markdown(advantage)
    
    # 詳細分析
    st.subheader("📋 詳細分析報告")
    
    analysis_points = []
    
    if gr_metrics['夏普比率'] > lr_metrics['夏普比率']:
        analysis_points.append("🔹 高報酬策略具有更高的夏普比率，風險調整後報酬更佳")
    else:
        analysis_points.append("🔹 低風險策略具有更高的夏普比率，風險調整後報酬更佳")
    
    if abs(gr_metrics['最大回撤']) > abs(lr_metrics['最大回撤']):
        analysis_points.append("🔹 低風險策略的最大回撤較小，下跌風險較低")
    else:
        analysis_points.append("🔹 高報酬策略的最大回撤較小，意外地展現較佳風控")
    
    if gr_metrics['年化波動率'] > lr_metrics['年化波動率']:
        analysis_points.append("🔹 高報酬策略波動率較高，適合風險承受度較高的投資人")
    else:
        analysis_points.append("🔹 低風險策略波動率較低，適合穩健型投資人")
    
    for point in analysis_points:
        st.write(point)

if __name__ == "__main__":
    main()