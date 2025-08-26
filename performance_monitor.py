"""性能監控模組"""
import time
import streamlit as st
import psutil
import threading
from datetime import datetime
import pandas as pd

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.memory_usage = []
        self.cpu_usage = []
        self.load_times = {}
        
    def start_monitoring(self):
        """開始性能監控"""
        self.start_time = time.time()
        
    def log_load_time(self, operation_name, start_time):
        """記錄載入時間"""
        load_time = time.time() - start_time
        self.load_times[operation_name] = load_time
        return load_time
    
    def get_system_stats(self):
        """獲取系統統計資訊"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': psutil.virtual_memory().available / (1024**3)
        }
    
    def show_performance_sidebar(self):
        """在側邊欄顯示性能資訊"""
        if st.sidebar.checkbox("🔧 性能監控", value=False):
            stats = self.get_system_stats()
            
            st.sidebar.subheader("系統資源")
            st.sidebar.metric("CPU使用率", f"{stats['cpu_percent']:.1f}%")
            st.sidebar.metric("記憶體使用率", f"{stats['memory_percent']:.1f}%")
            st.sidebar.metric("可用記憶體", f"{stats['memory_available_gb']:.1f}GB")
            
            if self.load_times:
                st.sidebar.subheader("載入時間")
                for operation, load_time in self.load_times.items():
                    st.sidebar.metric(operation, f"{load_time:.2f}秒")

# 全域性能監控器
monitor = PerformanceMonitor()

def time_function(func_name):
    """函數執行時間裝飾器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            load_time = monitor.log_load_time(func_name, start_time)
            
            # 如果載入時間超過5秒，顯示提醒
            if load_time > 5:
                st.info(f"⏱️ {func_name} 載入完成 ({load_time:.1f}秒)")
            
            return result
        return wrapper
    return decorator

@st.cache_data
def get_cached_data(cache_key):
    """通用快取數據獲取"""
    return st.session_state.get(cache_key)

def set_cached_data(cache_key, data):
    """設置快取數據"""
    st.session_state[cache_key] = data

def clear_cache():
    """清除快取"""
    if st.button("🗑️ 清除快取"):
        st.cache_data.clear()
        st.success("✅ 快取已清除")
        st.experimental_rerun()

def optimize_dataframe_display(df, max_rows=1000):
    """優化DataFrame顯示性能"""
    if len(df) > max_rows:
        st.info(f"📊 數據量較大（{len(df)}筆），僅顯示前{max_rows}筆")
        return df.head(max_rows)
    return df

def memory_efficient_calculation(data, chunk_size=10000):
    """記憶體高效的計算方式"""
    if len(data) <= chunk_size:
        return data
    
    # 分塊處理大數據集
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        # 這裡可以添加具體的計算邏輯
        results.append(chunk)
    
    return pd.concat(results)

class ProgressTracker:
    """進度追蹤器"""
    def __init__(self, total_steps, description="處理中..."):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
    def update(self, step_name=""):
        """更新進度"""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        self.progress_bar.progress(progress)
        
        status = f"{self.description} ({self.current_step}/{self.total_steps})"
        if step_name:
            status += f" - {step_name}"
        self.status_text.text(status)
        
    def finish(self):
        """完成進度追蹤"""
        self.progress_bar.empty()
        self.status_text.empty()

def lazy_load_charts():
    """延遲載入圖表"""
    if 'charts_loaded' not in st.session_state:
        st.session_state.charts_loaded = False
    
    if not st.session_state.charts_loaded:
        if st.button("📊 載入進階圖表"):
            st.session_state.charts_loaded = True
            st.experimental_rerun()
    
    return st.session_state.charts_loaded