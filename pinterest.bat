@echo off

ping /n 10 127.1>nul

echo %time%
set now_tme=%time%
set /a hh=%now_tme:~0,2%
set /a mm=%now_tme:~3,2%
set /a ss=%now_tme:~6,2%
set /a ns=(%hh%*60+%mm%)*60+%ss%
echo %hh%-%mm%-%ss%
echo current time  %ns%
echo %ns%>D:\autoPinterest\boot\config_time.txt

rem if exist Z:\host\autoPinterest\boot\hosts.txt @copy Z:\host\autoPinterest\boot\hosts.txt C:\Windows\System32\drivers\etc\hosts /y

xcopy Z:\host\autoPinterest D:\autoPinterest /y

xcopy Z:\host\autoPinterest\boot D:\autoPinterest\boot /y

ping /n 5 127.1>nul
start "" "D:\autoPinterest\main.py"


:startcmd

echo after 150s

ping /n 150 127.1>nul

echo %time%
set now_tme=%time%
set /a hh=%now_tme:~0,2%
set /a mm=%now_tme:~3,2%
set /a ss=%now_tme:~6,2%
set /a ns=(%hh%*60+%mm%)*60+%ss%
echo %hh%-%mm%-%ss%
echo current time  %ns%

echo now times min  %now_tme%
setlocal enabledelayedexpansion
set adslzhanghao=0
for /f "delims=" %%a in (D:\autoPinterest\boot\config_time.txt) do (set  adslzhanghao=%%a)


set /a ns1=%adslzhanghao%
echo text time  %ns1%

set /a tim_flag=%ns%-%ns1%

echo time difference %tim_flag%

if %tim_flag% LSS -180 (
	echo %tim_flag%
	taskkill /f /im python.exe
	taskkill /f /im py.exe
	taskkill /f /im chromedriver.exe
	taskkill /f /im chrome.exe
	taskkill /f /im geckodriver.exe
	ping /n 3 127.1>nul
	
	start "" "D:\autoPinterest\main.py"
	ping /n 5 127.1>nul
)

if %tim_flag% GTR 180 (
	echo %tim_flag%
	taskkill /f /im python.exe
	taskkill /f /im py.exe
	taskkill /f /im chromedriver.exe
	taskkill /f /im chrome.exe
	taskkill /f /im geckodriver.exe
	ping /n 3 127.1>nul
	start "" "D:\autoPinterest\main.py"
	ping /n 5 127.1>nul
)


goto startcmd