@echo off
PowerShell -NoExit -Command "& {.\portfolio_venv\Scripts\Activate.ps1; streamlit run .\app.py}"
pause
exit


