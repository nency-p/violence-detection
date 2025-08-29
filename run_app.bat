@echo off
echo Starting Violence Detection System...
echo.

echo Starting Flask server on port 5000...
start /B python app.py

echo Waiting for Flask server to initialize...
timeout /t 3 /nobreak >nul

echo Starting Streamlit dashboard on port 8501...
start /B streamlit run dashboard.py --server.port 8501 --server.headless true

echo Waiting for Streamlit dashboard to initialize...
timeout /t 5 /nobreak >nul

echo Opening browser to the application...
start http://localhost:5000

echo.
echo Both servers are now running!
echo - Main application: http://localhost:5000
echo - CSV dashboard: http://localhost:8501
echo.
echo Press any key to stop both servers...
pause >nul

echo Stopping servers...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im streamlit.exe >nul 2>&1
echo Servers stopped.