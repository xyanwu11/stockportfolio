"""配置文件 - 系統參數設定"""

# 快取設定
CACHE_TTL = 3600  # 快取存活時間（秒）

# 數據獲取設定
MAX_WORKERS = 3  # 並發獲取股票數據的最大線程數
RETRY_ATTEMPTS = 2  # 重試次數
REQUEST_DELAY = 0.1  # 請求間延遲（秒）

# 技術指標參數
ROLLING_WINDOW_SHORT = 30  # 短期滾動窗口（日）
ROLLING_WINDOW_LONG = 252  # 長期滾動窗口（日）
TRADING_DAYS_YEAR = 252  # 一年交易日數

# 風險指標參數
VAR_CONFIDENCE_LEVELS = [0.90, 0.95, 0.99, 0.995]
DRAWDOWN_THRESHOLD = 0.02  # 回撤閾值
EXTREME_EVENT_THRESHOLD = 2  # 極端事件閾值（標準差倍數）

# 圖表設定
CHART_HEIGHT_DEFAULT = 500
CHART_HEIGHT_LARGE = 800
CHART_COLORS = {
    'high_return': '#FF6B6B',
    'low_risk': '#4ECDC4',
    'benchmark': '#95A5A6',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}

# 預設日期範圍（基於GPT知識截止日的前向回測）
DEFAULT_START_DATE = '2024-10-01'  # GPT知識截止（2024/9/30）後的回測起點
DEFAULT_END_DATE = '2025-08-26'    # 當前日期
KNOWLEDGE_CUTOFF_DATE = '2024-09-30'  # GPT知識截止日

# 綜合評分權重
SCORE_WEIGHTS = {
    'sharpe_ratio': 0.4,
    'max_drawdown': 0.3,
    'win_rate': 0.3
}

# UI設定
ANIMATION_DURATION = 300  # 動畫持續時間（毫秒）
TRANSITION_EASE = 'cubic-bezier(0.4, 0, 0.2, 1)'

# 錯誤處理設定
LOG_FILE = 'portfolio_analysis.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# 數據驗證設定
MIN_DATA_POINTS = 30  # 最少數據點數
MAX_MISSING_DATA_RATIO = 0.1  # 最大缺失數據比例