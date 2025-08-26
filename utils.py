import streamlit as st
import pandas as pd
import numpy as np
from functools import wraps
import traceback
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('portfolio_analysis.log'),
        logging.StreamHandler()
    ]
)

def error_handler(func):
    """通用錯誤處理裝飾器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"函數 {func.__name__} 發生錯誤: {str(e)}"
            logging.error(f"{error_msg}\n{traceback.format_exc()}")
            
            # 在Streamlit中顯示友善的錯誤訊息
            st.error(f"❌ {error_msg}")
            st.expander("詳細錯誤資訊", expanded=False).code(traceback.format_exc())
            
            return None
    return wrapper

def validate_data(df, required_columns, df_name="DataFrame"):
    """驗證DataFrame的完整性"""
    if df is None or df.empty:
        st.error(f"❌ {df_name} 為空或不存在")
        return False
    
    missing_columns = []
    for i, col in enumerate(required_columns):
        if i >= len(df.columns):
            missing_columns.append(f"第{i+1}列({col})")
    
    if missing_columns:
        st.warning(f"⚠️ {df_name} 缺少必要欄位: {', '.join(missing_columns)}")
        return False
    
    return True

def safe_calculate_metrics(returns, metric_name="績效指標"):
    """安全計算績效指標"""
    try:
        if returns is None or len(returns) == 0:
            st.warning(f"⚠️ {metric_name} 計算失敗: 報酬率數據為空")
            return {}
        
        if returns.isna().all():
            st.warning(f"⚠️ {metric_name} 計算失敗: 所有報酬率數據都是NaN")
            return {}
        
        # 移除NaN值
        clean_returns = returns.dropna()
        if len(clean_returns) == 0:
            st.warning(f"⚠️ {metric_name} 計算失敗: 清理後的報酬率數據為空")
            return {}
        
        metrics = {}
        
        # 基本統計
        try:
            metrics['總報酬率'] = (1 + clean_returns).prod() - 1
        except:
            metrics['總報酬率'] = 0
        
        try:
            metrics['年化報酬率'] = (1 + clean_returns.mean()) ** 252 - 1
        except:
            metrics['年化報酬率'] = 0
        
        try:
            metrics['年化波動率'] = clean_returns.std() * np.sqrt(252)
        except:
            metrics['年化波動率'] = 0
        
        try:
            metrics['夏普比率'] = metrics['年化報酬率'] / metrics['年化波動率'] if metrics['年化波動率'] != 0 else 0
        except:
            metrics['夏普比率'] = 0
        
        # 最大回撤
        try:
            cumulative = (1 + clean_returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            metrics['最大回撤'] = drawdown.min()
        except:
            metrics['最大回撤'] = 0
        
        # 勝率
        try:
            metrics['勝率'] = (clean_returns > 0).mean()
        except:
            metrics['勝率'] = 0.5
        
        # VaR
        try:
            metrics['VaR_95%'] = clean_returns.quantile(0.05)
        except:
            metrics['VaR_95%'] = 0
        
        # 索提諾比率
        try:
            downside_returns = clean_returns[clean_returns < 0]
            if len(downside_returns) > 0:
                downside_deviation = downside_returns.std() * np.sqrt(252)
                metrics['索提諾比率'] = metrics['年化報酬率'] / downside_deviation if downside_deviation != 0 else 0
            else:
                metrics['索提諾比率'] = metrics['年化報酬率'] * 10  # 如果沒有負報酬，給一個高分
        except:
            metrics['索提諾比率'] = 0
        
        return metrics
        
    except Exception as e:
        st.error(f"❌ {metric_name} 計算時發生嚴重錯誤: {str(e)}")
        logging.error(f"計算 {metric_name} 時發生錯誤: {str(e)}\n{traceback.format_exc()}")
        return {}

def show_data_quality_info(df, name):
    """顯示數據品質資訊"""
    if df is None or df.empty:
        st.warning(f"⚠️ {name} 數據為空")
        return
    
    with st.expander(f"📊 {name} 數據品質資訊", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("總行數", len(df))
            st.metric("總列數", len(df.columns))
        
        with col2:
            nan_count = df.isna().sum().sum()
            st.metric("NaN值總數", nan_count)
            coverage = (1 - nan_count / (len(df) * len(df.columns))) * 100
            st.metric("數據覆蓋率", f"{coverage:.1f}%")
        
        with col3:
            if len(df.columns) > 0:
                date_range = f"{df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}" if hasattr(df.index[0], 'strftime') else "未知日期範圍"
                st.write(f"**日期範圍:**\n{date_range}")

def format_percentage(value, decimals=2):
    """安全格式化百分比"""
    try:
        if pd.isna(value) or value == float('inf') or value == float('-inf'):
            return "N/A"
        return f"{value:.{decimals}%}"
    except:
        return "N/A"

def format_number(value, decimals=2):
    """安全格式化數字"""
    try:
        if pd.isna(value) or value == float('inf') or value == float('-inf'):
            return "N/A"
        return f"{value:.{decimals}f}"
    except:
        return "N/A"

def create_fallback_chart_data():
    """創建備用圖表數據"""
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
    data = {
        '高報酬策略': np.random.normal(1.0002, 0.02, len(dates)).cumprod(),
        '低風險策略': np.random.normal(1.0001, 0.015, len(dates)).cumprod(),
    }
    return pd.DataFrame(data, index=dates)

@error_handler 
def safe_portfolio_calculation(stock_data, weights, portfolio_name):
    """安全計算投資組合報酬"""
    if stock_data is None or stock_data.empty:
        st.error(f"❌ {portfolio_name} 股票數據為空")
        return pd.Series()
    
    if not weights:
        st.error(f"❌ {portfolio_name} 權重資料為空")
        return pd.Series()
    
    # 檢查權重總和
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        st.warning(f"⚠️ {portfolio_name} 權重總和為 {weight_sum:.3f}，自動標準化至1.0")
        weights = {k: v/weight_sum for k, v in weights.items()}
    
    # 計算報酬率
    returns = stock_data.pct_change().dropna()
    
    if returns.empty:
        st.error(f"❌ {portfolio_name} 報酬率計算失敗")
        return pd.Series()
    
    # 確保所有權重對應的股票都存在
    missing_stocks = set(weights.keys()) - set(returns.columns)
    if missing_stocks:
        st.warning(f"⚠️ {portfolio_name} 缺少以下股票數據: {missing_stocks}")
        weights = {k: v for k, v in weights.items() if k not in missing_stocks}
    
    if not weights:
        st.error(f"❌ {portfolio_name} 沒有可用的股票數據")
        return pd.Series()
    
    # 計算投資組合報酬率
    portfolio_returns = (returns[list(weights.keys())] * pd.Series(weights)).sum(axis=1)
    
    return portfolio_returns