@echo off
PowerShell -NoExit -Command "& {.\.venv\Scripts\Activate.ps1; streamlit run .\auction.py}"

