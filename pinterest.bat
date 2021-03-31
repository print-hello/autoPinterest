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
echo %ns%>C:\Users\Administrator\Desktop\autoPinterest\boot\config_time.txt

rem if exist Z:\host\autoPinterest\boot\hosts.txt @copy Z:\host\autoPinterest\boot\hosts.txt C:\Windows\System32\drivers\etc\hosts /y

xcopy D:\autoPinterest C:\Users\Administrator\Desktop\autoPinterest /s/e/i/y

xcopy D:\autoPinterest\boot C:\Users\Administrator\Desktop\autoPinterest\boot /s/e/i/y

xcopy D:\autoPinterest\firefox_extension C:\Users\Administrator\Desktop\autoPinterest\firefox_extension /s/e/i/y

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
for /f "delims=" %%a in (C:\Users\Administrator\Desktop\autoPinterest\boot\config_time.txt) do (set  adslzhanghao=%%a)


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
	taskkill /f /im firefox.exe
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
	taskkill /f /im firefox.exe
	ping /n 3 127.1>nul
	start "" "D:\autoPinterest\main.py"
	ping /n 5 127.1>nul
)


goto startcmd