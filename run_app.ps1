Write-Host "Starting Portfolio Analysis Web App..." -ForegroundColor Green
Write-Host ""
Write-Host "訪問 http://localhost:8501 來使用分析介面" -ForegroundColor Yellow
Write-Host ""
Write-Host "按 Ctrl+C 停止應用程式" -ForegroundColor Cyan
Write-Host ""

try {
    python -m streamlit run app.py
}
catch {
    Write-Host "錯誤: 無法啟動Streamlit應用程式" -ForegroundColor Red
    Write-Host "請確保已安裝所需套件: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意鍵繼續..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")