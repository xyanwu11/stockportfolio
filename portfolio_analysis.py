import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def load_portfolios():
    """讀取兩個投資組合檔案"""
    try:
        great_reward = pd.read_excel('great reward.xlsx')
        low_risk = pd.read_excel('low risk.xlsx')
        
        print("=== 高報酬策略投資組合 ===")
        print(f"資料形狀: {great_reward.shape}")
        print(f"欄位: {list(great_reward.columns)}")
        print("\n前5筆資料:")
        print(great_reward.head())
        
        print("\n\n=== 低風險策略投資組合 ===")
        print(f"資料形狀: {low_risk.shape}")
        print(f"欄位: {list(low_risk.columns)}")
        print("\n前5筆資料:")
        print(low_risk.head())
        
        return great_reward, low_risk
    
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        return None, None

def get_stock_data(symbols, start_date, end_date):
    """獲取股票價格數據"""
    stock_data = {}
    for symbol in symbols:
        try:
            ticker = f"{symbol}.TW"
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not data.empty:
                # 處理多層索引情況
                if isinstance(data.columns, pd.MultiIndex):
                    if 'Adj Close' in data.columns.levels[0]:
                        stock_data[symbol] = data['Adj Close'].iloc[:, 0]
                    elif 'Close' in data.columns.levels[0]:
                        stock_data[symbol] = data['Close'].iloc[:, 0]
                else:
                    if 'Adj Close' in data.columns:
                        stock_data[symbol] = data['Adj Close']
                    elif 'Close' in data.columns:
                        stock_data[symbol] = data['Close']
                print(f"[OK] 成功獲取 {symbol} 的數據")
            else:
                print(f"[FAIL] 無法獲取 {symbol} 的數據")
        except Exception as e:
            print(f"[ERROR] 獲取 {symbol} 數據時出錯: {e}")
    
    return pd.DataFrame(stock_data)

def calculate_portfolio_returns(price_data, weights):
    """計算投資組合報酬率"""
    returns = price_data.pct_change().dropna()
    portfolio_returns = (returns * weights).sum(axis=1)
    return portfolio_returns

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

def backtest_portfolios(great_reward_df, low_risk_df, start_date='2020-01-01', end_date='2024-08-26'):
    """進行投資組合回測"""
    print("\n=== 開始回測分析 ===")
    
    # 獲取所有股票代碼 (使用列位置避免編碼問題)
    all_symbols = list(great_reward_df.iloc[:, 1].astype(str)) + list(low_risk_df.iloc[:, 1].astype(str))
    all_symbols = list(set(all_symbols))  # 去重
    
    print(f"獲取 {len(all_symbols)} 支股票的歷史數據...")
    stock_data = get_stock_data(all_symbols, start_date, end_date)
    
    if stock_data.empty:
        print("無法獲取股票數據，無法進行回測")
        return None, None
    
    # 準備權重 (使用列位置)
    gr_weights = great_reward_df.set_index(great_reward_df.columns[1])[great_reward_df.columns[2]].to_dict()
    lr_weights = low_risk_df.set_index(low_risk_df.columns[1])[low_risk_df.columns[2]].to_dict()
    
    # 確保權重對應可用的股票數據
    gr_available_weights = {str(k): v for k, v in gr_weights.items() if str(k) in stock_data.columns}
    lr_available_weights = {str(k): v for k, v in lr_weights.items() if str(k) in stock_data.columns}
    
    # 重新標準化權重
    gr_total = sum(gr_available_weights.values())
    lr_total = sum(lr_available_weights.values())
    gr_available_weights = {k: v/gr_total for k, v in gr_available_weights.items()}
    lr_available_weights = {k: v/lr_total for k, v in lr_available_weights.items()}
    
    print(f"高報酬策略可用股票數: {len(gr_available_weights)}")
    print(f"低風險策略可用股票數: {len(lr_available_weights)}")
    
    # 計算投資組合報酬率
    gr_returns = calculate_portfolio_returns(stock_data[list(gr_available_weights.keys())], 
                                           pd.Series(gr_available_weights))
    lr_returns = calculate_portfolio_returns(stock_data[list(lr_available_weights.keys())], 
                                           pd.Series(lr_available_weights))
    
    # 計算績效指標
    gr_metrics = calculate_performance_metrics(gr_returns)
    lr_metrics = calculate_performance_metrics(lr_returns)
    
    return gr_returns, lr_returns, gr_metrics, lr_metrics, stock_data

def plot_performance_comparison(gr_returns, lr_returns, gr_metrics, lr_metrics):
    """繪製績效比較圖"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 累積報酬率比較
    gr_cumulative = (1 + gr_returns).cumprod()
    lr_cumulative = (1 + lr_returns).cumprod()
    
    axes[0, 0].plot(gr_cumulative.index, gr_cumulative, label='高報酬策略', linewidth=2)
    axes[0, 0].plot(lr_cumulative.index, lr_cumulative, label='低風險策略', linewidth=2)
    axes[0, 0].set_title('累積報酬率比較')
    axes[0, 0].set_ylabel('累積報酬率')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # 滾動年化波動率
    gr_rolling_vol = gr_returns.rolling(252).std() * np.sqrt(252)
    lr_rolling_vol = lr_returns.rolling(252).std() * np.sqrt(252)
    
    axes[0, 1].plot(gr_rolling_vol.index, gr_rolling_vol, label='高報酬策略', linewidth=2)
    axes[0, 1].plot(lr_rolling_vol.index, lr_rolling_vol, label='低風險策略', linewidth=2)
    axes[0, 1].set_title('滾動年化波動率 (252天)')
    axes[0, 1].set_ylabel('波動率')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # 回撤分析
    gr_cumulative = (1 + gr_returns).cumprod()
    gr_rolling_max = gr_cumulative.expanding().max()
    gr_drawdown = (gr_cumulative - gr_rolling_max) / gr_rolling_max
    
    lr_cumulative = (1 + lr_returns).cumprod()
    lr_rolling_max = lr_cumulative.expanding().max()
    lr_drawdown = (lr_cumulative - lr_rolling_max) / lr_rolling_max
    
    axes[1, 0].fill_between(gr_drawdown.index, gr_drawdown, 0, alpha=0.3, label='高報酬策略')
    axes[1, 0].fill_between(lr_drawdown.index, lr_drawdown, 0, alpha=0.3, label='低風險策略')
    axes[1, 0].set_title('回撤分析')
    axes[1, 0].set_ylabel('回撤幅度')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # 績效指標比較
    metrics_names = ['年化報酬率', '年化波動率', '夏普比率', '最大回撤', '勝率']
    gr_values = [gr_metrics[name] for name in metrics_names]
    lr_values = [lr_metrics[name] for name in metrics_names]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    axes[1, 1].bar(x - width/2, gr_values, width, label='高報酬策略', alpha=0.8)
    axes[1, 1].bar(x + width/2, lr_values, width, label='低風險策略', alpha=0.8)
    axes[1, 1].set_title('關鍵績效指標比較')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(metrics_names, rotation=45)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('portfolio_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_analysis_report(gr_metrics, lr_metrics):
    """生成分析報告"""
    print("\n" + "="*60)
    print("投資組合績效回測報告")
    print("="*60)
    
    # 績效指標比較表
    comparison_df = pd.DataFrame({
        '高報酬策略': gr_metrics,
        '低風險策略': lr_metrics
    }).T
    
    print("\n[績效指標比較]:")
    print(comparison_df.round(4))
    
    # GPT適合策略分析
    print("\n[GPT策略適合性分析]:")
    
    analysis_points = []
    
    if gr_metrics['夏普比率'] > lr_metrics['夏普比率']:
        analysis_points.append("• 高報酬策略具有更高的夏普比率，風險調整後報酬更佳")
    else:
        analysis_points.append("• 低風險策略具有更高的夏普比率，風險調整後報酬更佳")
    
    if abs(gr_metrics['最大回撤']) > abs(lr_metrics['最大回撤']):
        analysis_points.append("• 低風險策略的最大回撤較小，下跌風險較低")
    else:
        analysis_points.append("• 高報酬策略的最大回撤較小，意外地展現較佳風控")
    
    if gr_metrics['年化波動率'] > lr_metrics['年化波動率']:
        analysis_points.append("• 高報酬策略波動率較高，適合風險承受度較高的投資人")
    else:
        analysis_points.append("• 低風險策略波動率較低，適合穩健型投資人")
    
    # 決定GPT更適合的策略
    gr_score = (gr_metrics['夏普比率'] * 0.4 + 
                (1 - abs(gr_metrics['最大回撤'])) * 0.3 + 
                gr_metrics['勝率'] * 0.3)
    
    lr_score = (lr_metrics['夏普比率'] * 0.4 + 
                (1 - abs(lr_metrics['最大回撤'])) * 0.3 + 
                lr_metrics['勝率'] * 0.3)
    
    for point in analysis_points:
        print(point)
    
    print(f"\n[綜合評分]:")
    print(f"高報酬策略: {gr_score:.4f}")
    print(f"低風險策略: {lr_score:.4f}")
    
    if gr_score > lr_score:
        recommended_strategy = "高報酬策略"
        reason = f"綜合考量夏普比率、最大回撤和勝率，高報酬策略得分更高({gr_score:.4f} vs {lr_score:.4f})"
    else:
        recommended_strategy = "低風險策略"  
        reason = f"綜合考量夏普比率、最大回撤和勝率，低風險策略得分更高({lr_score:.4f} vs {gr_score:.4f})"
    
    print(f"\n[建議GPT採用]: {recommended_strategy}")
    print(f"原因: {reason}")
    
    return recommended_strategy, comparison_df

if __name__ == "__main__":
    great_reward, low_risk = load_portfolios()
    
    if great_reward is not None and low_risk is not None:
        result = backtest_portfolios(great_reward, low_risk)
        if result[0] is not None:
            gr_returns, lr_returns, gr_metrics, lr_metrics, stock_data = result
            
            # 生成報告
            recommended_strategy, comparison_df = generate_analysis_report(gr_metrics, lr_metrics)
            
            # 繪製比較圖
            plot_performance_comparison(gr_returns, lr_returns, gr_metrics, lr_metrics)
            
            print(f"\n[圖表已保存]: portfolio_performance_comparison.png")
        else:
            print("回測失敗，請檢查股票代碼或網路連接")