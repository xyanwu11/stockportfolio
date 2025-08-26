import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy import stats

def create_correlation_heatmap(stock_data):
    """創建股票相關性熱圖"""
    if stock_data.empty:
        return None
    
    correlation_matrix = stock_data.pct_change().corr()
    
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="股票間相關性分析"
    )
    
    fig.update_layout(
        title_font_size=16,
        height=600,
        font=dict(size=10)
    )
    
    return fig

def create_return_distribution_comparison(gr_returns, lr_returns):
    """創建報酬率分布比較圖"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('高報酬策略分布', '低風險策略分布', '密度比較', 'Q-Q圖比較'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 直方圖
    fig.add_trace(
        go.Histogram(x=gr_returns, nbinsx=50, name='高報酬策略', 
                    marker_color='rgba(255, 107, 107, 0.7)'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Histogram(x=lr_returns, nbinsx=50, name='低風險策略', 
                    marker_color='rgba(78, 205, 196, 0.7)'),
        row=1, col=2
    )
    
    # 密度圖比較
    gr_hist, gr_bins = np.histogram(gr_returns.dropna(), bins=50, density=True)
    lr_hist, lr_bins = np.histogram(lr_returns.dropna(), bins=50, density=True)
    
    fig.add_trace(
        go.Scatter(x=gr_bins[:-1], y=gr_hist, mode='lines', name='高報酬密度',
                  line=dict(color='#FF6B6B', width=2)),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=lr_bins[:-1], y=lr_hist, mode='lines', name='低風險密度',
                  line=dict(color='#4ECDC4', width=2)),
        row=2, col=1
    )
    
    # Q-Q圖
    gr_sorted = np.sort(gr_returns.dropna())
    lr_sorted = np.sort(lr_returns.dropna())
    
    # 標準化為相同長度
    min_len = min(len(gr_sorted), len(lr_sorted))
    gr_qq = gr_sorted[:min_len] if len(gr_sorted) > min_len else gr_sorted
    lr_qq = lr_sorted[:min_len] if len(lr_sorted) > min_len else lr_sorted
    
    fig.add_trace(
        go.Scatter(x=gr_qq, y=lr_qq, mode='markers', name='實際分布',
                  marker=dict(color='#95A5A6', size=4)),
        row=2, col=2
    )
    
    # 理論線 (45度線)
    min_val = min(min(gr_qq), min(lr_qq))
    max_val = max(max(gr_qq), max(lr_qq))
    fig.add_trace(
        go.Scatter(x=[min_val, max_val], y=[min_val, max_val], 
                  mode='lines', name='理論線',
                  line=dict(color='red', dash='dash')),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="報酬率分布深度分析")
    return fig

def create_rolling_metrics_chart(gr_returns, lr_returns):
    """創建滾動指標圖表"""
    rolling_window = 252  # 一年
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('滾動夏普比率', '滾動Beta (相對於對方)', '滾動相關性'),
        vertical_spacing=0.08
    )
    
    # 滾動夏普比率
    gr_rolling_sharpe = (gr_returns.rolling(rolling_window).mean() * 252) / (gr_returns.rolling(rolling_window).std() * np.sqrt(252))
    lr_rolling_sharpe = (lr_returns.rolling(rolling_window).mean() * 252) / (lr_returns.rolling(rolling_window).std() * np.sqrt(252))
    
    fig.add_trace(
        go.Scatter(x=gr_rolling_sharpe.index, y=gr_rolling_sharpe, 
                  name='高報酬策略', line=dict(color='#FF6B6B')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=lr_rolling_sharpe.index, y=lr_rolling_sharpe,
                  name='低風險策略', line=dict(color='#4ECDC4')),
        row=1, col=1
    )
    
    # 滾動Beta
    rolling_cov = gr_returns.rolling(rolling_window).cov(lr_returns)
    rolling_var_lr = lr_returns.rolling(rolling_window).var()
    rolling_beta = rolling_cov / rolling_var_lr
    
    fig.add_trace(
        go.Scatter(x=rolling_beta.index, y=rolling_beta,
                  name='高報酬 vs 低風險 Beta', line=dict(color='#9B59B6')),
        row=2, col=1
    )
    
    # 滾動相關性
    rolling_corr = gr_returns.rolling(rolling_window).corr(lr_returns)
    
    fig.add_trace(
        go.Scatter(x=rolling_corr.index, y=rolling_corr,
                  name='相關係數', line=dict(color='#E67E22')),
        row=3, col=1
    )
    
    fig.update_layout(height=900, title_text="動態風險指標分析")
    return fig

def create_drawdown_analysis_chart(gr_returns, lr_returns):
    """創建回撤分析圖表"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('回撤持續時間分析', '回撤深度分佈'),
        vertical_spacing=0.12
    )
    
    def calculate_drawdown_periods(returns):
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        
        # 找出回撤期間
        in_drawdown = drawdown < 0
        drawdown_periods = []
        start = None
        
        for i, is_dd in enumerate(in_drawdown):
            if is_dd and start is None:
                start = i
            elif not is_dd and start is not None:
                drawdown_periods.append({
                    'start': start,
                    'end': i,
                    'duration': i - start,
                    'depth': drawdown.iloc[start:i].min()
                })
                start = None
        
        return drawdown_periods
    
    gr_dd_periods = calculate_drawdown_periods(gr_returns)
    lr_dd_periods = calculate_drawdown_periods(lr_returns)
    
    # 回撤持續時間散點圖
    if gr_dd_periods:
        gr_durations = [p['duration'] for p in gr_dd_periods]
        gr_depths = [abs(p['depth']) for p in gr_dd_periods]
        
        fig.add_trace(
            go.Scatter(x=gr_durations, y=gr_depths, mode='markers',
                      name='高報酬策略回撤', marker=dict(color='#FF6B6B', size=8)),
            row=1, col=1
        )
    
    if lr_dd_periods:
        lr_durations = [p['duration'] for p in lr_dd_periods]
        lr_depths = [abs(p['depth']) for p in lr_dd_periods]
        
        fig.add_trace(
            go.Scatter(x=lr_durations, y=lr_depths, mode='markers',
                      name='低風險策略回撤', marker=dict(color='#4ECDC4', size=8)),
            row=1, col=1
        )
    
    # 回撤深度分佈
    if gr_dd_periods and lr_dd_periods:
        fig.add_trace(
            go.Histogram(x=[abs(p['depth']) for p in gr_dd_periods], 
                        name='高報酬回撤深度', alpha=0.7, nbinsx=20,
                        marker_color='rgba(255, 107, 107, 0.7)'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Histogram(x=[abs(p['depth']) for p in lr_dd_periods], 
                        name='低風險回撤深度', alpha=0.7, nbinsx=20,
                        marker_color='rgba(78, 205, 196, 0.7)'),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="持續天數", row=1, col=1)
    fig.update_yaxes(title_text="回撤深度", row=1, col=1)
    fig.update_xaxes(title_text="回撤深度", row=2, col=1)
    fig.update_yaxes(title_text="頻率", row=2, col=1)
    
    fig.update_layout(height=700, title_text="回撤期間深度分析")
    return fig

def create_performance_attribution_chart(stock_data, weights, returns):
    """創建績效歸因圖表"""
    if stock_data.empty or not weights:
        return None
    
    # 計算個股貢獻
    stock_returns = stock_data.pct_change().dropna()
    contributions = {}
    
    for stock, weight in weights.items():
        if stock in stock_returns.columns:
            stock_contribution = stock_returns[stock] * weight
            contributions[stock] = {
                'total_contribution': stock_contribution.sum(),
                'volatility_contribution': stock_contribution.std() * np.sqrt(252),
                'weight': weight
            }
    
    if not contributions:
        return None
    
    # 創建氣泡圖
    stocks = list(contributions.keys())
    total_contribs = [contributions[s]['total_contribution'] for s in stocks]
    vol_contribs = [contributions[s]['volatility_contribution'] for s in stocks]
    weights_list = [contributions[s]['weight'] * 1000 for s in stocks]  # 調整氣泡大小
    
    fig = go.Figure(data=go.Scatter(
        x=vol_contribs,
        y=total_contribs,
        mode='markers+text',
        text=stocks,
        textposition="middle center",
        marker=dict(
            size=weights_list,
            color=total_contribs,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="報酬貢獻"),
            opacity=0.7,
            line=dict(width=2, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>' +
                      '報酬貢獻: %{y:.4f}<br>' +
                      '風險貢獻: %{x:.4f}<br>' +
                      '權重: %{marker.size:.1f}%<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title='投資組合績效歸因分析',
        xaxis_title='風險貢獻 (年化波動率)',
        yaxis_title='報酬貢獻',
        height=600,
        template='plotly_white'
    )
    
    return fig

def create_tail_risk_analysis(gr_returns, lr_returns):
    """創建尾部風險分析"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('極值理論分析', 'Expected Shortfall', '尾部相關性', '極端事件頻率'),
    )
    
    # VaR 和 ES 分析
    confidence_levels = [0.90, 0.95, 0.99, 0.995]
    
    gr_vars = [gr_returns.quantile(1-cl) for cl in confidence_levels]
    lr_vars = [lr_returns.quantile(1-cl) for cl in confidence_levels]
    
    # Expected Shortfall (條件風險價值)
    gr_es = [gr_returns[gr_returns <= gr_returns.quantile(1-cl)].mean() for cl in confidence_levels]
    lr_es = [lr_returns[lr_returns <= lr_returns.quantile(1-cl)].mean() for cl in confidence_levels]
    
    confidence_labels = ['90%', '95%', '99%', '99.5%']
    
    fig.add_trace(
        go.Scatter(x=confidence_labels, y=gr_es, mode='lines+markers',
                  name='高報酬 ES', line=dict(color='#FF6B6B')),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=confidence_labels, y=lr_es, mode='lines+markers',
                  name='低風險 ES', line=dict(color='#4ECDC4')),
        row=1, col=2
    )
    
    # 極端事件頻率 (超過 2 標準差的事件)
    gr_std = gr_returns.std()
    lr_std = lr_returns.std()
    
    gr_extreme_events = len(gr_returns[abs(gr_returns) > 2 * gr_std])
    lr_extreme_events = len(lr_returns[abs(lr_returns) > 2 * lr_std])
    
    fig.add_trace(
        go.Bar(x=['高報酬策略', '低風險策略'], 
               y=[gr_extreme_events, lr_extreme_events],
               marker_color=['#FF6B6B', '#4ECDC4']),
        row=2, col=2
    )
    
    fig.update_layout(height=800, title_text="尾部風險深度分析")
    return fig