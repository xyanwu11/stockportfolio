"""GPT投資組合建構問題診斷分析"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

def analyze_gpt_portfolio_issues(gr_returns_hist, lr_returns_hist, gr_returns_forward, lr_returns_forward, 
                                gr_metrics_hist, lr_metrics_hist, gr_metrics_forward, lr_metrics_forward):
    """分析GPT投資組合建構中的潛在問題"""
    
    st.markdown("## 🔍 GPT投資組合建構問題診斷")
    
    # 1. 時間穩定性分析
    st.subheader("📊 1. 時間穩定性分析 (Temporal Stability)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 歷史期間表現 (2020-2024/9)")
        hist_comparison = pd.DataFrame({
            '指標': ['年化報酬率', '夏普比率', '最大回撤', '勝率'],
            '高報酬策略': [
                f"{gr_metrics_hist.get('年化報酬率', 0):.2%}",
                f"{gr_metrics_hist.get('夏普比率', 0):.3f}",
                f"{gr_metrics_hist.get('最大回撤', 0):.2%}",
                f"{gr_metrics_hist.get('勝率', 0):.1%}"
            ],
            '低風險策略': [
                f"{lr_metrics_hist.get('年化報酬率', 0):.2%}",
                f"{lr_metrics_hist.get('夏普比率', 0):.3f}",
                f"{lr_metrics_hist.get('最大回撤', 0):.2%}",
                f"{lr_metrics_hist.get('勝率', 0):.1%}"
            ]
        })
        st.dataframe(hist_comparison, hide_index=True)
    
    with col2:
        st.markdown("### 🚀 前向期間表現 (2024/10-)")
        forward_comparison = pd.DataFrame({
            '指標': ['年化報酬率', '夏普比率', '最大回撤', '勝率'],
            '高報酬策略': [
                f"{gr_metrics_forward.get('年化報酬率', 0):.2%}",
                f"{gr_metrics_forward.get('夏普比率', 0):.3f}",
                f"{gr_metrics_forward.get('最大回撤', 0):.2%}",
                f"{gr_metrics_forward.get('勝率', 0):.1%}"
            ],
            '低風險策略': [
                f"{lr_metrics_forward.get('年化報酬率', 0):.2%}",
                f"{lr_metrics_forward.get('夏普比率', 0):.3f}",
                f"{lr_metrics_forward.get('最大回撤', 0):.2%}",
                f"{lr_metrics_forward.get('勝率', 0):.1%}"
            ]
        })
        st.dataframe(forward_comparison, hide_index=True)
    
    # 2. 績效穩定性指標
    st.subheader("⚖️ 2. 績效穩定性診斷")
    
    # 計算穩定性指標
    stability_metrics = calculate_stability_metrics(
        gr_metrics_hist, lr_metrics_hist, gr_metrics_forward, lr_metrics_forward
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("高報酬策略穩定性", f"{stability_metrics['gr_stability']:.1%}", 
                  help="數值越高表示前向表現與歷史表現越一致")
    
    with col2:
        st.metric("低風險策略穩定性", f"{stability_metrics['lr_stability']:.1%}",
                  help="數值越高表示前向表現與歷史表現越一致")
    
    with col3:
        overall_stability = (stability_metrics['gr_stability'] + stability_metrics['lr_stability']) / 2
        st.metric("整體穩定性", f"{overall_stability:.1%}",
                  help="兩策略的平均穩定性")
    
    # 3. 潛在問題診斷
    st.subheader("🚨 3. 潛在問題診斷")
    
    problems = diagnose_problems(stability_metrics, gr_metrics_hist, lr_metrics_hist, 
                               gr_metrics_forward, lr_metrics_forward)
    
    for problem in problems:
        if problem['severity'] == 'high':
            st.error(f"🔴 **嚴重問題**: {problem['title']}\n\n{problem['description']}")
        elif problem['severity'] == 'medium':
            st.warning(f"🟡 **中等問題**: {problem['title']}\n\n{problem['description']}")
        else:
            st.info(f"🔵 **輕微問題**: {problem['title']}\n\n{problem['description']}")
    
    # 4. 視覺化比較
    create_stability_visualization(gr_metrics_hist, lr_metrics_hist, gr_metrics_forward, lr_metrics_forward)
    
    # 5. 改善建議
    st.subheader("💡 5. GPT投資組合改善建議")
    
    recommendations = generate_recommendations(problems, stability_metrics)
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"建議 {i}: {rec['title']}", expanded=False):
            st.markdown(rec['content'])
    
    return problems, recommendations

def calculate_stability_metrics(gr_hist, lr_hist, gr_forward, lr_forward):
    """計算穩定性指標"""
    
    def calc_single_stability(hist_metrics, forward_metrics):
        """計算單一策略的穩定性"""
        key_metrics = ['年化報酬率', '夏普比率', '勝率']
        stability_scores = []
        
        for metric in key_metrics:
            hist_val = hist_metrics.get(metric, 0)
            forward_val = forward_metrics.get(metric, 0)
            
            if hist_val != 0:
                # 計算相對穩定性 (越接近1越穩定)
                ratio = min(hist_val, forward_val) / max(abs(hist_val), abs(forward_val), 0.001)
                stability_scores.append(max(0, ratio))
            else:
                stability_scores.append(0)
        
        return np.mean(stability_scores)
    
    return {
        'gr_stability': calc_single_stability(gr_hist, gr_forward),
        'lr_stability': calc_single_stability(lr_hist, lr_forward)
    }

def diagnose_problems(stability_metrics, gr_hist, lr_hist, gr_forward, lr_forward):
    """診斷GPT投資組合的問題"""
    problems = []
    
    # 1. 過擬合問題
    if stability_metrics['gr_stability'] < 0.7 or stability_metrics['lr_stability'] < 0.7:
        problems.append({
            'title': '過擬合問題 (Overfitting)',
            'severity': 'high',
            'description': """
GPT可能過度擬合歷史數據，導致策略在未來市場環境中表現不佳。
- **表現**: 歷史回測優異，但前向表現大幅下降
- **原因**: GPT基於歷史數據中的特定模式建構投資組合，但這些模式在未來可能不再有效
- **影響**: 投資者按GPT建議執行可能面臨預期外的損失
            """
        })
    
    # 2. 風險低估問題
    hist_risk = max(abs(gr_hist.get('最大回撤', 0)), abs(lr_hist.get('最大回撤', 0)))
    forward_risk = max(abs(gr_forward.get('最大回撤', 0)), abs(lr_forward.get('最大回撤', 0)))
    
    if forward_risk > hist_risk * 1.5:
        problems.append({
            'title': '風險低估問題 (Risk Underestimation)',
            'severity': 'high',
            'description': f"""
GPT可能低估了投資組合的真實風險水平。
- **歷史最大回撤**: {hist_risk:.2%}
- **前向最大回撤**: {forward_risk:.2%}
- **風險放大**: {forward_risk/hist_risk:.1f}倍
- **可能原因**: 歷史期間市場環境相對穩定，未充分考慮極端情況
            """
        })
    
    # 3. 市場環境適應性問題
    hist_sharpe_avg = (gr_hist.get('夏普比率', 0) + lr_hist.get('夏普比率', 0)) / 2
    forward_sharpe_avg = (gr_forward.get('夏普比率', 0) + lr_forward.get('夏普比率', 0)) / 2
    
    if forward_sharpe_avg < hist_sharpe_avg * 0.6:
        problems.append({
            'title': '市場環境適應性不足 (Poor Market Adaptability)',
            'severity': 'medium',
            'description': f"""
GPT建構的投資組合可能無法適應新的市場環境。
- **歷史平均夏普比率**: {hist_sharpe_avg:.3f}
- **前向平均夏普比率**: {forward_sharpe_avg:.3f}
- **表現衰退**: {((forward_sharpe_avg/hist_sharpe_avg - 1) * 100):.1f}%
- **可能原因**: 市場結構變化、投資者行為改變、政策環境變化
            """
        })
    
    # 4. 策略區分度問題
    hist_diff = abs(gr_hist.get('年化報酬率', 0) - lr_hist.get('年化報酬率', 0))
    forward_diff = abs(gr_forward.get('年化報酬率', 0) - lr_forward.get('年化報酬率', 0))
    
    if forward_diff < hist_diff * 0.5:
        problems.append({
            'title': '策略區分度降低 (Reduced Strategy Differentiation)',
            'severity': 'medium',
            'description': f"""
GPT建構的高報酬與低風險策略在前向期間的差異化程度降低。
- **歷史策略報酬差異**: {hist_diff:.2%}
- **前向策略報酬差異**: {forward_diff:.2%}
- **區分度下降**: {((forward_diff/hist_diff - 1) * 100):.1f}%
- **問題**: 可能表示策略建構邏輯不夠穩固
            """
        })
    
    # 5. 如果沒有發現問題
    if not problems:
        problems.append({
            'title': '策略表現穩定',
            'severity': 'low',
            'description': """
GPT建構的投資組合在前向回測期間表現相對穩定，未發現明顯問題。
這可能表示：
- GPT對市場的理解相對準確
- 投資組合具有一定的穩健性
- 但仍需持續監控更長期的表現
            """
        })
    
    return problems

def generate_recommendations(problems, stability_metrics):
    """生成改善建議"""
    recommendations = []
    
    if any(p['severity'] == 'high' for p in problems):
        recommendations.append({
            'title': '增強模型穩健性',
            'content': """
### 🔧 技術改善方案:
1. **交叉驗證**: 使用多個時間段進行驗證
2. **滾動窗口**: 定期更新投資組合配置
3. **壓力測試**: 在極端市場情境下測試策略
4. **多因子模型**: 結合更多風險因子進行建構

### 📊 投資組合調整:
- 降低單一股票權重上限 (如10-15%)
- 增加產業分散度
- 考慮加入防禦性資產
- 建立動態再平衡機制
            """
        })
    
    if stability_metrics['gr_stability'] < stability_metrics['lr_stability']:
        recommendations.append({
            'title': '優化高報酬策略',
            'content': """
### 🎯 高報酬策略改善:
1. **降低集中風險**: 減少對科技股的依賴
2. **增加價值因子**: 平衡成長與價值
3. **考慮週期性**: 加入景氣循環考量
4. **風險預算**: 設定更嚴格的風險限制

### 📈 具體建議:
- 台積電權重降至30%以下
- 增加傳統產業權重
- 考慮ESG因子
- 建立停損機制
            """
        })
    
    recommendations.append({
        'title': '建立監控機制',
        'content': """
### 🔍 持續監控指標:
1. **月度檢視**: 追蹤關鍵績效指標
2. **風險預警**: 設定回撤警戒線
3. **市場對標**: 與指數基金比較
4. **再平衡頻率**: 每季或半年調整

### 📋 監控指標:
- 滾動夏普比率 < 0.5 (警告)
- 最大回撤 > 20% (嚴重)
- 與大盤相關性 > 0.9 (過度集中)
- 策略偏離度 > 15% (需要調整)
        """
    })
    
    return recommendations

def create_stability_visualization(gr_hist, lr_hist, gr_forward, lr_forward):
    """創建穩定性視覺化圖表"""
    st.subheader("📊 4. 穩定性視覺化分析")
    
    # 雷達圖比較
    metrics = ['年化報酬率', '夏普比率', '勝率']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('高報酬策略：歷史 vs 前向', '低風險策略：歷史 vs 前向'),
        specs=[[{"type": "polar"}, {"type": "polar"}]]
    )
    
    # 正規化數據到0-1範圍
    def normalize_metrics(metrics_dict, max_vals):
        return [metrics_dict.get(metric, 0) / max_vals[metric] for metric in metrics]
    
    # 計算最大值用於正規化
    all_values = {
        '年化報酬率': [gr_hist.get('年化報酬率', 0), lr_hist.get('年化報酬率', 0), 
                    gr_forward.get('年化報酬率', 0), lr_forward.get('年化報酬率', 0)],
        '夏普比率': [gr_hist.get('夏普比率', 0), lr_hist.get('夏普比率', 0),
                   gr_forward.get('夏普比率', 0), lr_forward.get('夏普比率', 0)],
        '勝率': [gr_hist.get('勝率', 0), lr_hist.get('勝率', 0),
               gr_forward.get('勝率', 0), lr_forward.get('勝率', 0)]
    }
    
    max_vals = {metric: max(values) if max(values) > 0 else 1 for metric, values in all_values.items()}
    
    # 高報酬策略雷達圖
    gr_hist_norm = normalize_metrics(gr_hist, max_vals)
    gr_forward_norm = normalize_metrics(gr_forward, max_vals)
    
    fig.add_trace(go.Scatterpolar(
        r=gr_hist_norm,
        theta=metrics,
        fill='toself',
        name='歷史期間',
        line_color='rgba(255, 107, 107, 0.8)'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatterpolar(
        r=gr_forward_norm,
        theta=metrics,
        fill='toself',
        name='前向期間',
        line_color='rgba(255, 107, 107, 0.4)'
    ), row=1, col=1)
    
    # 低風險策略雷達圖
    lr_hist_norm = normalize_metrics(lr_hist, max_vals)
    lr_forward_norm = normalize_metrics(lr_forward, max_vals)
    
    fig.add_trace(go.Scatterpolar(
        r=lr_hist_norm,
        theta=metrics,
        fill='toself',
        name='歷史期間',
        line_color='rgba(78, 205, 196, 0.8)',
        showlegend=False
    ), row=1, col=2)
    
    fig.add_trace(go.Scatterpolar(
        r=lr_forward_norm,
        theta=metrics,
        fill='toself',
        name='前向期間',
        line_color='rgba(78, 205, 196, 0.4)',
        showlegend=False
    ), row=1, col=2)
    
    fig.update_layout(height=500, title="策略穩定性雷達圖比較")
    st.plotly_chart(fig, use_container_width=True)
    
    # 穩定性解讀
    st.markdown("""
    **圖表解讀**:
    - 實心區域：歷史期間表現
    - 半透明區域：前向期間表現
    - 重疊度越高：策略越穩定
    - 差異越大：可能存在過擬合問題
    """)

# 整合到主應用中的函數
def add_gpt_analysis_page():
    """添加GPT分析頁面到主應用"""
    return "🤖 GPT策略診斷"