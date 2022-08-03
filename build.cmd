@echo off
setlocal

if "%1"=="" goto :BUILD
goto %1

:CLEAN
del PyDeck.spec
rd /s /q .\build
rd /s /q .\dist
goto :EOF

:BUILD
pyinstaller --clean -F -c -i PyDeck.ico -n PyDeck src\main.py
goto :EOF

:RELEASE
call :CLEAN
call :BUILD
for /f "tokens=2 delims==' " %%a in ('findstr /R /C:"^_version[ ]*=[ ]*'.*'$" /X "src\main.py"') do set "__VER__=%%~a"
echo.
echo Release version: %__VER__%
echo.
copy /y PyDeck.stpl dist\
copy /y PyDeck.yaml dist\
copy /y README.md dist\
copy /y CHANGELOG.md dist\
xcopy /y icon\* dist\icon\
xcopy /y static\css\* dist\static\css\
xcopy /y static\js\* dist\static\js\
if not exist dist\static\screenshot\ mkdir dist\static\screenshot\

cd dist
zip -r ..\PyDeck-%__VER__%-win-x64.zip .\*
cd ..

goto :EOF
