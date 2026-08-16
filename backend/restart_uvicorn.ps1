# 重启uvicorn服务脚本

Write-Host "正在停止uvicorn服务..." -ForegroundColor Yellow

# 查找并停止uvicorn进程
$uvicornProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }

if ($uvicornProcess) {
    Stop-Process -Id $uvicornProcess.Id -Force
    Write-Host "✓ uvicorn服务已停止" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "未找到运行中的uvicorn进程" -ForegroundColor Yellow
}

Write-Host "`n正在启动uvicorn服务..." -ForegroundColor Yellow
Write-Host "命令: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`n" -ForegroundColor Cyan

# 启动uvicorn（在新窗口中，这样不会阻塞）
Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app","--reload","--host","0.0.0.0","--port","8000" -WorkingDirectory $PWD -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "`n✓ uvicorn服务重启完成！" -ForegroundColor Green
Write-Host "等待服务初始化..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host "`n测试LLM配置..." -ForegroundColor Cyan
python test_llm.py
