@echo off

SET PELICAN=pelican.exe
SET PELICANOPTS=-D

SET BASEDIR=%~dp0
SET INPUTDIR=%BASEDIR%content
SET OUTPUTDIR=%BASEDIR%output
SET CONFFILE=%BASEDIR%pelicanconf.py

if "%1"=="html" goto html
if "%1"=="clean" goto clean
if "%1"=="publish_github" goto publish_github
if "%1"=="help" goto help

echo Invalid parameter: %1
goto :help

:html
%PELICAN% %INPUTDIR% -o %OUTPUTDIR% -s %CONFFILE% %PELICANOPTS%
goto :eof

:clean
goto :eof

:publish_github
cd output
git add .
git commit -m "update"
git push origin master
cd ..
goto :eof

:help
echo Usage: %0 [html, clean, publish_github, help]