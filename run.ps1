# В оболочке PowerShell, перед тем как запускать скрипт, выполнить команду,
# разрешающую выполнение неподписанных скриптов для текущего сеанса оболочки:
# Set-ExecutionPolicy RemoteSigned -Scope Process
# затем запуск .\run
$env:FLASK_APP = "leasingco"
$env:FLASK_ENV = "development"
flask run