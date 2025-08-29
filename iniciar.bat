@echo off
echo.
echo ========================================
echo   🚀 Sistema Ágil - Inicializando...
echo ========================================
echo.

:: Ativar ambiente virtual
call .venv\Scripts\activate.bat

echo ✅ Ambiente virtual ativado
echo.
echo 📁 Módulos disponíveis:
echo    - Vistoria de Veículos (pasta: vistoria)
echo    - [Outros módulos serão adicionados aqui]
echo.
echo 🌐 Para iniciar a vistoria:
echo    cd vistoria
echo    python create_app.py
echo.
echo ========================================
pause
