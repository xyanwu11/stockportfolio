import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("🚀 啟動投資組合分析系統...")
    print("=" * 50)
    
    try:
        # 切換到正確目錄
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # 檢查必要檔案
        if not os.path.exists('app.py'):
            print("❌ 找不到 app.py")
            return
            
        if not os.path.exists('great reward.xlsx') or not os.path.exists('low risk.xlsx'):
            print("❌ 找不到投資組合Excel檔案")
            return
        
        print("✅ 檔案檢查完成")
        print("📊 啟動Streamlit...")
        print("🌐 瀏覽器將自動打開 http://localhost:8501")
        print("⏹️  按 Ctrl+C 停止服務")
        print("=" * 50)
        
        # 等待一下再打開瀏覽器
        import threading
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 啟動Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 服務已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        print("💡 請嘗試手動執行: python -m streamlit run app.py")

if __name__ == "__main__":
    main()