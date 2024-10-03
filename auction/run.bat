@echo off
PowerShell -NoExit -Command "& {cd 'E:\MyExperiments\auction'; .\venv\Scripts\Activate.ps1; streamlit run .\test.py}"

